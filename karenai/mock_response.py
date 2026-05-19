"""
Draft email builder — uses retrieved policy context until the LLM layer ships.
"""

from __future__ import annotations


def build_mock_draft_email(
    *,
    airline: str,
    issue_description: str,
    retrieved_policy: str = "",
) -> str:
    """
    Compose a structured complaint email grounded in the retrieved policy.

    Parameters
    ----------
    airline:
        Label from the airline dropdown.
    issue_description:
        Free-text claim from the user.
    retrieved_policy:
        Policy snippet returned by the RAG Context Store.
    """
    issue_snippet = (issue_description or "(no details provided yet)").strip()
    if len(issue_snippet) > 400:
        issue_snippet = issue_snippet[:397] + "..."

    policy_block = (
        retrieved_policy.strip()
        if retrieved_policy.strip()
        else "Applicable passenger rights provisions will be cited once policy retrieval completes."
    )

    return f"""Subject: Formal complaint & request for remedy — {airline}

Dear {airline} Customer Relations,

I am writing regarding a recent flight disruption and requesting appropriate
compensation and assistance under applicable passenger rights rules.

Summary of my case:
{issue_snippet}

Relevant policy basis (retrieved from carrier records):
{policy_block}

Based on the above, I believe I am entitled to the remedies described in your
conditions of carriage and applicable regulations. Please acknowledge receipt of
this message and provide a written response within the timeframe required by law.

Kind regards,
[Your name]
[Your booking reference / ticket number]
[Contact email / phone]
"""
