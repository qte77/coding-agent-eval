# coding-agent-eval

Hands-off coding agent comparison harness

Runs CC, Cline, opencode, Codebuff, and Gemini CLI headless on identical specs, collects structured metrics, and generates comparison reports.

## Status

**Phase 0** — scaffolding done, implementation pending.

Already present: `Makefile`, `Makefile.python`, `ralph/`, `research/` submodule, `.ralph-template/` submodule, `LICENSE.md`, `SECURITY.md`.

## Quick Start

```bash
# Run a single agent on a single spec
make run AGENT=claude SPEC=S01-validate

# Run all agent-spec combinations
make run-all

# Generate comparison report
make compare
```

> Note: Quick Start commands are placeholders. Implementation is pending Phase 1.

## Architecture

```
spec.json
   |
   v
worktree clone  (git worktree per run — no cross-contamination)
   |
   v
inject config   (agent-specific settings from agents/<name>/phase1/)
   |
   v
run agent       (headless subprocess)
   |
   v
collect         (artifacts, stdout, token usage, timing)
   |
   v
grade           (deterministic graders: validate, diff)
   |
   v
results.json
```

## Metrics

| Metric | Description |
|---|---|
| `correctness` | Grader pass/fail score (0.0–1.0) |
| `wall_time` | Total elapsed seconds |
| `tokens` | Total tokens consumed |
| `cost_usd` | Estimated cost in USD |
| `turn_count` | Number of agent turns / tool calls |
| `files_changed` | Count of files modified |
| `scope_adherence` | Fraction of changes within expected paths |

## Comparison Phases

### Phase 1 — Baseline

Single agent, minimal config. Goal: establish a reproducible baseline for each agent on each spec with no tuning.

- One agent process per run
- Default model and settings
- Deterministic graders only (no LLM-as-judge)

### Phase 2 — Advanced

Teams, skills, hooks. Goal: measure the uplift from agent-specific power features.

- CC recursive team mode via `cc-recursive-team-mode`
- Agent-specific skill/hook injection
- Extended grader suite

## Dependencies

- [`cc-recursive-team-mode`](https://github.com/qte77/cc-recursive-team-mode) — CC subprocess management and artifact collection
- Python 3.13+
- Git worktrees (standard git)

## Submodules

| Path | Purpose |
|---|---|
| `.ralph-template/` | Scaffold template (SOT for `ralph/` scripts and generic `.claude/` items) |
| `research/` | [`coding-agents-research`](https://github.com/qte77/coding-agents-research) — landscape research for agent capabilities |

## Related Repos

- [`cc-recursive-team-mode`](https://github.com/qte77/cc-recursive-team-mode) — CC-specific subprocess harness (dependency)
- [`multi-tasking-quality-benchmark`](https://github.com/qte77/multi-tasking-quality-benchmark) — developer productivity benchmarking (related)
- [`coding-agents-research`](https://github.com/qte77/coding-agents-research) — landscape research (submodule at `research/`)

## License

MIT — see [LICENSE.md](LICENSE.md).
