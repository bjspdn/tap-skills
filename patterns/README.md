# Patterns Catalog

Auto-discoverable design-pattern + refactoring catalog consumed by `tap` skills and agents. Vocabulary for ideation, decomposition, GREEN-shaping, and refactor planning.

## Layout

```
patterns/
├── README.md           # this file
├── _schema.md          # pattern card schema — every card conforms
├── _index.json         # machine-readable index: name → path, smell → patterns
├── creational/         # GoF creational
├── structural/         # GoF structural
├── behavioral/         # GoF behavioral
├── refactoring/        # Fowler refactorings — behavior-preserving operations
└── architectural/      # large-scale: Hexagonal, Clean, Onion, Repository, etc.
```

Each card lives at `patterns/<category>/<canonical-name>.md` and conforms to [`_schema.md`](_schema.md).

## How skills consume the catalog

Three discovery modes, in order of preference:

1. **By name** — when the consumer already knows the pattern:
   ```
   read ${CLAUDE_PLUGIN_ROOT}/patterns/<category>/<name>.md
   ```

2. **By smell** — when the consumer detected a code smell and needs candidate patterns:
   ```
   read ${CLAUDE_PLUGIN_ROOT}/patterns/_index.json
   index.smell_to_patterns["<smell-tag>"] → [array of card paths]
   ```

3. **By scan** — fallback when index is missing or stale:
   ```
   grep -lr "smells_it_fixes:.*<smell-tag>" ${CLAUDE_PLUGIN_ROOT}/patterns/
   ```

Skills should prefer mode 1 or 2. Mode 3 is a safety net.

## Consumer skills (today)

| Skill | What it consumes |
|---|---|
| `refactor` | Cards from `refactoring/` for technique selection during plan phase. Frontmatter `smells_it_fixes` drives smell→technique mapping. |
| `convey` | All categories during pattern-scan phase. Frontmatter `composes_with` informs GREEN shape recommendations. |
| `along` | All categories during whiteboard discussion. Body `OOP shape` + `FP shape` drive dual-paradigm explanations. |

## Frontmatter API surface

Every card exposes these queryable fields (full spec in [`_schema.md`](_schema.md)):

| Field | Type | Used by |
|---|---|---|
| `name` | string (kebab) | identity, name-lookup |
| `category` | enum | filter by scope |
| `aliases` | string[] | name-lookup with synonyms |
| `intent` | string | one-liner for menus and pickers |
| `smells_it_fixes` | string[] | smell→pattern routing |
| `smells_it_introduces` | string[] | trade-off surfacing |
| `composes_with` | string[] | nesting recommendations |
| `clashes_with` | string[] | conflict warnings |
| `test_invariants` | string[] | proof-test generation |

## Smell tag vocabulary

Smell tags are **shared across the catalog** — kebab-case, canonical. When introducing a new smell tag in a card's `smells_it_fixes` or `smells_it_introduces`, regenerate `_index.json` so consumers can route by it.

Common tags (non-exhaustive):

- `long-conditional-chain`, `switch-on-type`
- `duplicate-algorithm-variants`, `duplicate-error-handling`
- `long-parameter-list`, `repeated-param-threading`
- `feature-envy`, `inappropriate-intimacy`
- `primitive-obsession`, `data-clump`
- `god-class`, `large-class`, `long-method`
- `shotgun-surgery`, `divergent-change`
- `dead-code`, `speculative-generality`
- `comments-as-deodorant`, `unclear-naming`
- `mutable-shared-state`, `temporal-coupling`

## Index regeneration

`_index.json` is regenerated whenever cards are added, renamed, or have their frontmatter `smells_it_fixes` updated. Treat it as a build artifact.

## Adding a pattern

1. Pick category (`creational/structural/behavioral/refactoring/architectural`).
2. Create `<category>/<canonical-kebab-name>.md` conforming to [`_schema.md`](_schema.md).
3. Cite `refactoring.guru` and/or `martinfowler.com` in frontmatter `sources`.
4. Use existing kebab smell tags where possible; introduce new tags sparingly.
5. Regenerate `_index.json`.

## Sources

The catalog draws primarily from:

- [refactoring.guru](https://refactoring.guru) — GoF design patterns + Fowler refactorings catalog
- [martinfowler.com](https://martinfowler.com) — Patterns of Enterprise Application Architecture
- [refactoring.com](https://refactoring.com/catalog/) — Fowler's canonical refactoring catalog
- *Design Patterns: Elements of Reusable Object-Oriented Software* (Gang of Four, 1994)
- *Refactoring: Improving the Design of Existing Code* (Fowler, 1999/2018)
