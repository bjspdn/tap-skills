---
name: extract-subclass
category: refactoring
aliases: []
intent: >-
  Create a subclass for a cluster of features that is only used by some instances of the class
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/extractSubclass.html
smells_it_fixes:
  - type-code
  - refused-bequest
  - large-class
  - speculative-generality
smells_it_introduces:
  - parallel-inheritance-hierarchy
composes_with:
  - push-down-method
  - push-down-field
  - extract-superclass
clashes_with:
  - replace-inheritance-with-delegation
test_invariants:
  - "Instances of the new subclass behave identically to instances of the original class under the same feature-active conditions"
  - "Instances of the original class that do not use the extracted features are unaffected"
---

# Extract Subclass

## Intent

When a class has features — fields and methods — that are only used by some of its instances, those features likely represent a more specialized concept. Extracting a subclass for that specialization allows the base class to remain focused on the common case while the subclass captures the specialized behavior. It is an alternative to using a type-code flag to gate the specialized behavior.

## Structure

Before:
```
class JobItem {
  unitPrice(): Money
  isLabor(): Boolean
  employee(): Employee  // only relevant when isLabor() == true
}
```

After:
```
class JobItem {
  unitPrice(): Money
}
class LaborItem extends JobItem {
  employee(): Employee
  unitPrice(): Money  // override with labor-specific rate
}
```

## Applicability

- A subset of instances uses a cluster of fields and methods that other instances do not need
- The class contains a type-code flag used to gate the specialized behavior
- The specialization is stable enough to warrant a new type; it is not a fleeting runtime configuration

## Consequences

- **Focused base class** — the base class no longer carries features irrelevant to the general case
- **Type-safe specialization** — the specialization is enforced by the type system rather than a boolean flag
- **Instantiation complexity** — callers must now decide which class to instantiate; a factory method helps
- **Hierarchy depth increases** — adds one level to the inheritance hierarchy; prefer delegation if the specialization is highly dynamic

## OOP shape

```
// Before
class Employee {
  private type: EmployeeType
  private monthlyCost: Money
  private annualCost(): Money { return this.monthlyCost * 12 }
  private managedByBoard: Boolean  // only for managers
  private seniorityLevel: Int      // only for managers
}

// After
class Employee {
  private monthlyCost: Money
  annualCost(): Money { return this.monthlyCost * 12 }
}
class Manager extends Employee {
  private managedByBoard: Boolean
  private seniorityLevel: Int
}
```

## FP shape

```
// Before — variant-specific fields on a union type with flag
type Employee =
  | { kind: 'regular'; monthlyCost: Money }
  | { kind: 'manager'; monthlyCost: Money; seniorityLevel: Int }

// After — discriminated union (FP's subclass equivalent)
type RegularEmployee = { kind: 'regular'; monthlyCost: Money }
type Manager = { kind: 'manager'; monthlyCost: Money; seniorityLevel: Int }
type Employee = RegularEmployee | Manager
```

## Smells fixed

- **type-code** — a boolean or enum flag that gates a cluster of behavior is eliminated; the type system now enforces the distinction
- **refused-bequest** — instances that inherit methods they should never call refuse their bequest; subclass extraction gives each variant only what it needs
- **large-class** — features for a minority of instances bloat the class; subclass extraction moves them to where they belong
- **speculative-generality** — fields set to null or zero for most instances are a signal of misplaced generality; they belong on the specialized subclass

## Tests implied

- **Subclass-specific behavior** — assert that instances of the new subclass return the expected specialized behavior for the extracted features
- **Base class unaffected** — assert that instances of the base class still pass all existing tests and do not expose the extracted features

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/extractSubclass.html
