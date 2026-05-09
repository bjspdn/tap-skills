---
name: inline-class
category: refactoring
aliases: [collapse-class]
intent: >-
  Absorb a class that no longer carries enough responsibility into its most frequent collaborator
sources:
  - https://refactoring.guru/inline-class
  - https://refactoring.com/catalog/inlineClass.html
smells_it_fixes:
  - small-class-proliferation
  - speculative-generality
  - dead-code
smells_it_introduces:
  - large-class
  - divergent-change
composes_with:
  - move-method
  - move-field
clashes_with:
  - extract-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the absorbed class is no longer instantiated anywhere after inlining"
  - "callers of the original class methods receive identical results through the absorbing class"
---

# Inline Class

## Intent
A class is doing so little that it no longer justifies its existence. Pull all of its features into another class and delete it. This is the inverse of Extract Class and is applied when a previous extraction went too far, or when a class has been stripped of most of its responsibilities by other refactorings.

## Structure
```
Before:
  Person
    telephone: TelephoneNumber
    getTelephoneNumber() → telephone.toString()

  TelephoneNumber
    areaCode
    number
    toString()

After:
  Person
    areaCode
    number
    getTelephoneNumber()   ← logic inlined
  // TelephoneNumber deleted
```

## Applicability
- A class has been reduced to almost nothing after a series of refactorings
- A class exists only to pass data through without meaningful transformation
- Two classes should be merged before redistributing responsibilities differently (inline first, then re-extract)
- Speculative abstraction — a class was created for anticipated growth that never materialized

## Consequences
- **Gains**: eliminates unnecessary indirection; fewer types to understand and maintain
- **Costs**: the absorbing class grows; if the inlined class had multiple users, those call sites must all be updated

## OOP shape
```
// Before
class TelephoneNumber
  areaCode: String
  number: String
  toString(): String

class Person
  telephone: TelephoneNumber
  getTelephoneNumber(): String
    return telephone.toString()

// After
class Person
  areaCode: String
  number: String
  getTelephoneNumber(): String
    return "(" + areaCode + ") " + number
```

## FP shape
```
// Before: separate type with one function
type TelephoneNumber = { area_code, number }
format(t: TelephoneNumber) -> String

type Person = { name, telephone: TelephoneNumber }

// After: fields inlined into Person record
type Person = { name, area_code, number }
get_telephone(p: Person) -> String
```

## Smells fixed
- **small-class-proliferation**: a class too thin to justify existence is absorbed, reducing cognitive overhead
- **speculative-generality**: a type created for anticipated future use but never meaningfully used is collapsed
- **dead-code**: a class whose responsibilities have migrated elsewhere is cleanly removed

## Tests implied
- All callers of the now-deleted class's methods receive identical results via the absorbing class
- No remaining reference to the deleted class exists in the codebase after inlining

## Sources
- https://refactoring.guru/inline-class
- https://refactoring.com/catalog/inlineClass.html
