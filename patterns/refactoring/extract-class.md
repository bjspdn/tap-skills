---
name: extract-class
category: refactoring
aliases: [split-class]
intent: >-
  Split a class doing two jobs into two focused classes, each with a single clear responsibility
sources:
  - https://refactoring.guru/extract-class
  - https://refactoring.com/catalog/extractClass.html
smells_it_fixes:
  - large-class
  - god-class
  - divergent-change
  - data-clump
smells_it_introduces:
  - small-class-proliferation
  - indirection-overhead
composes_with:
  - move-method
  - move-field
  - hide-delegate
clashes_with:
  - inline-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "each extracted class can be tested in isolation without the parent class"
  - "no public API of the original class changes signature"
---

# Extract Class

## Intent
A single class carries responsibilities that belong to two separate concepts. Create a new class, move the relevant fields and methods into it, and adjust the original class to delegate where needed. This is the primary tool for enforcing the Single Responsibility Principle.

## Structure
```
Before:
  Person
    name
    officeAreaCode
    officeNumber
    getTelephoneNumber()

After:
  Person
    name
    officeTelephone: TelephoneNumber
    getTelephoneNumber() → delegates

  TelephoneNumber
    areaCode
    number
    getTelephoneNumber()
```

## Applicability
- A class has grown to hold two or more conceptually distinct responsibilities
- A subset of fields and methods forms a natural cluster that could be named independently
- You find yourself describing the class with "and" — it manages X and also handles Y
- A subgroup of data always changes together (a data clump hiding as class state)

## Consequences
- **Gains**: each class is easier to understand, test, and change independently; SRP is restored
- **Costs**: more classes to navigate; the extracted class must be composed back into the parent; can lead to over-extraction if applied mechanically

## OOP shape
```
// Before
class Person
  name: String
  areaCode: String
  number: String

  getTelephoneNumber(): String
    return "(" + areaCode + ") " + number

// After
class TelephoneNumber
  areaCode: String
  number: String

  toString(): String
    return "(" + areaCode + ") " + number

class Person
  name: String
  telephone: TelephoneNumber

  getTelephoneNumber(): String
    return telephone.toString()
```

## FP shape
```
// Before: flat record
type Person = { name, area_code, number }

// After: nested product types
type TelephoneNumber = { area_code, number }
type Person = { name, telephone: TelephoneNumber }

format_telephone(t: TelephoneNumber) -> String
```

## Smells fixed
- **large-class**: the original class was carrying too much state and behavior; extraction reduces it to one concern
- **god-class**: a class acting as a catch-all is decomposed into focused collaborators
- **divergent-change**: the class changed for multiple reasons; after extraction each class changes for one reason
- **data-clump**: fields that travel together are moved into their own type

## Tests implied
- All original public API entry points return the same results — test before and after with the same fixtures
- The extracted class can be constructed and tested without any reference to the parent class

## Sources
- https://refactoring.guru/extract-class
- https://refactoring.com/catalog/extractClass.html
