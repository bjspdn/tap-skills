---
name: separate-query-from-modifier
category: refactoring
aliases: [command-query-separation]
intent: >-
  Split a method that both returns a value and changes state into a pure query and a void modifier
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/separateQueryFromModifier.html
smells_it_fixes:
  - side-effect-in-query
  - temporal-coupling
  - mutable-shared-state
smells_it_introduces:
  - repeated-param-threading
composes_with:
  - rename-method
  - remove-setting-method
clashes_with: []
test_invariants:
  - "Queries are pure: calling a query method never changes observable state"
  - "Modifiers return void: calling a modifier never returns a meaningful value"
  - "Calling query then modifier produces the same observable result as the original combined call"
---

# Separate Query from Modifier

## Intent

A method that both answers a question and changes state violates the Command-Query Separation principle. It is impossible to call the method safely in read-only contexts and its side effects are invisible at the call site. Splitting the method into a pure query (no side effects, returns a value) and a void modifier (changes state, returns nothing) makes each responsibility explicit and composable.

## Structure

Before:
```
class SecuritySystem {
  checkAndArmAlarm(): AlertLevel  // returns level AND arms the alarm
}
```

After:
```
class SecuritySystem {
  alertLevel(): AlertLevel        // pure query
  armAlarm(): void                // void modifier
}

// Caller:
level = system.alertLevel()
system.armAlarm()
```

## Applicability

- A method returns a value but also has a non-trivial side effect (state change, I/O, notification)
- The method is called in read-only contexts such as assertions, logging, or conditional expressions where the side effect fires unexpectedly
- Testing the query result is difficult because calling the method changes the system under test

## Consequences

- **Referential transparency for queries** — pure queries can be called multiple times, memoized, or parallelized without concern
- **Explicit mutations** — all state changes are confined to named modifier methods, making mutation visible at call sites
- **Slightly more verbose callers** — two calls replace one; callers must explicitly sequence the query and modifier
- **Race condition window** — in concurrent code, the gap between query and modifier may allow interleaved mutations; requires external synchronization

## OOP shape

```
// Before
class Cart {
  removeItem(id: ItemId): Price {  // removes item AND returns new total
    this.items.remove(id)
    return this.total()
  }
}

// After
class Cart {
  total(): Price {                 // pure query
    return this.items.sum()
  }
  removeItem(id: ItemId): void {   // void modifier
    this.items.remove(id)
  }
}
```

## FP shape

```
// Before — function with hidden side effect
const removeItem = (cart: Cart, id: ItemId): Price => {
  mutate(cart, id)          // side effect
  return computeTotal(cart) // query
}

// After — pure computation separated from effect
const total = (cart: Cart): Price =>
  cart.items.reduce((sum, item) => sum + item.price, 0)

const removeItem = (cart: Cart, id: ItemId): Cart =>
  { ...cart, items: cart.items.filter(i => i.id !== id) }

// Caller chains explicitly
const newCart = removeItem(cart, id)
const newTotal = total(newCart)
```

## Smells fixed

- **side-effect-in-query** — a method that appears to be a getter but silently mutates state causes surprising behavior when called in logging, assertions, or watch expressions
- **temporal-coupling** — callers that need both the state change and the value are forced to call in a specific order; separation makes the sequence explicit
- **mutable-shared-state** — isolating all mutations to void modifiers makes it easier to audit every state-changing path in the codebase

## Tests implied

- **Queries are pure** — call the query method N times in succession; assert the return value is identical and no observable state changes between calls
- **Modifiers return void** — confirm the modifier's return type is void/unit and that its effect is measurable via a subsequent query call
- **Composed equivalence** — a sequence of `query(); modifier()` produces the same net state as the original combined method

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/separateQueryFromModifier.html
