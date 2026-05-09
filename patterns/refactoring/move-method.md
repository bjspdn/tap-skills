---
name: move-method
category: refactoring
aliases: [move-function]
intent: >-
  Move a method to the class that uses it most, eliminating feature envy and placing behavior with its data
sources:
  - https://refactoring.guru/move-method
  - https://refactoring.com/catalog/moveFunction.html
smells_it_fixes:
  - feature-envy
  - inappropriate-intimacy
  - divergent-change
smells_it_introduces:
  - scattered-delegation
composes_with:
  - extract-method
  - extract-class
  - move-field
clashes_with:
  - inline-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "method's observable output is identical at every call site after move"
  - "no new coupling is created between source and target class"
---

# Move Method

## Intent
A method lives in a class other than the one that owns the data it operates on. Move the method to the class it gravitates toward. This reduces feature envy, tightens cohesion in the receiving class, and loosens unnecessary coupling in the source class.

## Structure
```
Before:
  ClassA
    methodX()        ← uses ClassB fields heavily
      ClassB.field1
      ClassB.field2

After:
  ClassA
    methodX() → delegates or is removed

  ClassB
    methodX()        ← owns its own data
```

## Applicability
- The method references more features of another class than its own class
- The method's logic is only comprehensible in the context of another class
- Reducing coupling between two closely coupled classes
- Preparing for Extract Class by moving behavior first

## Consequences
- **Gains**: higher cohesion in receiving class; fewer cross-class references; source class becomes smaller
- **Costs**: call sites in source class may need delegation wrappers or direct reference updates; can scatter responsibility if applied too liberally

## OOP shape
```
// Before
class Order
  method discountedPrice(customer: Customer): Money
    if customer.membershipLevel == GOLD then ...
    if customer.purchaseHistory.size > 10 then ...

// After
class Customer
  method discountedPrice(order: Order): Money
    if self.membershipLevel == GOLD then ...
    if self.purchaseHistory.size > 10 then ...

class Order
  method discountedPrice(): Money
    return customer.discountedPrice(self)   // optional delegation
```

## FP shape
```
// Move the function to the module that owns the data
// Before: in order_module
discount_price(customer, order) -> money

// After: in customer_module
discount_price(customer, order) -> money
// order_module re-exports or removes its version
```

## Smells fixed
- **feature-envy**: the method was reaching into another object's internals; after the move it works on data it owns
- **inappropriate-intimacy**: source class no longer requires deep knowledge of target class internals
- **divergent-change**: change reasons for the method are now collocated with the class that changes for the same reasons

## Tests implied
- All call sites produce the same results before and after the move — exercise every call path
- No new dependency cycle is introduced between source and target modules

## Sources
- https://refactoring.guru/move-method
- https://refactoring.com/catalog/moveFunction.html
