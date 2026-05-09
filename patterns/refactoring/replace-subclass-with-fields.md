---
name: replace-subclass-with-fields
category: refactoring
aliases: [inline-subclass, collapse-subclass-hierarchy]
intent: >-
  Collapse subclasses that differ only in constant-returning methods into fields on the parent class
sources:
  - https://refactoring.guru/replace-subclass-with-fields
  - https://refactoring.com/catalog/replaceSubclassWithFields.html
smells_it_fixes:
  - subclass-proliferation
  - speculative-generality
  - dead-code
smells_it_introduces:
  - data-class
  - large-class
composes_with:
  - replace-type-code-with-class
  - inline-class
clashes_with:
  - replace-type-code-with-subclasses
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the parent class with fields produces the same constant values as the original subclass methods"
  - "all subclasses are deleted and no code instantiates them after the refactoring"
---

# Replace Subclass with Fields

## Intent
Subclasses exist only to return different constant values from overridden methods. The subclassing machinery is heavier than the variation it encodes. Replace the subclasses with instance variables on the parent class initialized at construction time. This is the inverse of Replace Type Code with Subclasses.

## Structure
```
Before:
  abstract class Person
    abstract isMale(): Boolean
    abstract getCode(): Char

  class Male extends Person
    isMale(): Boolean = true
    getCode(): Char = 'M'

  class Female extends Person
    isMale(): Boolean = false
    getCode(): Char = 'F'

After:
  class Person
    private _isMale: Boolean
    private _code: Char

    static createMale():   Person = Person(true,  'M')
    static createFemale(): Person = Person(false, 'F')

    isMale(): Boolean = _isMale
    getCode(): Char   = _code
```

## Applicability
- Subclasses have no distinct behavior — they only differ in constant return values
- The subclass hierarchy feels over-engineered for the amount of variation it models
- The type is fixed at construction and is just a discriminant for constant data
- You are collapsing a class hierarchy after behavioral variation was removed by previous refactorings

## Consequences
- **Gains**: fewer classes; simpler hierarchy; the type information is captured as data, not structure
- **Costs**: the parent class grows fields; the rich override mechanism is lost — adding behavior later requires re-introducing the hierarchy

## OOP shape
```
// Before — subclasses only return constants
abstract class Person
  abstract isMale(): Boolean
  abstract getCode(): String

class Male extends Person
  isMale(): Boolean = true
  getCode(): String = "M"

// After — constants become constructor parameters
class Person
  private _male: Boolean
  private _code: String

  constructor(isMale: Boolean, code: String)
    _male = isMale
    _code = code

  static male():   Person = Person(true, "M")
  static female(): Person = Person(false, "F")

  isMale(): Boolean = _male
  getCode(): String = _code
```

## FP shape
```
// Before: each variant is a tagged constructor that returns a constant
type Person = Male | Female

is_male(p: Person) = match p with Male -> true | Female -> false
get_code(p: Person) = match p with Male -> "M" | Female -> "F"

// After: single record type carrying the constants as data
type Person = { is_male: Boolean, code: String }

male   = { is_male: true,  code: "M" }
female = { is_male: false, code: "F" }
```

## Smells fixed
- **subclass-proliferation**: a thin subclass hierarchy that only encodes constants is collapsed to data
- **speculative-generality**: inheritance machinery added for anticipated variation that never materialized is removed
- **dead-code**: subclass override methods that only return literals are eliminated

## Tests implied
- The parent class factory methods produce objects whose accessor return values match what the subclass methods returned
- No code instantiates the deleted subclasses after the refactoring — no remaining references

## Sources
- https://refactoring.guru/replace-subclass-with-fields
- https://refactoring.com/catalog/replaceSubclassWithFields.html
