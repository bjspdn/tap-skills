# Ideation template

Reference for the markdown emitted by `tap:into` to `.tap/tickets/<slug>/ideation.md`.

`ideation.md` is the design memo — the crystallized output of the tap:into session. File-level change lists, task breakdown, and concrete implementation steps live in the sibling `task-NN-*.md` files emitted by `tap-convey`, not here. This file answers *what*, *why*, and *what shape* — including interface signatures and error design when the approach surfaces them.

The file is markdown with a small YAML frontmatter for machine-readable fields (`title`). All section structure lives in level-2 headings. Downstream agents read this file as raw context; the pipeline parser extracts `title` from frontmatter and `## Constraints` as a body section.

## Header

Every file opens with the same pattern:

```markdown
---
title: <feature>
---

# <feature>: Design intent
```

`<feature>` is the human-readable feature name in prose, not the slug.

## Schema

| Section               | Heading                | Required    | Purpose                                                                                              | Under-spec signal                                              |
| ----------------------| -----------------------| ------------| -----------------------------------------------------------------------------------------------------| ----------------------------------------------------------------|
| Intent                | `## Intent`            | always      | Observable behavior change after shipping                                                            | Restates the header; no observable difference named            |
| Context               | `## Context`           | usually     | Synthesized findings from the explore phase: current state, neighbors, gotchas — with file:line refs | "the codebase" with no file paths                              |
| Approach              | `## Approach`          | always      | Pattern + flow + invariants + seams + open decisions                                                 | One sentence; no flow steps; no named invariants               |
| Signatures            | `## Signatures`        | conditional | Pin interface shapes the implementation must satisfy                                                 | Prose description of "what the function does"; no shapes given |
| Error design          | `## Error design`      | conditional | Enumerate failures, error tags, and recovery strategies                                              | "Handle errors gracefully"; no failure mode named              |
| Constraints           | `## Constraints`       | always      | Hard rules the implementation must respect                                                           | Suggestions phrased as preferences                             |
| Boundaries            | `## Boundaries`        | always      | Explicitly NOT in scope                                                                              | Empty bullets, or duplicates intent in negation                |
| Open decisions        | `## Open decisions`    | usually     | Open questions surfaced during the tap:into sessions that were deferred                              | None named when the approach has obvious gaps                  |
| Considered & rejected | `## Considered & rejected` | usually | Approaches discussed during ideation + why losers lost                                               | Single bullet that restates the chosen approach                |
| Anti-patterns nearby  | `## Anti-patterns nearby` | optional | Shapes from patterns_discovery flagged as smells in neighboring code that this feature must NOT reproduce | Generic "spaghetti code" with no file:line ref |
| Failure modes         | `## Failure modes`     | optional    | Qualitative scenarios surfaced during discussion                                                     | Generic "unexpected input" with no behavior named              |
| Sources               | `## Sources`           | optional    | Web and repo refs that grounded the design                                                           | Bare URLs with no annotation                                   |

**`Signatures` and `Error design` are conditional**: include when `## Approach` describes a structural pattern with interface shapes or named failure modes. Drop the section entirely when neither applies (a single-config-line change does not need an interface table). Omitting beats stubbing.

**Drop optional sections entirely when empty**, BECAUSE empty bullets read as deferred work that was forgotten, while absence reads as "not applicable here".

## Approach block format

The `## Approach` section uses a structured sub-format so the flow, invariants, and seams stay readable instead of dissolving into prose:

```
PATTERN: <pattern name>
  WHAT: <one-line description of the pattern>
  HERE: <how the pattern is applied to this feature>
FLOW:
  1. <step — input enters where>
  2. <step — transformation>
  3. <step — output / side effect>
INVARIANTS:
  - <rule that must hold>
SEAMS:
  - <swappable interface — testability hook>
OPEN:
  - <decision deferred to planner>
```

Skip empty sub-sections — no `SEAMS:` block for a feature with no swappable boundary. `OPEN:` entries inside the approach block should also surface in the top-level `## Open decisions` section. Duplication is intentional, BECAUSE `OPEN:` keeps the deferred decision next to the pattern that surfaces it, while the top-level section is the planner's checklist.

## Artifact-size rule

**Describe reference artifacts (schemas, config examples, API shapes, data structures) over ~20 lines declaratively, not verbatim**, BECAUSE inlined artifacts bloat the file and burn planner tokens on reference material instead of actionable intent. State the requirements the artifact must satisfy and let the planner reconstruct it.

## Code blocks

Every code or pseudocode example MUST be wrapped in a fenced code block with a language tag (```` ```ts ````, ```` ```py ````, ```` ```pseudo ````). The fence keeps blank lines safe inside code, prevents markdown from interpreting `_`, `*`, `<`, `>` as formatting, and gives renderers syntax highlighting. Never paste raw code without a fence.

Do **not** use HTML/XML-style wrapper tags around sections — they trigger HTML-block parsing in markdown renderers and desync on blank lines, breaking display. Use heading levels for structure.

## Worked example

Synthetic example — fictional feature in a fictional repo. Stack chosen for illustration: a typed FP language with sum-type errors and an effect-tracked return type (e.g. TypeScript+Effect, Rust+Result, Haskell+IO). The shape is what to copy; replace names, paths, and stack with whatever the consuming repo actually uses.

````markdown
---
title: Cache user lookups
---

# Cache user lookups: Design intent

## Intent

Repeated lookups for the same user id within a single request hit the database every time. Add a per-process cache so the second lookup of a given id within the cache TTL returns from memory without a database round trip.

## Context

- `UserRepository` is the single source of user reads today; resolver-level callers each invoke `findById` directly (`src/data/UserRepository/UserRepository.ts:42`)
- Two existing per-process caches in the same package compose with a shared request-scoped lifecycle hook (`src/runtime/RequestScope/RequestScope.ts:18`) — neighbors to follow
- Web research surfaced TTL-on-read as the dominant pattern for read-through caches in this stack; TTL-on-write is rejected upstream because clock skew between writers leaks past expiry

## Approach

```
PATTERN: Memoized repository wrapper
  WHAT: A cache layer in front of an existing repository interface — reads check the cache, misses delegate and write back.
  HERE: Wrap UserRepository with CachedUserRepository that consults UserCache before calling UserRepository.findById.
FLOW:
1. Lookup input (user id) enters CachedUserRepository.findById
2. Look up the id in UserCache
3. On hit, return the cached User; on miss, call the inner repository and write the result back
INVARIANTS:
- TTL is enforced on read, not write — entries past TTL behave as misses
- Cache writes never replace a fresher concurrent write for the same id
SEAMS:
- UserCache is an interface — swappable with an in-memory stub for tests
OPEN:
- Cache backend: process-local map vs. shared in-memory store
```

## Signatures

```pseudo
UserCache:
  get:    (id: UserId)            -> Effect<Option<User>, UserCacheError>
  set:    (id: UserId, user: User) -> Effect<Unit, UserCacheError>
  evict:  (id: UserId)             -> Effect<Unit, UserCacheError>

CachedUserRepository.findById: same signature as UserRepository.findById — caching is transparent to callers
```

## Error design

- `UserCacheMiss` — not an error; represented as the empty case of `Option` from `get`
- `UserCacheReadFailed` — backend unreachable on read; recovery: fall through to inner repository (fail-open on read)
- `UserCacheWriteFailed` — backend rejected on write; recovery: log a warning, return the fetched user (fail-open on write)
- Inner repository errors propagate unchanged

## Constraints

- Cache hits return in under 5ms on a 10k-entry cache
- TTL is configurable; default 60 seconds
- No global mutable state — `UserCache` is provided via the same dependency mechanism the rest of the package uses

## Boundaries

- Not caching write paths or list queries
- Not introducing a network-backed cache
- Not changing the `User` type or the repository's public signature

## Open decisions

- Cache backend: process-local map vs. shared in-memory store — defer to planner
- Eviction policy under memory pressure — none specified; planner picks LRU vs. TTL-only

## Considered & rejected

- Cache at the resolver layer instead of the repository — repository-level reuse is broader and avoids duplicating logic per resolver
- Add a TTL field to the `User` type — couples cache concerns to the domain model

## Failure modes

- Concurrent writes for the same id: last write wins; readers may briefly see either value
- Stale read just past TTL: rejected by the read-side TTL check, treated as a miss
- Cache backend unreachable on read: fall through to inner repository (fail-open)

## Sources

- https://martinfowler.com/bliki/TwoHardThings.html — naming/invalidation framing
- `src/runtime/RequestScope/RequestScope.ts:18` — neighboring cache lifecycle pattern
````
