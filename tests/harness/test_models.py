"""Tests for harness Pydantic models (AgentBeats-compatible result schema).

Only non-trivial tests: computed logic, the strict+frozen guarantees we rely on, custom
validators, and the JSON serialization contract. Field defaults/bounds and plain containment
are deliberately not re-tested — they assert Pydantic's behavior, not ours.
"""

import pytest
from pydantic import ValidationError

from harness.models import (
    ExpectedSolution,
    GraderResult,
    IsolationTier,
    RunResult,
    SpecConfig,
    TokenUsage,
)


def _run_result_kwargs() -> dict[str, object]:
    return {
        "agent": "claude",
        "spec": "S01",
        "run_count": 3,
        "correctness": 0.9,
        "scope_adherence": 1.0,
        "wall_time_s": 12.5,
        "cost_usd": 0.03,
        "tokens": TokenUsage(prompt=100, completion=50, cache_read=10, cache_write=5),
        "turn_count": 7,
        "files_changed": 2,
        "isolation_tier": IsolationTier.T2,
        "grader_results": [GraderResult(grader="validate", score=1.0, passed=True)],
    }


def test_token_usage_total_sums_all_types() -> None:
    # The `total` property is our logic (sums the 4 split token types).
    tokens = TokenUsage(prompt=100, completion=50, cache_read=10, cache_write=5)
    assert tokens.total == 165


def test_run_result_is_frozen() -> None:
    # Results must be immutable once produced; guards the `frozen` config.
    rr = RunResult(**_run_result_kwargs())
    with pytest.raises(ValidationError):
        rr.agent = "cline"


def test_strict_mode_rejects_coercible_string() -> None:
    # strict=True must reject "3" -> int (lax pydantic would coerce). Guards against
    # silently accepting malformed data (e.g. untrusted agent output).
    with pytest.raises(ValidationError):
        RunResult(**{**_run_result_kwargs(), "run_count": "3"})


def test_run_result_json_round_trip() -> None:
    # AgentBeats compatibility: serialize -> deserialize must be lossless across the
    # nested TokenUsage / enum / grader list.
    rr = RunResult(**_run_result_kwargs())
    assert RunResult.model_validate_json(rr.model_dump_json()) == rr


def test_expected_solution_requires_fixture() -> None:
    # Our model_validator invariant: a solution is meaningless without a fixture.
    with pytest.raises(ValidationError):
        SpecConfig(id="S02", name="fix-bug", prompt="fix it", expected_solution=ExpectedSolution())


def test_spec_config_json_round_trip_with_solution() -> None:
    # Round-trip with the optional nested solution + the validator's happy path.
    sc = SpecConfig(
        id="S02",
        name="fix-bug",
        prompt="fix the off-by-one",
        target_files=["src/pagination.py"],
        fixture="fixtures/S02-fix-bug",
        expected_solution=ExpectedSolution(),
    )
    assert SpecConfig.model_validate_json(sc.model_dump_json()) == sc
