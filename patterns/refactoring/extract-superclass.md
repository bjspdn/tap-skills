---
name: extract-superclass
category: refactoring
aliases: []
intent: >-
  Create a superclass and move common features of two or more classes into it
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/extractSuperclass.html
smells_it_fixes:
  - duplicate-algorithm-variants
  - parallel-inheritance-hierarchy
  - shotgun-surgery
smells_it_introduces:
  - speculative-generality
composes_with:
  - pull-up-field
  - pull-up-method
  - extract-interface
clashes_with:
  - collapse-hierarchy
test_invariants:
  - "Each original class behaves identically after the refactoring — all existing tests pass"
  - "Common behavior accessed via the superclass type returns the same results as accessing it via the concrete type"
---

# Extract Superclass

## Intent

When two or more classes share features — fields, methods, or initialization logic — the duplication implies a missing abstraction. Extracting a superclass and pulling the shared features into it eliminates the duplication, names the common concept, and enables polymorphic use of the shared behavior. It is the structural complement to Extract Interface; where Extract Interface captures the protocol, Extract Superclass captures shared implementation.

## Structure

Before:
```
class Department {
  name: String
  annualCost(): Money
  headCount(): Int
}
class Employee {
  name: String
  annualCost(): Money
  id: EmployeeId
}
```

After:
```
class Party {
  name: String
  annualCost(): Money  // abstract or default
}
class Department extends Party {
  headCount(): Int
}
class Employee extends Party {
  id: EmployeeId
}
```

## Applicability

- Two or more classes share fields, methods, or initialization patterns with identical or near-identical implementations
- The shared features represent a coherent concept that deserves a name in the domain
- Single-inheritance constraints are not an obstacle (consider Extract Interface if they are)

## Consequences

- **Named shared abstraction** — the common concept acquires a type that can be referenced polymorphically
- **Single maintenance point** — shared features live in one place; fixes propagate automatically
- **Inheritance used for implementation sharing** — which can be brittle; if the classes differ significantly, delegation may be safer
- **Hierarchy depth increases** — callers may need to update type references from the concrete types to the new superclass

## OOP shape

```
// Before
class Employee {
  private name: String
  private id: EmployeeId
  annualCost(): Money { return this.salary * 12 }
}
class Department {
  private name: String
  private staff: List<Employee>
  annualCost(): Money { return this.staff.sum(e => e.annualCost()) }
}

// After
abstract class Party {
  protected name: String
  abstract annualCost(): Money
}
class Employee extends Party {
  private id: EmployeeId
  annualCost(): Money { return this.salary * 12 }
}
class Department extends Party {
  private staff: List<Employee>
  annualCost(): Money { return this.staff.sum(e => e.annualCost()) }
}
```

## FP shape

```
// Before — duplicated fields and functions
type Employee   = { name: String; salary: Money }
type Department = { name: String; staff: Employee[] }
const employeeAnnualCost   = (e: Employee): Money => e.salary * 12
const departmentAnnualCost = (d: Department): Money => d.staff.reduce(...)

// After — shared type constraint and typeclass-style protocol
type HasAnnualCost = { annualCost: () => Money }
type Named = { name: String }
type Party = Named & HasAnnualCost

// Each concrete type satisfies Party
const employee: Party   = { name: ..., annualCost: () => salary * 12 }
const department: Party = { name: ..., annualCost: () => staff.reduce(...) }
```

## Smells fixed

- **duplicate-algorithm-variants** — identical method bodies across sibling classes are collapsed into the superclass
- **parallel-inheritance-hierarchy** — two hierarchies that mirror each other feature-for-feature can be merged via a shared superclass at the root
- **shotgun-surgery** — a bug in shared logic requires N fixes across N classes; after extract superclass, one fix covers all

## Tests implied

- **Behavioral identity** — run all existing tests on each original class; assert zero regressions
- **Polymorphic access** — assert that accessing common behavior via a `Party`-typed reference returns the same result as accessing it via the concrete type

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/extractSuperclass.html
