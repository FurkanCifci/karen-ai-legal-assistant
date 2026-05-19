"""
KarenAI RAG Engine — Context Store architecture (Step 2).

This module implements the **Context Store**: a local, persistent vector database
that holds airline policy snippets. Downstream components (Execution Engine, LLM
drafting) will call ``retrieve_policy()`` to fetch grounded facts before generation.

Architecture (three layers)
---------------------------
1. **Ingestion** — ``init_database()`` converts seed ``Document`` objects (LangChain)
   into ChromaDB records with airline metadata.
2. **Indexing** — ChromaDB computes embeddings and persists them under ``data/chroma``.
3. **Retrieval** — ``retrieve_policy()`` performs metadata-filtered semantic search and
   returns the best-matching policy string.

Not wired to ``app.py`` yet — import from the execution engine in a later step.

Example::

    from karenai.rag_engine import init_database, retrieve_policy

    init_database()
    policy = retrieve_policy("Turkish Airlines", "My flight was cancelled last minute")
    print(policy)
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Context Store paths & collection identity
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_PERSIST_DIR = _PROJECT_ROOT / "data" / "chroma"
COLLECTION_NAME = "airline_policies"

# ---------------------------------------------------------------------------
# Seed policies (dummy snippets for development — not legal advice).
# LangChain ``Document`` models the ingestion payload before vector indexing.
# ---------------------------------------------------------------------------
_SEED_POLICIES: tuple[Document, ...] = (
    Document(
        page_content=(
            "Turkish Airlines cancellation policy: For international flights cancelled "
            "by the carrier, eligible passengers may claim up to $600 in compensation "
            "when rebooking is not offered within 24 hours."
        ),
        metadata={"airline": "Turkish Airlines", "topic": "cancellation"},
    ),
    Document(
        page_content=(
            "Turkish Airlines delay policy: Delays exceeding 5 hours on EU departures "
            "trigger duty-of-care meals, refreshments, and hotel accommodation when an "
            "overnight stay is required."
        ),
        metadata={"airline": "Turkish Airlines", "topic": "delay"},
    ),
    Document(
        page_content=(
            "Pegasus delay policy: For delays under EU261 thresholds, Pegasus typically "
            "offers a food voucher only; cash compensation applies mainly when delay "
            "exceeds 3 hours on eligible routes."
        ),
        metadata={"airline": "Pegasus", "topic": "delay"},
    ),
    Document(
        page_content=(
            "Pegasus cancellation policy: Involuntary cancellations may qualify for "
            "rebooking or refund; monetary compensation is limited compared to full-service "
            "carriers and depends on notice period and route."
        ),
        metadata={"airline": "Pegasus", "topic": "cancellation"},
    ),
    Document(
        page_content=(
            "Lufthansa cancellation policy: Under EU261, cancellations with less than "
            "14 days' notice may entitle passengers to €250–€600 depending on flight "
            "distance, unless extraordinary circumstances apply."
        ),
        metadata={"airline": "Lufthansa", "topic": "cancellation"},
    ),
    Document(
        page_content=(
            "Lufthansa delay policy: Delays over 3 hours on arrival can trigger EU261 "
            "compensation tiers; the airline must also provide care (meals, calls, hotel) "
            "while passengers wait."
        ),
        metadata={"airline": "Lufthansa", "topic": "delay"},
    ),
)


def _default_embedding_function() -> embedding_functions.EmbeddingFunction:
    """Chroma's bundled local model (all-MiniLM-L6-v2) — no external API keys."""
    return embedding_functions.DefaultEmbeddingFunction()


def _get_persistent_client() -> chromadb.PersistentClient:
    """Open (or create) the on-disk Chroma client for the Context Store."""
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(CHROMA_PERSIST_DIR),
        settings=Settings(anonymized_telemetry=False),
    )


def _get_or_create_collection(*, client: chromadb.PersistentClient | None = None) -> Collection:
    """Return the airline policy collection, creating it when missing."""
    chroma_client = client or _get_persistent_client()
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_default_embedding_function(),
        metadata={"description": "KarenAI Context Store — airline policy snippets"},
    )


def _collection_document_count(collection: Collection | None = None) -> int:
    """Return vector count in the policy collection."""
    coll = collection or _get_or_create_collection()
    return coll.count()


def _ingest_documents(collection: Collection, documents: list[Document]) -> int:
    """
    Index LangChain documents into ChromaDB (Context Store write path).

    Each record stores ``page_content`` as the embedded document and copies
    metadata (e.g. ``airline``, ``topic``) for filtered retrieval.
    """
    if not documents:
        return 0

    collection.add(
        ids=[str(uuid.uuid4()) for _ in documents],
        documents=[doc.page_content for doc in documents],
        metadatas=[doc.metadata for doc in documents],
    )
    return len(documents)


def init_database(*, reset: bool = False) -> int:
    """
    Populate the Context Store with seed airline policies.

    Idempotent by default: skips seeding when documents already exist unless
    ``reset=True`` (drops the collection and re-indexes from scratch).

    Returns
    -------
    int
        Number of policy documents in the collection after initialization.
    """
    client = _get_persistent_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            logger.info("Dropped collection %r for rebuild.", COLLECTION_NAME)
        except (ValueError, chromadb.errors.NotFoundError):
            pass

    collection = _get_or_create_collection(client=client)
    existing = _collection_document_count(collection)

    if not reset and existing > 0:
        logger.info(
            "Context Store already initialized (%d documents); skipping seed.",
            existing,
        )
        return existing

    if existing > 0:
        client.delete_collection(COLLECTION_NAME)
        collection = _get_or_create_collection(client=client)

    added = _ingest_documents(collection, list(_SEED_POLICIES))
    logger.info("Context Store seeded with %d policy documents.", added)
    return _collection_document_count(collection)


def retrieve_policy(airline_name: str, issue_text: str) -> str:
    """
    Query the Context Store for the policy most relevant to the user's issue.

    Uses semantic similarity on the issue description, scoped by ``airline`` metadata
    so Turkish Airlines policies are not mixed with Pegasus or Lufthansa rules.

    Parameters
    ----------
    airline_name:
        Carrier label matching seed metadata (e.g. ``"Turkish Airlines"``).
    issue_text:
        Passenger description (cancellation, delay, denied boarding, etc.).

    Returns
    -------
    str
        Top policy text, or a fallback message when no match is found.
    """
    collection = _get_or_create_collection()
    if _collection_document_count(collection) == 0:
        init_database()

    query = _build_retrieval_query(airline_name=airline_name, issue_text=issue_text)

    # Metadata filter = airline-scoped semantic search (core RAG retrieval step).
    results = collection.query(
        query_texts=[query],
        n_results=1,
        where={"airline": airline_name},
    )

    documents = results.get("documents") or []
    if documents and documents[0]:
        return documents[0][0]

    logger.warning(
        "No policy found for airline=%r; falling back to unfiltered search.",
        airline_name,
    )
    fallback = collection.query(query_texts=[query], n_results=1)
    fallback_docs = fallback.get("documents") or []
    if fallback_docs and fallback_docs[0]:
        return fallback_docs[0][0]

    return (
        f"No matching policy found in the Context Store for {airline_name!r}. "
        "Run init_database() to seed policies."
    )


def _build_retrieval_query(*, airline_name: str, issue_text: str) -> str:
    """Merge airline context and issue text into one embedding-friendly query."""
    issue = (issue_text or "").strip()
    if issue:
        return f"{airline_name} passenger rights claim: {issue}"
    return f"{airline_name} general compensation and delay policy"


def get_context_store_info() -> dict[str, Any]:
    """Debug helper: persist path, collection name, and document count."""
    return {
        "persist_directory": str(CHROMA_PERSIST_DIR),
        "collection_name": COLLECTION_NAME,
        "document_count": _collection_document_count(),
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    indexed = init_database(reset=True)
    print(f"Indexed {indexed} policies.\n")
    sample = retrieve_policy(
        "Turkish Airlines",
        "They cancelled my flight and only offered a voucher.",
    )
    print("Retrieved policy:\n", sample)
