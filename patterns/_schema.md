# Pattern Card Schema

Every pattern card under `patterns/<category>/` MUST conform to this schema. Skills and agents query frontmatter; humans read the body.

## Filename rules

- Canonical kebab-case pattern name: `strategy.md`, `extract-method.md`, `replace-conditional-with-polymorphism.md`.
- Lives under exactly one category subdirectory: `creational/`, `structural/`, `behavioral/`, `refactoring/`, `architectural/`.
- One pattern = one file. Aliases live in frontmatter, never as separate files.

## Frontmatter (required)

```yaml
---
name: strategy                         # canonical kebab-case, matches filename stem
category: behavioral                   # one of: creational | structural | behavioral | refactoring | architectural
aliases: [policy]                      # alternate names (kebab-case array). Empty array if none.
intent: >-                             # one-line summary, ≤ 120 chars, no trailing period
  Define a family of algorithms, encapsulate each, make them interchangeable
smells_it_fixes:                       # kebab-case smell tags. Greppable. Used by smell-scanner skills.
  - long-conditional-chain
  - switch-on-type
  - duplicate-algorithm-variants
smells_it_introduces:                  # kebab-case. Costs of applying this pattern.
  - over-abstraction-single-variant
composes_with:                         # kebab-case pattern names that nest/pair well
  - factory-method
  - dependency-injection
clashes_with:                          # kebab-case pattern names that conflict
  - singleton-collaborator-no-di
test_invariants:                       # plain-English assertions any correct impl must satisfy
  - "All variants conform to the strategy interface contract"
  - "Context delegates without inspecting strategy concrete type"
---
```

## Body (required sections, in order)

```markdown
# <Pattern Name>

## Intent
<2–4 sentence prose>

## Structure
<ASCII diagram OR bulleted role list>

## Applicability
<when to apply, bullet list>

## Consequences
<trade-offs, bullet list — gains AND costs>

## OOP shape
<abstract code shape — interface/class skeleton, NOT runnable>

## FP shape
<abstract code shape — function types/composition, NOT runnable. Omit ONLY if pattern has no natural FP form (rare)>

## Smells fixed
<one bullet per `smells_it_fixes` tag, expanded with concrete signal>

## Tests implied
<one bullet per `test_invariants` entry, with rationale>

## Sources
<bulleted URL list mirroring frontmatter `sources`>
```

## Hard rules

- Frontmatter is **canonical machine surface**. Body is human-readable mirror. Never let them drift.
- `name` field equals filename stem. Filename change = name change.
- `smells_it_fixes` and `composes_with` use kebab-case canonical tags shared across the catalog. Coordinate via `_index.json`.
- Code shapes are **abstract** — language-agnostic skeletons, type signatures, pseudocode. Never compilable.
- Sources prioritize: refactoring.guru → martinfowler.com → original GoF → other authoritative.
- One pattern, one file. Variants live as sub-headings inside the card, not separate files.

## Auto-discovery contract

Skills consume the catalog three ways:

1. **By name**: read `patterns/<category>/<name>.md` directly.
2. **By smell**: query `patterns/_index.json#smell_to_patterns[<smell>]` → list of pattern paths.
3. **By scan**: `grep -lr "smells_it_fixes:.*<smell>" patterns/` as fallback when index missing.

The frontmatter tags are the API. Body prose is documentation only.
