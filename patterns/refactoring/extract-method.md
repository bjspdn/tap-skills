---
name: extract-method
category: refactoring
aliases: [extract-function]
intent: >-
  Pull a code fragment into its own named method/function to improve readability and enable reuse
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/extract-method
  - https://refactoring.com/catalog/extractFunction.html
smells_it_fixes:
  - long-method
  - comments-as-deodorant
  - duplicate-code
  - unclear-naming
smells_it_introduces:
  - over-decomposition
composes_with:
  - extract-class
  - replace-temp-with-query
  - replace-method-with-method-object
clashes_with:
  - inline-method
test_invariants:
  - "Behavior preserved — all existing tests still pass after extraction"
  - "Extracted method has a single clear responsibility expressible in its name"
  - "No variables leak out of the extracted method that did not exist before"
---

# Extract Method

## Intent

When a code fragment is too long, does too many things, or requires a comment to explain what it does, move it into its own method with a name that reveals its intention. The caller becomes shorter and more readable; the extracted method becomes independently testable and reusable. This is the most frequently applied refactoring in Fowler's catalog and underlies almost every other composing-method technique.

## Structure

```
before:
  method doSomething(order)
    // validate order
    if order.amount < 0 then error
    if order.customer == null then error
    // calculate total
    base = order.amount * pricePerUnit
    discount = computeDiscount(order.customer)
    total = base - discount
    print(total)

after:
  method doSomething(order)
    validateOrder(order)
    total = calculateTotal(order)
    print(total)

  method validateOrder(order)
    if order.amount < 0 then error
    if order.customer == null then error

  method calculateTotal(order) -> Money
    base = order.amount * pricePerUnit
    discount = computeDiscount(order.customer)
    return base - discount
```

## Applicability

- A method is too long to read in one glance (more than ~10 lines is a signal).
- A code block is preceded by a comment explaining what it does — the comment title becomes the method name.
- The same fragment appears in two or more methods (deduplication via extraction).
- A block of code can be meaningfully named at a higher level of abstraction than its individual statements.

## Consequences

**Gains**
- Dramatically improves readability; the calling method reads like a prose outline.
- Enables reuse without duplication.
- Extracted method is independently testable at a fine-grained level.
- Enables further refactorings: the extracted method may itself be a candidate for moving to another class.

**Costs**
- If over-applied, produces a "method forest" of tiny, context-free methods that are hard to navigate.
- Passing many local variables as parameters creates long parameter lists — a signal to consider `replace-method-with-method-object` instead.
- Shallow call stacks become deeper; debuggers show more frames.

## OOP shape

```
class OrderProcessor
  // Before: all logic inline
  processOrder(order)
    // many lines…

  // After: extraction
  processOrder(order)
    validateOrder(order)
    total = calculateTotal(order)
    finalizeOrder(order, total)

  private validateOrder(order)
    // extracted validation logic

  private calculateTotal(order) -> Money
    // extracted calculation logic

  private finalizeOrder(order, total)
    // extracted finalization logic
```

## FP shape

```
// Extract as a named function; semantics identical to OOP extraction
processOrder :: Order -> Result
processOrder(order) =
  validateOrder(order) >>= order ->
  calculateTotal(order) >>= total ->
  finalizeOrder(order, total)

validateOrder :: Order -> Validated Order
calculateTotal :: Order -> Money
finalizeOrder  :: Order -> Money -> Result
```

## Smells fixed

- **long-method** — breaking a large method into named steps removes length and cognitive load simultaneously.
- **comments-as-deodorant** — when the only purpose of a comment is to name a block, that name belongs on a method instead.
- **duplicate-code** — a fragment appearing in multiple callsites is extracted once and called everywhere.
- **unclear-naming** — forcing a fragment into a named method demands a clear, intentional name, surfacing murky responsibility.

## Tests implied

- **Behavior preserved** — run the full test suite before and after; zero regressions permitted. This is the non-negotiable invariant of any behavior-preserving refactoring.
- **Single responsibility** — assert the extracted method's name matches its observable behavior; if you need "and" or "or" in the name, split further.
- **No variable leakage** — verify that no previously-local state is now exposed as public fields or returned unnecessarily.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/extract-method
- https://refactoring.com/catalog/extractFunction.html
