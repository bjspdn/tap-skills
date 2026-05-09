---
name: convey
description: Decomposes an existing `.tap/tickets/<slug>/ideation.md` into TDD task files in the same slug folder. Each task is a thin vertical slice (RED → GREEN → REFACTOR → COMMIT). Use when an ideation.md exists and the user wants it broken into actionable engineering tasks — invoked via `/tap-convey`, "convey this", "decompose this into tasks", "break it into TDD steps".
---

<phase name="writing">
  <purpose>
    Decompose `.tap/tickets/<slug>/ideation.md` into a series of `task-NN-<task-slug>.md` files in the same slug folder. Each file is a vertical TDD slice an engineer can execute end-to-end.
    Assume the engineer has questionable taste and limited codebase familiarity — be explicit. Assume someone with deep codebase knowledge reviews the tasks before they run, so over-specifying is safer than under-specifying.
  </purpose>

  <steps>
    <step name="ingestion">
      Resolve the target slug: if the user passed an argument (`/tap-convey <slug>`), use it. Otherwise scan `.tap/tickets/` for folders containing an `ideation.md` without any `task-*.md` siblings and use that slug.
      Disregard any prior conversation context about this feature — base all decisions on what `ideation.md` actually says, not on discussion that preceded it.
      Read `.tap/tickets/<slug>/ideation.md` end-to-end. Pay particular attention to `## Approach` (the pattern + flow), `## Signatures` (interface shapes when present), `## Constraints`, and `## Boundaries`.
      If the ideation references file:line locations you do not recognize, run targeted Grep / Read calls to ground yourself before slicing — do not invent file paths.
      Do not write anything yet.
    </step>
    <step name="dependency-scan">
      Before slicing, build a dependency map and an integration map of the files the ideation touches. Extract seed files from `ideation.md` — every `file:line` reference in `## Context`, `## Approach`, and `## Signatures`. Also extract new signatures, parameters, and injectable dependencies described in the ideation — these are the **projected changes** the scan must trace.
      Spawn a dependency scan agent:
      Agent(
        subagent_type: "general-purpose",
        model: "sonnet",
        description: "Build dependency + integration map",
        prompt: "
          You are scanning a codebase to build two maps for task ordering:
          1. A **consumer map** — who imports what (for leaves-first ordering)
          2. A **provider map** — for each new injectable the ideation introduces, trace the chain of callers upstream until you reach the data source or entry point (for wiring completeness)
          ## Seed files
          These files were identified in ideation.md as needing changes:
          {seed_files}
          ## Projected changes
          These are new signatures, parameters, or injectable dependencies
          described in the ideation that do not yet exist in the codebase:
          {projected_changes}
          ## Instructions — Consumer hops (import graph)
          1. **Read each seed file** — identify its exports/public API
             (functions, classes, types, constants it exposes)
          2. **Find consumers** — for each seed file, grep across the
             project source for files that import/use/include/require
             from it. Search patterns are language-dependent — look for:
             - import/from statements (JS/TS/Python)
             - use/mod statements (Rust)
             - import/package statements (Java/Go)
             - #include directives (C/C++)
             - require calls (Ruby/Lua/Node)
             Adapt to whatever language the codebase uses.
          3. **One hop out** — for each discovered consumer, check if
             IT is imported by other files. Do not recurse further —
             one hop is enough to surface transitive risk.
          4. **Classify** each file in the expanded set:
             - leaf: 0 dependents (nothing imports it)
             - shared: 1-5 dependents
             - high-fanout: 6+ dependents
          5. **Detect circular deps** — if file A imports B and B
             imports A (directly or through one hop), flag it.
          ## Instructions — Provider hops (integration graph)
          For each projected change (new param, new injectable, new
          service dependency), trace upstream through callers:
          6. **Hop 0 — Injection point**: which seed file introduces
             the new param/injectable? Read its function signature.
          7. **Hop 1 — Direct callers**: who calls that function today?
             Read each caller. Does it currently have access to the data
             the new param needs? Check: is the data imported, computed
             locally, passed in from above, or absent?
          8. **Hop 2+ — Follow absent data upstream**: if the caller
             does NOT have access, find ITS callers and repeat. Follow
             the chain until you find where the data originates (a
             config loader, an entry point, a factory, a DI container)
             or reach the application boundary.
          9. **Record the full provider chain** for each projected
             change — every file that must be modified to thread the
             data from source to injection point.
          ## Return format
          <dependency-map>
            <file path='src/services/AgentRunner/AgentRunner.ts'
                  classification='high-fanout'
                  seed='true'>
              <imports>src/types/Config.ts</imports>
              <imports>src/services/Logger/Logger.ts</imports>
              <imported-by>src/services/ParallelRunner/ParallelRunner.ts</imported-by>
              <imported-by>src/services/TicketRunner/TicketRunner.ts</imported-by>
            </file>
            <!-- one entry per file in the expanded set -->
          </dependency-map>
          <integration-map>
            <!-- one chain per projected change -->
            <provider-chain injectable='runQualityGates'
                           injection-point='src/services/TicketRunner/runTDDLoop/runTDDLoop.ts'>
              <hop n='0' file='runTDDLoop.ts'
                   role='accepts new optional param' />
              <hop n='1' file='TicketRunner.ts'
                   role='calls runTDDLoop — does NOT currently pass param'
                   has-access='false' />
              <hop n='2' file='TicketRunner.ts'
                   role='has loadTapConfig in scope but result is not threaded to ctx'
                   has-access='partial' />
              <data-source file='loadTapConfig.ts'
                           role='loads config.json — origin of qualityGates array' />
            </provider-chain>
          </integration-map>
          <warnings>
            <circular between='A.ts' and='B.ts' />
            <unreadable file='X.ts' reason='dynamic import expression' />
            <!-- provider chain warnings -->
            <dangling-injectable name='X'
              reason='no data source found within 4 hops — may need new config/factory' />
          </warnings>
          <signals>
            <high-consumer-count file='Y.ts' count='15'
              note='consider extracting a facade before refactoring' />
            <deep-provider-chain injectable='X' hops='4'
              note='data must thread through 4 intermediaries — consider a service/context pattern' />
          </signals>
          ## Rules
          - Do NOT read entire files — scan exports, import lines, and
            function signatures only
          - Do NOT follow dependencies into node_modules, vendor/,
            or third-party code
          - Do NOT recurse past one hop from consumers (consumer map)
          - DO follow provider chains as deep as needed until you find
            the data source or hit the application boundary (provider map)
          - If import pattern is unreadable (dynamic, generated),
            log it in <warnings> and move on
          - Hard cap: return the maps, nothing else. No recommendations,
            no task ordering — that is the main agent's job.
        "
      )
      Wait for the agent to return. Use both maps in the slicing step below — the consumer map for ordering, the integration map for wiring tasks.
    </step>
    <step name="pattern-scan">
      After the dependency-scan returns, spawn a pattern-recognition agent to identify structural patterns near the seed files. This agent reads the pattern catalog and neighboring modules to determine which patterns should shape each task's GREEN step.
      Agent(
        subagent_type: "general-purpose",
        model: "sonnet",
        description: "Build pattern map from neighbors",
        prompt: "
          You are scanning a codebase to build a pattern map that tells the task emitter how to shape GREEN implementations. The goal: new code should compose with its neighbors, not against them. When a pattern already exists nearby, GREEN should follow that shape instead of producing naive code that REFACTOR must collapse later.
          ## Inputs
          Seed files from ideation.md:
          {seed_files}
          Pattern catalog root:
          ${CLAUDE_PLUGIN_ROOT}/patterns/
          ## Instructions
          1. **Read `${CLAUDE_PLUGIN_ROOT}/patterns/README.md`** to learn the discovery API. Then query patterns by smell tag using the index (`${CLAUDE_PLUGIN_ROOT}/patterns/_index.json#smell_to_patterns[<tag>]`) or read all `behavioral/` and `refactoring/` cards if doing a broad scan. Internalize the smell → technique mapping — these are the patterns you are looking for.
          2. **For each seed file**, read the neighboring modules:
             - Same directory: sibling files
             - Direct imports: files the seed imports from
             - Direct consumers: files that import from the seed (from the dependency map if available)
          3. **Match patterns** — for each neighbor, check if its structure matches any technique from the catalog:
             - Descriptor array + executor: `ReadonlyArray<[tag, handler]>` iterated in a loop
             - Strategy via function record: `Record<string, Function>` or equivalent passed as config
             - Closure capture factory: outer function closes over shared state, returns inner functions taking fewer params
             - Scoped resource lifecycle: acquire + release registered together (Effect.acquireRelease, try-with-resources, context managers, RAII)
             - Shared error mapper: same error-transformation block appearing 3+ times
             - Generic type + instantiation: one generic replacing N near-identical types
             - Pipeline/loop: steps described as data, executed in generic loop
          4. **Predict smells** — for each seed file, based on the ideation's described behavior, predict which smell the naive GREEN might produce:
             - Will it create 3+ similar functions? → descriptor-array candidate
             - Will it thread 5+ params through multiple functions? → closure-capture candidate
             - Will it repeat error handling? → shared-error-mapper candidate
             - Will it create a resource without scoped cleanup? → scoped-lifecycle candidate
          5. **Recommend shape** — for each seed file where a pattern match exists in neighbors OR a smell is predicted, recommend the pattern to use in GREEN.
          ## Return format
          <pattern-map>
            <file path='src/services/Example/Example.ts'>
              <neighbor-pattern name='descriptor-array-executor'
                evidence='src/services/Pipeline/tddLoop.ts:101 — phaseDescriptors array'
                confidence='strong' />
              <predicted-smell name='similar-step-functions'
                reason='ideation describes 4 processing phases with identical signatures' />
              <green-shape>
                Use a descriptor array for the processing phases instead of 4 separate functions.
                Reference: tddLoop.ts:101 phaseDescriptors pattern.
              </green-shape>
            </file>
            <file path='src/services/Other/Other.ts'>
              <!-- no pattern match, no predicted smell -->
              <green-shape>No pattern recommendation — use vanilla minimum implementation.</green-shape>
            </file>
          </pattern-map>
          ## Rules
          - Only recommend patterns with 'strong' confidence (pattern exists in a neighbor) or clear smell prediction
          - Never force a pattern where none fits — 'No pattern recommendation' is a valid output
          - Every pattern claim must cite file:line evidence
          - Do NOT recommend patterns from the catalog that have no neighbor evidence AND no predicted smell — catalog is vocabulary, not a checklist
          - Hard cap: return the pattern-map, nothing else. No task ordering, no implementation advice.
        "
      )
      Wait for the agent to return. Use the pattern-map alongside the dependency-map and integration-map in the slicing and emission steps below.
    </step>
    <step name="slicing">
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
      - Dangling injectables: if a provider chain has no data source, surface to the user before emitting — a new config entry, factory, or service may be needed.
      - Deep provider chains (4+ hops): flag as architectural signal — the data is threading through too many intermediaries, consider a context/service pattern.
    </step>
    <step name="emission">
      For each task, write a file at `.tap/tickets/<slug>/task-{NN}-<task-slug>.md` where `{NN}` is zero-padded (`01`, `02`, ...). Each file must conform to the [task contract](task-contract.md).
      **File format**: every task file is markdown with YAML frontmatter. Frontmatter holds machine fields (`id`, `files`, `context`); the body holds prose phases as `## RED` / `## GREEN` / `## REFACTOR` / `## COMMIT`, each split into `### Action` / `### Example` / `### Verify` / `### Done`. Code lives in fenced code blocks (```` ```ts ````, ```` ```sh ````). Do **not** use HTML/XML-style tags inside the body — they trigger HTML-block parsing in markdown renderers and desync on blank lines, breaking display.
      **Context frontmatter rule**: every task file must include a `context:` array in frontmatter. For each symbol the task references — types, functions, interfaces, constants — read its definition site and include `name`, `path`, `line`, and `signature` (use YAML `|` block scalar for multi-line signatures). For symbols introduced by the ideation that do not yet exist, set `new: true` and omit `path` / `line`. The dependency-scan agent already collected import/export data and provider chains; propagate this data into the task files so the executing agent never has to explore the codebase to find where symbols live or what they look like.
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
    </step>
    <step name="integration-check">
      After all task files are emitted, verify wiring completeness using the integration map from the dependency-scan step. For each `<provider-chain>`:
      1. **Injection point covered**: the task that introduces the new injectable/param exists.
      2. **Every hop with `has-access='false'` has a task**: a file that needs modification to thread data through must appear in some task's `<files><modify>` block.
      3. **Data source connected**: the file that originates the data (config loader, factory, entry point) is modified by a task that threads it to the next hop.
      4. **Wiring task tests the integration seam**: the RED test for a wiring task verifies data flows end-to-end — not just that the function accepts the param, but that the param reaches its destination with real data.
      5. **No orphaned optionals**: if a task introduces an optional param that is REQUIRED for the feature to function, verify that every production caller has a task that passes the real implementation — not relying on the default/fallback path.
      If gaps exist, add wiring tasks before proceeding to self-review. Each missing hop in a provider chain is a potential silent failure in production.
    </step>
    <step name="self-review">
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
    </step>
    <step name="independent-audit">
      After self-review passes, spawn a separate agent to audit the emitted artifacts. This agent has no shared context with the ideation discussion or the decomposition reasoning — it sees only the files. If the ideation converged on a wrong abstraction, the self-review (which shares this conversation's context) cannot catch it. This agent can.
      Agent(
        subagent_type: "general-purpose",
        model: "sonnet",
        description: "Independent task audit",
        prompt: "
          You are auditing a set of TDD task files against their source ideation document. You have no prior context about this feature — you are seeing these artifacts for the first time.
          ## Inputs
          Read these files:
          1. `.tap/tickets/{slug}/ideation.md` — the design spec
          2. All `.tap/tickets/{slug}/task-*.md` files — the decomposed tasks
          ## Audit checklist
          1. **Coverage**: every behavior in ideation `## Intent` and `## Approach` is exercised by at least one task's RED test. List any uncovered behaviors.
          2. **Coherence**: do the tasks, read sequentially in numeric `id` order, tell a coherent story? Are there logical gaps where task N+1 assumes something task N doesn't produce? (Tasks run sequentially in numeric order — there is no parallelism.)
          3. **Context frontmatter**: does every task have a `context:` array in its YAML frontmatter? Do the symbols listed actually exist at the paths cited? Spot-check 3-5 symbols by reading the cited files.
          4. **Ordering**: is the numeric `id` ordering leaves-first? Could any later task be moved earlier without breaking its prerequisites?
          5. **Contradictions**: do any tasks contradict ideation `## Constraints` or `## Boundaries`?
          6. **Abstraction smell**: does the ideation's chosen pattern (## Approach → PATTERN) actually fit the problem, or is there a simpler approach the ideation overlooked? Be specific — name what's overcomplicated and what simpler shape would work.
          ## Return format
          <audit>
            <pass>true|false</pass>
            <coverage-gaps>
              - <behavior from ideation not covered by any task>
            </coverage-gaps>
            <coherence-issues>
              - <gap between task N and task N+1>
            </coherence-issues>
            <context-spot-checks>
              - <symbol> at <path:line> — found|missing|signature-mismatch
            </context-spot-checks>
            <ordering-issues>
              - <task that could move earlier in the numeric order>
            </ordering-issues>
            <contradictions>
              - <task vs constraint>
            </contradictions>
            <abstraction-smell>
              - <concern about the chosen pattern, if any>
            </abstraction-smell>
          </audit>
          Hard cap: return the audit, nothing else. No fixes — just diagnosis.
        "
      )
      If the audit returns `<pass>false</pass>`, fix the issues it identified in the task files and re-run the audit. If the audit flags an abstraction smell, surface it to the user for a decision before proceeding — do not silently override the ideation's chosen approach.
    </step>
    <step name="commit"> 
      Wait for user's approval before committing anything. Probe the user to tell you, if everything is good you can commit.
      Check if the ideation.md + tickets have been commited, if that's not the case: commit the tickets created + ideation.md under `docs(<slug>): <description>`.
    </step>
  </steps>

  <done>
    All tasks emitted, self-review passed, summary surfaced to the user & tickets committed
  </done>
</phase>

<general-rules>
  - One task = one observable behavior. Tests must verify behavior, not implementation details.
  - RED is meaningful only if the test fails for the right reason (assertion mismatch, not missing module).
  - REFACTOR keeps behavior unchanged. New behavior = new RED → GREEN cycle in a new task.
  - Commit only when the test passes. Pre-commit hook failures = fix the issue, never skip hooks.
  - Task framing is language-agnostic; only the test command and commit message format adapt to the consuming repo.
</general-rules>

<next-step>
The planning phase is now over. Every tickets have been created under .tap/tickets/<slug>/*.
Surface to the user that he can now can launch the command `tap run <slug>` in a separate terminal to let the agents pick up the work.
</next-step>