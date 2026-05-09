---
name: analysis
description: Analyze TDD run logs — extract metrics, normalize across runs, rank efficiency, compare effort levels
---

## Step 1: Extract metrics

Run:
```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analysis/extract_metrics.py .tap/logs/
```

Capture the JSON output. If `features` is empty, tell the user no runs were found and stop.

## Step 2: Resolve effort levels

For each feature in the JSON that has a `parent_sha`, run:
```
git show <parent_sha>:.tap/config.json
```

Extract `agents.Composer.effort` (and `agents.Composer.model` if present). Tag each feature with its effort level.

## Step 3: Auto-estimate difficulty

For each feature, compute a difficulty weight starting at 1.0:

- `debugger_invoked` → +0.3
- code-writer input tokens > 50% of TDD total (test-writer + code-writer + refactorer input tokens) → +0.3
- refactorer turns > 2× test-writer turns → +0.2
- if `.tap/logs/<feature>/reviewer.output.json` exists and `blockers >= 2` → +0.2
- Cap at 3.0

## Step 4: Normalize and rank

Compute per-task metrics: divide totals by `tasks_completed`.

Compute per-weighted-unit metrics: divide totals by `tasks_completed × difficulty_weight`.

Composite efficiency score (lower = better), using min-max normalization across all features before weighting:

| Dimension | Weight |
|---|---|
| Input tokens per weighted unit | 40% |
| Tool calls per weighted unit | 25% |
| Turns per weighted unit | 20% |
| Debugger penalty (1 if invoked, 0 if not) | 15% |

## Step 5: Render report

Present in this order:

1. **Raw totals table** — feature, total input tokens, output tokens, tool calls, turns, cache %, cost
2. **Per-task efficiency table** — ranked by cost/task ascending
3. **Difficulty-weighted ranking** — composite scores, ranked ascending
4. **HIGH vs LOW effort comparison** — if both levels present: show averages and ratio for cost, tokens, turns
5. **Key takeaways** — 3–5 bullets, actionable insights only

## Step 6: Follow-up

Stay ready to drill into per-role breakdowns, compare specific features, or answer questions about individual runs.

---

Adapt verbosity to the conversation style — terse if caveman mode is active, full prose otherwise.
