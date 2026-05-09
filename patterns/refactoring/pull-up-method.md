---
name: pull-up-method
category: refactoring
aliases: []
intent: >-
  Move methods with identical or equivalent bodies from subclasses up to the superclass to eliminate duplication
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/pullUpMethod.html
smells_it_fixes:
  - duplicate-algorithm-variants
  - parallel-inheritance-hierarchy
  - shotgun-surgery
smells_it_introduces:
  - large-class
composes_with:
  - pull-up-field
  - pull-up-constructor-body
  - form-template-method
clashes_with:
  - push-down-method
test_invariants:
  - "Each subclass produces the same result from the pulled-up method as it did from its own copy"
  - "The superclass method can be invoked via a superclass-typed reference and behaves identically"
---

# Pull Up Method

## Intent

When two or more subclasses contain methods that do the same thing, the duplication is a maintenance liability: any fix or enhancement must be applied in N places. Moving the method to the superclass eliminates the redundancy and establishes a single authoritative implementation. If the bodies are nearly but not exactly identical, apply Form Template Method first to isolate the differing parts before pulling up the common skeleton.

## Structure

Before:
```
class ResidentialCustomer extends Customer {
  annualCharge(): Money { ... }
}
class BusinessCustomer extends Customer {
  annualCharge(): Money { ... }  // identical body
}
```

After:
```
class Customer {
  annualCharge(): Money { ... }  // single implementation
}
```

## Applicability

- Two or more sibling subclasses contain methods with identical or equivalent bodies
- The method references only fields and methods that already exist on the superclass (or can be pulled up first)
- No subclass needs to override the pulled-up method with different behavior

## Consequences

- **Single point of maintenance** — fixes and enhancements apply once; all subclasses benefit automatically
- **Superclass responsibility grows** — a superclass that accumulates too many pulled-up methods can become a God Class
- **Subtle difference risk** — methods that appear identical but differ in a type reference or a field name require careful comparison before merging
- **Polymorphism preserved** — subclasses can still override if their behavior legitimately diverges

## OOP shape

```
// Before
class Salesman extends Employee {
  getName(): String { return this.name }
}
class Engineer extends Employee {
  getName(): String { return this.name }
}

// Step 1: ensure field is on superclass (Pull Up Field)
// Step 2: pull method
class Employee {
  protected name: String
  getName(): String { return this.name }
}
class Salesman extends Employee { }
class Engineer extends Employee { }
```

## FP shape

```
// Before — duplicated functions per variant
const salesmanName = (s: Salesman): String => s.name
const engineerName = (e: Engineer): String => e.name

// After — polymorphic on shared Employee type
type Employee = { name: String }
const getName = (e: Employee): String => e.name

// Subtype values satisfy the constraint
getName(salesman)
getName(engineer)
```

## Smells fixed

- **duplicate-algorithm-variants** — the same method body existing in N sibling classes is the canonical duplication smell; pull-up removes it at the source
- **parallel-inheritance-hierarchy** — when two hierarchies mirror each other method-for-method, pull-up is the tool that collapses the parallel structure
- **shotgun-surgery** — a bug in the shared logic requires N identical fixes across N subclasses; after pull-up, one fix covers all

## Tests implied

- **Per-subclass equivalence** — for each original subclass, assert that calling the method via the superclass type produces the same result as the subclass-owned method did
- **Override not needed** — assert that neither subclass overrides the pulled-up method (unless intentional divergence was known before the refactoring)

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/pullUpMethod.html
