---
name: inline-variable
category: refactoring
aliases: [inline-temp, inline-explaining-variable]
intent: >-
  Replace a temporary variable that is assigned once with the expression it holds when the variable name adds no clarity
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/inline-temp
  - https://refactoring.com/catalog/inlineVariable.html
smells_it_fixes:
  - over-decomposition
  - speculative-generality
smells_it_introduces: []
composes_with:
  - inline-method
  - replace-temp-with-query
clashes_with:
  - extract-variable
test_invariants:
  - "Behavior preserved — all existing tests still pass after inlining"
  - "Inlined expression is simple enough that the reader needs no intermediate label"
---

# Inline Variable

## Intent

A temporary variable assigned once and used once in a simple expression is often noise. Inlining it directly into its single use site removes the variable without reducing readability — provided the expression itself is short and clear. Inline Variable is the inverse of Extract Variable and is most often applied as a preparatory step before Extract Method or Inline Method.

## Structure

```
before:
  basePrice = order.basePrice()
  return basePrice > 1000

after:
  return order.basePrice() > 1000
```

## Applicability

- A temporary variable is assigned a single expression and used exactly once.
- The expression is short and clear enough to be understood at the use site without a label.
- The variable is blocking another refactoring — for example, Inline Method cannot proceed while a temp holds the method's return value.
- The variable was introduced as an explain-variable but the method has since been renamed so the context is already clear.

## Consequences

**Gains**
- Removes a one-assignment, one-use variable that contributes no explanatory value.
- Enables further refactoring (especially Inline Method).
- Reduces declared-variable count, shortening the method.

**Costs**
- If the expression is non-trivial, inlining makes the use site harder to read — Extract Variable was the right move in the first place.
- Duplication risk if the variable was preventing the same expression from being typed multiple times.

## OOP shape

```
method isExpensive(order) -> Boolean
  // Before
  basePrice = order.basePrice()
  return basePrice > 1000

  // After
  return order.basePrice() > 1000
```

## FP shape

```
-- Before
isExpensive :: Order -> Bool
isExpensive order =
  let basePrice = orderBasePrice order
  in  basePrice > 1000

-- After
isExpensive :: Order -> Bool
isExpensive order = orderBasePrice order > 1000
```

## Smells fixed

- **over-decomposition** — a temp that was introduced "for clarity" but names something already obvious from the expression is clutter; inlining cleans it up.
- **speculative-generality** — a variable created in anticipation of reuse that never came to pass.

## Tests implied

- **Behavior preserved** — run the full test suite; the inlined expression must produce identical results.
- **Expression simplicity** — the inlined expression should be evaluable by a reader in a single glance; if it requires a double-take, revert and keep the variable.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/inline-temp
- https://refactoring.com/catalog/inlineVariable.html
