---
name: preserve-whole-object
category: refactoring
aliases: []
intent: >-
  Pass the whole object to a method instead of extracting several values from it before the call
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/preserveWholeObject.html
smells_it_fixes:
  - long-parameter-list
  - data-clump
  - feature-envy
smells_it_introduces:
  - inappropriate-intimacy
composes_with:
  - introduce-parameter-object
  - replace-parameter-with-method-call
clashes_with:
  - replace-parameter-with-method-call
test_invariants:
  - "Behavior is identical before and after: the same field values are read inside the method"
  - "The method does not access fields of the passed object beyond those it previously received as individual parameters"
---

# Preserve Whole Object

## Intent

When a caller extracts several values from an object and passes them individually to a method, the method is implicitly coupled to that object's data without being coupled to the object itself. Passing the whole object instead shortens the parameter list, and if the method later needs additional fields from the same source, no signature change is required. The trade-off is a direct dependency on the object's type.

## Structure

Before:
```
low  = room.daysTempRange.low
high = room.daysTempRange.high
plan.withinRange(low, high)
```

After:
```
plan.withinRange(room.daysTempRange)
```

## Applicability

- Several parameters at a call site all originate from the same source object
- The method already knows about the source object type (or should)
- The set of fields passed tends to grow as the method evolves
- The caller is not trying to hide the source object from the method for isolation reasons

## Consequences

- **Shorter parameter lists** — multiple arguments collapse to one
- **Future-proof** — if the method needs additional fields, no signature change required
- **Direct dependency introduced** — the method now depends on the whole object type, not just primitive values; this can reduce testability if the object is hard to construct
- **May violate Law of Demeter in reverse** — passing a rich object to a utility method can give it more access than it should have

## OOP shape

```
// Before
class HeatingPlan {
  withinRange(low: Temp, high: Temp): Boolean { ... }
}
// Caller
plan.withinRange(room.tempRange.low, room.tempRange.high)

// After
class HeatingPlan {
  withinRange(range: TempRange): Boolean {
    return range.low >= this.min && range.high <= this.max
  }
}
// Caller
plan.withinRange(room.tempRange)
```

## FP shape

```
// Before
const withinRange = (low: Temp, high: Temp, plan: Plan): Boolean =>
  low >= plan.min && high <= plan.max

// Caller destructures before passing
withinRange(room.tempRange.low, room.tempRange.high, plan)

// After — pass the range record whole
const withinRange = (range: TempRange, plan: Plan): Boolean =>
  range.low >= plan.min && range.high <= plan.max

withinRange(room.tempRange, plan)
```

## Smells fixed

- **long-parameter-list** — three or four arguments extracted from the same source collapse into one object reference
- **data-clump** — values that always travel together (low/high, x/y/z, start/end) are kept in their natural container rather than scattered across the signature
- **feature-envy** — a caller that pulls data out of an object and hands it to another method is doing the second method's data-gathering work for it

## Tests implied

- **Behavioral identity** — assert that passing the whole object yields the same result as passing individually extracted fields with the same values
- **Access boundary** — confirm the method only reads the fields it previously received; accessing additional fields would indicate scope creep introduced by the refactoring

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/preserveWholeObject.html
