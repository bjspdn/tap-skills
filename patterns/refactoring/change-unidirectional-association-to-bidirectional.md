---
name: change-unidirectional-association-to-bidirectional
category: refactoring
aliases: [add-back-pointer]
intent: >-
  Add a reverse pointer to a one-way association when both ends need to navigate to each other
sources:
  - https://refactoring.guru/change-unidirectional-association-to-bidirectional
  - https://refactoring.com/catalog/changeUnidirectionalAssociationToBidirectional.html
smells_it_fixes:
  - feature-envy
  - inappropriate-intimacy
  - long-chained-navigation
smells_it_introduces:
  - synchronization-coupling
  - bidirectional-dependency
composes_with:
  - change-bidirectional-association-to-unidirectional
  - hide-delegate
clashes_with:
  - change-bidirectional-association-to-unidirectional
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "back-pointer and forward-pointer are always consistent: navigating both directions reaches the correct objects"
  - "adding or removing the association updates both ends atomically"
---

# Change Unidirectional Association to Bidirectional

## Intent
Class A knows about Class B, but B frequently needs to navigate back to A. B is forced to query or search to find its A, creating roundabout code. Add a back-pointer from B to A and keep both references consistent. This is the inverse of Change Bidirectional Association to Unidirectional.

## Structure
```
Before:
  Order → Customer      ← one-way
  Customer has no direct reference to its Orders

After:
  Order ↔ Customer      ← bidirectional
  Order._customer: Customer
  Customer._orders: Set<Order>
  // both maintained in sync
```

## Applicability
- The class at the non-referencing end frequently needs to find its partner, causing navigation overhead
- Queries from B to A are common and performance of a linear search is unacceptable
- The relationship is conceptually bidirectional but was originally implemented unidirectionally
- Adding the back-pointer is simpler than caching the result via another mechanism

## Consequences
- **Gains**: direct navigation in both directions; eliminates search overhead
- **Costs**: both ends must be kept in sync whenever the association changes; creates a bidirectional dependency between the two classes

## OOP shape
```
class Order
  private _customer: Customer

  setCustomer(c: Customer)
    if _customer != null
      _customer._orders.remove(self)
    _customer = c
    if c != null
      c._orders.add(self)

class Customer
  _orders: Set<Order>       // back-pointer added

  addOrder(o: Order)
    o.setCustomer(self)     // delegate to Order to maintain consistency
```

## FP shape
```
// FP approach: maintain two maps in a shared state atom
type AssociationDB = {
  order_to_customer: Map<OrderId, CustomerId>,
  customer_to_orders: Map<CustomerId, Set<OrderId>>
}

assign_customer(db, order_id, customer_id) =
  db
  |> set_order_customer(order_id, customer_id)
  |> add_customer_order(customer_id, order_id)
```

## Smells fixed
- **feature-envy**: code that navigated from B back to A through external queries is replaced by direct access
- **inappropriate-intimacy**: roundabout navigation accessing third-party structures is eliminated
- **long-chained-navigation**: multi-hop traversal to find the partner is replaced by a single pointer

## Tests implied
- After assigning an Order to a Customer, `customer.orders` contains that Order and `order.customer` is that Customer
- After removing the association, neither end retains a stale reference

## Sources
- https://refactoring.guru/change-unidirectional-association-to-bidirectional
- https://refactoring.com/catalog/changeUnidirectionalAssociationToBidirectional.html
