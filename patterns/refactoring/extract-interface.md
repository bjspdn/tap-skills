---
name: extract-interface
category: refactoring
aliases: []
intent: >-
  Extract a subset of a class's interface into a separate interface type so clients depend only on what they use
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/extractInterface.html
smells_it_fixes:
  - inappropriate-intimacy
  - speculative-generality
  - god-class
smells_it_introduces:
  - over-abstraction-single-variant
composes_with:
  - extract-superclass
  - replace-inheritance-with-delegation
clashes_with: []
test_invariants:
  - "All clients that depended on the concrete class still compile when their references are updated to the interface type"
  - "The extracted interface contains only the methods the client actually calls"
---

# Extract Interface

## Intent

When only a subset of a class's methods is used by a particular client, that client is coupled to more of the class than it needs. Extracting an interface that covers only the relevant subset lets the client depend on a minimal contract, enables substitution with any compliant implementation, and makes the separation of responsibilities explicit. It is the protocol-only complement to Extract Superclass.

## Structure

Before:
```
class Employee {
  getRate(): Money
  hasSpecialSkill(): Boolean
  getName(): String
  getDepartment(): Department
}
// Billing only uses getRate() and hasSpecialSkill()
```

After:
```
interface Billable {
  getRate(): Money
  hasSpecialSkill(): Boolean
}
class Employee implements Billable {
  getRate(): Money { ... }
  hasSpecialSkill(): Boolean { ... }
  getName(): String { ... }
  getDepartment(): Department { ... }
}
// Billing depends on Billable, not Employee
```

## Applicability

- A client uses only a slice of a class's methods and should not be coupled to the rest
- Multiple unrelated classes could satisfy the same protocol; an interface makes this substitutability explicit
- You need to introduce a test double (mock/stub) for a client dependency without subclassing a concrete class

## Consequences

- **Narrow dependency** — clients depend on the minimum interface they require (Interface Segregation Principle)
- **Testability** — any implementation satisfying the interface can be injected; concrete classes are no longer required in tests
- **Multiple implementations** — new classes can satisfy the interface without inheriting from anything
- **Proliferation risk** — too many fine-grained interfaces adds navigational overhead; balance with cohesion

## OOP shape

```
// Before
class TimeSheet {
  billableHours(employee: Employee): Money {
    rate  = employee.getRate()
    hours = this.hoursFor(employee)
    return rate * hours
  }
}

// After
interface Billable {
  getRate(): Money
}
class TimeSheet {
  billableHours(billable: Billable): Money {
    return billable.getRate() * this.hours
  }
}
class Employee implements Billable {
  getRate(): Money { ... }
  // other methods not part of Billable
}
```

## FP shape

```
// Before — function depends on the full Employee record type
const billableHours = (employee: Employee, hours: Int): Money =>
  employee.getRate() * hours

// After — depends only on the Billable capability (structural typing)
type Billable = { getRate: () => Money }
const billableHours = (billable: Billable, hours: Int): Money =>
  billable.getRate() * hours

// Any record with getRate satisfies Billable; no explicit declaration needed
// In Haskell/typeclass terms: class Billable a where getRate :: a -> Money
```

## Smells fixed

- **inappropriate-intimacy** — a client that receives a full `Employee` object when it only needs `getRate()` has access to far more than it should; the interface restricts that access
- **speculative-generality** — a monolithic class interface forced on every client whether they need all of it or not; the interface makes the truly needed subset explicit
- **god-class** — extracting interfaces from a large class is the first step in breaking its monolithic dependency surface

## Tests implied

- **Client compiles on interface** — update the client's parameter type to the interface; assert it compiles without requiring access to methods not in the interface
- **Substitutability** — assert that a test double implementing only the interface methods can be passed to the client and produces the expected behavior

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/extractInterface.html
