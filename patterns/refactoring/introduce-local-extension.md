---
name: introduce-local-extension
category: refactoring
aliases: [extension-class, wrapper-class]
intent: >-
  Create a subclass or wrapper around an unmodifiable server class to house methods the server should own
sources:
  - https://refactoring.guru/introduce-local-extension
  - https://refactoring.com/catalog/introduceLocalExtension.html
smells_it_fixes:
  - feature-envy
  - repeated-param-threading
  - primitive-obsession
  - scattered-delegation
smells_it_introduces:
  - subclass-proliferation
  - wrapping-complexity
composes_with:
  - introduce-foreign-method
  - extract-class
  - move-method
clashes_with:
  - inline-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the extension class passes all tests the original class would pass for the same operations"
  - "all clients that needed the foreign behavior use the extension type instead of the original"
---

# Introduce Local Extension

## Intent
Multiple foreign methods have accumulated in a client for a server class you cannot modify. Consolidate them by creating a subclass (extension via inheritance) or a wrapper (extension via composition) of the server class, housing the new methods there. The extension becomes the canonical type for clients that need the augmented behavior.

## Structure
```
// Option A: Subclass extension
class MfDate extends Date
  nextDay(): MfDate
  dayOfYear(): Int

// Option B: Wrapper extension
class MfDate
  private _inner: Date
  nextDay(): MfDate
  dayOfYear(): Int
  // delegate all original Date methods to _inner
```

## Applicability
- Three or more foreign methods have accumulated across clients for the same server type
- Multiple client classes need the same extensions (Introduce Foreign Method no longer scales)
- The server class is from a closed library, external SDK, or restricted module
- Choose subclass when the server class is not final and you can freely substitute; choose wrapper when you need tighter control or the server is final/sealed

## Consequences
- **Gains**: all augmented behavior lives in one named type; clients get a clean API; easy to test in isolation
- **Costs**: every place that creates the server type must now create the extension type instead; wrapper requires delegating all original methods

## OOP shape
```
// Unmodifiable server
class Date
  year: Int; month: Int; day: Int

// Subclass form
class MfDate extends Date
  constructor(year, month, day)
    super(year, month, day)

  nextDay(): MfDate
    return MfDate(year, month, day + 1)

  weeksTilDeadline(deadline: MfDate): Int
    return (deadline - self) / 7

// Wrapper form
class MfDate
  _d: Date
  constructor(date: Date)
    _d = date
  nextDay(): MfDate
    return MfDate(Date(_d.year, _d.month, _d.day + 1))
  // re-expose all Date methods via delegation
```

## FP shape
```
// New opaque type wraps the library type
type MfDate = { inner: LibDate }

// Smart constructor
mf_date(lib_date) = { inner: lib_date }

// Extension functions
next_day(d: MfDate) -> MfDate
weeks_til_deadline(d: MfDate, deadline: MfDate) -> Int
```

## Smells fixed
- **feature-envy**: scattered foreign methods on client classes migrate to a dedicated extension type
- **repeated-param-threading**: the server instance no longer threads through client helpers — it is the extension object's self
- **primitive-obsession**: raw library types are wrapped in a named domain type with semantic operations
- **scattered-delegation**: all extensions live in one place instead of across many client classes

## Tests implied
- The extension type produces the same results as the original type for all pre-existing operations — test delegation completeness
- All clients use the extension type; no client retains inline foreign-method logic

## Sources
- https://refactoring.guru/introduce-local-extension
- https://refactoring.com/catalog/introduceLocalExtension.html
