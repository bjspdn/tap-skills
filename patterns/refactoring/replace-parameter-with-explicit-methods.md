---
name: replace-parameter-with-explicit-methods
category: refactoring
aliases: []
intent: >-
  Split a method that switches on a parameter value into separate, explicitly named methods for each case
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/replaceParameterWithExplicitMethods.html
smells_it_fixes:
  - switch-on-type
  - long-conditional-chain
  - unclear-naming
smells_it_introduces:
  - duplicate-algorithm-variants
composes_with:
  - rename-method
  - extract-method
clashes_with:
  - parameterize-method
test_invariants:
  - "Each new explicit method replicates exactly the behavior of the original for its corresponding parameter value"
  - "The original combined method (if retained as a shim) delegates without adding logic"
---

# Replace Parameter with Explicit Methods

## Intent

When a method uses a parameter solely to dispatch between entirely different behaviors — typically via a large conditional or switch — the parameter is acting as a poor-man's method selector. Creating a separate, explicitly named method for each case eliminates the conditional, improves discoverability, and lets the type system prevent invalid parameter values. It is the inverse of Parameterize Method.

## Structure

Before:
```
class Shape {
  setValue(name: String, value: Number): void {
    if (name == "height") this.height = value
    else if (name == "width") this.width = value
    else throw Error("unknown field")
  }
}
```

After:
```
class Shape {
  setHeight(value: Number): void { this.height = value }
  setWidth(value: Number): void  { this.width = value }
}
```

## Applicability

- The parameter is only used to branch between completely different code paths
- The set of valid parameter values is small, closed, and known at compile time
- Type safety is important: illegal values should be rejected at compile time, not runtime
- The behavior for each case is simple enough to merit its own name (avoids over-extraction)

## Consequences

- **Type-safe dispatch** — invalid states are unrepresentable; the wrong method simply doesn't exist
- **Discoverable API** — IDEs enumerate the explicit methods; callers see intent in autocomplete
- **API surface growth** — N cases produce N methods; large N bloats the class interface
- **Harder to extend dynamically** — adding a new case requires a new method; parameterized dispatch would need only a new argument value

## OOP shape

```
// Before
class Employee {
  applyChange(type: ChangeType, amount: Money): void {
    switch (type) {
      case RAISE:      this.salary += amount; break
      case BONUS:      this.bonus  += amount; break
      case DEDUCTION:  this.salary -= amount; break
    }
  }
}

// After
class Employee {
  applyRaise(amount: Money): void      { this.salary += amount }
  applyBonus(amount: Money): void      { this.bonus  += amount }
  applyDeduction(amount: Money): void  { this.salary -= amount }
}
```

## FP shape

```
// Before — dispatches on string tag
const applyChange = (type: string, amount: Money, emp: Employee): Employee => {
  if (type === 'raise')     return { ...emp, salary: emp.salary + amount }
  if (type === 'bonus')     return { ...emp, bonus:  emp.bonus  + amount }
  if (type === 'deduction') return { ...emp, salary: emp.salary - amount }
  throw Error('unknown type')
}

// After — each path is a named function
const applyRaise     = (amount: Money, emp: Employee): Employee =>
  ({ ...emp, salary: emp.salary + amount })
const applyBonus     = (amount: Money, emp: Employee): Employee =>
  ({ ...emp, bonus:  emp.bonus  + amount })
const applyDeduction = (amount: Money, emp: Employee): Employee =>
  ({ ...emp, salary: emp.salary - amount })
```

## Smells fixed

- **switch-on-type** — a `switch` or `if/else` chain that selects behavior based on a string or enum parameter is replaced by dedicated methods, each with a clear name
- **long-conditional-chain** — the dispatch logic is eliminated entirely; conditions collapse into method selection
- **unclear-naming** — the intent of each path is captured in the method name rather than hidden inside a conditional branch

## Tests implied

- **Per-case equivalence** — for each original branch, assert the new explicit method produces the same outcome as calling the original with the corresponding parameter value
- **Invalid-input rejection** — confirm that the original runtime error for unknown parameter values is now prevented at compile time (no such method exists)

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/replaceParameterWithExplicitMethods.html
