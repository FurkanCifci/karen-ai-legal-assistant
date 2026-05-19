"""
KarenAI — Dark Tech dashboard UI (glassmorphism, agent stepper, Judge glows).
"""

from __future__ import annotations

import html
import re

import streamlit as st
import streamlit.components.v1 as components

from karenai.config import (
    AIRLINES,
    APP_TAGLINE,
    APP_TITLE,
    ARCHITECTURE_SIDEBAR_MD,
    DEVELOPER_NAME,
    DEVELOPER_TITLE,
    LINKEDIN_URL,
    PIPELINE_STEP_DRAFT,
    PIPELINE_STEP_JUDGE,
    PIPELINE_STEP_RAG,
)
from karenai.types import StepStatus

__all__ = [
    "StepStatus",
    "inject_premium_styles",
    "render_pipeline_stepper",
    "render_sidebar",
    "render_hero",
    "render_claim_form",
    "render_legal_foundation_card",
    "render_judge_verdict_card",
    "render_refined_notice_card",
    "render_idle_state",
]

_PIPELINE_STEPS: tuple[tuple[str, str], ...] = (
    PIPELINE_STEP_RAG,
    PIPELINE_STEP_DRAFT,
    PIPELINE_STEP_JUDGE,
)

# Single-line SVG — avoids Streamlit markdown breaking multiline HTML
_LINKEDIN_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" '
    'role="img" aria-hidden="true"><path fill="#0A66C2" d="M20.447 20.452h-3.554v-5.569'
    "c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414"
    "v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337"
    " 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9"
    'h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451'
    'C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'
)


def inject_premium_styles() -> None:
    """Dark Tech design system — deep charcoal canvas, glass cards, white typography."""
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

          :root {
            --bg-canvas: #101114;
            --bg-elevated: #121215;
            --glass: rgba(26, 28, 38, 0.62);
            --glass-strong: rgba(32, 34, 46, 0.78);
            --text-primary: #F8F9FA;
            --text-muted: #A8B0C2;
            --text-dim: #7B8499;
            --border-indigo: rgba(100, 108, 255, 0.1);
            --border-focus: rgba(100, 108, 255, 0.45);
            --shadow-glass: 0 10px 40px rgba(0, 0, 0, 0.35);
            --shadow-depth: 0 16px 48px rgba(0, 0, 0, 0.45);
            --radius: 24px;
            --indigo: #646CFF;
            --indigo-glow: rgba(100, 108, 255, 0.35);
            --focus-ring: 0 0 0 3px rgba(100, 108, 255, 0.28);
            --amber-glow: 0 0 0 1px rgba(251, 191, 36, 0.35), 0 12px 40px rgba(245, 158, 11, 0.12);
            --steel-glow: 0 0 0 1px rgba(100, 108, 255, 0.28), 0 12px 40px rgba(99, 102, 241, 0.15);
          }

          html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.01em;
          }

          .stApp {
            background: radial-gradient(ellipse 120% 80% at 50% -20%, #1a1c28 0%, var(--bg-canvas) 55%, #0a0b0d 100%) !important;
            color: var(--text-primary) !important;
            color-scheme: dark;
          }

          .block-container {
            max-width: 720px !important;
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
          }

          header[data-testid="stHeader"] { background: transparent !important; }
          #MainMenu, footer, header[data-testid="stHeader"] nav { visibility: hidden; }

          /* Global typography on dark canvas */
          .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
          h1, h2, h3, h4, h5, h6, label, p {
            color: var(--text-primary);
          }

          /* ── Glass surfaces ───────────────────────────────────────────── */
          .karen-glass,
          .karen-panel,
          .karen-card,
          .agent-pipeline {
            background: var(--glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-indigo);
            border-radius: var(--radius);
            box-shadow: var(--shadow-glass);
          }

          /* ── Form controls (dark glass) ──────────────────────────────── */
          label[data-testid="stWidgetLabel"],
          .stMarkdown p.panel-label {
            color: var(--text-muted) !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase;
            font-size: 0.72rem !important;
          }

          div[data-baseweb="select"] > div,
          .stSelectbox div[data-baseweb="select"] > div {
            background: var(--glass-strong) !important;
            border: 1px solid var(--border-indigo) !important;
            border-radius: 16px !important;
            color: var(--text-primary) !important;
            box-shadow: var(--shadow-glass) !important;
          }

          div[data-baseweb="select"] span,
          div[data-baseweb="select"] input {
            color: var(--text-primary) !important;
            -webkit-text-fill-color: var(--text-primary) !important;
          }

          div[data-baseweb="select"]:focus-within > div {
            border-color: var(--border-focus) !important;
            box-shadow: var(--focus-ring), var(--shadow-depth) !important;
          }

          div[data-baseweb="popover"], ul[role="listbox"] {
            background: #1a1c26 !important;
            border: 1px solid var(--border-indigo) !important;
          }

          ul[role="listbox"] li {
            color: var(--text-primary) !important;
            background: #1a1c26 !important;
          }

          ul[role="listbox"] li:hover,
          ul[role="listbox"] li[aria-selected="true"] {
            background: rgba(100, 108, 255, 0.18) !important;
          }

          .stTextArea textarea,
          div[data-baseweb="textarea"] textarea {
            background: var(--glass-strong) !important;
            border: 1px solid var(--border-indigo) !important;
            border-radius: 20px !important;
            color: var(--text-primary) !important;
            -webkit-text-fill-color: var(--text-primary) !important;
            box-shadow: var(--shadow-glass) !important;
            font-size: 0.96rem !important;
            line-height: 1.6 !important;
          }

          .stTextArea textarea::placeholder {
            color: var(--text-dim) !important;
            opacity: 1 !important;
          }

          .stTextArea textarea:focus,
          div[data-baseweb="textarea"] textarea:focus {
            border-color: var(--border-focus) !important;
            box-shadow: var(--focus-ring), var(--shadow-depth) !important;
            outline: none !important;
          }

          [data-testid="stSelectbox"] [data-baseweb="select"] * {
            color: var(--text-primary) !important;
          }

          div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #7C6FE0 0%, #4F46E5 100%) !important;
            border: 1px solid rgba(100, 108, 255, 0.35) !important;
            border-radius: 16px !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            box-shadow: 0 10px 28px rgba(79, 70, 229, 0.35) !important;
          }

          div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 14px 36px rgba(100, 108, 255, 0.45) !important;
          }

          /* ── Sidebar control room ───────────────────────────────────── */
          section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #14151c 0%, #101114 100%) !important;
            border-right: 1px solid var(--border-indigo) !important;
          }

          section[data-testid="stSidebar"] .block-container {
            padding-top: 1.5rem !important;
            display: flex;
            flex-direction: column;
            min-height: 100%;
          }

          section[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
          section[data-testid="stSidebar"] [data-testid="stMarkdown"] li,
          section[data-testid="stSidebar"] [data-testid="stMarkdown"] strong {
            color: var(--text-muted) !important;
            font-size: 0.88rem !important;
            line-height: 1.55 !important;
          }

          .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            margin-bottom: 1.25rem;
          }

          .sidebar-logo {
            width: 36px;
            height: 36px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            background: rgba(100, 108, 255, 0.15);
            color: var(--indigo);
            border-radius: 12px;
            border: 1px solid var(--border-indigo);
            font-size: 0.95rem;
          }

          .sidebar-name {
            font-weight: 700;
            font-size: 1.05rem;
            color: var(--text-primary);
            letter-spacing: -0.02em;
          }

          .sidebar-arch-title {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-dim);
            margin: 0 0 0.6rem 0;
          }

          .hardware-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            margin-top: 1rem;
            padding: 0.48rem 0.88rem;
            background: rgba(16, 17, 20, 0.85);
            border: 1px solid rgba(34, 197, 94, 0.22);
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 600;
            color: #D1FAE5;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 4px 16px rgba(0,0,0,0.25);
          }

          .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: #22C55E;
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.85);
            animation: pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
          }

          @keyframes pulse-green {
            0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.65); transform: scale(1); }
            50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); transform: scale(1.05); }
          }

          /* ── Hero ───────────────────────────────────────────────────── */
          .karen-hero { text-align: center; margin-bottom: 1.75rem; }

          .karen-hero-badge {
            display: inline-block;
            padding: 0.38rem 0.9rem;
            margin-bottom: 0.85rem;
            background: rgba(100, 108, 255, 0.12);
            border: 1px solid var(--border-indigo);
            color: #C7D2FE;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-transform: uppercase;
          }

          .karen-hero-title {
            font-size: 2.45rem;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin: 0 0 0.2rem 0;
            color: var(--text-primary);
          }

          .karen-hero-subtitle {
            font-size: 1rem;
            font-weight: 500;
            color: var(--indigo);
            margin: 0 0 0.7rem 0;
          }

          .karen-hero-desc {
            font-size: 0.93rem;
            line-height: 1.65;
            color: var(--text-muted);
            max-width: 540px;
            margin: 0 auto;
          }

          .karen-panel {
            padding: 1.75rem 1.75rem 1.35rem;
            margin-bottom: 1.35rem;
          }

          .panel-label {
            color: var(--text-muted) !important;
            margin: 0 0 0.45rem 0;
          }

          /* ── Pipeline stepper ───────────────────────────────────────── */
          .agent-pipeline {
            padding: 1.25rem 1.35rem;
            margin-bottom: 1.35rem;
          }

          .pipeline-title {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-dim);
            margin: 0 0 1rem 0;
          }

          .pipeline-step {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.7rem 0.85rem;
            margin-bottom: 0.5rem;
            border-radius: 14px;
            border: 1px solid transparent;
          }

          .pipeline-step:last-child { margin-bottom: 0; }

          .step-pending {
            opacity: 0.5;
            background: rgba(255, 255, 255, 0.02);
          }

          .step-active {
            background: rgba(100, 108, 255, 0.12);
            border-color: var(--border-indigo);
            box-shadow: var(--focus-ring);
            animation: step-pulse 1.6s ease-in-out infinite;
          }

          .step-done {
            background: rgba(16, 185, 129, 0.08);
            border-color: rgba(16, 185, 129, 0.2);
          }

          @keyframes step-pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(100, 108, 255, 0.2); }
            50% { box-shadow: 0 0 0 8px rgba(100, 108, 255, 0); }
          }

          .step-label {
            flex: 1;
            font-size: 0.87rem;
            font-weight: 500;
            color: var(--text-primary);
          }

          .step-badge {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
          }

          .step-pending .step-badge { color: var(--text-dim); background: rgba(255,255,255,0.05); }
          .step-active .step-badge { color: #C7D2FE; background: rgba(100, 108, 255, 0.2); }
          .step-done .step-badge { color: #6EE7B7; background: rgba(16, 185, 129, 0.15); }

          /* ── Result cards ───────────────────────────────────────────── */
          .karen-card {
            padding: 1.55rem 1.65rem;
            margin-bottom: 1.25rem;
          }

          .card-header {
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
            margin-bottom: 1rem;
          }

          .card-icon {
            width: 40px;
            height: 40px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            font-size: 1rem;
          }

          .rule-icon { background: rgba(100, 108, 255, 0.18); color: #A5B4FC; }
          .draft-icon { background: rgba(16, 185, 129, 0.15); color: #6EE7B7; }

          .card-eyebrow {
            margin: 0;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #A5B4FC;
          }

          .draft-card .card-eyebrow { color: #6EE7B7; }

          .card-title {
            margin: 0.12rem 0 0 0;
            font-size: 1.02rem;
            font-weight: 600;
            color: var(--text-primary);
          }

          .card-body {
            margin: 0;
            font-size: 0.92rem;
            line-height: 1.68;
            color: #E5E7EB;
          }

          .judge-card.judge-high-risk {
            background: linear-gradient(145deg, rgba(45, 35, 20, 0.75), rgba(26, 28, 38, 0.85));
            border-color: rgba(245, 158, 11, 0.35);
            box-shadow: var(--amber-glow);
          }

          .judge-card.judge-high-risk .judge-icon {
            background: rgba(245, 158, 11, 0.2);
            color: #FBBF24;
          }

          .judge-card.judge-high-risk .card-eyebrow,
          .judge-card.judge-high-risk .tactic-label { color: #FBBF24; }

          .judge-card.judge-high-risk .score-pill {
            background: rgba(245, 158, 11, 0.15);
            color: #FDE68A;
            border: 1px solid rgba(245, 158, 11, 0.3);
          }

          .judge-card.judge-high-risk .risk-banner {
            display: block;
            margin-bottom: 0.75rem;
            padding: 0.45rem 0.7rem;
            border-radius: 10px;
            background: rgba(245, 158, 11, 0.12);
            color: #FCD34D;
            font-size: 0.78rem;
            font-weight: 600;
          }

          .judge-card.judge-low-risk {
            background: linear-gradient(145deg, rgba(30, 32, 55, 0.8), rgba(26, 28, 38, 0.88));
            border-color: rgba(100, 108, 255, 0.28);
            box-shadow: var(--steel-glow);
          }

          .judge-card.judge-low-risk .judge-icon {
            background: rgba(100, 108, 255, 0.2);
            color: #A5B4FC;
          }

          .judge-card.judge-low-risk .card-eyebrow,
          .judge-card.judge-low-risk .tactic-label { color: #A5B4FC; }

          .judge-card.judge-low-risk .score-pill {
            background: rgba(100, 108, 255, 0.15);
            color: #C7D2FE;
            border: 1px solid rgba(100, 108, 255, 0.25);
          }

          .judge-card .risk-banner { display: none; }

          .score-pill {
            display: inline-block;
            margin-top: 0.45rem;
            padding: 0.38rem 0.8rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.84rem;
          }

          .tactic-line {
            margin-top: 0.9rem;
            padding-top: 0.9rem;
            border-top: 1px solid var(--border-indigo);
            font-size: 0.9rem;
            color: #E5E7EB;
          }

          .tactic-label { font-weight: 600; }

          .draft-body {
            margin: 0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Inter', ui-monospace, monospace;
            font-size: 0.84rem;
            line-height: 1.65;
            color: #E5E7EB;
            background: rgba(10, 11, 15, 0.55);
            border: 1px solid var(--border-indigo);
            border-radius: 16px;
            padding: 1.1rem 1.2rem;
          }

          .idle-card { text-align: center; padding: 2.4rem 2rem; }

          .idle-icon {
            width: 50px;
            height: 50px;
            margin: 0 auto 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(100, 108, 255, 0.15);
            color: #A5B4FC;
            border-radius: 14px;
          }

          .idle-title {
            margin: 0 0 0.5rem 0;
            font-weight: 600;
            color: var(--text-primary);
          }

          .idle-text {
            margin: 0;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-muted);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar_footer() -> None:
    """
    Sidebar-only developer signature with LinkedIn icon.

    Rendered via ``components.html`` so SVG/link markup is not escaped by Streamlit.
    """
    safe_url = html.escape(LINKEDIN_URL, quote=True)
    footer_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  body {{
    margin: 0;
    padding: 0;
    font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    background: transparent;
  }}
  .dev-footer {{
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(100, 108, 255, 0.12);
  }}
  .dev-line {{
    margin: 0;
    font-size: 0.78rem;
    font-weight: 500;
    color: #7B8499;
    letter-spacing: 0.01em;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }}
  .linkedin-icon-link {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(100, 108, 255, 0.12);
    text-decoration: none;
    transition: background 0.2s ease, transform 0.15s ease;
  }}
  .linkedin-icon-link:hover {{
    background: rgba(10, 102, 194, 0.2);
    transform: translateY(-1px);
  }}
</style></head><body>
  <div class="dev-footer">
    <p class="dev-line">
      Made by {html.escape(DEVELOPER_NAME)} — {html.escape(DEVELOPER_TITLE)}
      <a class="linkedin-icon-link" href="{safe_url}" target="_blank" rel="noopener noreferrer" title="LinkedIn">
        {_LINKEDIN_ICON_SVG}
      </a>
    </p>
  </div>
</body></html>"""
    components.html(footer_html, height=72, scrolling=False)


def _build_pipeline_html(step_statuses: list[StepStatus]) -> str:
    rows: list[str] = []
    badge_labels = {"pending": "Waiting", "active": "Running", "done": "Done"}

    for (icon, label), status in zip(_PIPELINE_STEPS, step_statuses):
        rows.append(
            f"""
            <div class="pipeline-step step-{status}">
                <span class="step-icon">{icon}</span>
                <span class="step-label">{html.escape(label)}</span>
                <span class="step-badge">{badge_labels[status]}</span>
            </div>
            """
        )

    return f"""
    <div class="agent-pipeline karen-glass">
        <p class="pipeline-title">Multi-Agent Pipeline</p>
        {''.join(rows)}
    </div>
    """


def render_pipeline_stepper(step_statuses: list[StepStatus]) -> None:
    st.markdown(_build_pipeline_html(step_statuses), unsafe_allow_html=True)


def render_sidebar() -> None:
    """Dark control-room sidebar with hardware status + single footer signature."""
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-control-room">
                <div class="sidebar-brand">
                    <span class="sidebar-logo">✦</span>
                    <span class="sidebar-name">KarenAI</span>
                </div>
                <p class="sidebar-arch-title">Architecture Control Panel</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(ARCHITECTURE_SIDEBAR_MD)
        st.markdown(
            """
            <div class="hardware-pill">
                <span class="status-dot"></span>
                RAG + Judge pipeline active
            </div>
            """,
            unsafe_allow_html=True,
        )
        _render_sidebar_footer()


def render_hero() -> None:
    st.markdown(
        f"""
        <div class="karen-hero">
            <div class="karen-hero-badge">Multi-Agent Legal AI</div>
            <h1 class="karen-hero-title">{html.escape(APP_TITLE)}</h1>
            <p class="karen-hero-subtitle">{html.escape(APP_TAGLINE)}</p>
            <p class="karen-hero-desc">
                Enterprise passenger-rights workflow on a secure dark stack —
                RAG retrieval, draft compilation, and adversarial Judge scoring.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_claim_form() -> tuple[str, str, bool]:
    st.markdown('<div class="karen-panel karen-glass">', unsafe_allow_html=True)
    st.markdown('<p class="panel-label">Target carrier</p>', unsafe_allow_html=True)

    airline = st.selectbox(
        "Target carrier",
        options=list(AIRLINES),
        label_visibility="collapsed",
        help="Which airline should this correspondence be addressed to?",
    )

    st.markdown('<p class="panel-label">Describe your flight issue</p>', unsafe_allow_html=True)
    issue_text = st.text_area(
        "Describe your flight issue",
        height=160,
        placeholder=(
            "My Turkish Airlines flight TK123 was cancelled without rebooking. "
            "I was stranded overnight and received no compensation..."
        ),
        label_visibility="collapsed",
    )

    submitted = st.button(
        "Unleash Karen · Draft Email",
        type="primary",
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    return airline, issue_text, submitted


def render_legal_foundation_card(policy_text: str) -> None:
    safe_policy = html.escape(policy_text.strip())
    st.markdown(
        f"""
        <div class="karen-card rule-card karen-glass">
            <div class="card-header">
                <span class="card-icon rule-icon">§</span>
                <div>
                    <p class="card-eyebrow">Card 1</p>
                    <p class="card-title">Retrieved Legal Foundation (The Rule)</p>
                </div>
            </div>
            <p class="card-body">{safe_policy}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_judge_verdict_card(*, score: int, verdict_text: str, new_tactic: str) -> None:
    risk_class = "judge-high-risk" if score <= 5 else "judge-low-risk"
    risk_banner = (
        '<p class="risk-banner">⚠ High Risk of Giving In — voucher trap detected</p>'
        if score <= 5
        else ""
    )
    safe_verdict = _format_card_body(verdict_text)
    safe_tactic = html.escape(new_tactic.strip())

    st.markdown(
        f"""
        <div class="karen-card judge-card karen-glass {risk_class}">
            <div class="card-header">
                <span class="card-icon judge-icon">⚖</span>
                <div>
                    <p class="card-eyebrow">Card 2</p>
                    <p class="card-title">The Judge's Verdict &amp; Pushover Score</p>
                </div>
            </div>
            {risk_banner}
            <span class="score-pill">Pushover Score: {score}/10</span>
            <p class="card-body">{safe_verdict}</p>
            <p class="tactic-line"><span class="tactic-label">New Tactic:</span> {safe_tactic}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_refined_notice_card(email_body: str) -> None:
    safe_email = html.escape(email_body.rstrip())
    st.markdown(
        f"""
        <div class="karen-card draft-card karen-glass">
            <div class="card-header">
                <span class="card-icon draft-icon">✉</span>
                <div>
                    <p class="card-eyebrow">Card 3</p>
                    <p class="card-title">The Refined Legal Notice / Email Draft</p>
                </div>
            </div>
            <pre class="draft-body">{safe_email}</pre>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_idle_state() -> None:
    st.markdown(
        """
        <div class="karen-card idle-card karen-glass">
            <div class="idle-icon">✦</div>
            <p class="idle-title">Ready when you are</p>
            <p class="idle-text">
                Select an airline, describe your disruption, and watch the multi-agent
                pipeline execute — RAG → Draft → Judge.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_card_body(text: str) -> str:
    escaped = html.escape(text.strip())
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
