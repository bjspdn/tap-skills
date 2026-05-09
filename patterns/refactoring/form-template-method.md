---
name: form-template-method
category: refactoring
aliases: [template-method-refactoring]
intent: >-
  Unify similar algorithms in subclasses by extracting the common skeleton into the superclass and leaving the differing steps as abstract methods
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/formTemplateMethod.html
smells_it_fixes:
  - duplicate-algorithm-variants
  - parallel-inheritance-hierarchy
  - shotgun-surgery
smells_it_introduces:
  - speculative-generality
composes_with:
  - pull-up-method
  - extract-method
clashes_with:
  - replace-inheritance-with-delegation
test_invariants:
  - "Each subclass produces the same overall result from the template method as it did from its original standalone method"
  - "The abstract step methods in each subclass are called in the order the template method defines"
---

# Form Template Method

## Intent

When subclass methods follow the same overall algorithm but differ in specific steps, the algorithm skeleton is duplicated while only the steps vary. The Template Method pattern addresses this by moving the skeleton into the superclass as a concrete method that calls abstract hook methods. Each subclass then overrides only the steps that differ. Form Template Method is the refactoring that introduces this structure from existing duplication.

## Structure

Before:
```
class ResidentialStatement {
  statement(): String {
    // header
    // charge loop
    // footer — different from commercial
  }
}
class CommercialStatement {
  statement(): String {
    // header
    // charge loop — different from residential
    // footer — different from residential
  }
}
```

After:
```
abstract class Statement {
  statement(): String {     // template method — skeleton on superclass
    return header() + chargeLoop() + footer()
  }
  abstract header(): String
  abstract chargeLoop(): String
  abstract footer(): String
}
class ResidentialStatement extends Statement { ... }
class CommercialStatement extends Statement { ... }
```

## Applicability

- Two or more subclass methods implement the same algorithm but differ in one or more steps
- The steps that differ can be cleanly identified and extracted as discrete units
- The algorithm's overall sequence is invariant across all subclasses
- Single-inheritance is not a constraint (for multi-inheritance scenarios, consider Extract Interface + delegation)

## Consequences

- **Eliminated skeleton duplication** — the algorithm structure lives in one place; changes to the sequence require one edit
- **Clear variation points** — abstract methods name and document exactly where subclasses are expected to differ
- **Inheritance coupling** — subclasses are tightly bound to the superclass's algorithm skeleton; changing the skeleton may break all subclasses
- **Hollywood Principle** — the superclass calls subclass methods; the inversion of control can be surprising to new readers

## OOP shape

```
// Before
class GermanOrder {
  price(): Money {
    base = quantity * unitPrice
    tax  = base * 0.19
    return base + tax
  }
}
class USOrder {
  price(): Money {
    base     = quantity * unitPrice
    discount = largeOrderDiscount(quantity)
    tax      = (base - discount) * 0.08
    return base - discount + tax
  }
}

// After
abstract class Order {
  price(): Money {          // template method
    base = this.basePrice()
    return base - this.discount(base) + this.tax(base)
  }
  abstract basePrice(): Money
  abstract discount(base: Money): Money
  abstract tax(base: Money): Money
}
```

## FP shape

```
// Before — two near-identical functions
const germanPrice = (q: Int, unitPrice: Money): Money => ...
const usPrice     = (q: Int, unitPrice: Money): Money => ...

// After — higher-order template function
type PriceSteps = {
  basePrice: (q: Int, up: Money) => Money
  discount:  (base: Money) => Money
  tax:       (base: Money) => Money
}
const priceTemplate = (steps: PriceSteps) => (q: Int, up: Money): Money => {
  base = steps.basePrice(q, up)
  return base - steps.discount(base) + steps.tax(base)
}

const germanPrice = priceTemplate({ basePrice: ..., discount: _ => 0, tax: base => base * 0.19 })
const usPrice     = priceTemplate({ basePrice: ..., discount: largeOrderDiscount, tax: base => base * 0.08 })
```

## Smells fixed

- **duplicate-algorithm-variants** — the algorithm skeleton duplicated across subclasses is collapsed into one template method; only genuinely different steps remain per subclass
- **parallel-inheritance-hierarchy** — when two hierarchies mirror each other method-for-method with near-identical algorithms, form-template-method collapses the parallel skeleton
- **shotgun-surgery** — a change to the algorithm structure requires edits in N subclasses; after applying this refactoring, only the superclass skeleton needs to change

## Tests implied

- **Per-subclass equivalence** — assert that each subclass's `statement()` (or equivalent) returns the same result via the template method as it did from its original standalone implementation
- **Step invocation order** — assert that the abstract steps are invoked in the sequence the template method specifies (use spies or order-sensitive assertions)

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/formTemplateMethod.html
