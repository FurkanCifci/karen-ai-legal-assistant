"""
Shared type aliases for KarenAI.

Kept in a lightweight module (no Streamlit) so ``StepStatus`` is always importable.
"""

from __future__ import annotations

from typing import Literal

# Pipeline stepper states: pending → active → done
StepStatus = Literal["pending", "active", "done"]

# Runtime tuple for validation / iteration
STEP_STATUS_VALUES: tuple[str, ...] = ("pending", "active", "done")

__all__ = ["StepStatus", "STEP_STATUS_VALUES"]
