# Task Contract

Reference for task files emitted by `tap-convey` to `.tap/tickets/<slug>/task-NN-<task-slug>.md`.

Each task file is a single vertical TDD slice — one observable behavior delivered end-to-end through whatever layers it touches. Tasks are language-agnostic in framing; the engineer adapts test commands and syntax to the consuming repo.

## File format

Every task file is markdown with YAML frontmatter.

- **Frontmatter** holds machine-readable fields: `id`, `files`, `context`. Parsed by the pipeline once via YAML.
- **Body** holds prose phases as level-2 headings (`## RED`, `## GREEN`, `## REFACTOR`), each phase split into level-3 sub-sections (`### Action`, `### Example`, `### Verify`, `### Done`).
- **Code** lives in fenced code blocks (```` ```ts ````, ```` ```sh ````). The fence keeps blank lines safe and lets renderers syntax-highlight.

This format renders cleanly in any CommonMark viewer and parses cleanly with two regex helpers (`sliceH2`, `sliceH3`). Do **not** use HTML/XML tags inside the body — they trigger HTML-block parsing in markdown renderers and desync on blank lines.

## TDD philosophy

The cycle is **RED → GREEN → REFACTOR**. Each phase has a strict purpose:

- **RED**: write the smallest test that captures *one observable behavior* of the component. Test through the public seam (the interface a caller would actually use), not through private internals. Run the test and verify it fails — and fails for the *right reason*: an assertion mismatch, not a missing module. A test that fails because the file does not yet exist is not a meaningful RED.
- **GREEN**: write the minimum code that makes the test pass. Do not generalize. Do not handle cases the test does not exercise. Resist the urge to "while I'm here". Hardcoding the right answer is acceptable in GREEN if that is what the test requires; the next task's RED will force the generalization.
- **REFACTOR**: improve the structure of the code while keeping all tests green. **Refactor never changes behavior.** Adding a new error case, handling new input shapes, extending the contract — those are *new behaviors* and belong in a *new task* (next RED → GREEN cycle), not in REFACTOR. The REFACTOR `### Action` must name **specific operations** with **concrete targets**: extract function X from Y, rename A to B, inline helper C into D, deduplicate pattern across E and F. "Improve structure" or "clean up" is not actionable — if no concrete refactoring is needed, write `No refactoring needed — structure is adequate` and the executor will skip the REFACTOR commit entirely.

## Per-phase commits

Each phase (RED, GREEN, REFACTOR) commits its own work. There is no separate COMMIT phase. The executor (`run`) enforces the commit format:

- RED   → `test(<task-id>): <subject>` — test gate may be red; tsc / lint / build must pass
- GREEN → `feat(<task-id>): <subject>` — all four gates must pass
- REFACTOR → `refactor(<task-id>): <subject>` — all four gates must pass; spec-declared no-op skips entirely (no commit)

Every phase commit carries trailers: `Tap-Task: <task-id>`, `Tap-Phase: RED|GREEN|REFACTOR`, `Tap-Files: <comma-paths>`.

Task files do not include a `## COMMIT` phase. The executor handles staging and committing; phase agents only declare the work.

## Expand-contract pattern

When a change breaks the public API of a shared module (one with multiple consumers), use the expand-contract pattern to keep every task independently compilable:

1. **Expand** — add the new API alongside the old in the shared module. Both APIs work. Existing consumers are untouched.
2. **Migrate** — one task per consumer file, switching from the old API to the new. Each task compiles because both APIs exist.
3. **Contract** — remove the old API from the shared module. All consumers have already migrated.

Each step is its own task with its own RED → GREEN → REFACTOR cycle (each phase commits itself per `run`'s commit policy). The key property: **every commit leaves the codebase in a compilable, test-passing state**.

When to use expand-contract:
- The file being changed is classified `shared` (1-5 dependents) or `high-fanout` (6+ dependents) by the dependency scan
- The change breaks the file's public API (renamed export, changed signature, removed function)

When NOT to use expand-contract:
- The change is internal (refactoring private implementation, no public API break)
- The file is a leaf (0 dependents — nothing imports it)
- The file has exactly one consumer and they can be modified together atomically

If expand-contract produces a large number of migration tasks (10+), flag this in the task summary as an architectural signal — the high consumer count suggests a missing abstraction layer or facade.

## Vertical slicing

Each task is a vertical slice: one behavior delivered end-to-end through every layer it touches. **Do not slice horizontally** — one task for types, one for the implementation, one for the tests will produce tasks that cannot independently pass and cannot independently commit.

Slicing criteria:

- One task = one behavior the user (or the next layer up) can observe
- The RED test exercises the seam at the level the behavior actually lives at — not the deepest internal helper, not the top-level CLI if the behavior is internal
- The slice should be small enough to land in one commit, large enough to deliver something testable
- If a behavior requires creating a new module **and** integrating it, prefer two tasks: (1) the module with its own behavior tested via its seam, (2) the integration with its own behavior tested at the integration seam
- Order tasks so that an earlier task never depends on a file a later task creates

## Behavior tests, not implementation tests

Tests verify *what* the component does for callers, not *how* it does it. A test is an implementation test (and should be rewritten) if it:

- mocks a private collaborator the public seam does not expose
- asserts on internal state instead of returned values or observable side effects
- breaks when the implementation is refactored without changing behavior

A behavior test stays green through every refactor of the same contract.

## Schema

````markdown
---
id: <NN-kebab-slug>
files:
  create:
    - exact/path/to/new-file.ext
  modify:
    - path: exact/path/to/existing-file.ext
      anchor: symbol or function anchor
context:
  - name: SymbolName
    path: src/path/to/definition.ext
    line: 42
    signature: |
      exact type / interface / function signature as it exists in the codebase
  - name: AnotherSymbol
    path: src/path/to/other.ext
    line: 7
    signature: |
      type AnotherSymbol = ...
  - name: NewSymbol
    new: true
    signature: |
      get: (id: UserId) -> Effect<Option<User>, UserCacheError>
---

# <NN-kebab-slug>

## RED

### Action
Write the failing test that captures one observable behavior.

### Example
```<lang>
{{pseudo-code test — see Worked example}}
```

### Verify
```sh
{{repo-conventional test command}}
```

### Done
Test fails with the expected assertion error.

## GREEN

### Pattern hint
<!-- optional: only when pattern-scan identified a matching pattern -->
Compose using <pattern-name> (see <evidence-file:line>).

### Action
Write the minimum code that makes the test pass.

### Example
```<lang>
{{pseudo-code implementation — see Worked example}}
```

### Verify
```sh
{{repo-conventional test command}}
```

### Done
Test passes.

## REFACTOR

### Action
Improve structure while keeping the test green. No new behavior.

### Example
```<lang>
{{pseudo-code refactor — see Worked example}}
```

### Verify
```sh
{{repo-conventional test command}}
```

### Done
Test still passes; structure improved (rename / extract / inline / deduplicate).
````

The `files` field uses `create:` for new paths and a list of `{ path, anchor }` objects under `modify:` for existing paths. **Anchor modifications by symbol name (function, class, exported binding), not by line number** — line numbers shift on edit and the anchor goes stale before the engineer applies the task.

## Context block

The `context:` array in frontmatter lists every symbol the task references — types, interfaces, functions, constants — with their definition site (path + line) and exact signature. This grounds the executing agent so it never has to explore the codebase to find where a symbol lives or what it looks like.

Each context entry has:
- `name`: the identifier as used in the task's code
- `path`: workspace-relative path to the definition file (omit for `new: true` symbols)
- `line`: line number of the definition, best-effort (omit for `new: true` symbols)
- `signature`: the exact type / interface / function signature, copied from the source file (use YAML `|` block scalar to preserve newlines)
- `new: true` (optional): set when the symbol is introduced by the ideation and does not yet exist in the codebase

Include symbols from the dependency-scan's consumer map and integration map. For new symbols, copy the signature from `## Signatures` in `ideation.md`.

## Task ordering

Tasks are emitted with numeric `id` prefixes (`01-…`, `02-…`) for human readability and as a tiebreaker, but the executor (`run`) does NOT execute strictly in numeric order. `run` infers waves from `context[]` symbol ownership and runs wave-mates in parallel when their `files.create` ∪ `files.modify` are disjoint.

Convey's job is to:
1. Order tasks leaves-first per the dependency-scan consumer map (so numeric order is a sensible default if wave inference degenerates).
2. Populate `context[]` accurately so wave inference produces the intended plan.

See `run/RUN_FLOW.md > Wave inference` for the algorithm.

## Pattern hints

The optional `### Pattern hint` sub-section inside `## GREEN` tells the executing agent to shape the implementation after a structural pattern discovered in neighboring modules. When present, it names the pattern (from `pattern-catalog.md`) and cites the evidence file:line where the pattern already exists.

- **When emitted**: only when the pattern-scan step found a matching pattern in a neighboring module with `strong` confidence.
- **When omitted**: no neighbor pattern matched. GREEN defaults to "minimum code that passes" without a prescribed shape.
- **Effect on GREEN**: the `### Action` and `### Example` are shaped to follow the hinted pattern — e.g., using a descriptor array instead of N separate functions. This produces code that composes with its neighbors from the start, reducing or eliminating REFACTOR work.
- **Effect on REFACTOR**: when GREEN followed a pattern-hint, REFACTOR often becomes "No refactoring needed — GREEN followed pattern, structure is adequate." When GREEN had no hint, REFACTOR checks if a pattern from `pattern-catalog.md` fits the output.

## No placeholders

Each `### Action`, `### Example`, `### Verify`, and `### Done` must contain the actual content the engineer will execute. Never emit:

- `TODO`, `TBD`, `FIXME`
- Empty sub-sections
- `{{name}}`-style template tokens reaching the final file
- Vague verbs ("set up the thing", "wire it together", "handle the case")

If you cannot write the concrete content, the task is under-specified — go back to `ideation.md` and resolve the gap, or surface a question to the user before emitting.

## Worked example

Synthetic example for the *Cache user lookups* feature from the ideation template. Pseudo-code is intentionally not tied to one language; the engineer translates to the consuming repo's stack.

````markdown
---
id: 01-cache-hit-returns-stored-user
files:
  create:
    - src/data/CachedUserRepository/CachedUserRepository.ext
    - src/data/CachedUserRepository/CachedUserRepository.test.ext
  modify: []
context:
  - name: UserRepository
    path: src/data/UserRepository/UserRepository.ext
    line: 12
    signature: |
      interface UserRepository {
        findById: (id: UserId) => Effect<Option<User>, UserRepoError>
      }
  - name: UserId
    path: src/types/User.d.ext
    line: 3
    signature: |
      type UserId = Brand<string, "UserId">
  - name: User
    path: src/types/User.d.ext
    line: 8
    signature: |
      type User = { readonly id: UserId; readonly name: string; readonly email: string }
  - name: UserCache
    new: true
    signature: |
      get: (id: UserId) -> Effect<Option<User>, UserCacheError>
      set: (id: UserId, user: User) -> Effect<Unit, UserCacheError>
---

# 01-cache-hit-returns-stored-user

## RED

### Action
Write a behavior test asserting that a second `findById` call within TTL returns the cached value without re-invoking the inner repository.

### Example
```pseudo
test "second findById within TTL returns cached user without hitting inner repository":
  arrange:
    inner_repo  := stub UserRepository
      inner_repo.findById(user_id_a) returns user_a
    user_cache  := in_memory UserCache with TTL = 60s
    cached_repo := CachedUserRepository(inner_repo, user_cache)
  act:
    first_call  := cached_repo.findById(user_id_a)
    second_call := cached_repo.findById(user_id_a)
  assert:
    inner_repo.findById was called exactly once
    first_call  equals user_a
    second_call equals user_a
```

### Verify
```sh
bun test src/data/CachedUserRepository
```

### Done
Test fails because `CachedUserRepository` does not yet exist or returns nothing.

## GREEN

### Action
Implement the smallest `CachedUserRepository` that satisfies the test — check cache, delegate on miss, write back.

### Example
```pseudo
class CachedUserRepository(inner_repo, user_cache):
  findById(id):
    cached := user_cache.get(id)
    if cached is present:
      return cached
    fresh := inner_repo.findById(id)
    user_cache.set(id, fresh)
    return fresh
```

### Verify
```sh
bun test src/data/CachedUserRepository
```

### Done
Test passes.

## REFACTOR

### Action
Rename `inner_repo` to `delegate` for clarity and extract the cache-write step into a private helper. Behavior unchanged; the test stays green. No new test added — new behavior belongs in a new task.

### Example
```pseudo
class CachedUserRepository(delegate, user_cache):
  findById(id):
    cached := user_cache.get(id)
    if cached is present:
      return cached
    return self.fetch_and_cache(id)

  private fetch_and_cache(id):
    fresh := delegate.findById(id)
    user_cache.set(id, fresh)
    return fresh
```

### Verify
```sh
bun test src/data/CachedUserRepository
```

### Done
Test still passes; structure improved.
````
