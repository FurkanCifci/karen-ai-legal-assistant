"""
Application constants and copy used across the Streamlit UI.

All symbols listed in ``__all__`` are part of the public API — import them via::

    from karenai.config import JUDGING_MESSAGE, LOADING_MESSAGE
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Page & branding
# ---------------------------------------------------------------------------
APP_TITLE: str = "KarenAI"
APP_TAGLINE: str = "Passenger Rights Enforcer"
PAGE_TITLE: str = "KarenAI"
PAGE_ICON: str = "✈️"

# ---------------------------------------------------------------------------
# Airline selection (dropdown)
# ---------------------------------------------------------------------------
AIRLINES: tuple[str, ...] = (
    "Turkish Airlines",
    "Lufthansa",
    "Pegasus",
)

# ---------------------------------------------------------------------------
# Sidebar copy
# ---------------------------------------------------------------------------
ARCHITECTURE_SIDEBAR_MD: str = """
**Execution Engine** orchestrates tools, airline rules, and the end-to-end claim workflow.

**RAG Context Store** retrieves grounded policy snippets from a local vector database before drafting.

**The Judge** scores drafts for pushover risk, Goodhart's Law voucher traps, and suggests your next tactic.
"""

# ---------------------------------------------------------------------------
# Multi-agent pipeline step labels (visual stepper in ui.py)
# ---------------------------------------------------------------------------
PIPELINE_STEP_RAG: tuple[str, str] = ("🔍", "Retrieving Airline Rules from ChromaDB...")
PIPELINE_STEP_DRAFT: tuple[str, str] = ("✍️", "Compiling Legal Complaint Draft...")
PIPELINE_STEP_JUDGE: tuple[str, str] = ("⚖️", "Simulating The Judge & Pushover Risk Analysis...")

# Legacy spinner copy (kept for backwards-compatible imports)
LOADING_MESSAGE: str = "Karen is searching the legal archives..."
JUDGING_MESSAGE: str = "The Judge is reviewing Karen's draft..."

# ---------------------------------------------------------------------------
# Developer branding
# ---------------------------------------------------------------------------
DEVELOPER_NAME: str = "Furkan Cifci"
DEVELOPER_TITLE: str = "Prospect Engineer"
LINKEDIN_URL: str = "https://www.linkedin.com/in/furkan-cifci/"

# ---------------------------------------------------------------------------
# Session-state keys (used in app.py)
# ---------------------------------------------------------------------------
SESSION_DRAFT_VISIBLE: str = "draft_result_visible"
SESSION_LAST_MOCK_EMAIL: str = "last_mock_email"
SESSION_RETRIEVED_POLICY: str = "retrieved_policy"
SESSION_JUDGE_SCORE: str = "judge_pushover_score"
SESSION_JUDGE_VERDICT: str = "judge_verdict_text"
SESSION_JUDGE_TACTIC: str = "judge_new_tactic"

# Bump when adding/removing public constants (helps detect stale .pyc during dev).
CONFIG_VERSION: str = "2026-05-19-dashboard"

__all__: list[str] = [
    "APP_TITLE",
    "APP_TAGLINE",
    "PAGE_TITLE",
    "PAGE_ICON",
    "AIRLINES",
    "ARCHITECTURE_SIDEBAR_MD",
    "PIPELINE_STEP_RAG",
    "PIPELINE_STEP_DRAFT",
    "PIPELINE_STEP_JUDGE",
    "LOADING_MESSAGE",
    "JUDGING_MESSAGE",
    "DEVELOPER_NAME",
    "DEVELOPER_TITLE",
    "LINKEDIN_URL",
    "SESSION_DRAFT_VISIBLE",
    "SESSION_LAST_MOCK_EMAIL",
    "SESSION_RETRIEVED_POLICY",
    "SESSION_JUDGE_SCORE",
    "SESSION_JUDGE_VERDICT",
    "SESSION_JUDGE_TACTIC",
    "CONFIG_VERSION",
]
