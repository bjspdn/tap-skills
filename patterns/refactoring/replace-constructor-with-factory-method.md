---
name: replace-constructor-with-factory-method
category: refactoring
aliases: [replace-constructor-with-factory-function]
intent: >-
  Replace a constructor call with a named factory method to communicate intent and decouple callers from concrete types
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/replaceConstructorWithFactoryMethod.html
smells_it_fixes:
  - unclear-naming
  - inappropriate-intimacy
  - type-code
smells_it_introduces:
  - speculative-generality
composes_with:
  - remove-setting-method
  - hide-method
  - extract-subclass
clashes_with: []
test_invariants:
  - "The factory method returns an instance of the expected concrete type for each valid input"
  - "Behavior is identical to direct construction with the same arguments"
---

# Replace Constructor with Factory Method

## Intent

Constructors are tied to a specific class name, cannot return a subtype, and give no hint of intent when there are multiple valid construction modes. A factory method is a named entry point that communicates why an object is being created, can return any subtype, and hides the concrete class from callers. This makes the creation point extensible and self-documenting.

## Structure

Before:
```
employee = new Employee(ENGINEER)
```

After:
```
employee = Employee.createEngineer()
// or: EmployeeFactory.create(EmployeeType.ENGINEER)
```

## Applicability

- The constructor is called with a type code that selects between different configurations or subtypes
- There are multiple semantically distinct ways to create an object that a constructor name cannot convey
- The concrete class should be hidden from callers (e.g. to enable substitution of subtypes)
- You need to return a cached or pooled instance rather than always allocating a new one

## Consequences

- **Named creation intent** — `createFromFile`, `createAnonymous`, `createEngineer` communicate purpose that `new Foo(...)` cannot
- **Subtype flexibility** — the factory can return any subtype; the constructor is locked to one class
- **Caching and pooling** — the factory can return existing instances; constructors always allocate
- **Extra indirection** — one more method in the call chain; IDEs may be slower to navigate to the actual constructor
- **Not a standard language construct** — callers must know to use the factory rather than `new`

## OOP shape

```
// Before — type-code constructor
class Employee {
  constructor(type: EmployeeType) { ... }
}
new Employee(EmployeeType.ENGINEER)

// After — named factory methods
class Employee {
  private constructor(type: EmployeeType) { ... }

  static createEngineer(): Employee  { return new Employee(ENGINEER) }
  static createSalesman(): Employee  { return new Employee(SALESMAN) }
  static createManager(): Employee   { return new Employee(MANAGER) }
}
Employee.createEngineer()
```

## FP shape

```
// Before — constructor-equivalent plain function
const makeEmployee = (type: EmployeeType): Employee => ({ type, ... })

// After — named factory functions per intent
const makeEngineer = (): Employee => makeEmployee(ENGINEER)
const makeSalesman = (): Employee => makeEmployee(SALESMAN)

// Or: factory module
const EmployeeFactory = {
  engineer: (): Employee => ({ type: ENGINEER, ... }),
  salesman: (): Employee => ({ type: SALESMAN, ... }),
}
```

## Smells fixed

- **unclear-naming** — `new Employee(2)` says nothing; `Employee.createManager()` encodes the intent
- **inappropriate-intimacy** — callers that knew which integer code to pass to the constructor no longer need that internal knowledge
- **type-code** — integer or enum type codes passed to constructors are eliminated; the factory method name encodes the type

## Tests implied

- **Correct type returned** — for each factory method, assert the returned instance is of the expected concrete type and has the expected initial state
- **Behavioral equivalence** — assert that `Employee.createEngineer()` produces an object behaviorally identical to `new Employee(ENGINEER)` would have

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/replaceConstructorWithFactoryMethod.html
