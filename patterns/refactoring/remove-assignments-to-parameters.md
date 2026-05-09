---
name: remove-assignments-to-parameters
category: refactoring
aliases: []
intent: >-
  Introduce a local variable for post-entry mutations instead of reassigning an incoming parameter
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/remove-assignments-to-parameters
  - https://refactoring.com/catalog/removeAssignmentsToParameters.html
smells_it_fixes:
  - mutable-shared-state
  - unclear-naming
smells_it_introduces: []
composes_with:
  - split-temporary-variable
  - extract-method
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass after removing the assignment"
  - "The original parameter value is unchanged throughout the method body"
  - "The introduced local variable carries the mutated state with an unambiguous name"
---

# Remove Assignments to Parameters

## Intent

A parameter represents the value the caller passed in. Reassigning it inside the method confuses readers: after the assignment, does the name refer to the caller's value or the new value? The fix is to introduce a new local variable for the mutated value and leave the parameter immutable. In pass-by-reference languages, mutating a parameter can also silently modify the caller's object, making this a correctness concern as well as a readability one.

## Structure

```
before:
  method discount(inputVal, quantity)
    if quantity > 50
      inputVal -= 2        // reassigning the parameter!
    return inputVal * 0.9

after:
  method discount(inputVal, quantity)
    result = inputVal
    if quantity > 50
      result -= 2
    return result * 0.9
```

## Applicability

- A method reassigns a parameter variable (not a mutation of the object the parameter points to — that is a separate concern).
- The parameter's original value is needed later in the method, or the semantics are ambiguous after reassignment.
- The method is a candidate for further extraction, and parameter mutation blocks clean separation.

## Consequences

**Gains**
- The parameter retains its original meaning throughout the method — readers never lose track of what the caller passed.
- Eliminates accidental aliasing bugs in pass-by-reference contexts.
- The local variable can be named to reflect its new role, improving clarity.

**Costs**
- Adds one variable declaration; purely mechanical in impact.

## OOP shape

```
class PriceCalculator
  // Before
  applyDiscount(inputPrice, quantity)
    if quantity > 50
      inputPrice -= 2          // parameter reassigned — confusing
    return inputPrice * taxRate

  // After
  applyDiscount(inputPrice, quantity)
    adjustedPrice = inputPrice   // local variable takes over
    if quantity > 50
      adjustedPrice -= 2
    return adjustedPrice * taxRate
```

## FP shape

```
-- In pure FP, parameters are immutable by construction; this smell cannot occur.
-- In impure/imperative FP style, the equivalent is shadowing a binding:

-- Smell (shadowing with same name, confusing)
applyDiscount inputPrice qty =
  inputPrice = if qty > 50 then inputPrice - 2 else inputPrice  -- rebinding
  inputPrice * taxRate

-- Fixed (new binding, unambiguous)
applyDiscount inputPrice qty =
  let adjustedPrice = if qty > 50 then inputPrice - 2 else inputPrice
  in  adjustedPrice * taxRate
```

## Smells fixed

- **mutable-shared-state** — reassigning a pass-by-reference parameter mutates the caller's object as a hidden side effect; introducing a local variable severs that aliasing.
- **unclear-naming** — after a parameter is reassigned, its name no longer describes what it holds; a new local variable with an appropriate name restores the semantic contract.

## Tests implied

- **Behavior preserved** — the full test suite passes; observable outputs are identical.
- **Parameter immutability** — assert that the original parameter's value is unchanged at any observable point; a test that inspects the caller's value after the call confirms no aliasing occurred.
- **Local variable clarity** — the introduced variable's name correctly describes the mutated value in all branches.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/remove-assignments-to-parameters
- https://refactoring.com/catalog/removeAssignmentsToParameters.html
