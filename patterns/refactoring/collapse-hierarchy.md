---
name: collapse-hierarchy
category: refactoring
aliases: []
intent: >-
  Merge a superclass and subclass that are no longer different enough to justify a two-level hierarchy
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/collapseHierarchy.html
smells_it_fixes:
  - speculative-generality
  - parallel-inheritance-hierarchy
smells_it_introduces:
  - large-class
composes_with:
  - pull-up-method
  - pull-up-field
clashes_with:
  - extract-superclass
  - extract-subclass
test_invariants:
  - "All behavior present in both classes is available on the merged class"
  - "All call sites that used either the superclass or subclass type compile against the merged class"
---

# Collapse Hierarchy

## Intent

As a codebase evolves, subclasses can become so similar to their parent that the distinction no longer carries its weight. A hierarchy with too little differentiation adds conceptual overhead for no benefit. Collapsing the subclass into the superclass (or vice versa) removes the unnecessary level, simplifies the type model, and reduces the number of classes a reader must understand.

## Structure

Before:
```
class Employee { name: String; rate: Money }
class SalariedEmployee extends Employee { }  // adds nothing
```

After:
```
class Employee { name: String; rate: Money }
```

## Applicability

- A subclass has no fields or methods beyond what it inherits from the parent
- The subclass was created speculatively for a distinction that never materialized
- A previous refactoring (e.g. Pull Up Method, Pull Up Field) has moved everything to the superclass, leaving the subclass empty

## Consequences

- **Simpler type model** — one fewer class for readers and tools to track
- **Call-site impact** — references to the eliminated class type must be updated to the surviving class; may be a breaking change for external APIs
- **Direction choice** — collapse toward the superclass (keep the name) or toward the subclass (keep the subclass name); choose the name that best communicates the concept
- **Behavior preserved** — no logic changes; purely structural

## OOP shape

```
// Before
class Party {
  protected name: String
  annualCost(): Money { ... }
}
class ActiveParty extends Party {
  // no additional fields or methods — subclass is vacuous
}

// After — collapse subclass into parent
class Party {
  protected name: String
  annualCost(): Money { ... }
}
// ActiveParty eliminated; all references updated to Party
```

## FP shape

```
// Before — unnecessary type alias / thin wrapper
type Employee = { name: String; rate: Money }
type SalariedEmployee = Employee  // structural duplicate

// After — single type
type Employee = { name: String; rate: Money }
```

## Smells fixed

- **speculative-generality** — a subclass created "in case we need different behavior later" that never diverged is pure speculation; collapsing it removes the pretense
- **parallel-inheritance-hierarchy** — when two hierarchies mirror each other and one level in each is vacuous, collapsing the empty level reduces the parallel structure

## Tests implied

- **Behavioral completeness** — assert that the merged class passes all tests that previously applied to both the superclass and the subclass
- **No lost behavior** — confirm via diff that no method or field present on the eliminated class was absent from the surviving class before the merge

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/collapseHierarchy.html
