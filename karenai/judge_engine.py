"""
KarenAI Judge Engine — quality gate and coaching layer (Step 5).

The Judge analyzes draft emails against retrieved policy context, detects
Goodhart's Law traps (e.g. cheap vouchers), scores assertiveness, and suggests
a next negotiation tactic via the Pollinations text API.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/openai"
POLLINATIONS_GET_URL = "https://text.pollinations.ai/"
REQUEST_TIMEOUT_SECONDS = 90

JUDGE_SYSTEM_PROMPT = """You are "The Judge" and "The Coach" for KarenAI, an autonomous passenger rights assistant.

Your job is to evaluate a DRAFT EMAIL against the RETRIEVED POLICY CONTEXT provided by the user message.

Analyze rigorously:
1. Does the draft cite and leverage the retrieved policy, or is it vague?
2. Goodhart's Law check: Did Karen implicitly accept a cheap voucher, meal coupon, or low-ball offer instead of demanding the full statutory/cash remedy the policy supports?
3. Pushover Score (1–10): 1 = capitulating pushover who thanks the airline; 10 = fierce, professional advocate grounded in policy.
4. Provide a concise verdict (strengths + gaps).
5. Provide exactly ONE sentence "New Tactic" for tomorrow's negotiation.

Respond in this EXACT format (no extra sections):
PUSHOVER_SCORE: X/10
VERDICT: <2-4 sentences>
NEW_TACTIC: <exactly one sentence>
"""


@dataclass(frozen=True)
class JudgeVerdict:
    """Structured output from The Judge."""

    pushover_score: int
    verdict_text: str
    new_tactic: str
    raw_response: str

    def formatted_display(self) -> str:
        """Human-readable block for the UI card."""
        return (
            f"**Pushover Score:** {self.pushover_score}/10\n\n"
            f"{self.verdict_text.strip()}\n\n"
            f"**New Tactic for tomorrow:** {self.new_tactic.strip()}"
        )


def evaluate_draft(policy_context: str, drafted_email: str) -> JudgeVerdict:
    """
    Call Pollinations to act as The Judge and The Coach.

    Parameters
    ----------
    policy_context:
        Retrieved airline rule from the RAG Context Store.
    drafted_email:
        Email draft to evaluate.

    Returns
    -------
    JudgeVerdict
        Parsed score, verdict, and tactic (with safe fallback on API errors).
    """
    user_payload = _build_user_prompt(policy_context, drafted_email)

    try:
        raw = _call_pollinations_openai(user_payload)
        if not raw.strip():
            raw = _call_pollinations_get(user_payload)
        return _parse_judge_response(raw)
    except Exception as exc:
        logger.exception("Judge evaluation failed: %s", exc)
        return _fallback_verdict(policy_context, drafted_email, error=str(exc))


def _build_user_prompt(policy_context: str, drafted_email: str) -> str:
    """Assemble the evaluation brief sent to the model."""
    policy = (policy_context or "No policy context retrieved.").strip()
    draft = (drafted_email or "No draft provided.").strip()
    return (
        "RETRIEVED POLICY CONTEXT:\n"
        f"{policy}\n\n"
        "DRAFT EMAIL TO EVALUATE:\n"
        f"{draft}\n\n"
        "Evaluate the draft now using the required output format."
    )


def _call_pollinations_openai(user_prompt: str) -> str:
    """
    POST to the OpenAI-compatible Pollinations endpoint (preferred for system prompts).
    """
    payload: dict[str, Any] = {
        "model": "openai",
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 600,
        "stream": False,
    }

    response = requests.post(
        POLLINATIONS_TEXT_URL,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    data = response.json()
    return str(data["choices"][0]["message"]["content"])


def _call_pollinations_get(user_prompt: str) -> str:
    """
    Fallback GET endpoint with ``system`` query parameter when POST fails.
    """
    combined = f"{user_prompt}\n\n{JUDGE_SYSTEM_PROMPT}"
    url = f"{POLLINATIONS_GET_URL}{quote(combined[:8000])}"
    response = requests.get(
        url,
        params={"model": "openai", "temperature": 0.4, "system": JUDGE_SYSTEM_PROMPT},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.text


def _parse_judge_response(raw: str) -> JudgeVerdict:
    """Extract score, verdict, and tactic from model output."""
    text = raw.strip()

    score_match = re.search(
        r"PUSHOVER_SCORE:\s*(\d{1,2})\s*/\s*10",
        text,
        re.IGNORECASE,
    )
    verdict_match = re.search(
        r"VERDICT:\s*(.+?)(?=NEW_TACTIC:|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    tactic_match = re.search(
        r"NEW_TACTIC:\s*(.+?)\s*$",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    score = int(score_match.group(1)) if score_match else _infer_score_from_text(text)
    score = max(1, min(10, score))

    verdict = verdict_match.group(1).strip() if verdict_match else text[:500]
    tactic = tactic_match.group(1).strip() if tactic_match else (
        "Escalate in writing and refuse voucher-only settlements until cash compensation is confirmed."
    )

    return JudgeVerdict(
        pushover_score=score,
        verdict_text=verdict,
        new_tactic=tactic,
        raw_response=text,
    )


def _infer_score_from_text(text: str) -> int:
    """Best-effort score when the model omits the structured line."""
    for pattern in (r"(\d{1,2})\s*/\s*10", r"score[:\s]+(\d{1,2})"):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return max(1, min(10, int(match.group(1))))
    return 6


def _fallback_verdict(
    policy_context: str,
    drafted_email: str,
    *,
    error: str = "",
) -> JudgeVerdict:
    """
    Offline heuristic when Pollinations is unreachable.

    Checks for voucher language and policy citations without external API.
    """
    draft_lower = drafted_email.lower()
    policy_lower = policy_context.lower()

    voucher_terms = ("voucher", "coupon", "meal token", "food voucher", "accept your offer")
    cited_policy = any(
        token in draft_lower for token in policy_lower.split()[:8] if len(token) > 4
    )

    score = 7
    if any(term in draft_lower for term in voucher_terms):
        score = 4
    if not cited_policy and policy_context.strip():
        score = max(3, score - 2)

    verdict = (
        "The Judge API was unavailable, so this is a local heuristic review. "
        "The draft appears grounded in retrieved policy."
        if cited_policy
        else "The Judge API was unavailable. Consider citing the retrieved policy more explicitly."
    )
    if error:
        verdict += f" (API: {error[:120]})"

    return JudgeVerdict(
        pushover_score=score,
        verdict_text=verdict,
        new_tactic=(
            "Tomorrow, reply in writing refusing voucher-only remedies and demand "
            "cash compensation aligned with the retrieved policy."
        ),
        raw_response="",
    )
