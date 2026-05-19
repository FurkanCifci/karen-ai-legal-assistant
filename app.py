"""
KarenAI — world-class multi-agent dashboard (RAG + Judge pipeline).
"""

from __future__ import annotations

from typing import Any

import streamlit as st
from dotenv import load_dotenv

from karenai.config import (
    PAGE_ICON,
    PAGE_TITLE,
    SESSION_DRAFT_VISIBLE,
    SESSION_JUDGE_SCORE,
    SESSION_JUDGE_TACTIC,
    SESSION_JUDGE_VERDICT,
    SESSION_LAST_MOCK_EMAIL,
    SESSION_RETRIEVED_POLICY,
)
from karenai.judge_engine import evaluate_draft
from karenai.mock_response import build_mock_draft_email
from karenai.rag_engine import init_database, retrieve_policy
from karenai.types import StepStatus
from karenai.ui import (
    inject_premium_styles,
    render_claim_form,
    render_hero,
    render_idle_state,
    render_judge_verdict_card,
    render_legal_foundation_card,
    render_pipeline_stepper,
    render_refined_notice_card,
    render_sidebar,
)


def initialise_session_state() -> None:
    """Ensure expected keys exist before widgets read or write them."""
    defaults: dict[str, object] = {
        SESSION_DRAFT_VISIBLE: False,
        SESSION_LAST_MOCK_EMAIL: "",
        SESSION_RETRIEVED_POLICY: "",
        SESSION_JUDGE_SCORE: 0,
        SESSION_JUDGE_VERDICT: "",
        SESSION_JUDGE_TACTIC: "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _update_pipeline(stepper_slot: Any, statuses: list[StepStatus]) -> None:
    """Refresh the visual agent stepper in place."""
    with stepper_slot.container():
        render_pipeline_stepper(statuses)


def process_claim(*, airline: str, issue_text: str) -> None:
    """
    Full multi-agent pipeline with real-time stepper animation.

    1. RAG retrieval (ChromaDB)
    2. Draft compilation
    3. Judge evaluation (Pollinations)
    """
    stepper_slot = st.empty()

    _update_pipeline(stepper_slot, ["active", "pending", "pending"])
    policy = retrieve_policy(airline, issue_text)
    st.session_state[SESSION_RETRIEVED_POLICY] = policy

    _update_pipeline(stepper_slot, ["done", "active", "pending"])
    draft = build_mock_draft_email(
        airline=airline,
        issue_description=issue_text,
        retrieved_policy=policy,
    )
    st.session_state[SESSION_LAST_MOCK_EMAIL] = draft

    _update_pipeline(stepper_slot, ["done", "done", "active"])
    verdict = evaluate_draft(policy, draft)
    st.session_state[SESSION_JUDGE_SCORE] = verdict.pushover_score
    st.session_state[SESSION_JUDGE_VERDICT] = verdict.verdict_text
    st.session_state[SESSION_JUDGE_TACTIC] = verdict.new_tactic

    _update_pipeline(stepper_slot, ["done", "done", "done"])
    st.session_state[SESSION_DRAFT_VISIBLE] = True


def render_results() -> None:
    """Completed pipeline stepper + Cards 1–3."""
    has_results = bool(st.session_state.get(SESSION_DRAFT_VISIBLE))

    if not has_results:
        render_idle_state()
        return

    render_pipeline_stepper(["done", "done", "done"])

    policy = str(st.session_state.get(SESSION_RETRIEVED_POLICY, ""))
    email_body = str(st.session_state.get(SESSION_LAST_MOCK_EMAIL, ""))
    score = int(st.session_state.get(SESSION_JUDGE_SCORE, 0) or 0)
    verdict_text = str(st.session_state.get(SESSION_JUDGE_VERDICT, ""))
    new_tactic = str(st.session_state.get(SESSION_JUDGE_TACTIC, ""))

    if policy:
        render_legal_foundation_card(policy)

    if verdict_text or score:
        render_judge_verdict_card(
            score=score or 6,
            verdict_text=verdict_text or "No verdict returned.",
            new_tactic=new_tactic or "Follow up in writing within 14 days.",
        )

    if email_body:
        render_refined_notice_card(email_body)


def main() -> None:
    load_dotenv()

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="centered",
        initial_sidebar_state="expanded",
    )

    initialise_session_state()
    inject_premium_styles()
    init_database()

    render_sidebar()
    render_hero()

    airline, issue_text, submitted = render_claim_form()

    if submitted:
        process_claim(airline=airline, issue_text=issue_text)

    render_results()


if __name__ == "__main__":
    main()
