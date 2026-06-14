"""Grader interface — deterministic worktree scoring (no LLM calls in Phase 1)."""

from abc import ABC, abstractmethod
from pathlib import Path

from harness.models import GraderResult, SpecConfig


class Grader(ABC):
    """A deterministic grader. Subclasses set ``name`` and implement ``grade``."""

    name: str

    @abstractmethod
    def grade(self, worktree: Path, spec: SpecConfig) -> GraderResult:
        """Score the agent's changes in ``worktree`` for ``spec``."""
