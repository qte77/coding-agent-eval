"""Tests for harness Pydantic models (AgentBeats-compatible result schema)."""

import pytest
from pydantic import ValidationError

from harness.models import (
    GraderResult,
    HarnessConfig,
    IsolationTier,
    RunResult,
    SpecConfig,
    SpecResult,
    TokenUsage,
)


def _token_usage() -> TokenUsage:
    return TokenUsage(prompt=100, completion=50, cache_read=10, cache_write=5)


def _run_result() -> RunResult:
    return RunResult(
        agent="claude",
        spec="S01",
        run_count=3,
        correctness=0.9,
        scope_adherence=1.0,
        wall_time_s=12.5,
        cost_usd=0.03,
        tokens=_token_usage(),
        turn_count=7,
        files_changed=2,
        isolation_tier=IsolationTier.T2,
        grader_results=[GraderResult(grader="validate", score=1.0, passed=True)],
    )


class TestTokenUsage:
    def test_total_sums_all_token_types(self) -> None:
        # arrange / act
        tu = _token_usage()
        # assert
        assert tu.total == 165

    def test_cache_tokens_default_to_zero(self) -> None:
        tu = TokenUsage(prompt=10, completion=20)
        assert tu.cache_read == 0
        assert tu.cache_write == 0
        assert tu.total == 30

    def test_negative_tokens_rejected(self) -> None:
        with pytest.raises(ValidationError):
            TokenUsage(prompt=-1, completion=0)


class TestGraderResult:
    def test_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            GraderResult(grader="diff", score=1.5, passed=False)


class TestIsolationTier:
    def test_has_three_tiers(self) -> None:
        assert {t.value for t in IsolationTier} == {"T0", "T1", "T2"}


class TestRunResult:
    def test_constructs_with_valid_data(self) -> None:
        rr = _run_result()
        assert rr.agent == "claude"
        assert rr.tokens.total == 165
        assert rr.isolation_tier is IsolationTier.T2

    def test_is_frozen(self) -> None:
        rr = _run_result()
        with pytest.raises(ValidationError):
            rr.agent = "cline"

    def test_strict_mode_rejects_coercible_string(self) -> None:
        # In lax mode "3" would coerce to 3; strict mode must reject it.
        with pytest.raises(ValidationError):
            RunResult(
                agent="claude",
                spec="S01",
                run_count="3",
                correctness=0.9,
                scope_adherence=1.0,
                wall_time_s=1.0,
                cost_usd=0.0,
                tokens=_token_usage(),
                turn_count=1,
                files_changed=0,
                isolation_tier=IsolationTier.T2,
            )

    def test_correctness_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            RunResult(
                agent="claude",
                spec="S01",
                run_count=3,
                correctness=1.2,
                scope_adherence=1.0,
                wall_time_s=1.0,
                cost_usd=0.0,
                tokens=_token_usage(),
                turn_count=1,
                files_changed=0,
                isolation_tier=IsolationTier.T2,
            )

    def test_stddev_fields_default_to_zero(self) -> None:
        rr = _run_result()
        assert rr.correctness_stddev == 0.0
        assert rr.tokens_stddev == 0.0

    def test_json_round_trip_preserves_value(self) -> None:
        rr = _run_result()
        restored = RunResult.model_validate_json(rr.model_dump_json())
        assert restored == rr


class TestSpecResult:
    def test_holds_runs_across_agents(self) -> None:
        sr = SpecResult(spec="S01", runs=[_run_result()])
        assert sr.runs[0].agent == "claude"


class TestSpecConfig:
    def test_target_files_defaults_empty(self) -> None:
        sc = SpecConfig(id="S01", name="validate", prompt="do the thing")
        assert sc.target_files == []


class TestHarnessConfig:
    def test_run_count_and_tier_defaults(self) -> None:
        hc = HarnessConfig(agents=["claude"], specs=["S01"])
        assert hc.run_count == 3
        assert hc.target_isolation_tier is IsolationTier.T2
