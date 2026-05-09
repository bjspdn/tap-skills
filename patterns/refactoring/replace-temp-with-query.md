---
name: replace-temp-with-query
category: refactoring
aliases: []
intent: >-
  Replace a temporary variable that holds a computed value with a call to a query method computing that value
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/replace-temp-with-query
  - https://refactoring.com/catalog/replaceTempWithQuery.html
smells_it_fixes:
  - long-method
  - duplicate-code
  - mutable-shared-state
smells_it_introduces:
  - repeated-computation
composes_with:
  - extract-method
  - extract-variable
  - replace-method-with-method-object
clashes_with:
  - inline-variable
test_invariants:
  - "Behavior preserved — all existing tests still pass after replacement"
  - "Query method is pure — same inputs always return same result with no side effects"
  - "Every former use of the temp produces identical results when replaced by the query call"
---

# Replace Temp With Query

## Intent

A local variable that holds the result of an expression is private to its method, making the computed value invisible to subclasses and other methods. Extracting the expression into a query method makes it available everywhere in the class and opens it to overriding in subclasses. This refactoring is a prerequisite for Extract Method when the temp is referenced in the block you want to extract — eliminating the temp eliminates a parameter.

## Structure

```
before:
  method getPrice() -> Money
    basePrice = quantity * unitPrice
    if basePrice > 1000
      return basePrice * 0.95
    else
      return basePrice * 0.98

after:
  method getPrice() -> Money
    if basePrice() > 1000
      return basePrice() * 0.95
    else
      return basePrice() * 0.98

  method basePrice() -> Money
    return quantity * unitPrice
```

## Applicability

- A temp is assigned exactly once from a pure expression and is used only as a read-only value.
- The expression could be useful to subclasses or other methods on the class.
- The temp is blocking an Extract Method because multiple fragments reference it.
- You want to eliminate complex method signatures by removing parameter-passing of computed values.

## Consequences

**Gains**
- Makes the computed value accessible to subclasses and other methods — avoids duplication across methods.
- Simplifies Extract Method by removing the need to pass temps as parameters.
- Query methods are independently testable.

**Costs**
- Adds overhead if the expression is expensive and called repeatedly — memoise or cache if needed.
- If the expression has side effects, this refactoring is unsafe; the expression must be pure.
- Introduces a method call where a field lookup existed — minor readability change in the caller.

## OOP shape

```
class Order
  quantity: Integer
  unitPrice: Money

  // Before
  getPrice() -> Money
    basePrice = quantity * unitPrice
    discountFactor = basePrice > 1000 ? 0.95 : 0.98
    return basePrice * discountFactor

  // After
  getPrice() -> Money
    return basePrice() * discountFactor()

  basePrice() -> Money
    return quantity * unitPrice

  discountFactor() -> Float
    return basePrice() > 1000 ? 0.95 : 0.98
```

## FP shape

```
-- Before: let-binding holds computation
getPrice :: Order -> Money
getPrice order =
  let base   = order.quantity * order.unitPrice
      factor = if base > 1000 then 0.95 else 0.98
  in  base * factor

-- After: named functions replace let-bindings
basePrice :: Order -> Money
basePrice order = order.quantity * order.unitPrice

discountFactor :: Order -> Float
discountFactor order = if basePrice order > 1000 then 0.95 else 0.98

getPrice :: Order -> Money
getPrice order = basePrice order * discountFactor order
```

## Smells fixed

- **long-method** — a method crowded with temp declarations shrinks once computations move to query methods.
- **duplicate-code** — the same expression computed in multiple methods is extracted once and shared.
- **mutable-shared-state** — a temp that was updated in multiple branches is replaced by a pure, side-effect-free query.

## Tests implied

- **Behavior preserved** — the full test suite passes; the query method must reproduce the temp's value in every case.
- **Pure query** — assert the query method has no observable side effects; calling it twice produces the same result.
- **Identical results at every use** — for each former reference to the temp, assert the query call returns the same value.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/replace-temp-with-query
- https://refactoring.com/catalog/replaceTempWithQuery.html
