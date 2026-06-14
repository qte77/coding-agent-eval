"""Tests for ValidateGrader — runs `make validate` in the worktree (1.0 pass / 0.0 fail)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from harness.graders.validate_grader import ValidateGrader
from harness.models import SpecConfig


def _grade_with_returncode(returncode: int, stderr: str = ""):
    spec = SpecConfig(id="S0", name="n", prompt="p")
    proc = MagicMock(returncode=returncode, stdout="", stderr=stderr)
    with patch("harness.graders.validate_grader.subprocess.run", return_value=proc) as run:
        return ValidateGrader().grade(Path("/wt"), spec), run


def test_passing_validate_scores_one():
    result, _ = _grade_with_returncode(0)
    assert result.score == 1.0
    assert result.passed


def test_failing_validate_scores_zero_and_keeps_detail():
    result, _ = _grade_with_returncode(2, stderr="ruff: 3 errors")
    assert result.score == 0.0
    assert not result.passed
    assert "ruff: 3 errors" in result.details


def test_runs_make_validate_in_the_worktree():
    _, run = _grade_with_returncode(0)
    args, kwargs = run.call_args
    assert args[0] == ["make", "validate"]
    assert kwargs["cwd"] == Path("/wt")
    assert kwargs["check"] is False  # never raise on a failing run; that's the signal
