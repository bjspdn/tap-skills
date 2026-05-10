---
name: refactor
description: Aggressive structural refactoring targeting 80% reduction in countable lines — logic, orchestration, type ceremony, data constants — without changing behavior. Formatting, comments, whitespace, and naming are excluded from the metric and must never be degraded. Splits monolithic files into focused submodules. The original file becomes a lean entry point. Trigger ONLY on explicit `/tap-refactor` invocation. Not for small cleanups or formatting.
---

## Principle

**Target: eliminate 80% of countable lines without changing behavior.**

"Countable lines" = logic, orchestration, type ceremony, data constants. NOT formatting, comments, whitespace, blank lines, or names. The metric measures structural elimination — duplication collapsed, dead abstractions removed, unnecessary ceremony replaced with tighter patterns.

Three hard rules:

1. **The original file becomes a lean entry point.** It keeps only what defines the module's identity — interface definitions, public API surface, and wiring (e.g., layer construction, factory export, class declaration). All implementation logic moves into focused submodules. The entry point imports and re-exports, but does not implement.

2. **Logic and behavior are genuinely refactored, not relocated or reformatted.** Moving 1000 lines into 5 files of 200 lines each is not refactoring — it's scattering. Success means: duplicate logic collapsed, dead abstractions removed, parameter ceremony replaced with tighter patterns, redundant wrappers inlined.

3. **Names, comments, and formatting are sacred.** `createUserSession` stays `createUserSession` — never `cUS`, never `create`, never a single-letter abbreviation. Names carry intent and semantics; shortening them destroys readability for zero structural gain. Comments travel with the code they annotate. Formatting is the formatter's job. Any "reduction" a formatter would undo was not a reduction.

If the file cannot honestly hit 80%, say so and explain the irreducible complexity. Forcing artificial cuts is worse than reporting a lower number.

Use a collaborative tone. When proposing cuts, explain what pattern enables the reduction and why the removed code was unnecessary.

## What counts as a real reduction

- **Duplicate logic collapsed**: N copies of the same pattern → 1 parameterized version
- **Dead abstraction removed**: wrapper that adds no value over calling the underlying thing directly
- **Type alias extraction**: N identical type signatures → 1 alias + N references
- **Data-driven loop**: N identical call sites that differ only in a parameter → loop over array
- **Inline at call site**: helper used exactly once, trivial enough to inline
- **Responsibility moved to natural home**: logic that belongs in an existing sibling module, not a new file

## What does NOT count (hard prohibitions)

These produce zero countable-line reduction and are **never allowed**:

- **Renaming for brevity**: `createUserSession` → `cUS` is an instant fail. Names are semantic, not cosmetic. Shortening them destroys intent for zero structural gain.
- **Stripping comments**: comments are not countable lines. Removing them saves nothing and destroys context.
- **Compressing formatting**: putting multi-line expressions on one line, removing whitespace or blank lines — the formatter owns this and will revert it.
- **Any change a formatter would undo**: `prettier`/`rustfmt`/`gofmt`/equivalent is the authority on formatting, not the refactor.
- **Relocating without collapsing**: moving 200 lines from file A to file B with no structural change is scattering, not reducing.

## Phase: discover

Run when the user invokes `/tap-refactor` without specifying a target file, or asks which files are candidates.

Infer the project's primary language from file extensions and config files (package.json, Cargo.toml, go.mod, pyproject.toml, Makefile, etc.) or CLAUDE.md. Run **two** `find` commands — one for source files, one for test files:

- Source root: `src/`, `lib/`, `app/`, or whatever the project uses
- File extension: `.ts`, `.rs`, `.go`, `.py`, `.java`, `.rb`, etc.
- Exclude patterns for source scan: test files (`*.test.*`, `*.spec.*`, `*_test.*`), generated code, and language-specific non-source files (e.g. `.d.ts` for TypeScript, `_pb.go` for Go protobuf)
- Test scan: only test files (`*.test.*`, `*.spec.*`, `*_test.*`)

Example (source): `find <src-root> -name '*.<ext>' ! -name '*.test.*' ! -name '*_test.*' -exec wc -l {} + | sort -rn | head -15`
Example (tests):  `find <src-root> \( -name '*.test.*' -o -name '*.spec.*' -o -name '*_test.*' \) -exec wc -l {} + | sort -rn | head -10`

Present results as two ranked tables (source files and test files) with file path and line count. Test monoliths are just as real as source monoliths — large test files with repeated setup, copy-pasted assertions, or mixed concerns are valid refactor targets. Recommend the top 2-3 candidates across both tables. Let the user pick a target before proceeding.

If the user already specified a target file, skip this phase entirely.

## Phase: investigate

Read the target file. Spawn up to 3 Explore agents in parallel:

1. **Structure audit**: Read the target file. Map sections: types, helpers, orchestration, data constants. Identify duplication patterns — repeated error handling, similar function signatures, copy-paste parameter lists. Count how many distinct behaviors exist.

2. **Consumer scan**: grep for imports/requires of the target module across the project. Read the test file. List exported symbols and error identifiers that are behavioral contracts.

3. **Sibling patterns**: Check how other modules at the same level are structured. Look for established split patterns (re-export shim + submodules) and shared helpers that already exist.

Present findings as a table: section name, line range, smell (duplication / dead abstraction / parameter ceremony / inline candidate).

For each section, answer: **where does this logic naturally belong?** Options:
- An existing sibling module that already handles related concerns
- A new focused file named after its single responsibility
- Inline at the call site (if trivial and used once)
- Eliminated entirely (dead abstraction, no-op framework, redundant wrapper)

## Phase: research

Before planning, consult the local pattern catalog first, then fall back to refactoring.guru for any patterns not yet in the catalog.

**Step 1 — Local catalog (preferred)**

For each smell identified during the investigate phase:
1. Query the catalog by smell tag — either:
   - **Mode 2 (index lookup)**: read `${CLAUDE_PLUGIN_ROOT}/patterns/_index.json` and look up `smell_to_patterns[<tag>]` to get a list of matching pattern names + categories.
   - **Mode 3 (grep fallback)**: `grep -lr "smells_it_fixes:.*<tag>" ${CLAUDE_PLUGIN_ROOT}/patterns/`
2. Read the matching pattern card(s) from `${CLAUDE_PLUGIN_ROOT}/patterns/refactoring/`.
3. Cross-reference with `${CLAUDE_PLUGIN_ROOT}/patterns/structural/` and `${CLAUDE_PLUGIN_ROOT}/patterns/behavioral/` if a structural or behavioral pattern fits the smell.
4. Consult `references/line-counting.md` for countable-line measurement rules.

**Step 2 — Web fallback (only for patterns NOT in the local catalog)**

If a smell has no matching card in the local catalog, use WebFetch on the relevant refactoring.guru URL:

- Repeated similar functions → `https://refactoring.guru/design-patterns/template-method`
- Long parameter lists → `https://refactoring.guru/refactoring/techniques/simplifying-method-calls`
- Sequential step orchestration → `https://refactoring.guru/design-patterns/command`
- Conditional logic with shared structure → `https://refactoring.guru/design-patterns/strategy`
- General decomposition → `https://refactoring.guru/refactoring/techniques/composing-methods`
- Class/module splitting → `https://refactoring.guru/refactoring/techniques/moving-features-between-objects`

Map each smell to a specific technique. For each technique, describe what **logic** it eliminates — not how many lines it saves.

## Phase: plan

Enter plan mode. The plan must include:

- **Countable-lines audit**: count lines in the target file, broken into countable (logic, orchestration, type ceremony, data constants) and non-countable (formatting, comments, whitespace, blank lines, imports). State the baseline countable number and the 80% target. Show projected reduction per technique — the numbers must add up.
- **Behavior inventory**: list every distinct behavior in the file (e.g., "checkpoint serialization", "phase retry with debugger fallback", "reviewer blocker dispatch"). This is the unit of analysis — not lines.
- **Destination map**: for every behavior, what happens to it — migrates to new file, inlined at call site, or eliminated entirely. Format: `behavior → destination — technique`
- **Eliminations**: which behaviors are genuinely removed (dead code, redundant wrappers, duplicate logic that collapses). Be specific about WHY each is unnecessary.
- **New files**: each new file with its single responsibility. Each file should own exactly one behavior or a tightly-related cluster.
- **Entry point shape**: what stays in the original file (interface, wiring, re-exports)
- **Technique table**: each technique, which behaviors it affects, what countable lines it eliminates
- **Preservation list**: every exported symbol, every error identifier, every consumer import path — these must survive unchanged
- **Verification commands**: the project's test runner, type checker, linter, and build command (read from CLAUDE.md, package.json, Makefile, or equivalent)
- **Test coverage for new files**: for each new submodule, state whether it is covered by existing tests through the entry point, or needs its own colocated test file. Ask the user whether they want colocated tests created for extracted submodules.
- **Feasibility check**: if 80% is not achievable, state the realistic ceiling and explain the irreducible complexity. Do not inflate projections.

Wait for user approval before writing code.

## Phase: execute

Implement the refactoring directly. Do not delegate to a subagent — the investigation and planning context is critical for making good decisions.

Write files in dependency order: helpers first, then modules that import them, entry point last.

Rules:
- The original file keeps only interface/API surface and wiring. All implementation logic lives in submodules.
- Error identifiers (string tags, error codes, exception class names) preserved character-for-character.
- Function and variable names stay descriptive. Top-level exports use full names.
- **Do not compress formatting.** Write code in the same style as the rest of the project. Let the formatter own line breaks, indentation, and wrapping. A refactor that a formatter undoes was not a refactor.
- **Preserve comments.** When extracting code into a new file, carry its comments along. Comments are not part of the functional line count, so removing them produces no real reduction — it just destroys context. Section dividers, TSDoc, and inline explanations all travel with the code they annotate.
- Test files are read-only. If a test fails, the refactored code has a bug — fix the code, not the test.

After writing all files, verify in this order:

1. **Tests first** — run the target module's test file (identified during investigation). This is the behavioral proof. If tests fail, the refactor broke behavior — fix before proceeding.
2. **Full test suite** — run the project's full test suite to catch regressions in consumers.
3. **Quality gates** — type checker, linter, build. If lint fails on unused imports (common after splits), fix and re-run.

## Anti-rationalization table

Do not produce these rationalizations. If you catch yourself reasoning toward one, stop and take the correct action.

| Where | Rationalization | Real problem | Correct action |
|---|---|---|---|
| Discover | "I already know which file to refactor" | Skips line-count ranking, misses larger candidates or test monoliths | Run both find commands (source + test). Present ranked tables. Let the user pick |
| Investigate | "I can see the structure from reading the file" | Skips consumer scan and sibling pattern check, misses behavioral contracts and established split patterns | Spawn all 3 Explore agents. Consumer imports and sibling conventions are not visible from the target file alone |
| Research | "I know this pattern well enough, skip the catalog" | Misses local catalog cards with `composes_with`/`clashes_with` data. Falls back to generic knowledge | Query local catalog first (Mode 2 or Mode 3). Web fallback only for patterns not in the catalog |
| Plan | "We're at 78%, close enough to 80%" | Settling below target without explaining irreducible complexity. 78% is not 80% | Either find the remaining 2% or state specifically what cannot be reduced and why. "Close enough" is not a feasibility check |
| Plan | "These comments add to the line count" | Counts non-countable lines (comments, formatting, whitespace) as reductions to inflate the number | Only logic, orchestration, type ceremony, and data constants are countable. Comments are sacred — removing them is zero reduction |
| Plan | "Moving code to 5 new files reduces the original" | Scattering is not reducing. 1000 lines in 5 files of 200 is still 1000 lines of logic | Reduction means eliminating: collapsing duplicates, removing dead abstractions, inlining single-use helpers. Relocation alone is zero reduction |
| Execute | "This test needs to adapt to the new structure" | Modifying tests during refactor. If tests fail, the refactor broke behavior | Tests are read-only. If a test fails, the refactored code has a bug — fix the code, not the test |
| Execute | "This name is too long, shortening improves readability" | Renaming for brevity destroys intent. `createUserSession` → `cUS` is an instant fail | Names are semantic. `createUserSession` stays `createUserSession`. Shortening for line count is a hard prohibition |
| Execute | "I'll remove these comments since the code is self-explanatory now" | Comments are not countable lines. Removing them is zero reduction and destroys context | Comments travel with the code they annotate. Section dividers, docstrings, inline explanations — all preserved |
| Execute | "The formatter will fix this later" | Writing code in a different style than the project, hoping the formatter normalizes it | Write code in the same style as the rest of the project from the start. Don't rely on the formatter to paper over style drift |
| Report | "Projected reduction was 82% but actual is 71% — rounding up" | Inflating reported numbers to match projection | Report exact numbers. If actual differs from projected, explain what was irreducible. Honest reporting builds trust |

## Phase: report

Report format:
```
## Refactor: <module name>

Countable lines: <before> → <after> (<X>% reduction)
Non-countable (preserved): <comments> comments, <formatting> formatting lines
Files: 1 → <M> (entry point: <L> lines)

Logic eliminated:
- <what was removed> — <why it was unnecessary> — <N countable lines>
- ...

Logic restructured:
- <behavior> → <new location> — <technique applied> — <N countable lines>
- ...

Quality gates: tests ✓ | typecheck ✓ | lint ✓ | build ✓
```

If the 80% target was not met, explain what the irreducible complexity is — the code was already well-factored, or the behaviors are genuinely distinct and necessary. Never inflate numbers by counting formatting or comment removal.
