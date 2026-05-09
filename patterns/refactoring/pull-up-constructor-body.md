---
name: pull-up-constructor-body
category: refactoring
aliases: []
intent: >-
  Move common constructor initialization code from subclass constructors into a superclass constructor
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/pullUpConstructorBody.html
smells_it_fixes:
  - duplicate-algorithm-variants
smells_it_introduces:
  - large-class
composes_with:
  - pull-up-field
  - pull-up-method
clashes_with: []
test_invariants:
  - "Each subclass instance is initialized to the same state after construction as before the refactoring"
  - "The superclass constructor call (super) is the first statement in each subclass constructor"
---

# Pull Up Constructor Body

## Intent

When subclass constructors share initialization code, that code is duplicated in the same way as any other method body. Because constructors cannot be simply pulled up the same way methods can (due to language constraints on `super()` calls and initialization order), the common initialization is moved into the superclass constructor and invoked via `super()`. Subclass constructors then contain only the initialization that is truly specific to them.

## Structure

Before:
```
class Manager extends Employee {
  constructor(name, id, grade) {
    this.name = name
    this.id = id
    this.grade = grade
  }
}
class Salesman extends Employee {
  constructor(name, id) {
    this.name = name
    this.id = id
  }
}
```

After:
```
class Employee {
  constructor(name, id) {
    this.name = name
    this.id = id
  }
}
class Manager extends Employee {
  constructor(name, id, grade) {
    super(name, id)
    this.grade = grade
  }
}
class Salesman extends Employee {
  constructor(name, id) {
    super(name, id)
  }
}
```

## Applicability

- Two or more subclass constructors begin with identical or near-identical initialization statements
- The shared initialization involves fields that have already been pulled up to the superclass
- The language supports calling a superclass constructor explicitly (`super()`)

## Consequences

- **Eliminated constructor duplication** — common initialization lives in one place; adding a new field to the shared set requires one change
- **Enforced initialization order** — `super()` is mandated as the first call, making initialization sequence explicit
- **Superclass constructor signature grows** — parameters for pulled-up fields must be threaded through subclass constructors to the `super()` call
- **Subclass constructors simplify** — after pulling up the common parts, subclass constructors contain only subclass-specific initialization

## OOP shape

```
// Before
class Engineer extends Employee {
  constructor(name: String, id: EmployeeId, skill: String) {
    this.name = name      // duplicated
    this.id   = id        // duplicated
    this.skill = skill
  }
}

// After
class Employee {
  constructor(name: String, id: EmployeeId) {
    this.name = name
    this.id   = id
  }
}
class Engineer extends Employee {
  constructor(name: String, id: EmployeeId, skill: String) {
    super(name, id)
    this.skill = skill
  }
}
```

## FP shape

```
// Before — duplicated base-field initialization per factory
const makeEngineer = (name: String, id: Id, skill: String): Engineer =>
  ({ name, id, skill })
const makeSalesman = (name: String, id: Id, quota: Money): Salesman =>
  ({ name, id, quota })

// After — shared base constructor composed in
const makeEmployee = (name: String, id: Id): Employee => ({ name, id })
const makeEngineer = (name: String, id: Id, skill: String): Engineer =>
  ({ ...makeEmployee(name, id), skill })
const makeSalesman = (name: String, id: Id, quota: Money): Salesman =>
  ({ ...makeEmployee(name, id), quota })
```

## Smells fixed

- **duplicate-algorithm-variants** — identical initialization statements copy-pasted across subclass constructors are collapsed into the superclass constructor, which is the single authoritative source for common initialization logic

## Tests implied

- **Post-construction state** — assert that each subclass instance has the same value for shared fields after construction as it did before the pull-up
- **Subclass-specific state intact** — assert that subclass-specific fields (e.g. `grade`, `skill`) are correctly initialized by the remaining subclass-specific constructor code

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/pullUpConstructorBody.html
