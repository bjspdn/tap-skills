---
name: convey
description: Decomposes an existing `.tap/tickets/<slug>/ideation.md` into TDD task files in the same slug folder. Each task is a thin vertical slice (RED → GREEN → REFACTOR; the executor commits each phase itself). Use when an ideation.md exists and the user wants it broken into actionable engineering tasks — invoked via `/tap-convey`, "convey this", "decompose this into tasks", "break it into TDD steps".
---

## Phase: writing

### Purpose

Decompose `.tap/tickets/{slug}/ideation.md` into a series of `task-{NN}-{task-slug}.md` files in the same slug folder. Each file is a vertical TDD slice an engineer can execute end-to-end.

Assume the engineer has questionable taste and limited codebase familiarity — be explicit. Assume someone with deep codebase knowledge reviews the tasks before they run, so over-specifying is safer than under-specifying.

### Step: ingestion

Resolve the target slug: if the user passed an argument (`/tap-convey {slug}`), use it. Otherwise scan `.tap/tickets/` for folders containing an `ideation.md` without any `task-*.md` siblings and use that slug.

Disregard any prior conversation context about this feature — base all decisions on what `ideation.md` actually says, not on discussion that preceded it.

Read `.tap/tickets/{slug}/ideation.md` end-to-end. Pay particular attention to `## Approach` (the pattern + flow), `## Signatures` (interface shapes when present), `## Constraints`, and `## Boundaries`.

If the ideation references file:line locations you do not recognize, run targeted Grep / Read calls to ground yourself before slicing — do not invent file paths.

Do not write anything yet.

After reading `ideation.md`, detect the consuming repo's test command by reading the project manifest:

- `package.json` → `scripts.test` (e.g. `bun test`, `jest`, `vitest run`)
- `Cargo.toml` → `cargo test`
- `pyproject.toml` / `setup.py` → `pytest` (check `tool.pytest` / `[tool.pytest.ini_options]`) or `python -m unittest`
- `go.mod` → `go test ./...`
- `pom.xml` / `build.gradle` → `mvn test` / `gradle test`
- `Gemfile` → `bundle exec rspec` or `bundle exec rake test`

Capture the resolved command as `$TEST_COMMAND`. Every emitted task's `### Verify` block under RED, GREEN, and REFACTOR must use this command, scoped to the task's file path when possible (e.g. `bun test path/to/file`).

If no manifest matches, ask the user: "What command runs the test suite scoped to a single file?"

### Step: dependency-scan

Before slicing, build a dependency map and an integration map of the files the ideation touches. Extract seed files from `ideation.md` — every `file:line` reference in `## Context`, `## Approach`, and `## Signatures`. Also extract new signatures, parameters, and injectable dependencies described in the ideation — these are the **projected changes** the scan must trace.

**Projected-changes extraction protocol** — fill the `{projected_changes}` slot by parsing `ideation.md`:

- New symbols → every entry in `## Signatures`
- Injectables (new dependencies threaded through callers) → every entry in `## Approach > SEAMS:`
- New error tags → every entry in `## Error design`
- New params → any signature in `## Signatures` whose params are not present in the matching pre-existing signature at hop-0 (the seed file's current signature)

When `## Signatures` or `## Error design` is absent, drop those rows; do not invent projected changes.

Spawn a dependency scan agent:

```text
Agent(
  subagent_type: "DependencyScanner",
  description: "Build dependency + integration map",
  prompt: "
    seed_files: {list from ideation file:line refs}
    projected_changes: {list extracted via the projected-changes protocol}
  "
)
```

Wait for the agent to return. Use both maps in the slicing step below — the consumer map for ordering, the integration map for wiring tasks.

### Step: pattern-scan

After the dependency-scan returns, spawn a pattern-recognition agent to identify structural patterns near the seed files. This agent reads the pattern catalog at `${CLAUDE_PLUGIN_ROOT}/patterns/` and neighboring modules to determine which patterns should shape each task's GREEN step.

```text
Agent(
  subagent_type: "PatternScanner",
  description: "Build pattern map from neighbors",
  prompt: "
    seed_files: {list from ideation file:line refs}
    ideation_path: .tap/tickets/{slug}/ideation.md
  "
)
```

Wait for the agent to return. Use the pattern-map alongside the dependency-map and integration-map in the slicing and emission steps below.

### Step: slicing

Decide how many tasks the ideation needs. Each task must be a *vertical slice*: one observable behavior, end-to-end, testable in isolation. Do not slice horizontally (one task for types, one for implementation, one for tests) — horizontal slices produce tasks that cannot pass on their own.

See the [task contract](task-contract.md) for vertical-slicing criteria, the TDD philosophy each task must follow, and the [expand-contract pattern](task-contract.md#expand-contract-pattern) for breaking changes to shared modules.

**Ordering** — use the consumer map from the previous step:

- Order tasks leaves-first: files with fewest dependents go first, high-fanout files go last.
- Default to one file per task. A module and its colocated test count as one unit.

**Pattern annotation** — use the pattern-map from the pattern-scan step:

- For each task, check if its seed file has a `<green-shape>` recommendation in the pattern-map.
- If yes, attach the pattern name + evidence to the task for use during emission (a `### Pattern hint` sub-section under `## GREEN`).
- If a pattern-map entry says "No pattern recommendation", the task gets no pattern annotation.

**Wiring tasks from the integration map** — for each `<provider-chain>` in the integration map:

- Every file in the chain that needs modification gets a task (or is covered by an existing task).
- Wiring tasks come AFTER the task that introduces the injectable and BEFORE the task that tests the end-to-end behavior.
- A wiring task's RED test verifies that the data flows from source to injection point — e.g., "config loaded at entry point reaches the module that needs it."
- If a provider chain has `has-access='false'` at any hop, that hop MUST have a corresponding task that threads the data through.

Note: `<provider-chain>` here refers to the integration-map XML returned by the dependency-scan agent (an internal data structure passed between agents), not to a tag inside emitted task files.

**Breaking changes to shared modules** — when a change breaks a seed file's public API and the file is classified `shared` or `high-fanout`:

1. Task N: add new API alongside old in the shared module (expand)
2. Task N+1..N+K: migrate each consumer to the new API (one task per consumer file)
3. Task N+K+1: remove the old API from the shared module (contract)

When the change is internal (no public API break), a single task on the seed file is sufficient — no expand-contract needed.

**Warnings** — if the dependency map contains warnings, handle them:

- Circular deps: note in affected task files ("circular dependency between X and Y — ordering is best-effort"), continue with best-effort leaves-first ordering.
- Unreadable imports: fall back to the heuristic "an earlier task never relies on a file a later task creates" for those files.
- High consumer count (>10): flag in the task summary as architectural signal ("file X has N direct consumers — consider extracting a facade"), still emit one-task-per-consumer.
- Dangling injectables: if a provider chain has no data source within 4 hops, halt emission and ask the user via multi-choice:
  (a) Add a new config entry to thread the data — surface concrete file path
  (b) Add a factory or DI container — surface where it should live
  (c) Reject the feature scope as currently designed — return to /tap-into for re-ideation
  Resume emission only after the user picks.
- Deep provider chains (4+ hops): flag as architectural signal — the data is threading through too many intermediaries, consider a context/service pattern.

### Step: emission

For each task, write a file at `.tap/tickets/{slug}/task-{NN}-{task-slug}.md` where `{NN}` is zero-padded (`01`, `02`, ...). Each file must conform to the [task contract](task-contract.md).

**File format**: every task file is markdown with YAML frontmatter. Frontmatter holds machine fields (`id`, `files`, `context`); the body holds prose phases as `## RED` / `## GREEN` / `## REFACTOR`, each split into `### Action` / `### Example` / `### Verify` / `### Done`. There is no `## COMMIT` phase — the executor (`run`) commits each phase itself; see `task-contract.md > Per-phase commits`. Code lives in fenced code blocks (```` ```ts ````, ```` ```sh ````). Do **not** use HTML/XML-style tags inside the body — they trigger HTML-block parsing in markdown renderers and desync on blank lines, breaking display.

**Context frontmatter rule**: every task file must include a `context:` array in frontmatter. For each symbol the task references — types, functions, interfaces, constants — read its definition site and include `name`, `path`, `line`, and `signature` (use YAML `|` block scalar for multi-line signatures). For symbols introduced by the ideation that do not yet exist, set `new: true` and omit `path` / `line`. The dependency-scan agent already collected import/export data and provider chains; propagate this data into the task files so the executing agent never has to explore the codebase to find where symbols live or what they look like.

**Anchor selection rule**: when a task modifies an existing file, the `modify[].anchor` MUST be a symbol name (function, class, exported binding) — not a line number. Line numbers shift on edit and go stale before the engineer applies the task. To pick the anchor:

1. Take the file:line evidence from dependency-scan.
2. Open the file at that line and find the smallest enclosing named symbol (function / method / class / exported const).
3. Use that symbol's name as the anchor.

If no enclosing named symbol exists (e.g. top-level imports), use a stable nearby identifier (the first export below the line) and add a `### Action` instruction in the task body explaining what to insert and where relative to the anchor.

**Test command rule**: every `### Verify` block uses the `$TEST_COMMAND` resolved in ingestion, scoped to the task's file when the runner supports path scoping. Never hardcode `bun test` (or any specific runner) unless it's the resolved command.

**Pattern-shaped GREEN rule**: when a task has a pattern annotation from the slicing step:

- Add a `### Pattern hint` sub-section as the first child of `## GREEN`, naming the pattern and citing the evidence file:line from the pattern-map.
- Shape the GREEN `### Action` to incorporate the pattern — e.g., "Write minimum code using a descriptor array + executor loop" instead of just "Write minimum code that passes."
- Shape the GREEN `### Example` to show code following the pattern shape, not naive implementation.

When a task has no pattern annotation:

- No `### Pattern hint` sub-section. GREEN stays vanilla "minimum code that passes."
- REFACTOR `### Action` gets a fallback check: "Query `${CLAUDE_PLUGIN_ROOT}/patterns/` (see README.md for discovery API) to see if a pattern fits the GREEN output and apply it. Otherwise: no refactoring needed — structure is adequate."

**REFACTOR concreteness rule**: every REFACTOR `### Action` must name specific operations (extract/rename/inline/deduplicate) with concrete file:symbol targets. If GREEN was pattern-shaped and produced clean code that needs no restructuring, write `No refactoring needed — GREEN followed pattern, structure is adequate.` under `### Action` instead of inventing vague cleanup work. Vague refactor instructions cause agents to burn 40+ turns flailing.

**One concern per task**: if a task touches more than 2 files across different services, split it. High turn counts correlate with tasks that combine unrelated wiring (e.g. "emit events from runners" that touches TicketRunner + ParallelRunner + runTickets = 3 separate concerns).

**Code fences in examples**: every `### Example` containing code MUST use a fenced code block with a language tag (```` ```ts ````, ```` ```py ````, ```` ```sh ````). The fence keeps blank lines safe inside code, prevents markdown parsers from interpreting `_`, `*`, `<`, `>` as formatting, and gives renderers syntax highlighting. Never paste raw code without a fence.

Emit task files directly using the Write tool.

### Step: wave-preview

Run the wave-inference algorithm from `run/RUN_FLOW.md > Wave inference` against the emitted tasks. Build the symbol-owner map from each task's `context[]` (entries with `new: true` map to the task whose `files.create` introduces them); derive task deps; topo-sort; split waves on file overlap.

Surface the resulting wave plan as a table:

| Wave | Tasks (id) | Reason |
|------|------------|--------|
| 0    | 01, 02     | no incoming deps |
| 1    | 03, 04     | depend on 01 / 02 |

Smells to flag (not auto-fail, but surface to user before audit):

- Cycle detected → halt; the dependency-scan / context[] is wrong
- Every task in wave 0 → context[] missing dependencies, no parallelism captured
- One mega-wave (every task in same wave) → file-overlap split forced everything serial despite no symbol deps; check if the file layout is too coarse
- Wave depth > task count / 2 → over-serialized, possibly missing siblings

If any smell flags, fix `context[]` or the slicing before proceeding to integration-check.

### Step: integration-check

After all task files are emitted, verify wiring completeness using the integration map from the dependency-scan step. For each `<provider-chain>`:

1. **Injection point covered**: the task that introduces the new injectable/param exists.
2. **Every hop with `has-access='false'` has a task**: a file that needs modification to thread data through must appear in some task's `files.modify` frontmatter list.
3. **Data source connected**: the file that originates the data (config loader, factory, entry point) is modified by a task that threads it to the next hop.
4. **Wiring task tests the integration seam**: the RED test for a wiring task verifies data flows end-to-end — not just that the function accepts the param, but that the param reaches its destination with real data.
5. **No orphaned optionals**: if a task introduces an optional param that is REQUIRED for the feature to function, verify that every production caller has a task that passes the real implementation — not relying on the default/fallback path.

If gaps exist, add wiring tasks before proceeding to self-review. Each missing hop in a provider chain is a potential silent failure in production.

### Step: self-review

After integration-check passes, re-read `ideation.md` and verify:

- Every behavior implied by `## Intent` and `## Approach` is exercised by at least one task's RED test
- Every signature in `## Signatures` (when present) is created or modified by some task
- Every error case in `## Error design` (when present) has a RED test
- No task violates `## Constraints` or crosses `## Boundaries`
- Tasks are ordered such that each task's prerequisites are satisfied by earlier tasks
- No placeholder tokens (`TODO`, `TBD`, `{{...}}`) remain in any emitted task file
- Every REFACTOR `### Action` names concrete operations with file:symbol targets (no "improve structure" or "clean up")
- No task modifies files across more than 2 services (split if so)
- Every `<provider-chain>` from the integration map has full task coverage (integration-check passed)
- **Pattern consistency**: for tasks with `### Pattern hint`, verify the GREEN `### Example` actually follows the hinted pattern — not just a label on vanilla code. If the example doesn't match the pattern shape, rewrite the example or remove the hint.
- **Context completeness**: every symbol referenced in a task's phase blocks (types, functions, interfaces, constants) must appear in that task's `context:` frontmatter array with a valid path and signature. Spot-check 3-5 symbol paths by reading the cited files.
- **Markdown well-formedness**: every task file parses as valid YAML frontmatter + markdown body. Every `### Example` containing code is wrapped in a fenced code block with a language tag. No bare HTML/XML tags appear inside the body.

If gaps exist, that's ok. Edit the affected task files (or add new ones) and re-check. Report the resulting task list to the user with a one-line summary per task. It's much better to catch gaps here than let the pipeline fail down the line.

### Step: independent-audit

After self-review passes, spawn a separate agent to audit the emitted artifacts. This agent has no shared context with the ideation discussion or the decomposition reasoning — it sees only the files. If the ideation converged on a wrong abstraction, the self-review (which shares this conversation's context) cannot catch it. This agent can.

```text
Agent(
  subagent_type: "IndependentAuditor",
  description: "Independent task audit",
  prompt: "
    slug: {ticket-slug}
  "
)
```

If the audit returns `<pass>false</pass>`, fix the issues it identified in the task files and re-run the audit. If the audit flags an abstraction smell, surface it to the user for a decision before proceeding — do not silently override the ideation's chosen approach.

### Step: commit

Wait for user's approval before committing anything. Probe the user to tell you, if everything is good you can commit.

Check if the ideation.md + tickets have been commited, if that's not the case: commit the tickets created + ideation.md under `docs({slug}): {description}`.

**Done when**: All tasks emitted, self-review passed, summary surfaced to the user & tickets committed.

## General rules

- One task = one observable behavior. Tests must verify behavior, not implementation details.
- RED is meaningful only if the test fails for the right reason (assertion mismatch, not missing module).
- REFACTOR keeps behavior unchanged. New behavior = new RED → GREEN cycle in a new task.
- Commit only when the test passes. Pre-commit hook failures = fix the issue, never skip hooks.
- Task framing is language-agnostic; only the test command and commit message format adapt to the consuming repo.

## Next step

The planning phase is now over. Every tickets have been created under `.tap/tickets/{slug}/*`.

Surface to the user that he can now can launch the command `tap run {slug}` in a separate terminal to let the agents pick up the work.
