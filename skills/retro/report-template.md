# Run Report Template

Reference for the markdown emitted by `tap:retro` to `.tap/retros/<slug>-<YYYY-MM-DD>.md`.

Each report is scoped to one completed run. It captures the timeline, metrics, failures, and structural observations for that run only. The durable layer is `_profile.json` — reports are ephemeral.

## Template

```markdown
# Retro: <slug>

> **Date:** <YYYY-MM-DD> | **Branch:** tap-<slug> | **Commits:** <parent_sha>..<merge_sha> | **Tasks:** <N>

## Summary

| Metric | Value |
|--------|-------|
| Tasks completed | <completed>/<total> |
| Saga-isolated | <count> |
| Debugger retries | <count> |
| Reviewer verdict | <pass/fail> |
| Pattern adherence | <followed>/<total hints> |

## Per-task breakdown

| Task | RED | GREEN | REFACTOR | Retries | Pattern | Status |
|------|-----|-------|----------|---------|---------|--------|
<for each task, one row>

Status values: `completed`, `saga-isolated`, `partial` (survived but missing optional phase).
Phase values: `pass` (clean), `retry` (required DEBUG), `skip` (intentional no-op), `fail` (saga-isolated at this phase), `--` (never reached).

## Turn heatmap

| Task | Commits | Time span | Fix density | Heat |
|------|---------|-----------|-------------|------|
<tasks sorted by heat score, descending>

## Token & cost analysis

> _Source: agent dispatch usage summaries returned by the Agent tool during run execution._

| Phase | Avg tokens | Min | Max | Tasks |
|-------|-----------|-----|-----|-------|
| RED | <avg> | <min> | <max> | <N> |
| GREEN | <avg> | <min> | <max> | <N> |
| REFACTOR | <avg> | <min> | <max> | <N> |
| DEBUG | <avg> | <min> | <max> | <N> |
| **Total run** | — | — | — | **<sum>** |

### Per-task token breakdown

| Task | RED | GREEN | REFACTOR | DEBUG | Total | Outlier |
|------|-----|-------|----------|-------|-------|---------|
<for each task, one row — token counts per phase, total, and outlier flag (yes/no)>

### Outliers (3x+ run average)

<bulleted list of outlier tasks with their characteristics>
<e.g. "task-03-complex-wiring: 45k tokens (avg: 12k) — 5 files, pattern: strategy, 2 DEBUG retries">

_If no outliers: "No outlier tasks detected."_
_If token data unavailable: "Token data unavailable for this run (older run format or sketch execution)."_

## Failure taxonomy

| Task | Phase | Category | Detail |
|------|-------|----------|--------|
<for each failure, one row — detail from Tap-Decisions or commit subject>

_Empty table if no failures occurred._

## Pattern smell correlations

| Pattern | Smell tag | Task | Failure category | Phase |
|---------|-----------|------|------------------|-------|
<for each pattern_smell_correlation entry, one row>

_Empty table if no correlations found._

## Observations

<bulleted list of structural observations from this run>
<each observation cites sample counts and rates>
<tentative observations (sample_count < 3) are prefixed with "[tentative]">
```
