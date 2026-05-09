---
name: replace-method-with-method-object
category: refactoring
aliases: [extract-method-object]
intent: >-
  Turn a large method with many local variables into its own class where locals become fields and sub-steps become methods
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/replace-method-with-method-object
  - https://refactoring.com/catalog/replaceMethodWithMethodObject.html
smells_it_fixes:
  - long-method
  - long-parameter-list
  - mutable-shared-state
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - extract-method
  - replace-temp-with-query
  - strategy
clashes_with:
  - inline-method
test_invariants:
  - "Behavior preserved — all existing tests still pass after extracting the method object"
  - "The method object's compute() entry point returns exactly what the original method returned"
  - "Locals that were temps are now fields initialized in the constructor or compute()"
---

# Replace Method With Method Object

## Intent

When a long method has so many local variables that Extract Method cannot cleanly separate sub-steps — because they all share the same pool of temps — move the entire method into a new class. The parameters and local variables become fields; the sub-steps become private methods. This unlocks Extract Method on the new class's methods without parameter lists growing unmanageable, since all shared state is on `this`.

## Structure

```
before:
  class Account
    gamma(inputVal, quantity, yearToDate) -> Number
      importantValue1 = (inputVal * quantity) + delta()
      importantValue2 = (inputVal * yearToDate) + 100
      if yearToDate - importantValue1 > 100
        importantValue2 -= 20
      importantValue3 = importantValue2 * 7
      return importantValue3 - 2 * importantValue1

after:
  class Account
    gamma(inputVal, quantity, yearToDate) -> Number
      return GammaCalculation(this, inputVal, quantity, yearToDate).compute()

  class GammaCalculation
    account, inputVal, quantity, yearToDate  // former params
    importantValue1, importantValue2, importantValue3  // former locals

    constructor(account, inputVal, quantity, yearToDate)
      // assign all fields

    compute() -> Number
      importantValue1 = (inputVal * quantity) + account.delta()
      importantValue2 = (inputVal * yearToDate) + 100
      adjustImportantValue2()
      importantValue3 = importantValue2 * 7
      return importantValue3 - 2 * importantValue1

    private adjustImportantValue2()
      if yearToDate - importantValue1 > 100
        importantValue2 -= 20
```

## Applicability

- A method is too long and deeply entangled with local variables to decompose via Extract Method alone.
- Many local variables prevent clean extraction because every candidate sub-method would need them all as parameters.
- The computation has clear sub-phases that would benefit from individual naming and testability.
- The algorithm is complex enough to warrant its own lifecycle (e.g., strategy variant, command pattern).

## Consequences

**Gains**
- Unlocks Extract Method on the method object: shared state is on `this`, no parameter explosion.
- The computation's phases become named, independently testable methods.
- Enables polymorphism on the computation via Strategy or Template Method.

**Costs**
- Introduces a new class for a single operation — may feel like over-engineering for a simple method.
- The method object class has no identity beyond hosting the computation; it is essentially a closure made explicit.
- Callers and tests that stub or mock the original method need to account for the new indirection.

## OOP shape

```
// Original class delegates
class OriginalClass
  complexMethod(a, b, c) -> Result
    return MethodObject(this, a, b, c).compute()

// New method-object class
class MethodObject
  origin: OriginalClass
  a, b, c: InputType
  x, y, z: IntermediateType   // former local variables

  constructor(origin, a, b, c)
    // assign all fields; initialize intermediates to zero/null

  compute() -> Result
    phaseOne()
    phaseTwo()
    return combine()

  private phaseOne()
    x = a * b + origin.helperValue()

  private phaseTwo()
    y = b * c - x
    if y > threshold then z = adjust(y)

  private combine() -> Result
    return x + y + z
```

## FP shape

```
-- FP equivalent: a record capturing all shared state, passed through a pipeline
type MethodState = { origin: Origin, a: A, b: B, c: C, x: X, y: Y, z: Z }

complexMethod :: Origin -> A -> B -> C -> Result
complexMethod origin a b c =
  initialState origin a b c
    |> phaseOne
    |> phaseTwo
    |> combine

initialState :: Origin -> A -> B -> C -> MethodState
phaseOne     :: MethodState -> MethodState
phaseTwo     :: MethodState -> MethodState
combine      :: MethodState -> Result
```

## Smells fixed

- **long-method** — a method too large to decompose is turned into a class where each phase is a small, named method.
- **long-parameter-list** — extracting sub-methods from a long method creates many-parameter helpers; method-object eliminates those parameters by making them fields.
- **mutable-shared-state** — local variables shared across deeply nested branches become explicit, named fields whose lifecycle is clear.

## Tests implied

- **Behavior preserved** — the full test suite passes; the original method's return value is reproduced exactly by `compute()`.
- **Entry-point equivalence** — given identical inputs, `MethodObject(origin, a, b, c).compute()` == `origin.complexMethod(a, b, c)`.
- **Temps-as-fields** — assert that all intermediate values that were formerly temps are now accessible (at least to tests) as named fields after `compute()` runs, enabling fine-grained inspection.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/replace-method-with-method-object
- https://refactoring.com/catalog/replaceMethodWithMethodObject.html
