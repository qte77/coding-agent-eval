# coding-agent-eval

Hands-off coding agent comparison harness

Runs CC, Cline, opencode, Codebuff, and Antigravity CLI headless on identical specs, collects structured metrics, and generates comparison reports.

**Write-up:** the evaluator in an open agentic coding harness — [An Open Agentic Coding Harness](https://qte77.github.io/open-agentic-coding-harness/).

## Status

**Phase 0** — graders-first slice in progress; collector and runner implementation pending.

Already present: `Makefile`, `Makefile.python`, `research/` submodule, `LICENSE`, `SECURITY.md`.

Grader package: `Grader` ABC + `ValidateGrader` and `ScopeGrader` implemented; `SolutionGrader`
stubbed (TDD red — spec tests added as `xfail`, implementation pending). Evaluated agents: CC, Cline,
opencode, Codebuff, Antigravity CLI (renamed from Gemini CLI 2026-06-18).

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

See [docs/architecture.md](docs/architecture.md) for the full data flow, component descriptions, metrics definitions, and phase definitions.

## Dependencies

- [`cc-recursive-team-mode`](https://github.com/qte77/cc-recursive-team-mode) — CC subprocess management and artifact collection

## Submodules

| Path | Purpose |
|---|---|
| `research/` | [`ai-agents-research`](https://github.com/qte77/ai-agents-research) — landscape research for agent capabilities |

## Related Repos

- [`cc-recursive-team-mode`](https://github.com/qte77/cc-recursive-team-mode) — CC-specific subprocess harness (dependency)
- [`multi-tasking-quality-benchmark`](https://github.com/qte77/multi-tasking-quality-benchmark) — developer productivity benchmarking (related)
- [`ai-agents-research`](https://github.com/qte77/ai-agents-research) — landscape research (submodule at `research/`)

## License

Apache-2.0 — see [LICENSE](LICENSE).
