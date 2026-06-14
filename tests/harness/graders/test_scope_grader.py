"""Tests for ScopeGrader — fraction of changed files within the spec's target_files."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from harness.graders.scope_grader import ScopeGrader
from harness.models import SpecConfig


def _grade(git_stdout: str, target_files: list[str]):
    spec = SpecConfig(id="S0", name="n", prompt="p", target_files=target_files)
    proc = MagicMock(returncode=0, stdout=git_stdout, stderr="")
    with patch("harness.graders.scope_grader.subprocess.run", return_value=proc):
        return ScopeGrader().grade(Path("/wt"), spec)


def test_partial_scope_is_fraction_in_target():
    # README.md is outside target_files → 2 of 3 changes in scope.
    r = _grade("src/a.py\nsrc/b.py\nREADME.md\n", ["src/a.py", "src/b.py"])
    assert r.score == 2 / 3
    assert not r.passed


def test_dir_prefix_target_matches_nested_file():
    r = _grade("src/pkg/mod.py\n", ["src/pkg"])
    assert r.score == 1.0
    assert r.passed


def test_no_changes_is_fully_in_scope():
    r = _grade("", ["src/a.py"])
    assert r.score == 1.0
    assert r.passed


def test_no_target_files_means_no_scope_constraint():
    r = _grade("anything.py\n", [])
    assert r.score == 1.0
    assert r.passed
