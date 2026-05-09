---
name: encapsulate-field
category: refactoring
aliases: [add-getter-setter, privatize-field]
intent: >-
  Make a public field private and provide getter/setter methods to control external access
sources:
  - https://refactoring.guru/encapsulate-field
  - https://refactoring.com/catalog/encapsulateVariable.html
smells_it_fixes:
  - inappropriate-intimacy
  - mutable-shared-state
  - shotgun-surgery
smells_it_introduces:
  - accessor-noise
composes_with:
  - self-encapsulate-field
  - replace-data-value-with-object
  - encapsulate-collection
clashes_with:
  - self-encapsulate-field
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "all external access to the field routes through the getter/setter"
  - "the field is no longer accessible as a public member"
---

# Encapsulate Field

## Intent
A public field can be read or written by any external code without the class knowing or being able to react. Make the field private and expose it through getter and setter methods. This gives the class control over reads and writes, making it possible to add validation, notification, or computed logic later without changing external call sites.

## Structure
```
Before:
  class Person
    name: String    ← public

  person.name = "Alice"
  print(person.name)

After:
  class Person
    private _name: String

    getName(): String
      return _name

    setName(n: String): Unit
      _name = n

  person.setName("Alice")
  print(person.getName())
```

## Applicability
- A public field is directly accessed by external classes
- Validation, transformation, or notification logic needs to be added around field access in the future
- Preparing a field for replacement by a computed value or delegation
- Enforcing information hiding as a baseline OOP discipline

## Consequences
- **Gains**: field access is centralized; validation or side effects can be added without changing callers; field can be replaced by computation transparently
- **Costs**: adds accessor boilerplate; verbose for simple read-only values in languages without property syntax

## OOP shape
```
// Before
class Customer
  public email: String

// After
class Customer
  private _email: String

  getEmail(): String
    return _email

  setEmail(e: String): Unit
    validate(e)             // hook point
    _email = e
    notifyChanged()         // hook point
```

## FP shape
```
// FP: fields are always accessed via module functions; no public field exposure
type Customer = { email: String }   // opaque outside the module

// Module exposes:
get_email(c: Customer) -> String = c.email
set_email(c: Customer, e: String) -> Customer =
  validate!(e)
  { c | email: e }
```

## Smells fixed
- **inappropriate-intimacy**: external classes no longer reach directly into the object's data
- **mutable-shared-state**: mutations to the field are channeled through the setter, providing a single interception point
- **shotgun-surgery**: logic that was scattered at every raw assignment site can now be centralized in the setter

## Tests implied
- External code cannot access the field directly — the field is not in the public API
- The getter returns the value set by the setter; the setter applies any validation before storing

## Sources
- https://refactoring.guru/encapsulate-field
- https://refactoring.com/catalog/encapsulateVariable.html
