---
name: retro
description: Post-mortem analysis of completed /tap-run executions. Extracts commit trailers, classifies failures, computes per-agent and per-pattern metrics, and emits a two-layer output — an ephemeral run report plus a rolling aggregate profile. Use when the user invokes `/tap-retro`, says "run retro", "what happened in that run", "analyze the run", "post-mortem", or wants to understand why a pipeline succeeded or failed.
---


# tap-retro

Read-only post-mortem of completed `/tap:run` executions. Two-layer output: an ephemeral run report (`.tap/retros/<slug>-<YYYY-MM-DD>.md`) scoped to one run, and a rolling aggregate profile (`.tap/retros/_profile.json`) that accumulates structural observations across runs.

Retro never modifies source code or task files. It reads git history, task specs, and reviewer output — nothing else.

## Phase: discovery

### Purpose

Identify which completed runs to analyze. A run is "completed" when its slug exists under `.tap/tickets/done/<slug>/`.

### Step: resolve-targets

If the user passed a slug argument (`/tap-retro <slug>`), use that slug. Verify it exists under `.tap/tickets/done/<slug>/` — if not, halt and surface: "No completed run found for slug `<slug>`. Check `.tap/tickets/done/` for available slugs."

If no argument was passed:

1. List all directories under `.tap/tickets/done/`.
2. List all existing retro reports under `.tap/retros/` (filenames match `<slug>-<YYYY-MM-DD>.md`).
3. Compute the "unretro'd" set: slugs in `done/` that have no corresponding report in `retros/`.
4. If unretro'd slugs exist, analyze all of them (in lex order). Surface the list to the user: "Analyzing N unretro'd run(s): slug-a, slug-b, ..."
5. If every slug already has a report, list available slugs and ask the user which to re-analyze. A re-analysis overwrites the existing report and updates the profile with fresh data.

### Step: locate-commits

For each target slug:

1. Read the task files at `.tap/tickets/done/<slug>/task-*.md` to extract all `id:` values from frontmatter.
2. Search the git log on the current branch for commits carrying `Tap-Task:` trailers that reference any of those task ids:
   ```
   git log --all --format="%H %s%n%(trailers:key=Tap-Task,valueonly)" | grep -B1 "<task-id>"
   ```
   Collect all matching commit SHAs.
3. Find the **commit range**:
   - `merge_sha` — the latest commit in the set (chronologically).
   - `parent_sha` — the commit immediately before the earliest commit in the set: `git rev-parse <earliest_sha>~1`.
4. Detect the branch name from commit messages or reflog: look for `tap-<slug>` references.
5. Record: `slug`, `parent_sha`, `merge_sha`, `branch`, `task_ids[]`, `task_count`.

If no commits with matching trailers are found, surface: "No commits found with Tap-Task trailers for slug `<slug>`. The run may not have completed normally." Skip this slug.

## Phase: extraction

### Purpose

Parse the commit range and build a structured timeline of every phase, failure, and decision for the run.

### Step: parse-commits

For each target slug, extract the full commit data within `parent_sha..merge_sha`:

```
git log <parent_sha>..<merge_sha> --format="COMMIT:%H%nSUBJECT:%s%nDATE:%aI%nTap-Task:%(trailers:key=Tap-Task,valueonly)%nTap-Phase:%(trailers:key=Tap-Phase,valueonly)%nTap-Files:%(trailers:key=Tap-Files,valueonly)%nTap-Decisions:%(trailers:key=Tap-Decisions,valueonly)%n---"
```

Parse each commit into a structured record:

```
{
  sha, subject, date,
  tap_task,          # task id or "reviewer"
  tap_phase,         # RED | GREEN | REFACTOR | DEBUG
  tap_files,         # comma-separated paths
  tap_decisions,     # one-line (Debugger only)
  commit_type        # inferred from subject prefix: test/feat/refactor/fix
}
```

Sort commits chronologically (oldest first).

### Step: build-task-timeline

Group commits by `tap_task`. For each task id, build a timeline:

1. **Phases completed**: which of RED, GREEN, REFACTOR have a commit (excluding DEBUG).
2. **Phases skipped**: which phases are absent. REFACTOR may be legitimately skipped (no-op in spec) — check the task file's `## REFACTOR ### Action` to distinguish intentional skip from failure skip.
3. **Fix commits**: count commits with `tap_phase == DEBUG` for this task (Debugger Shape A retries).
4. **Saga-isolated**: a task is saga-isolated if it has RED but no GREEN, or if it has RED+GREEN but was explicitly dropped (no merge integration). Detect by checking if the task's commits are followed by later tasks' commits without this task progressing past its last phase.
5. **Timestamps**: earliest commit date, latest commit date — used for the turn heatmap.

### Step: extract-reviewer-verdict

Find commits where `tap_task == "reviewer"` or `tap_phase == DEBUG` with `tap_task == "reviewer"` (Shape B). If a Reviewer commit exists:

- Parse the commit message body for structured verdict data (Blocker count, Warning count, pass/fail).
- If no explicit verdict in the commit, infer from the presence/absence of Shape B Debug commits:
  - No Shape B commits after Reviewer → Reviewer passed (or only Warnings/minors).
  - Shape B commits exist → Reviewer found Blockers. Check if a second Reviewer commit follows Shape B — if yes and no further Shape B, Blockers were resolved.

Record: `reviewer_verdict` (pass/fail), `blocker_count`, `warning_count`.

### Step: extract-pattern-hints

For each task, read `.tap/tickets/done/<slug>/task-*.md` and look for `### Pattern hint` sections under `## GREEN`. Extract:

- `pattern_name` — the pattern referenced (e.g., "strategy", "observer", "descriptor-array").
- `followed` — check if the GREEN commit's subject or diff aligns with the pattern. A GREEN commit that exists and has no subsequent DEBUG commits for that task suggests the pattern was followed successfully. A GREEN that required DEBUG retries suggests the pattern may have been ignored or was insufficient.

Classify each task's pattern status:
- `followed` — pattern hint present AND clean GREEN (no DEBUG retries for GREEN phase).
- `ignored` — pattern hint present AND GREEN required DEBUG retries or saga-isolated.
- `N/A` — no pattern hint in the task spec.

### Step: classify-failures

For each task that has DEBUG commits or was saga-isolated, classify the failure:

Read the commit subjects and `Tap-Decisions` trailers from DEBUG commits. Map each failure to a category:

| Category | Phase | Signal | Quality |
|----------|-------|--------|---------|
| `missing-module` | RED | Test imports a module that doesn't exist yet | Bad RED — test should fail on assertion, not import |
| `assertion-mismatch` | RED | Test assertion doesn't match expected shape | Good RED — this is the correct failure mode |
| `compilation-error` | GREEN | tsc/build fails | GREEN didn't compile |
| `logic-error` | GREEN | Tests fail on wrong return value / behavior | GREEN compiled but logic is wrong |
| `type-error` | GREEN | Type mismatch in implementation | GREEN has type issues |
| `broke-behavior` | REFACTOR | Existing tests fail after refactor | REFACTOR changed behavior |
| `gate-failure` | any | A quality gate (lint, tsc, build, test) fails | Gate-specific — record which gate |
| `wiring-gap` | GREEN | Provider/injectable not threaded | Missing data path |
| `scope-violation` | any | Change outside task boundary | Agent went out of scope |

Use the `Tap-Decisions` trailer as the primary classifier when present. Fall back to commit subject parsing when `Tap-Decisions` is absent.

## Phase: analysis

### Purpose

Compute all metrics for the run report (Layer 1) and update structural observations for the profile (Layer 2).

### Step: compute-run-metrics

For each target slug, compute:

- **Tasks completed**: count of tasks with all expected phases (RED + GREEN, with REFACTOR optional per spec).
- **Tasks saga-isolated**: count of tasks that were dropped mid-pipeline.
- **Debugger retries**: total DEBUG commits across all tasks.
- **Reviewer verdict**: pass/fail from extraction.
- **Pattern adherence**: count of tasks where pattern was `followed` vs total tasks with pattern hints.
- **Success rate**: `tasks_completed / total_tasks`.
- **Saga-isolation rate**: `tasks_saga_isolated / total_tasks`.
- **Debugger invocation rate**: `tasks_with_debug_commits / total_tasks`.

### Step: compute-turn-heatmap

For each task, compute a "heat" score based on:

1. **Time span**: difference between earliest and latest commit timestamp for that task.
2. **Fix commit density**: number of DEBUG commits relative to phase commits.
3. **Commit count**: total commits for the task (phases + fixes).

Rank tasks by heat score (highest = most agent effort consumed). This identifies tasks that were disproportionately expensive.

### Step: compute-agent-performance

Aggregate per-agent stats across all tasks in this run:

- **TestWriter**: tasks where RED completed, tasks where RED required DEBUG retry, tasks where RED saga-isolated.
- **CodeWriter**: tasks where GREEN completed, tasks where GREEN required DEBUG retry, tasks where GREEN saga-isolated.
- **Refactorer**: tasks where REFACTOR completed, tasks where REFACTOR was skipped (intentional no-op), tasks where REFACTOR required DEBUG retry.

For each agent, compute: `failure_rate`, `retry_rate`, `skip_rate`.

### Step: detect-structural-patterns

Cross-reference task properties with outcomes to identify structural patterns. For each task, determine properties from the task file frontmatter:

- **File count**: number of entries in `files.create` + `files.modify`.
- **Context depth**: number of entries in `context[]`.
- **Cross-service**: whether files span multiple top-level directories (heuristic for cross-service).

Compute correlations:

1. "Tasks touching >N files saga-isolate at rate X" — group tasks by file count threshold (2, 3, 5) and compute saga-isolation rate per group.
2. "Phase Y fails at rate Z for agent W" — per-phase failure rates.
3. "Pattern hint P correlates with clean GREEN at rate Q" — group by pattern name, compute rate of clean GREEN (no DEBUG).
4. "Gate G fails most often during phase H" — parse failure categories to extract gate names and phases.

### Step: compute-token-consumption

Capture token usage per task and per phase from the session's agent dispatch results. The Agent tool returns a usage summary after each subagent completes — these summaries are the source of truth for token data.

**Data source**: when `tap:run` dispatches phase agents (TestWriter, CodeWriter, Refactorer, Debugger), the Agent tool's response includes `input_tokens` and `output_tokens` consumed by that subagent call. If `SESSION_RESUME.json` or an equivalent run artifact captures these values, read them. Otherwise, token data is unavailable — record `"token_data": "unavailable"` and skip quantitative analysis for this run.

When token data IS available, compute per-task:

```
{
  task_id,
  phases: {
    RED:      { input_tokens, output_tokens, total_tokens },
    GREEN:    { input_tokens, output_tokens, total_tokens },
    REFACTOR: { input_tokens, output_tokens, total_tokens },  // null if skipped
    DEBUG:    { input_tokens, output_tokens, total_tokens, invocations: N }  // null if none
  },
  total_tokens,
  outlier: <bool>  // true if total_tokens > 3x run average
}
```

Then compute run-level aggregates:

1. **Per-phase averages**: mean `total_tokens` for RED, GREEN, REFACTOR, DEBUG across all tasks in the run. This reveals if a phase is consistently cheaper/more expensive.
2. **Outlier tasks**: tasks consuming 3x+ the run average. Flag these — complexity was likely underestimated at decomposition time.
3. **Total run consumption**: sum of all task tokens.

### Step: cross-reference-pattern-smells

For each pattern extracted in `extract-pattern-hints`, read its pattern card at `${CLAUDE_PLUGIN_ROOT}/patterns/<category>/<pattern_name>.md` and collect the `smells_it_introduces` frontmatter field (a list of kebab-case smell tags).

Cross-reference those smell tags against the run's failure taxonomy (from `classify-failures`). A failure maps to an introduced smell when the failure's `category` matches or is a sub-string of a smell tag (e.g., failure category `over-abstraction` matches smell tag `over-abstraction-single-variant`), or when the failure `detail` text contains the smell tag verbatim.

For each match, record a `pattern_smell_correlation` entry:

```
{
  pattern,          # pattern name from the hint
  smell_tag,        # the matching smells_it_introduces tag
  task,             # task id where the failure occurred
  failure_category, # from classify-failures
  phase             # phase where the failure occurred
}
```

If no matches are found, skip silently -- this step produces zero entries in most clean runs.

These entries feed into `_profile.json`'s `pattern_signals` via the `update-profile` step (as `smell_correlations` sub-entries) to accumulate evidence across runs.

### Step: update-profile

Load `.tap/retros/_profile.json` if it exists. If not, initialize an empty profile.

For each structural observation from this run:

1. **agent_performance**: merge this run's per-agent stats into the profile's running totals. Recompute rates.
2. **slicing_signals**: for each correlation found in detect-structural-patterns, find or create a matching entry. Increment `sample_count`, update `rate` as a running average, set `last_seen` to today's date. Set `confidence`:
   - `sample_count < 3` → `"tentative"`
   - `sample_count >= 3` → `"established"`
3. **pattern_signals**: merge pattern adherence and clean-GREEN rates per pattern name. For each `pattern_smell_correlation` entry from `cross-reference-pattern-smells`, find or create a `smell_correlations` sub-entry on the matching pattern signal; increment `failure_count`, set `last_seen`.
4. **gate_signals**: merge gate failure rates per gate per phase.
5. **smell_signals**: if the retro detects recurring failure patterns (same category appearing 3+ times across runs), check the pattern catalog at `${CLAUDE_PLUGIN_ROOT}/patterns/` for matching smell tags. Add entries mapping failure patterns to smell tags.
6. **token_signals**: if token data was available for this run, merge into the profile:
   - Per-phase averages: weighted-average merge of `avg_tokens_per_phase.<PHASE>` with existing profile values.
   - Per-complexity-class averages: if tasks can be classified by complexity (file count as proxy — 1-2 files = `simple`, 3-4 = `moderate`, 5+ = `complex`), compute average tokens per class and merge.
   - Outlier registry: append outlier tasks (3x+ average) with their characteristics (`pattern_used`, `file_count`, `phase_breakdown`). Keep only the 20 most recent outliers (FIFO eviction).

**Expiry**: after merging, scan all profile entries. Any entry where `last_seen` is older than `expiry_threshold_runs` runs (default 20) gets removed. Increment `runs_analyzed`. Set `last_updated` to today's date.

## Phase: emission

### Purpose

Write the run report and profile, then surface actionable findings.

### Step: write-run-report

For each target slug, write the report to `.tap/retros/<slug>-<YYYY-MM-DD>.md`. Create the `.tap/retros/` directory if it doesn't exist.

Follow the [report template](report-template.md) exactly.

### Step: write-profile

Write or update `.tap/retros/_profile.json`. Create the directory if needed.

Follow the [profile schema](profile-schema.md) for structure, merge rules, confidence thresholds, and expiry logic.

### Step: surface-findings

Present key findings to the user. Structure the output as:

1. **Run summary** — one-line per slug analyzed: "slug-name: N/M tasks completed, K retries, reviewer passed/failed."

2. **Threshold crossings** — any profile entry that moved from `tentative` to `established` in this analysis. These are new structural observations backed by 3+ samples:
   - "NEW: CodeWriter failure rate is 0.25 across 4 runs (established). Consider reviewing task decomposition granularity."
   - "NEW: Tasks touching >3 files saga-isolate at 60% (established). Consider splitting multi-file tasks."

3. **Surprises** — results that deviate from expectations or prior profile data:
   - High failure rate for an agent that was previously reliable.
   - A pattern hint that correlates with MORE failures, not fewer.
   - A gate that fails in a phase where it shouldn't (e.g., tsc failing in REFACTOR suggests behavior change).

4. **Actionable suggestions** — tied to specific structural observations with sample counts. Only surface suggestions backed by `established` confidence:
   - "CodeWriter effort:low fails at 40% (5 samples) — consider effort:medium in agent frontmatter for complex tasks."
   - "Pattern 'strategy' correlates with 100% clean GREEN (4 samples) — prioritize strategy-shaped decomposition for similar features."
   - "tsc gate fails at 15% during GREEN (10 samples) — TestWriter may be emitting type-incompatible test fixtures."

Do NOT surface tentative observations as actionable suggestions. Prefix tentative findings with "[tentative]" and present them as "early signals, not yet reliable."

## Anti-rationalization table

Do not produce these rationalizations. If you catch yourself reasoning toward one, stop and take the correct action.

| Where | Rationalization | Real problem | Correct action |
|---|---|---|---|
| Discovery | "Run was clean, nothing worth analyzing" | Skips retro for successful runs. Clean runs are signal too — they build the profile's success baselines | Analyze every completed run. Success data is as valuable as failure data for establishing rates |
| Locate commits | "Commit messages are clear enough, skip trailer parsing" | Infers task/phase from subjects instead of parsing Tap-Task/Tap-Phase trailers. Subjects can drift from actual phase | Always parse trailers. `Tap-Task` and `Tap-Phase` are the structured contract. Subjects are human-readable, not machine-reliable |
| Build timeline | "Task has no REFACTOR commit, it failed" | Assumes missing REFACTOR = failure. The task spec may declare REFACTOR as no-op (intentional skip) | Check the task file's `## REFACTOR ### Action` before classifying. Intentional skip ≠ failure |
| Extract patterns | "No pattern hints in this run, skip pattern analysis" | Skips pattern extraction entirely. Tasks without hints should be classified as N/A, not ignored | Classify every task: `followed`, `ignored`, or `N/A`. The N/A count is useful data — it shows how much of the pipeline runs unguided |
| Classify failures | "Tap-Decisions trailer says enough, don't need to read the diff" | Takes the Debugger's self-reported diagnosis at face value without verifying against commit content | Use Tap-Decisions as primary classifier but cross-reference with commit subject and phase. Debugger's diagnosis may be incomplete |
| Compute metrics | "Only 2 samples but the signal is strong, mark as established" | Inflates confidence. Tentative threshold exists for a reason — small samples produce unreliable rates | `sample_count < 3` = tentative. Always. Strong signal from 2 samples is anecdotal, not established |
| Detect patterns | "No structural patterns in this run" | Skips correlation computation because results seem obvious or uniform | Always compute correlations for file-count thresholds, per-phase failure rates, pattern adherence, and gate failures. "Nothing found" is a valid result — not computing is not |
| Update profile | "Profile already has this data, no need to merge" | Skips merge because existing data "looks the same." Rates shift with new samples — even confirming data updates the average | Always merge. Recompute weighted averages, increment sample counts, update last_seen. Stale data expires — fresh data keeps entries alive |
| Surface findings | "All tentative signals look actionable, surfacing them" | Presents tentative observations (< 3 samples) as actionable guidance. Premature advice based on noise | Only surface established signals as actionable. Prefix tentative findings with "[tentative]" and frame as early signals, not recommendations |
| Surface findings | "I'll add my own interpretation of what went wrong" | Invents correlations or narratives not backed by the data. Retro reports facts, not theories | Tie every observation to specific sample counts and rates. If the data doesn't support a claim, don't make it |
| Token analysis | "Token data isn't available, skip the whole section" | Omits the section entirely instead of recording unavailability. Future retros need to know the data gap exists | Always emit the token section. If data is unavailable, write `"token_data": "unavailable"` and state "Token data unavailable for this run" in the report. The absence is itself data |
| Token analysis | "This task used a lot of tokens because it was complex" | Rationalizes high consumption without checking whether it's actually an outlier relative to the run average | Apply the 3x threshold mechanically. A task is an outlier if `total_tokens > 3 * run_average` — not because it "seems complex" |

## Constraints

- Keep retro read-only — analyze source code and task files, modify neither.
- Treat profile entries with `sample_count < 3` as `tentative` — present them with that qualifier, not as facts.
- Accept that ephemeral reports go stale — that's by design. The profile is the durable layer.
- Tie actionable suggestions to specific structural observations with sample counts.
- Require meaningful sample sizes before drawing correlations. 1 failure is noise, 5 failures in the same pattern is signal.
- Skip slugs gracefully when they have no commits with Tap trailers — surface the absence honestly.
- If `.tap/retros/` doesn't exist, create it. If `_profile.json` doesn't exist, initialize it with `version: 1`, `runs_analyzed: 0`, and empty arrays/objects.
- Use `YYYY-MM-DD` for all dates.
- Limit git operations to read-only commands: `git log`, `git diff`, `git rev-parse`.
