# Profile Schema

Reference for `.tap/retros/_profile.json` — the rolling aggregate that accumulates structural observations across runs.

## JSON Schema

```json
{
  "version": 1,
  "last_updated": "<YYYY-MM-DD>",
  "runs_analyzed": <N>,
  "agent_performance": {
    "<AgentName>": {
      "runs": <N>,
      "tasks": <N>,
      "failures": <N>,
      "retries": <N>,
      "skips": <N>,
      "failure_rate": <0.0-1.0>,
      "retry_rate": <0.0-1.0>,
      "skip_rate": <0.0-1.0>,
      "last_seen": "<YYYY-MM-DD>"
    }
  },
  "slicing_signals": [
    {
      "property": "<description of task property threshold>",
      "outcome": "<saga_isolation | debug_retry | clean_green>",
      "rate": <0.0-1.0>,
      "sample_count": <N>,
      "confidence": "<tentative | established>",
      "last_seen": "<YYYY-MM-DD>"
    }
  ],
  "pattern_signals": [
    {
      "pattern": "<pattern name>",
      "adherence_rate": <0.0-1.0>,
      "clean_green_rate": <0.0-1.0>,
      "sample_count": <N>,
      "confidence": "<tentative | established>",
      "last_seen": "<YYYY-MM-DD>",
      "smell_correlations": [
        {
          "smell_tag": "<kebab-case tag from smells_it_introduces>",
          "failure_count": <N>,
          "last_seen": "<YYYY-MM-DD>"
        }
      ]
    }
  ],
  "gate_signals": [
    {
      "gate": "<gate name>",
      "phase": "<RED | GREEN | REFACTOR>",
      "failure_rate": <0.0-1.0>,
      "sample_count": <N>,
      "confidence": "<tentative | established>",
      "last_seen": "<YYYY-MM-DD>"
    }
  ],
  "smell_signals": [
    {
      "failure_pattern": "<recurring failure category>",
      "smell_tag": "<tag from pattern catalog>",
      "occurrences": <N>,
      "last_seen": "<YYYY-MM-DD>"
    }
  ],
  "expiry_threshold_runs": 20
}
```

## Merge rules

When merging a new run's data into an existing profile:

- **agent_performance**: sum `tasks`, `failures`, `retries`, `skips` into running totals. Recompute rates as `failures / tasks`, etc. Increment `runs`.
- **slicing_signals**: match on `property` + `outcome`. Update `rate` as weighted average: `(old_rate * old_sample_count + new_rate * new_sample_count) / (old_sample_count + new_sample_count)`. Increment `sample_count`.
- **pattern_signals**: match on `pattern`. Same weighted-average merge for rates. For `smell_correlations`, match on `smell_tag` within the pattern entry; increment `failure_count`, update `last_seen`.
- **gate_signals**: match on `gate` + `phase`. Same weighted-average merge.
- **smell_signals**: match on `failure_pattern`. Increment `occurrences`.

## Confidence thresholds

- `sample_count < 3` → `"tentative"` — do not surface as actionable guidance
- `sample_count >= 3` → `"established"` — safe to surface as actionable

## Expiry

After merging, scan all profile entries. Any entry where `last_seen` is older than `expiry_threshold_runs` runs (default 20) gets removed. Increment `runs_analyzed`. Set `last_updated` to today's date.
