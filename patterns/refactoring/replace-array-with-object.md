---
name: replace-array-with-object
category: refactoring
aliases: [array-to-record]
intent: >-
  Replace an array used as a heterogeneous record with an object whose named fields make each slot's meaning explicit
sources:
  - https://refactoring.guru/replace-array-with-object
  - https://refactoring.com/catalog/replaceArrayWithObject.html
smells_it_fixes:
  - primitive-obsession
  - data-clump
  - unclear-naming
smells_it_introduces:
  - small-class-proliferation
composes_with:
  - replace-data-value-with-object
  - extract-class
clashes_with:
  - replace-record-with-data-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "each positional array access is replaced by a named field access that returns the same value"
  - "the new object's fields cover every index that was used in the original array"
---

# Replace Array with Object

## Intent
An array is used to hold heterogeneous data where each position has a fixed, different meaning (e.g., row[0] = name, row[1] = score). Replace it with an object whose named fields make each element's role explicit. Positional magic numbers disappear; the record is self-documenting.

## Structure
```
Before:
  row = ["Liverpool", "15", "35"]
  name  = row[0]
  wins  = row[1]
  points = row[2]

After:
  row = Performance(name="Liverpool", wins=15, points=35)
  name  = row.name
  wins  = row.wins
  points = row.points
```

## Applicability
- An array is used as a positional record, each index representing a different concept
- Array indices are referenced by magic numbers spread through the code
- Adding a new "field" requires shifting all subsequent index references
- The data structure is passed between methods and the meaning of positions is not obvious from context

## Consequences
- **Gains**: self-documenting field names; compiler/type-checker catches wrong-field bugs; easy to add/remove fields
- **Costs**: slightly more verbose construction; callers must be updated from index access to field access

## OOP shape
```
// Before
row: Array<Any> = ["Liverpool", 15, 35]
name   = row[0]
wins   = row[1]
points = row[2]

// After
class Performance
  name: String
  wins: Int
  points: Int

row = Performance(name="Liverpool", wins=15, points=35)
name   = row.name
wins   = row.wins
points = row.points
```

## FP shape
```
// Before: tuple / positional array
row = ("Liverpool", 15, 35)
(name, wins, points) = row

// After: named record / product type
type Performance = { name: String, wins: Int, points: Int }
row = { name: "Liverpool", wins: 15, points: 35 }

// Destructuring by name, not position
{ name, wins, points } = row
```

## Smells fixed
- **primitive-obsession**: a raw array acting as a record is replaced by a first-class domain type
- **data-clump**: the cluster of positional values that always travel together is named and typed
- **unclear-naming**: magic index numbers are replaced by expressive field names

## Tests implied
- Each named field returns the same value as the corresponding array index did — test all fields
- No code in the codebase references the old array by integer index after the refactoring

## Sources
- https://refactoring.guru/replace-array-with-object
- https://refactoring.com/catalog/replaceArrayWithObject.html
