---
name: replace-delegation-with-inheritance
category: refactoring
aliases: []
intent: >-
  Replace a field-plus-forwarding-methods pattern with direct inheritance when the class uses the full delegated interface
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/replaceDelegationWithInheritance.html
smells_it_fixes:
  - repeated-param-threading
  - duplicate-algorithm-variants
smells_it_introduces:
  - refused-bequest
  - inappropriate-intimacy
composes_with:
  - pull-up-method
  - pull-up-field
clashes_with:
  - replace-inheritance-with-delegation
test_invariants:
  - "All behavior previously forwarded to the delegate is now available directly via inheritance"
  - "No forwarding stub methods remain after the refactoring"
---

# Replace Delegation with Inheritance

## Intent

When a class holds a delegate object and forwards nearly every method call to it — essentially re-exposing the full delegate interface — the forwarding layer is boilerplate without benefit. If the "has-a" relationship is actually "is-a" (the class genuinely is a kind of the delegate's type), replacing the field with direct inheritance eliminates the forwarding stubs and lets the class use the superclass methods without redirection. It is the inverse of Replace Inheritance with Delegation.

## Structure

Before:
```
class Employee {
  private delegate: Person = new Person()
  getName(): String   { return this.delegate.getName() }
  getAge(): Int       { return this.delegate.getAge() }
  getAddress(): Address { return this.delegate.getAddress() }
  // ... forwards every Person method
}
```

After:
```
class Employee extends Person {
  // Person methods available directly; no forwarding stubs
}
```

## Applicability

- The class forwards the majority of its methods to the delegate without adding logic
- The class is used interchangeably with the delegate type in the codebase
- There is a genuine "is-a" relationship — an Employee truly is a Person
- The delegate class is not shared with other objects (i.e. the delegate is not a flyweight or shared collaborator)

## Consequences

- **Forwarding boilerplate eliminated** — N stub methods are replaced by one `extends` declaration
- **Polymorphic substitutability restored** — the class can be used wherever the former delegate type is expected
- **Inheritance coupling reintroduced** — the class is now bound to the superclass's full interface, including methods it may not want; apply Replace Inheritance with Delegation if this proves problematic
- **Delegate sharing broken** — if the delegate was shared between objects, inheritance cannot replicate that sharing

## OOP shape

```
// Before — full delegation boilerplate
class Employee {
  private person: Person
  constructor(person: Person) { this.person = person }
  getName(): String    { return this.person.getName() }
  getAge(): Int        { return this.person.getAge() }
  getAddress(): String { return this.person.getAddress() }
}

// After — direct inheritance
class Employee extends Person {
  // getName(), getAge(), getAddress() inherited directly
}
```

## FP shape

```
// Before — thin wrapper module that only re-exports
import * as Person from './person'
export const getName    = (e: Employee) => Person.getName(e.person)
export const getAge     = (e: Employee) => Person.getAge(e.person)
export const getAddress = (e: Employee) => Person.getAddress(e.person)

// After — Employee IS a Person (structural subtype)
type Person   = { name: String; age: Int; address: String }
type Employee = Person & { employeeId: EmployeeId }
// getName, getAge, getAddress work directly on Employee values
```

## Smells fixed

- **repeated-param-threading** — forwarding stubs that do nothing but pass arguments through to the delegate are a form of noise threading; inheritance eliminates the redirection layer
- **duplicate-algorithm-variants** — when multiple classes all forward identical method sets to the same delegate type, inheritance from a shared base collapses the forwarding duplication

## Tests implied

- **No forwarding stubs remaining** — assert that the class has no methods consisting solely of `return this.delegate.method(args)`
- **Inherited behavior identical** — assert that calling a formerly-delegated method directly on the class produces the same result as calling it on the former delegate

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/replaceDelegationWithInheritance.html
