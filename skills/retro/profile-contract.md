# Profile Contract

Reference for skills and agents that consume `.tap/retros/_profile.json`. The profile is produced by `/tap:retro` and accumulates structural observations across runs. This document defines how consumers read and apply its signals.

## Location

```
.tap/retros/_profile.json
```

If the file does not exist, skip all profile-informed adjustments — the pipeline runs identically without it. Never fail or halt because the profile is absent.

## Read protocol

1. Check if `.tap/retros/_profile.json` exists.
2. If yes, parse it. The schema is defined in `skills/retro/SKILL.md > Phase: emission > Step: write-profile`.
3. Only act on entries where `confidence == "established"` (sample_count ≥ 3). Ignore `"tentative"` entries — they are noise until confirmed.
4. Apply the relevant signal category for your role (see below).

## Signal categories and consumers

### agent_performance

**Who reads it**: `run` orchestrator, `sketch` orchestrator, phase agents (TestWriter, CodeWriter, Refactorer).

```json
"agent_performance": {
  "CodeWriter": { "failure_rate": 0.35, "retry_rate": 0.2, ... }
}
```

**How to apply**:

- **Orchestrator** (run/sketch): if an agent's `failure_rate > 0.3` (established), include a one-line warning in the agent's dispatch prompt: `"Profile note: this agent has a {rate}% failure rate across {N} tasks. Take extra care with {common failure category if available}."` Do not change the model or effort — surface the signal, let the agent self-adjust.
- **Phase agent** (self-awareness): if your own agent name appears with `failure_rate > 0.3`, read the profile's `gate_signals` for your typical failure phase to understand what gates you tend to trip. Invest an extra verification pass on those gates before committing.

### slicing_signals

**Who reads it**: `convey` skill during the slicing step.

```json
"slicing_signals": [
  { "property": "files_touched > 3", "outcome": "saga_isolation", "rate": 0.6, "confidence": "established" }
]
```

**How to apply**:

- During Step: slicing, after building the initial task list, check each task against established slicing signals.
- If a task matches a property with a high saga-isolation rate (> 0.4), flag it in the self-review: `"Profile warning: tasks matching '{property}' saga-isolate at {rate}. Consider splitting."` The emitter decides whether to split — the signal is advisory.
- Do not auto-split. Surface the signal; human or self-review acts on it.

### pattern_signals

**Who reads it**: `convey` skill during pattern-shaped GREEN emission, `into` skill during approach discussion, `sketch` during pattern-check, `PatternsDiscoverer` and `PatternScanner` agents.

```json
"pattern_signals": [
  { "pattern": "strategy", "clean_green_rate": 1.0, "confidence": "established" }
]
```

**How to apply**:

- **convey / sketch**: when choosing between multiple candidate patterns for a task's GREEN shape, prefer patterns with higher `clean_green_rate` (established). Mention the rate in the pattern hint: `"Pattern 'strategy' has 100% clean GREEN rate across {N} samples."` This is a tiebreaker, not an override — neighbor conventions still take priority.
- **into**: during Step: approaches, if an approach maps to a pattern with established performance data, surface it: `"Profile data: pattern '{name}' has {rate}% clean GREEN rate."` Let the user factor it into their decision.
- **PatternsDiscoverer / PatternScanner**: when ranking candidate patterns, boost patterns with established high `clean_green_rate`. Demote patterns with established low rates. Cite the profile data in the recommendation shape.

### gate_signals

**Who reads it**: phase agents (TestWriter, CodeWriter, Refactorer), `run` orchestrator, `sketch` orchestrator.

```json
"gate_signals": [
  { "gate": "tsc", "phase": "GREEN", "failure_rate": 0.15, "confidence": "established" }
]
```

**How to apply**:

- **Phase agent**: if an established gate signal matches your phase, run that gate FIRST in your verification sequence (before other gates) and inspect the output carefully. E.g., if tsc fails 15% during GREEN, CodeWriter should run tsc immediately after writing code, before running the full gate battery.
- **Orchestrator**: no action needed — agents self-adjust. The orchestrator surfaces gate_signals in the dispatch prompt only when `failure_rate > 0.3` for the dispatched phase.

### smell_signals

**Who reads it**: `PatternsDiscoverer` agent, `PatternScanner` agent, `refactor` skill.

```json
"smell_signals": [
  { "failure_pattern": "compilation-error", "smell_tag": "inappropriate-intimacy", "occurrences": 5 }
]
```

**How to apply**:

- **PatternsDiscoverer / PatternScanner**: when scanning for patterns near seed files, cross-reference with smell_signals. If a recurring failure pattern maps to a smell tag, check whether the seed files exhibit that smell. Surface it in the pattern map if so.
- **refactor**: during the investigate phase, check smell_signals for the target file. If the file appears in areas where a mapped smell has high occurrences, prioritize that smell in the reduction plan.

### token_signals

**Who reads it**: `run` orchestrator, `convey` skill during slicing/task estimation.

```json
"token_signals": {
  "avg_tokens_per_phase": { "RED": 8000, "GREEN": 15000, "REFACTOR": 6000, "DEBUG": 20000 },
  "avg_tokens_per_complexity": { "simple": 12000, "moderate": 25000, "complex": 50000 },
  "sample_count": 5,
  "confidence": "established",
  "outlier_registry": [ { "task_id": "task-03-complex-wiring", "total_tokens": 45000, ... } ]
}
```

**How to apply**:

- **Orchestrator** (run): use `avg_tokens_per_complexity` to anticipate which tasks in the current wave may be expensive. If a task matches the `complex` class (5+ files) and established data shows high token consumption, no action needed — this is observational context for post-run retro.
- **convey**: during slicing, if established token data shows that tasks with certain properties (high file count, specific patterns) are outliers, surface this as a decomposition advisory: `"Profile note: tasks touching 5+ files average {N} tokens (established, {sample_count} samples). Consider splitting."` Advisory only — do not auto-split.
- **retro** (self): use `outlier_registry` to detect recurring outlier characteristics. If the same pattern or file-count profile appears in 3+ outlier entries, surface it as an established finding.

**Token data may be unavailable** for older runs, sketch-mode executions, or interrupted sessions. When `token_signals` is absent or `sample_count == 0`, skip all token-informed adjustments silently.

## Hard rules

- **Never halt on missing profile.** The profile is optional enrichment. Every skill and agent must function identically without it.
- **Never act on tentative data.** Only `established` entries (sample_count ≥ 3) drive behavior adjustments.
- **Surface, don't override.** Profile signals are advisory. They inform decisions — they don't make them. A pattern with 100% clean GREEN rate is a good sign, not a mandate.
- **Cite the data.** When surfacing a profile signal, include the rate and sample count so the human can judge relevance.
- **No circular writes.** Consumers read the profile. Only `retro` writes it. No skill or agent modifies `_profile.json`.
