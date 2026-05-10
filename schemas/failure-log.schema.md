# Failure Log Schema

Defines the `.failure-log.json` structure written to `.tap/worktrees/<slug>/` during a `/tap:run` execution. The Debugger appends entries after diagnosis; the orchestrator reads them before dispatching subsequent agents.

## Location

`<worktree_path>/.failure-log.json`

Ephemeral — lives in the worktree, deleted when the worktree is cleaned up after merge.

## Shape

```json
[
  {
    "task_id": "01-truncate",
    "phase": "RED",
    "failure_type": "missing-module",
    "files_involved": ["src/helpers/truncate.ts", "src/helpers/index.ts"],
    "root_cause": "truncate module not exported from barrel file",
    "resolution": "added truncate to barrel exports",
    "timestamp": "2026-05-10T14:32:00Z"
  }
]
```

## Fields

| Field            | Type     | Required | Description                                                     |           |                                    |
| ------------------| ----------| ----------| -----------------------------------------------------------------| -----------| ------------------------------------|
| `task_id`        | string   | yes      | Task identifier (e.g. `01-truncate`)                            |           |                                    |
| `phase`          | enum     | yes      | `RED` \                                                         | `GREEN` \ | `REFACTOR` — the phase that failed |
| `failure_type`   | enum     | yes      | One of the retro taxonomy values (see below)                    |           |                                    |
| `files_involved` | string[] | yes      | Paths relative to repo root that were implicated in the failure |           |                                    |
| `root_cause`     | string   | yes      | One-line summary of what went wrong                             |           |                                    |
| `resolution`     | string   | yes      | What Debugger did to fix it, or `"saga-isolated"` if unresolved |           |                                    |
| `timestamp`      | string   | yes      | ISO 8601 timestamp                                              |           |                                    |

## `failure_type` values

From the retro failure taxonomy:

- `missing-module` — import/require target does not exist or is not exported
- `assertion-mismatch` — test assertion fails with unexpected value
- `compilation-error` — tsc / type-check / build fails
- `logic-error` — implementation produces wrong result
- `type-error` — type mismatch at call site or return
- `broke-behavior` — refactor changed observable behavior
- `gate-failure` — lint / build / other non-test gate fails
- `wiring-gap` — dependency injection or module wiring incomplete
- `scope-violation` — agent touched files outside declared scope

## Consumers

- **Debugger** — appends entries after diagnosis (Shape A or Shape B).
- **Orchestrator** — reads before each agent dispatch; filters by file overlap with the next task's `context[].path` / `files.modify[]` / `files.create[]`; injects matching entries as `<failure-context>` in the agent prompt.
- **TestWriter, CodeWriter, Refactorer** — consume `<failure-context>` as warnings when present in their prompt.
