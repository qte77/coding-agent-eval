# Spike #22 — Dependency De-risking (2026-06)

Resolves the dependency unknowns that gate the harness build (issue #22). Scoped here to
**bullet 1 (`cc-recursive-team-mode`)**, which is the only #22 item that gates the scaffold (#8)
and models (#9). The remaining bullets (agent headless modes + Antigravity binary → #11;
repo-baseline payload audit → #25; Anthropic pricing → run-time) stay open under #22.

## `cc-recursive-team-mode` — install method + API

**Verified (2026-06-14, via the public repo `qte77/cc-recursive-team-mode`):**

- **Not published to PyPI.** It is a public **git** project, installed as a dev dependency via
  `uv` (its own `make setup_dev`), i.e. a `git+https://…` dependency, not `pip install cc-recursive-team-mode`.
- **Import name:** `cc_recursive` (note: distribution name uses dashes, import uses underscores).
- **Public Python API:** `from cc_recursive import run, RunConfig, RunProfile`.
  - `run(config: RunConfig) -> RunResult`
  - `RunResult` (Pydantic) carries: `exit_code: int`, `tokens: int`, `cost_usd: float`,
    `tool_calls: list`.
  - Helpers: `load_prompt()`, `parse_session()` (parses Claude session artifacts).
- **Headless CLI wrapper:** `scripts/cc-recursive-team.sh` (drive without Python).

## Decision

Declare `cc-recursive-team-mode` as a **git-based optional dependency** under
`[project.optional-dependencies].agents`, **not** in the CI-synced `dev` group.

**Why:**
- CI runs `uv sync --group dev`, which does not install optional extras → the git dependency
  cannot redden CI (and we avoid resolving a git URL on every CI run).
- It is not *used* until the Claude Code collector (#10) shells out to `cc_recursive.run()` —
  so wiring it now would be speculative (YAGNI). #10 installs the `agents` extra and consumes
  the API documented above.

**Consumption note for #10:** prefer the Python API (`run(RunConfig) -> RunResult`) over the
shell wrapper so `exit_code`/`tokens`/`cost_usd`/`tool_calls` come back typed; map those onto the
harness `RunResult`/`TokenUsage` models. `parse_session()` may cover the transcript-JSONL token
split.
