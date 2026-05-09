# Pattern Catalog — Proven Refactoring Techniques

Techniques proven across refactors with measured line savings. Reference during the research phase.

## Smell → Technique Mapping

| Smell                                                    | Technique                                                                                          | Typical savings            |
| ----------------------------------------------------------| ----------------------------------------------------------------------------------------------------| ----------------------------|
| Functions taking 5+ params, repeated across module       | **Closure capture** — factory closes over shared state, inner functions take 1-2 params            | 40-60% of param ceremony   |
| N similar functions with shared structure                | **Command/data-driven** — loop over descriptors instead of N separate functions                    | 70-80% of step code        |
| Identical error-handling blocks repeated                 | **Deduplicate catch/guard** — extract shared error-mapping helper                                  | 50-70% of error code       |
| Wrapper function used once, body trivial                 | **Inline trivial wrapper** — delete function, paste body at call site                              | 100% of wrapper            |
| Abstraction where most implementations are no-ops        | **Kill dead abstraction** — remove framework, use direct calls                                     | 80-100% of framework       |
| Functions with identical signatures but different bodies | **Form Template Method** — extract shared skeleton, pass varying part as function                  | 50-60% per function group  |
| Section dividers / doc comments on internal helpers      | **File decomposition** — splitting provides organization, comments become redundant                | 100% of divider comments   |
| Type definitions with repeated structure                 | **Generic type + instantiation** — one generic replaces N near-identical types                     | 60-80% of type defs        |
| Long conditional chains selecting similar behavior       | **Strategy via function map** — `Record<string, handler>` or `Map` lookup replaces switch/if chain | 40-60% of conditional code |
| Sequential orchestration with per-step ceremony          | **Pipeline/loop** — describe steps as data, execute in generic loop                                | 60-80% of orchestration    |

## Cross-Language Patterns

These apply regardless of language or framework:

| Pattern                                  | What it replaces                              | When to use                                                                                                                       |
| ------------------------------------------| -----------------------------------------------| -----------------------------------------------------------------------------------------------------------------------------------|
| Factory with closures                    | Repeated param threading across functions     | When 3+ functions share the same 3+ parameters                                                                                    |
| Descriptor array + executor              | N nearly-identical step functions             | When steps follow the same structure with different data                                                                          |
| Shared error mapper                      | Copy-pasted try/catch or error-mapping blocks | When the same error transformation appears 3+ times                                                                               |
| Re-export shim                           | Monolithic file with many exports             | When splitting — preserves original import path temporarily so consumers don't break. Consumers should migrate to direct imports. |
| `writeIfAbsent` / `copyIfAbsent` pattern | Check-then-act with error mapping repeated    | When "check exists → create if missing" appears 3+ times                                                                          |

## Line Counting Rules

Functional lines = total lines minus:
- Blank lines (`^\s*$`)
- Comment-only lines (language-specific: `//`, `#`, `/* */`, `"""`, etc.)
- Lines that are purely formatter output (auto-added by prettier/black/gofmt that wouldn't exist in compact style are still structural — count them)

Quick count for common languages:
- JS/TS/Java/C: `grep -cv '^\s*$\|^\s*//' <file>`
- Python/Ruby/Shell: `grep -cv '^\s*$\|^\s*#' <file>`
- Rust/Go: `grep -cv '^\s*$\|^\s*//' <file>`

These slightly overcount (miss multi-line comment blocks) but are consistent and fast.
