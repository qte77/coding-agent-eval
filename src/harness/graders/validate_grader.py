"""ValidateGrader — runs `make validate` in the worktree; 1.0 on pass, 0.0 on fail."""

import subprocess
from pathlib import Path

from harness.graders.base import Grader
from harness.models import GraderResult, SpecConfig

_DETAIL_MAX = 500


class ValidateGrader(Grader):
    """Behavioral correctness: did the agent's changes make `make validate` pass?"""

    name = "validate"

    def grade(self, worktree: Path, spec: SpecConfig) -> GraderResult:
        proc = subprocess.run(  # noqa: S603 — fixed argv, trusted worktree path; S607 make on PATH
            ["make", "validate"],  # noqa: S607
            cwd=worktree,
            capture_output=True,
            text=True,
            check=False,
        )
        passed = proc.returncode == 0
        details = (proc.stderr or proc.stdout).strip()[-_DETAIL_MAX:]
        return GraderResult(
            grader=self.name, score=1.0 if passed else 0.0, passed=passed, details=details
        )
