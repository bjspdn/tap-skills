# Smell Warnings Schema

Defines the `.smell-warnings.json` structure written to `.tap/worktrees/<slug>/` during a `/tap:run` execution. The orchestrator appends entries after GREEN or REFACTOR commits when the task's pattern hint has `smells_it_introduces` tags that match heuristic signals in the committed diff. Consumed by the next phase agent via `<smell-warnings>` block injection.

## Location

`<worktree_path>/.smell-warnings.json`

Ephemeral — lives in the worktree, deleted when the worktree is cleaned up after merge.

## Shape

```json
[
  {
    "task_id": "01-truncate",
    "phase_that_introduced": "GREEN",
    "pattern_applied": "strategy",
    "smell_tag": "over-abstraction-single-variant",
    "evidence": "diff adds interface DiscountStrategy with only one implementing class",
    "files": ["src/discount/strategy.ts", "src/discount/flat-discount.ts"],
    "timestamp": "2026-05-10T14:35:00Z"
  }
]
```

## Fields

| Field                  | Type     | Required | Description                                                                 |
|------------------------|----------|----------|-----------------------------------------------------------------------------|
| `task_id`              | string   | yes      | Task identifier (e.g. `01-truncate`)                                        |
| `phase_that_introduced`| enum     | yes      | `GREEN` \| `REFACTOR` — the phase whose commit triggered the detection     |
| `pattern_applied`      | string   | yes      | Kebab-case pattern name from the task's `### Pattern hint`                  |
| `smell_tag`            | string   | yes      | Kebab-case smell tag from the pattern card's `smells_it_introduces`         |
| `evidence`             | string   | yes      | One-line description of what in the diff matched the heuristic              |
| `files`                | string[] | yes      | Paths relative to repo root where the smell signal was detected             |
| `timestamp`            | string   | yes      | ISO 8601 timestamp                                                          |

## Consumers

- **Orchestrator** — appends entries after GREEN/REFACTOR phase commits when heuristic smell signals are detected. Reads the file before the next phase dispatch and builds `<smell-warnings>` for the agent prompt.
- **Refactorer** — primary consumer. Smell warnings are prescriptive: actively address detected smells during REFACTOR phase.
- **CodeWriter** — secondary consumer. Smell warnings are informational only: be aware, but do not restructure GREEN around them.
