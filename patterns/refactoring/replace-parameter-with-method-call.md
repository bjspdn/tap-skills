---
name: replace-parameter-with-method-call
category: refactoring
aliases: [replace-parameter-with-method]
intent: >-
  Remove a parameter by having the method invoke the computation itself instead of receiving the result
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/replaceParameterWithMethodCall.html
smells_it_fixes:
  - long-parameter-list
  - repeated-param-threading
smells_it_introduces:
  - feature-envy
composes_with:
  - remove-parameter
  - preserve-whole-object
clashes_with:
  - add-parameter
test_invariants:
  - "Behavior is identical: the value the caller computed and passed is the same value the method now computes internally"
  - "The removed parameter was not used to influence control flow at the call site"
---

# Replace Parameter with Method Call

## Intent

When a caller computes a value and passes it to a method that could equally well compute that value itself, the parameter is unnecessary indirection. Removing the parameter and moving the computation inside the method shortens the caller's signature and eliminates the caller's obligation to understand how to produce the value. The method becomes more self-contained.

## Structure

Before:
```
basePrice = quantity * itemPrice
discount  = getDiscount(quantity, itemPrice)
shipping  = getShipping(quantity, basePrice)
price     = getPrice(basePrice, discount, shipping)
```

After:
```
price = getPrice(quantity, itemPrice)
// getPrice computes basePrice, discount, shipping internally
```

## Applicability

- The value passed as a parameter can be computed entirely from information the receiving method already has access to
- The computation is not expensive or side-effectful
- The caller does not use the computed value for anything other than passing it in

## Consequences

- **Shorter call signatures** — callers need to supply less data
- **Encapsulated computation** — the derivation logic moves to one authoritative location
- **Reduced flexibility** — callers that legitimately need to supply different computed values can no longer do so; if that flexibility is needed, keep the parameter
- **Potential hidden coupling** — the method now internally calls other methods; its dependency graph widens

## OOP shape

```
// Before
class Order {
  getPrice(basePrice: Money, discount: Discount, shipping: Money): Money { ... }
}
// Caller
order.getPrice(order.basePrice(), order.discount(), order.shipping())

// After
class Order {
  getPrice(): Money {
    base     = this.basePrice()
    discount = this.discount()
    shipping = this.shipping()
    return base - discount + shipping
  }
}
// Caller
order.getPrice()
```

## FP shape

```
// Before — caller must assemble inputs
const getPrice = (basePrice: Money, discount: Money, shipping: Money): Money =>
  basePrice - discount + shipping

// Caller
getPrice(basePrice(order), discount(order), shipping(order))

// After — method composes sub-computations
const getPrice = (order: Order): Money =>
  basePrice(order) - discount(order) + shipping(order)

getPrice(order)
```

## Smells fixed

- **long-parameter-list** — derived values that can be computed from existing state are no longer threaded through the call chain as explicit arguments
- **repeated-param-threading** — a value computed at the top of a call chain and passed down through several layers can be eliminated if a deeper method can compute it directly

## Tests implied

- **Behavioral identity** — assert that for the same order state, `getPrice()` after refactoring returns the same value as `getPrice(basePrice, discount, shipping)` did before
- **Parameter is not missing** — confirm the removed parameter is not needed for any caller-side use; its value should be fully reproducible from the receiver's own state

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/replaceParameterWithMethodCall.html
