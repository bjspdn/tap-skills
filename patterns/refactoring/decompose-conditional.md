---
name: decompose-conditional
category: refactoring
aliases: []
intent: >-
  Extract the condition and each branch of a complex conditional into named methods that reveal their intent
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/decompose-conditional
  - https://refactoring.com/catalog/decomposeConditional.html
smells_it_fixes:
  - long-conditional-chain
  - long-method
  - comments-as-deodorant
smells_it_introduces:
  - over-decomposition
composes_with:
  - extract-method
  - extract-variable
  - consolidate-conditional-expression
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass after decomposition"
  - "Each extracted method's name states what the condition or branch means, not how it works"
  - "The calling method reads as a sequence of named decisions, not a wall of boolean logic"
---

# Decompose Conditional

## Intent

Complex conditionals — especially with `if-then-else` blocks that each span multiple lines — hide intent inside syntax. The condition itself may combine several factors; the then-branch and else-branch may be non-obvious computations. Apply Extract Method to the condition, the then-branch, and the else-branch separately, giving each a name that conveys meaning rather than mechanism. The calling code then reads like a policy statement.

## Structure

```
before:
  if date.before(SUMMER_START) || date.after(SUMMER_END)
    charge = quantity * winterRate + winterServiceCharge
  else
    charge = quantity * summerRate

after:
  if isWinter(date)
    charge = winterCharge(quantity)
  else
    charge = summerCharge(quantity)

  method isWinter(date) -> Boolean
    return date.before(SUMMER_START) || date.after(SUMMER_END)

  method winterCharge(quantity) -> Money
    return quantity * winterRate + winterServiceCharge

  method summerCharge(quantity) -> Money
    return quantity * summerRate
```

## Applicability

- An `if` condition combines multiple factors requiring mental parsing.
- The then-branch or else-branch contains non-trivial computation warranting its own name.
- A comment appears before the condition or branches explaining what they do.
- The logic reads better as a policy ("charge for winter") than as a mechanism (compound boolean).

## Consequences

**Gains**
- Calling code reads as an intention-revealing policy rather than a wall of conditionals.
- Each extracted method is individually understandable and testable.
- Comment-as-deodorant patterns disappear — the name is the comment.

**Costs**
- More methods; navigating requires jumping between them.
- Over-applying to trivially simple conditions adds noise rather than clarity.

## OOP shape

```
class BillingCalculator
  // Before
  computeCharge(date, quantity) -> Money
    if date.before(SUMMER_START) || date.after(SUMMER_END)
      return quantity * winterRate + serviceCharge
    else
      return quantity * summerRate

  // After
  computeCharge(date, quantity) -> Money
    if isWinter(date) then return winterCharge(quantity)
    else                   return summerCharge(quantity)

  private isWinter(date) -> Boolean
    return date.before(SUMMER_START) || date.after(SUMMER_END)

  private winterCharge(quantity) -> Money
    return quantity * winterRate + serviceCharge

  private summerCharge(quantity) -> Money
    return quantity * summerRate
```

## FP shape

```
-- Extracted condition and branches as named functions
isWinter     :: Date -> Bool
winterCharge :: Quantity -> Money
summerCharge :: Quantity -> Money

computeCharge :: Date -> Quantity -> Money
computeCharge date qty =
  if isWinter date
    then winterCharge qty
    else summerCharge qty
```

## Smells fixed

- **long-conditional-chain** — a multi-factor boolean condition is replaced by an intention-revealing predicate function.
- **long-method** — branch bodies extracted as methods shrink the containing method to a readable policy statement.
- **comments-as-deodorant** — any comment explaining what the condition or branch does becomes the extracted method's name.

## Tests implied

- **Behavior preserved** — the full test suite passes; decomposition is purely structural.
- **Method name matches intent** — review check: each extracted name makes the conditional readable as prose without consulting the method body.
- **Calling method as policy** — the `if isWinter … else` reads as a business rule, not an implementation detail.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/decompose-conditional
- https://refactoring.com/catalog/decomposeConditional.html
