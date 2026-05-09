---
name: change-value-to-reference
category: refactoring
aliases: [value-to-shared-reference]
intent: >-
  Convert a value object to a reference object so that multiple owners share one instance with consistent identity
sources:
  - https://refactoring.guru/change-value-to-reference
  - https://refactoring.com/catalog/changeValueToReference.html
smells_it_fixes:
  - mutable-shared-state
  - data-clump
  - duplicate-algorithm-variants
smells_it_introduces:
  - temporal-coupling
  - shared-mutable-identity
composes_with:
  - replace-data-value-with-object
  - change-reference-to-value
clashes_with:
  - change-reference-to-value
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "all entities referencing the same logical object hold the same instance"
  - "mutation of the shared object is visible to all holders simultaneously"
---

# Change Value to Reference

## Intent
Multiple copies of what should be the same object exist independently. When one copy is updated, others don't reflect the change. Convert the value object to a reference object — stored once in a registry or factory — so all holders share a single instance. This is the inverse of Change Reference to Value.

## Structure
```
Before:
  Order A → Customer("Acme")    ← copy
  Order B → Customer("Acme")    ← separate copy
  // updating one does not affect the other

After:
  customerRegistry["Acme"] → Customer("Acme")   ← one instance
  Order A → ref to registry["Acme"]
  Order B → ref to registry["Acme"]
```

## Applicability
- The same real-world entity appears as independent copies that can drift out of sync
- Multiple objects must share a mutable entity and see the same current state
- An entity has identity that transcends its attribute values (same customer across many orders)
- Preparing for persistence where entity identity is managed by a store

## Consequences
- **Gains**: consistent state — all holders always see current data; identity is explicit
- **Costs**: lifecycle management becomes necessary; shared mutable state is harder to reason about; requires a registry or factory

## OOP shape
```
class CustomerRegistry
  private store: Map<String, Customer>

  getOrCreate(name: String): Customer
    if not store.contains(name)
      store[name] = Customer(name)
    return store[name]

class Order
  customer: Customer    ← reference, not copy
  constructor(customerName: String, registry: CustomerRegistry)
    customer = registry.getOrCreate(customerName)
```

## FP shape
```
// FP equivalent: shared mutable cell managed by an atom/ref
type CustomerRef = Ref<Customer>

customer_registry: Map<String, CustomerRef> = mutable({})

get_customer(name) =
  match map_get(customer_registry, name) with
  | Some(ref) -> ref
  | None ->
    ref = atom(make_customer(name))
    map_set(customer_registry, name, ref)
    ref

// Holders deref the atom to read; update! to mutate
```

## Smells fixed
- **mutable-shared-state**: duplicated copies are collapsed to one reference, so state changes propagate consistently
- **data-clump**: the same customer data scattered across many order copies is unified in a single authoritative instance
- **duplicate-algorithm-variants**: logic applied to each copy redundantly is applied once to the shared instance

## Tests implied
- Mutating the shared object through one holder is immediately visible to all other holders
- A factory/registry never creates two distinct instances for the same logical identity

## Sources
- https://refactoring.guru/change-value-to-reference
- https://refactoring.com/catalog/changeValueToReference.html
