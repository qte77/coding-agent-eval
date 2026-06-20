"""SolutionGrader — diff overlap vs the canonical expected_solution.

Computes partial credit: the fraction of lines in the canonical diff
(``broken`` -> ``solution``) that the agent's diff also reproduces.

Behaviour:
- ``None`` expected_solution  -> skipped (score 1.0, passed True, details "skipped").
- Empty canonical diff        -> score 1.0 (nothing to reproduce).
- Otherwise                   -> ``len(agent_lines & canonical_lines) / len(canonical_lines)``.
"""

from pathlib import Path

from harness.graders.base import Grader
from harness.models import GraderResult, SpecConfig


class SolutionGrader(Grader):
    """Structural partial credit: how much of the canonical fix did the agent reproduce?"""

    name = "solution"

    def grade(self, worktree: Path, spec: SpecConfig) -> GraderResult:
        """Score the agent's diff against the canonical solution diff.

        ``spec.fixture`` + ``spec.expected_solution.solution_dir`` locate the
        canonical solution tree (M1: sibling of ``broken/``).  The agent's diff
        is ``git diff`` (working tree vs baseline commit).

        Returns a ``GraderResult`` with ``score`` in ``[0, 1]``.
        """
        raise NotImplementedError
