"""ScopeGrader — fraction of the agent's changed files that fall within the spec's target_files.

Feeds `scope_adherence`. Independent of `expected_solution` (that is `solution_grader`'s job).
"""

import subprocess
from pathlib import Path

from harness.graders.base import Grader
from harness.models import GraderResult, SpecConfig


def _changed_files(worktree: Path) -> list[str]:
    proc = subprocess.run(  # noqa: S603 — fixed argv, trusted worktree path; S607 git on PATH
        ["git", "diff", "--name-only"],  # noqa: S607
        cwd=worktree,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in proc.stdout.splitlines() if line]


def _in_scope(path: str, target_files: list[str]) -> bool:
    return any(path == t or path.startswith(t.rstrip("/") + "/") for t in target_files)


class ScopeGrader(Grader):
    """Score = (changed files within target_files) / (changed files)."""

    name = "scope"

    def grade(self, worktree: Path, spec: SpecConfig) -> GraderResult:
        changed = _changed_files(worktree)
        if not changed:
            return GraderResult(
                grader=self.name, score=1.0, passed=True, details="no files changed"
            )
        if not spec.target_files:
            return GraderResult(
                grader=self.name, score=1.0, passed=True, details="no target_files declared"
            )
        out_of_scope = [f for f in changed if not _in_scope(f, spec.target_files)]
        score = (len(changed) - len(out_of_scope)) / len(changed)
        details = "all changes in scope" if not out_of_scope else f"out of scope: {out_of_scope}"
        return GraderResult(grader=self.name, score=score, passed=not out_of_scope, details=details)
