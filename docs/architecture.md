---
title: Architecture - coding-agent-eval
description: System design and technical decisions for the coding agent comparison harness
category: technical
created: 2026-03-22
updated: 2026-03-22
version: 1.0.0
---

# Architecture: coding-agent-eval

## Data Flow

```
spec.json
   |
   v
worktree clone      (isolated git worktree per run)
   |
   v
inject config       (agent-specific settings from agents/<name>/phase1/)
   |
   v
run agent           (headless subprocess)
   |
   v
collect artifacts   (stdout, timing, token usage, raw output)
   |
   v
grade               (deterministic graders)
   |
   v
results.json
```

## Components

### Runner (`src/harness/runner.py`)

Orchestrates the full run cycle for a single `(agent, spec)` pair.

Responsibilities:
- Clone a git worktree for isolation
- Call the appropriate collector
- Call all registered graders in sequence
- Assemble and write `RunResult` to `results/<agent>-<spec>.json`

### Collectors (`src/harness/collectors/`)

Collector ABC defines the interface. Each agent has its own implementation.

| Module | Agent | Method |
|---|---|---|
| `cc_collector.py` | Claude Code | Wraps `cc-recursive-team-mode` via subprocess; parses `raw_stream.jsonl` for token/turn data |
| `generic_collector.py` | Cline, opencode, Codebuff, Gemini CLI | Invokes agent CLI directly; captures stdout/stderr and wall time |

Integration with `cc-recursive-team-mode`:

```
cc_collector
   |
   v
cc-recursive-team-mode (external dependency)
   |-- subprocess: claude -p "..." --output-format json
   |-- env: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 (teams mode)
   |-- artifacts: raw_stream.jsonl -> token count, turn count, cost
   v
CCTraceAdapter (parses artifacts into RunResult fields)
```

### Graders (`src/harness/graders/`)

Graders are deterministic — no LLM calls in Phase 1.

| Module | Grader | Input | Output |
|---|---|---|---|
| `validate_grader.py` | `validate_grader` | worktree path | runs `make validate`; 1.0 on pass, 0.0 on fail |
| `diff_grader.py` | `diff_grader` | git diff vs expected | fraction of expected changes present |

### Models (`src/harness/models.py`)

All data contracts use Pydantic models.

| Model | Purpose |
|---|---|
| `HarnessConfig` | Global harness settings (agents list, specs list, results dir) |
| `SpecConfig` | Parsed `specs/S0N-<name>.json` — prompt, target files, expected diff |
| `RunResult` | Single `(agent, spec)` run outcome — all metrics |
| `GraderResult` | Output of one grader — name, score, details |
| `SpecResult` | Aggregated results for one spec across all agents |

## Directory Structure

```
coding-agent-eval/
  agents/
    claude/
      phase1/           # Minimal CC config (CLAUDE.md, settings.json)
      phase2/           # Teams, skills, hooks (Phase 2)
    cline/
      phase1/
    opencode/
      phase1/
    codebuff/
      phase1/
    gemini/
      phase1/
  specs/
    S01-validate.json   # Spec: run make validate on a broken repo
    S02-fix-bug.json    # Spec: fix a single known bug
    S03-add-feature.json
  results/              # Output directory (gitignored)
    claude-S01.json
    comparison.md
  src/
    harness/
      runner.py
      models.py
      collectors/
        __init__.py
        base.py         # Collector ABC
        cc_collector.py
        generic_collector.py
      graders/
        __init__.py
        base.py         # Grader ABC
        validate_grader.py
        diff_grader.py
  tests/
    harness/
      test_runner.py
      test_models.py
      collectors/
        test_cc_collector.py
        test_generic_collector.py
      graders/
        test_validate_grader.py
        test_diff_grader.py
  research/             # submodule: ai-agents-research
  .ralph-template/      # submodule: scaffold template SOT
  Makefile
  Makefile.python
  LICENSE
  SECURITY.md
```

## Metrics

| Metric | Type | Source | Description |
|---|---|---|---|
| `correctness` | `float` (0.0–1.0) | graders | Weighted average of grader scores |
| `wall_time` | `float` (seconds) | collector | Total elapsed time from subprocess start to finish |
| `tokens` | `int` | collector | Total tokens consumed (prompt + completion) |
| `cost_usd` | `float` | collector | Estimated cost in USD |
| `turn_count` | `int` | collector | Number of agent turns / tool calls |
| `files_changed` | `int` | collector | Count of files modified in the worktree |
| `scope_adherence` | `float` (0.0–1.0) | diff_grader | Fraction of changes within spec-expected paths |

## Comparison Phases

### Phase 1 — Baseline

Goal: reproducible baseline per agent per spec with no tuning.

- Single agent process per run
- Default model and settings for each agent
- Deterministic graders only (validate + diff)
- No skill injection, no hooks

### Phase 2 — Advanced

Goal: measure uplift from agent-specific power features.

- CC recursive team mode via `cc-recursive-team-mode` (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
- Agent-specific skill/hook injection from `agents/<name>/phase2/`
- Extended grader suite (to be defined)
- CC solo vs CC teams comparison as first experiment

## External Dependencies

```
coding-agent-eval
   |
   +-- cc-recursive-team-mode   (CC subprocess mgmt, artifact parsing)
   |
   +-- research/              (submodule: landscape research, informational only)
   |
   +-- .ralph-template/       (submodule: scaffold template SOT)
```

`cc-recursive-team-mode` is a runtime dependency for the CC collector. All other agents are invoked via direct subprocess calls with no additional harness dependency.
