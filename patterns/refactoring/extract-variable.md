---
name: extract-variable
category: refactoring
aliases: [introduce-explaining-variable, extract-explaining-variable]
intent: >-
  Assign a complex expression to a well-named temporary variable to make the expression's purpose visible
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/extract-variable
  - https://refactoring.com/catalog/extractVariable.html
smells_it_fixes:
  - comments-as-deodorant
  - unclear-naming
  - long-conditional-chain
smells_it_introduces:
  - long-method
composes_with:
  - extract-method
  - replace-temp-with-query
  - decompose-conditional
clashes_with:
  - inline-variable
test_invariants:
  - "Behavior preserved — all existing tests still pass after extraction"
  - "Variable name makes the intent of the expression unambiguous without a comment"
---

# Extract Variable

## Intent

When an expression is hard to understand at a glance — a complex conditional, a chained computation, or a magic number — assign it to a local variable whose name explains what it represents. This is the smallest scope of explanation: the name lives inside the method. If the same expression appears in multiple methods, prefer Extract Method instead, which makes the name reusable across the class.

## Structure

```
before:
  if (order.quantity > 100 && order.itemPrice > 200) ||
     order.employee.isManager()
    giveDiscount(order)

after:
  isLargeOrder     = order.quantity > 100 && order.itemPrice > 200
  isManagedAccount = order.employee.isManager()
  if isLargeOrder || isManagedAccount
    giveDiscount(order)
```

## Applicability

- An expression is long or nested enough that a reader must pause to decode it.
- A value is computed once but referenced in nearby lines without a clear label.
- A conditional guard mixes several concerns and comments are being added to explain parts of it.
- As a stepping stone: extract a variable first, then promote it to a query method via Replace Temp With Query.

## Consequences

**Gains**
- Adds readable labels to opaque expressions — comments-as-deodorant disappear.
- Aids debugging: the intermediate value can be inspected in a debugger.
- Makes the intent of conditionals immediately clear.

**Costs**
- Increases line count of the method; too many explained variables make a method longer without reducing it.
- Scope is local: if the same expression appears elsewhere, duplication remains. Extract Method is the broader fix.

## OOP shape

```
method applyPricing(order)
  // Before: everything inline
  if (order.qty > 100 && order.price > 200) || order.emp.isManager()
    discount = 0.1

  // After: expressions named
  isHighVolume    = order.qty > 100 && order.price > 200
  isManagerBuyer  = order.emp.isManager()
  qualifiesForDiscount = isHighVolume || isManagerBuyer
  if qualifiesForDiscount
    discount = 0.1
```

## FP shape

```
// Let-binding is the FP equivalent of an explaining variable
applyPricing :: Order -> Discount
applyPricing(order) =
  let isHighVolume   = order.qty > 100 && order.price > 200
      isManagerBuyer = order.emp.isManager
      qualifies      = isHighVolume || isManagerBuyer
  in  if qualifies then Discount 0.1 else NoDiscount
```

## Smells fixed

- **comments-as-deodorant** — a comment like `// check if large order` above a boolean expression should be the variable's name, not a comment.
- **unclear-naming** — magic numbers and raw boolean expressions get semantically meaningful labels.
- **long-conditional-chain** — a multi-clause condition split into named sub-expressions reads as logic rather than syntax.

## Tests implied

- **Behavior preserved** — the full test suite passes; the extraction is purely cosmetic to the runtime.
- **Variable name unambiguous** — code review check: can a new reader understand the guard without consulting surrounding context?

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/extract-variable
- https://refactoring.com/catalog/extractVariable.html
