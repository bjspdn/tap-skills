---
name: inline-method
category: refactoring
aliases: [inline-function]
intent: >-
  Replace a method call with the method body when the method's name adds no clarity over its content
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/inline-method
  - https://refactoring.com/catalog/inlineFunction.html
smells_it_fixes:
  - speculative-generality
  - over-decomposition
  - unclear-naming
smells_it_introduces:
  - long-method
  - duplicate-code
composes_with:
  - extract-method
  - replace-method-with-method-object
clashes_with:
  - extract-method
test_invariants:
  - "Behavior preserved — all existing tests still pass after inlining"
  - "Calling sites produce identical observable outputs before and after"
---

# Inline Method

## Intent

Sometimes a method body is as clear as its name, or more so — the indirection adds no value. Inline Method is the inverse of Extract Method: copy the method body back into each call site and remove the method. This is also a useful preparatory step before a larger restructuring, such as moving logic to a different class or merging a small helper back into a method-object.

## Structure

```
before:
  method getRating(driver) -> Integer
    return moreThanFiveLateDeliveries(driver) ? 2 : 1

  method moreThanFiveLateDeliveries(driver) -> Boolean
    return driver.numberOfLateDeliveries > 5

after:
  method getRating(driver) -> Integer
    return (driver.numberOfLateDeliveries > 5) ? 2 : 1
```

## Applicability

- A method's body is as self-explanatory as its name, making the call an unnecessary hop.
- A method was extracted prematurely and its name no longer reveals useful intent.
- You are about to reorganise a group of methods and want to clear indirect delegation first.
- A class has too many small delegating methods making the call graph hard to follow.

## Consequences

**Gains**
- Removes meaningless indirection; the logic is visible at the call site.
- Simplifies the class interface when the extracted method was too implementation-specific.
- Reduces the method count, making the class easier to scan.

**Costs**
- If the inlined body is non-trivial and called in many places, duplication creeps back.
- Inlining a method used by more than one caller requires repeating the body everywhere — prefer Extract Method on the result if the body is still complex.
- Inlining into a recursive method is unsafe without careful analysis.

## OOP shape

```
class Rater
  // Before
  getRating(driver) -> Integer
    return moreThanFiveLateDeliveries(driver) ? 2 : 1

  private moreThanFiveLateDeliveries(driver) -> Boolean
    return driver.lateDeliveries > 5

  // After
  getRating(driver) -> Integer
    return (driver.lateDeliveries > 5) ? 2 : 1
  // moreThanFiveLateDeliveries removed
```

## FP shape

```
// Before
getRating :: Driver -> Int
getRating(d) = if moreThanFiveLate(d) then 2 else 1

moreThanFiveLate :: Driver -> Bool
moreThanFiveLate(d) = d.lateDeliveries > 5

// After — predicate inlined, helper removed
getRating :: Driver -> Int
getRating(d) = if d.lateDeliveries > 5 then 2 else 1
```

## Smells fixed

- **speculative-generality** — a helper method extracted "just in case" but never reused is noise; inlining removes the dead abstraction.
- **over-decomposition** — a method forest where single-line delegators obscure the actual logic is simplified by inlining trivial helpers.
- **unclear-naming** — a helper whose name is no clearer than the expression it wraps is better removed.

## Tests implied

- **Behavior preserved** — run the full test suite before and after; identical results required at every call site.
- **Identical observable outputs** — if tests use return-value assertions or spy on side effects, verify each call site independently before removing the method.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/inline-method
- https://refactoring.com/catalog/inlineFunction.html
