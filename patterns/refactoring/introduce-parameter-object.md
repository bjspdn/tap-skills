---
name: introduce-parameter-object
category: refactoring
aliases: []
intent: >-
  Replace a recurring group of parameters with a single object that encapsulates them
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/introduceParameterObject.html
smells_it_fixes:
  - long-parameter-list
  - data-clump
  - repeated-param-threading
smells_it_introduces:
  - extra-type
composes_with:
  - preserve-whole-object
  - rename-method
  - extract-method
clashes_with: []
test_invariants:
  - "Behavior is identical before and after: fields in the new object carry the same values the individual parameters did"
  - "No logic migrates into the parameter object during this refactoring step"
---

# Introduce Parameter Object

## Intent

When the same cluster of parameters travels together across multiple methods, those parameters are a data clump begging to be named. Replacing them with a dedicated parameter object gives the grouping an identity, removes repetition from every affected signature, and often reveals behavior that naturally belongs on the new object. The refactoring is safe when restricted to structural change; behavior migration to the new type is a separate, subsequent step.

## Structure

Before:
```
amountInvoiced(start: Date, end: Date): Money
amountReceived(start: Date, end: Date): Money
amountOverdue(start: Date, end: Date): Money
```

After:
```
amountInvoiced(period: DateRange): Money
amountReceived(period: DateRange): Money
amountOverdue(period: DateRange): Money

class DateRange {
  start: Date
  end: Date
}
```

## Applicability

- The same two or more parameters appear together in multiple method signatures
- The group has a natural domain name (a date range, a coordinate pair, a measurement window)
- Methods performing comparisons or checks on the grouped values could migrate to the new object
- Parameter lists exceed 3–4 items and a subset clearly belongs together

## Consequences

- **Shorter signatures** — N parameters become one; all affected methods benefit simultaneously
- **Named concept** — the group acquires an identity in the domain language
- **Migration target** — methods that manipulate the grouped values can move onto the new object in later refactorings (e.g. `dateRange.includes(date)`)
- **New type to maintain** — introduces a class or record that must be documented and kept consistent
- **Temporary duplication** — during transition, old and new signatures coexist

## OOP shape

```
// Before
class Ledger {
  amountInvoiced(start: Date, end: Date): Money { ... }
  amountReceived(start: Date, end: Date): Money { ... }
}

// Step 1: introduce the object (value object, no behavior yet)
class DateRange {
  start: Date
  end: Date
  constructor(start, end) { this.start = start; this.end = end }
}

// Step 2: add new overload, keep old during migration
class Ledger {
  amountInvoiced(period: DateRange): Money { ... }
}
```

## FP shape

```
// Before — date pair threaded everywhere
type DatePair = { start: Date; end: Date }

const amountInvoiced = (start: Date, end: Date): Money => ...
const amountReceived = (start: Date, end: Date): Money => ...

// After — named record
type DateRange = { start: Date; end: Date }

const amountInvoiced = (period: DateRange): Money => ...
const amountReceived = (period: DateRange): Money => ...

// Behavior can later migrate: includes, overlaps, duration
const includes = (period: DateRange, date: Date): Boolean =>
  date >= period.start && date <= period.end
```

## Smells fixed

- **long-parameter-list** — a cluster of related parameters is replaced with a single named object, immediately reducing arity across all affected signatures
- **data-clump** — parameters that always travel together are given a type, making their relationship explicit and enforced
- **repeated-param-threading** — the grouped values no longer need to be passed down through multiple call layers individually

## Tests implied

- **Behavioral identity** — for each affected method, assert that constructing the parameter object with the original values and calling the refactored signature yields the same result as the original signature
- **No logic migration** — the parameter object contains only data after this refactoring step; assert it has no methods beyond accessors (behavior migration is a separate step)

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/introduceParameterObject.html
