---
name: change-bidirectional-association-to-unidirectional
category: refactoring
aliases: [remove-back-pointer]
intent: >-
  Remove one direction of a two-way link when only one end needs to navigate to the other
sources:
  - https://refactoring.guru/change-bidirectional-association-to-unidirectional
  - https://refactoring.com/catalog/changeBidirectionalAssociationToUnidirectional.html
smells_it_fixes:
  - bidirectional-dependency
  - inappropriate-intimacy
  - mutable-shared-state
smells_it_introduces:
  - long-chained-navigation
composes_with:
  - change-unidirectional-association-to-bidirectional
  - remove-middle-man
clashes_with:
  - change-unidirectional-association-to-bidirectional
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the removed back-pointer is never accessed after the refactoring"
  - "the class that lost its pointer can still reach the partner object through the surviving path"
---

# Change Bidirectional Association to Unidirectional

## Intent
Two classes hold references to each other, but only one direction is actually needed. The unused back-pointer creates a coupling and synchronization obligation with no benefit. Remove it. The class that lost its pointer can either accept the partner as a parameter or navigate via the surviving direction. This is the inverse of Change Unidirectional Association to Bidirectional.

## Structure
```
Before:
  Order ↔ Customer
  Order._customer: Customer
  Customer._orders: Set<Order>   ← rarely used

After:
  Order → Customer
  Order._customer: Customer      ← kept
  Customer._orders removed       ← eliminated
```

## Applicability
- One end of a bidirectional association is rarely or never traversed
- The back-pointer was added speculatively and the anticipated queries never materialized
- The dependency cycle between the two classes causes circular-import or layering problems
- Simplifying an object graph to make serialization, cloning, or testing easier

## Consequences
- **Gains**: removes synchronization obligation; eliminates circular dependency; simpler object lifecycle
- **Costs**: the class that lost the pointer must receive it as a parameter or navigate via a longer path when it occasionally needs it

## OOP shape
```
// Before
class Customer
  _orders: Set<Order>   // bidirectional back-pointer

class Order
  _customer: Customer

// After
class Customer
  // _orders removed

class Order
  _customer: Customer

  // When Customer needs to work with its orders,
  // pass the Order collection as a parameter
  static processOrders(customer: Customer, orders: Collection<Order>)
```

## FP shape
```
// Before: both maps
type DB = { order_to_customer, customer_to_orders }

// After: single map
type DB = { order_to_customer: Map<OrderId, CustomerId> }

// When customer's orders are needed, pass them explicitly
process_orders(customer_id, orders: List<Order>) = ...
```

## Smells fixed
- **bidirectional-dependency**: the circular reference between the two classes is broken, enabling independent evolution
- **inappropriate-intimacy**: Customer no longer needs to maintain an internal set of Order references
- **mutable-shared-state**: one fewer shared mutable collection to coordinate on mutation

## Tests implied
- The removed back-pointer is not referenced anywhere after the refactoring — grep confirms no references
- Any code that previously used the back-pointer receives its data via parameter passing or the surviving pointer

## Sources
- https://refactoring.guru/change-bidirectional-association-to-unidirectional
- https://refactoring.com/catalog/changeBidirectionalAssociationToUnidirectional.html
