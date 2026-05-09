---
name: sketch
description: Rapid TDD prototype for small, single-behavior changes — lighter than the full into/convey/run pipeline. Generates an in-memory task spec, then executes RED/GREEN/REFACTOR immediately on the current branch using the same phase agents. No worktree, no tickets on disk, no decomposition. Use when user invokes `/tap-sketch`, says "sketch this", "quick prototype", "small TDD change", "just do it TDD-style", "sketch a fix for X", or describes a change that is clearly a single behavior touching 1-3 files.
---

# tap-sketch

Rapid prototype mode. The user describes a small feature or fix; you validate scope, build an in-memory task spec, and drive RED/GREEN/REFACTOR on the current branch. No `.tap/tickets/`, no worktree, no decomposition, no waves, no Reviewer. The value proposition is speed with TDD discipline intact.

## Phase: scope-check

### Purpose

Confirm the change is small enough for sketch. Sketch handles ONE behavior touching at most 3 files. Anything larger belongs in the full pipeline.

### Step: validate

1. **Parse the user's description.** Identify the behavior being requested. Count the independent behaviors implied. If the description maps to multiple independent behaviors (e.g., "add validation AND change the serialization format"), stop immediately:

   > "This implies multiple independent behaviors. Use `/tap:into` to scope and decompose it properly."

   Do not proceed. One behavior per sketch, no exceptions.

2. **Read the target area.** Identify 2-3 files near the change site. Read them to understand:
   - The language, test framework, and idiom in use
   - The module's public seam (what the test will exercise)
   - Whether the change is additive (new function/method) or modificative (changing existing behavior)

3. **Count files.** If the change requires creating or modifying more than 3 files (excluding the test file), stop:

   > "This touches too many files for sketch. Use `/tap:into` to plan it properly."

4. **Detect the test command.** Read the project manifest to resolve `$TEST_COMMAND`:
   - `package.json` → `scripts.test` (e.g., `bun test`, `jest`, `vitest run`)
   - `Cargo.toml` → `cargo test`
   - `pyproject.toml` / `setup.py` → `pytest`
   - `go.mod` → `go test ./...`
   - `pom.xml` / `build.gradle` → `mvn test` / `gradle test`
   - `Gemfile` → `bundle exec rspec` or `bundle exec rake test`

   If no manifest matches, ask: "What command runs the test suite scoped to a single file?"

5. **Resolve quality gates.** Check in order:
   - `.tap/config.json` → `qualityGates` array
   - `CLAUDE.md` → `## Quality gates` section
   - If neither exists, ask the user: "What quality gate commands should pass before each commit? (e.g., typecheck, lint, build, test)"

   Capture as `$QUALITY_GATES` (JSON array of shell commands).

### Done

Scope is validated: one behavior, at most 3 files, test command resolved, quality gates resolved.

## Phase: spec

### Purpose

Build the in-memory task spec — the same information a `task-NN-*.md` file would contain, but held in context instead of written to disk. Surface it to the user for approval before execution.

### Step: identify

Identify the ONE behavior:
- What is being added, changed, or fixed?
- What file(s) will be created or modified?
- Where does the test file live (co-located? `__tests__/`? `test/`?)
- What is the public seam the test will exercise?

### Step: profile-check

If `.tap/retros/_profile.json` exists, read established `agent_performance`, `pattern_signals`, and `gate_signals` entries. Apply per the [profile contract](${CLAUDE_PLUGIN_ROOT}/skills/retro/profile-contract.md). Carry forward relevant signals for the dispatch prompts in Phase: execute.

### Step: pattern-check

Quick pattern catalog consultation — not a full PatternScanner spawn. The catalog discovery API is documented at `${CLAUDE_PLUGIN_ROOT}/patterns/README.md`; three modes exist (by-name, by-smell, by-scan). Sketch uses by-smell only.

1. Read `${CLAUDE_PLUGIN_ROOT}/patterns/_index.json`.
2. Identify the files being modified. Read 1-2 neighbors of those files. Look for structural shapes — repeated conditionals, data clumps, long parameter lists, wrapper layers, etc.
3. **Smell routing**: for each smell observed in the target area, look up `smell_to_patterns["<smell-tag>"]` in the index to get candidate pattern names. Resolve synonyms via `aliases` in the index before assuming a pattern is absent — e.g., the user may say "wrapper" but the catalog entry is `adapter`.
4. **Read the card**: for each candidate, read `${CLAUDE_PLUGIN_ROOT}/patterns/<category>/<name>.md` (the `path` field in `patterns[<name>]` gives the exact location). Extract:
   - `intent` — does the pattern match the behavior being sketched?
   - `composes_with` — does it compose with patterns the neighbors already use?
   - `clashes_with` — does it conflict with anything in the target area?
   - `test_invariants` — useful for shaping the RED test.
   - `OOP shape` / `FP shape` — useful for shaping GREEN.
5. If a pattern fits naturally, carry it forward as a hint for GREEN and RED:
   - GREEN shape follows the card's OOP/FP shape for the target paradigm.
   - RED shape incorporates relevant `test_invariants` from the card.
   - REFACTOR checks `composes_with` for structural alignment with neighbors.
   If nothing fits, move on — do not force a pattern where none applies.

### Step: shape

Build the spec with these sections:

- **Behavior**: one-sentence description of the observable behavior being added/changed.
- **Files**: list of files to create and/or modify (including the test file).
- **RED shape**: what the test asserts, what public seam it exercises, what failure message proves it fails for the right reason.
- **GREEN shape**: minimum implementation that makes the test pass. If a pattern hint was identified, note it here.
- **REFACTOR shape**: specific operations (extract/rename/inline/deduplicate) with concrete targets. If GREEN will already be clean, state: "No refactoring needed — structure is adequate."
- **Verify command**: `$TEST_COMMAND` scoped to the test file path.

### Step: approval

Surface the spec to the user in a readable format. Wait for explicit approval before proceeding to Phase: execute.

If the user requests changes to the spec, revise and re-surface. If the user's revisions expand scope beyond one behavior or 3 files, redirect to `/tap:into`.

### Done

User has approved the in-memory spec. Proceed to execution.

## Phase: execute

### Purpose

Drive RED/GREEN/REFACTOR sequentially using the same phase agents as `/tap:run`. Each phase dispatches one agent, waits for its result, and handles failure before proceeding.

### Step: prepare

Capture `$PARENT_SHA` — the current HEAD before sketch begins:

```
git rev-parse --short HEAD
```

This is the rollback point if any phase fails irrecoverably.

Capture `$REPO_ROOT` — the repository root:

```
git rev-parse --show-toplevel
```

Generate `$TICKET_SLUG` as `sketch-<YYYYMMDD-HHmmss>` using the current timestamp.

### Step: red

Dispatch TestWriter with the in-memory spec passed inline (since there is no task file on disk):

```
Agent(
  subagent_type: "TestWriter",
  description: "Write failing test for sketch",
  prompt: "
    task_file_path: INLINE — no file on disk. Task spec follows below.
    worktree_path: $REPO_ROOT
    quality_gates: $QUALITY_GATES
    ticket_slug: $TICKET_SLUG
    parent_sha: $PARENT_SHA
    commit_lock: not applicable — single task, no parallelism

    --- INLINE TASK SPEC ---
    id: sketch
    files:
      create: [<files to create from spec>]
      modify: [<files to modify from spec>]

    ## RED
    ### Action
    <RED shape from the approved spec>
    ### Verify
    $TEST_COMMAND <test-file-path>
    ### Done
    Test fails for the right reason: <expected failure from spec>.

    ## GREEN
    ### Action
    <GREEN shape from the approved spec>
    ### Verify
    $TEST_COMMAND <test-file-path>
    ### Done
    Test passes. All quality gates green.

    ## REFACTOR
    ### Action
    <REFACTOR shape from the approved spec>
    ### Verify
    $TEST_COMMAND <test-file-path>
    ### Done
    Tests still pass. All quality gates green. Structure improved (or no-op).
  "
)
```

**On success**: proceed to Step: green.

**On failure**: attempt one self-fix — dispatch Debugger Shape A:

```
Agent(
  subagent_type: "Debugger",
  description: "Fix RED failure for sketch",
  prompt: "
    TDD phase \"RED\" failed for task \"sketch\".

    <full inline task spec from above>

    Failure output:
    <stderr/stdout from the failed TestWriter run>

    worktree_path: $REPO_ROOT
    quality_gates: $QUALITY_GATES
    parent_sha: $PARENT_SHA
    commit_lock: not applicable
  "
)
```

If Debugger succeeds, re-dispatch TestWriter. If Debugger gives up or a second TestWriter attempt fails, revert all changes since `$PARENT_SHA`:

```
git reset --hard $PARENT_SHA
```

Surface the failure to the user:

> "RED phase failed after one retry. Changes reverted. Here's what went wrong: <reason>"

Stop. Do not proceed to GREEN.

### Step: green

Dispatch CodeWriter with the same inline spec:

```
Agent(
  subagent_type: "CodeWriter",
  description: "Write implementation for sketch",
  prompt: "
    task_file_path: INLINE — no file on disk. Task spec follows below.
    worktree_path: $REPO_ROOT
    quality_gates: $QUALITY_GATES
    ticket_slug: $TICKET_SLUG
    parent_sha: $PARENT_SHA
    commit_lock: not applicable — single task, no parallelism

    --- INLINE TASK SPEC ---
    <same full inline spec as RED>
  "
)
```

**On success**: proceed to Step: refactor.

**On failure**: same pattern — Debugger Shape A once, re-dispatch CodeWriter on success. On second failure, revert GREEN changes only (reset to the RED commit, not to `$PARENT_SHA` — keep the test):

```
git reset --hard <RED-commit-sha>
```

Surface the failure:

> "GREEN phase failed after one retry. RED test is preserved. Here's what went wrong: <reason>"

Stop.

### Step: refactor

If the spec's REFACTOR shape is "No refactoring needed — structure is adequate", skip this step entirely. Surface:

> "REFACTOR skipped — GREEN produced clean structure."

Otherwise, dispatch Refactorer:

```
Agent(
  subagent_type: "Refactorer",
  description: "Refactor sketch implementation",
  prompt: "
    task_file_path: INLINE — no file on disk. Task spec follows below.
    worktree_path: $REPO_ROOT
    quality_gates: $QUALITY_GATES
    ticket_slug: $TICKET_SLUG
    parent_sha: $PARENT_SHA
    commit_lock: not applicable — single task, no parallelism

    --- INLINE TASK SPEC ---
    <same full inline spec as RED>
  "
)
```

**On failure**: keep GREEN. Do not revert. Surface a warning:

> "REFACTOR failed but GREEN is preserved. The implementation works; structural improvement was not applied. Reason: <reason>"

### Done

All dispatched phases completed (or REFACTOR skipped/failed gracefully).

## Phase: verify

### Purpose

Final quality gate sweep and user-facing summary.

### Step: gates

Run every command in `$QUALITY_GATES` sequentially from `$REPO_ROOT`. All must exit clean. If any gate fails at this point, surface the failure — do not silently proceed. The user decides whether to fix manually or revert.

### Step: summary

Surface a summary to the user:

```
Sketch complete: $TICKET_SLUG

Behavior: <one-line from spec>
Files changed:
  - <path> (created/modified)
  - <path> (created/modified)

Commits:
  - <RED commit sha + subject>
  - <GREEN commit sha + subject>
  - <REFACTOR commit sha + subject> (or "skipped")

All quality gates passed.
```

### Done

Sketch is complete. Commits are on the current branch at HEAD.

## General rules

These rules apply across all phases and steps:

- **One behavior per sketch.** If the description implies multiple independent behaviors, redirect to `/tap:into`. No exceptions. Sketch is not a shortcut to skip planning — it is a shortcut for changes that do not need planning.
- **RED must fail for the right reason.** An assertion mismatch or module-missing error pointing at the file GREEN will create. A test that passes without implementation is too weak — the sketch halts.
- **REFACTOR never changes behavior.** The RED test stays green after REFACTOR. New behavior requires a new sketch or a full pipeline run.
- **Never `--no-verify`, never `--amend`.** Hook failures are real failures. Fix the underlying issue, create a new commit.
- **No worktree.** Sketch works on the current branch. Commits land on HEAD.
- **No task files on disk.** The spec lives in context. Nothing is written to `.tap/tickets/`.
- **Commit subjects follow conventional format.** `test(sketch): ...` for RED, `feat(sketch): ...` for GREEN, `refactor(sketch): ...` for REFACTOR. Trailers: `Tap-Task: sketch`, `Tap-Phase: RED|GREEN|REFACTOR`, `Tap-Files: <paths>`.
- **Failure handling is bounded.** One retry per phase via Debugger Shape A. Second failure reverts the phase and halts. No infinite loops.
- **Sketch is for speed, not for cutting corners on TDD.** The RED/GREEN/REFACTOR cycle is non-negotiable. The test comes first. The implementation comes second. The refactor comes third (or is explicitly skipped). This is the discipline that makes sketch trustworthy despite being fast.
