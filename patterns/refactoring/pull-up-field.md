---
name: pull-up-field
category: refactoring
aliases: []
intent: >-
  Move a field that appears identically in two or more subclasses up to the common superclass
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/pullUpField.html
smells_it_fixes:
  - duplicate-algorithm-variants
  - parallel-inheritance-hierarchy
smells_it_introduces:
  - large-class
composes_with:
  - pull-up-method
  - pull-up-constructor-body
clashes_with:
  - push-down-field
test_invariants:
  - "Both subclasses read and write the field identically after it moves to the superclass"
  - "No subclass-specific initialization logic was accidentally merged during the pull-up"
---

# Pull Up Field

## Intent

When two or more subclasses declare the same field independently, the duplication implies the field belongs at a higher abstraction level. Moving it to the superclass eliminates the duplicate declarations and makes the shared data visible to all subclasses through a single, authoritative definition. It is a prerequisite for Pull Up Method when the method references the duplicated field.

## Structure

Before:
```
class Salesman extends Employee { private name: String }
class Engineer extends Employee { private name: String }
```

After:
```
class Employee {
  protected name: String
}
class Salesman extends Employee { }
class Engineer extends Employee { }
```

## Applicability

- Two or more sibling subclasses declare a field with the same name and the same type
- The field serves the same conceptual purpose in each subclass
- No subclass assigns the field a meaningfully different default or initialization strategy

## Consequences

- **Eliminated duplication** — one field declaration replaces N identical ones
- **Enables further pull-ups** — methods in subclasses that reference the field can now be pulled up as well
- **Superclass grows** — the superclass accumulates state; over-eager pull-ups can produce a God Class
- **Visibility may need widening** — private fields must become protected or package-scoped when moved to the superclass

## OOP shape

```
// Before
class Salesman extends Employee {
  private name: String
  private quota: Money
}
class Engineer extends Employee {
  private name: String
  private skill: String
}

// After
class Employee {
  protected name: String  // pulled up
}
class Salesman extends Employee {
  private quota: Money
}
class Engineer extends Employee {
  private skill: String
}
```

## FP shape

```
// Before — duplicated fields in separate record types
type Salesman = { name: String; quota: Money }
type Engineer = { name: String; skill: String }

// After — shared base record via intersection or extension
type Employee = { name: String }
type Salesman = Employee & { quota: Money }
type Engineer = Employee & { skill: String }
```

## Smells fixed

- **duplicate-algorithm-variants** — identical field declarations in sibling classes are a structural form of copy-paste duplication; pulling them up removes the redundancy
- **parallel-inheritance-hierarchy** — when two hierarchies mirror each other field-for-field, pulling up shared fields is the first step toward collapsing the parallel structure

## Tests implied

- **Field accessible from superclass** — assert that instances of each subclass expose the field through the superclass reference type without casting
- **No initialization regression** — assert that the field's value after construction equals the value it had before the pull-up for each subclass

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/pullUpField.html
