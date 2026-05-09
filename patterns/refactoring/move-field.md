---
name: move-field
category: refactoring
aliases: [move-attribute]
intent: >-
  Relocate a field to the class that uses it most, so data lives beside the behavior that governs it
sources:
  - https://refactoring.guru/move-field
  - https://refactoring.com/catalog/moveField.html
smells_it_fixes:
  - feature-envy
  - inappropriate-intimacy
  - data-clump
smells_it_introduces:
  - accessor-indirection
composes_with:
  - move-method
  - extract-class
  - self-encapsulate-field
clashes_with:
  - inline-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "every read and write of the field produces identical values after the move"
  - "source class accessors delegate correctly until all references are updated"
---

# Move Field

## Intent
A field is used more by another class than by its own class. Move it there so that data and the behavior operating on it are collocated. This is a companion to Move Method and together they pull a coherent cluster of responsibilities into a single class.

## Structure
```
Before:
  ClassA
    field: T          ← only read by ClassB methods

  ClassB
    uses ClassA.field repeatedly

After:
  ClassA
    (field removed or delegated)

  ClassB
    field: T          ← owns its data
```

## Applicability
- A field is accessed more from outside its class than from within
- A class is being extracted and the field belongs with the extracted behavior
- Reducing the information one class must know about another
- Data-clump members that travel together should live in the same type

## Consequences
- **Gains**: receiving class becomes more self-contained; coupling between source and receiver decreases
- **Costs**: source class may need a delegation accessor during the transition; call sites referencing the old location must be updated

## OOP shape
```
// Before
class Customer
  discountRate: Decimal

class Order
  method charge(): Money
    return amount * (1 - customer.discountRate)

// After
class Order
  discountRate: Decimal     ← moved here

class Customer
  // discountRate removed or kept as delegating getter
  get discountRate(): Decimal
    return orders.current.discountRate
```

## FP shape
```
// Before: customer record carries discount_rate
type Customer = { id, name, discount_rate }
charge(order, customer) = order.amount * (1 - customer.discount_rate)

// After: order record carries discount_rate
type Order = { id, amount, discount_rate }
charge(order) = order.amount * (1 - order.discount_rate)
```

## Smells fixed
- **feature-envy**: behavior that reaches across class boundaries for data now finds that data locally
- **inappropriate-intimacy**: the source class no longer exposes an internal field to satisfy a foreign consumer
- **data-clump**: fields that always move together can be relocated to the same type, exposing the clump

## Tests implied
- Every accessor of the original field returns the same value after the move — test all read paths
- Every mutator of the original field produces the same side effects — test all write paths

## Sources
- https://refactoring.guru/move-field
- https://refactoring.com/catalog/moveField.html
