---
name: introduce-null-object
category: refactoring
aliases: [null-object-pattern]
intent: >-
  Replace null checks with a no-op object that implements the expected interface with safe default behaviour
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/introduce-null-object
  - https://refactoring.com/catalog/introduceSpecialCase.html
smells_it_fixes:
  - long-conditional-chain
  - duplicate-error-handling
  - primitive-obsession
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - replace-conditional-with-polymorphism
  - factory-method
  - strategy
clashes_with:
  - replace-nested-conditional-with-guard-clauses
test_invariants:
  - "Behavior preserved — all existing tests still pass after introducing the null object"
  - "Null object implements every method of the interface with safe, no-op or default-value behaviour"
  - "All former null-check sites are eliminated — no null reference is passed to callers"
---

# Introduce Null Object

## Intent

Repeated null checks for the same object type scatter defensive conditionals throughout the codebase. Each check is a branching point that handles the "no object" case separately from the normal case. Introduce a Null Object: a class that implements the same interface but provides safe, do-nothing or default-value implementations. Callers receive the null object instead of null and need no conditional — all calls are safe. This is a special case of Replace Conditional With Polymorphism where the "absent" case becomes a first-class object.

## Structure

```
before:
  customer = site.getCustomer()
  if customer == null
    plan = BillingPlan.basic()
  else
    plan = customer.getPlan()

  if customer == null
    name = "occupant"
  else
    name = customer.getName()

after:
  // NullCustomer implements Customer with safe defaults
  customer = site.getCustomer()   // returns NullCustomer instead of null
  plan = customer.getPlan()        // NullCustomer.getPlan() → BillingPlan.basic()
  name = customer.getName()        // NullCustomer.getName() → "occupant"
```

## Applicability

- The same null check for the same type is repeated in multiple places across the codebase.
- The null case has a consistent default behaviour that can be encoded in one place.
- You want to eliminate null as a return value from a factory or repository, returning a typed "absent" object instead.
- The collaboration with the object is read-only or produces side-effect-free defaults (mutation via a null object can be surprising).

## Consequences

**Gains**
- Eliminates all null guards for the target type — callers treat "present" and "absent" uniformly.
- Encapsulates the default/absent behavior in one tested class.
- Consistent with the Open/Closed Principle: adding new "absent" behaviours requires a new class, not editing every call site.

**Costs**
- The null object makes it harder to detect truly erroneous "absent" situations — errors can silently propagate as no-ops.
- Every method on the interface must have a sensible default; complex interfaces may be hard to provide a null object for.
- Introduces a class whose existence may surprise developers unfamiliar with the pattern.

## OOP shape

```
interface Customer
  getName()  -> String
  getPlan()  -> BillingPlan
  isNull()   -> Boolean

class RealCustomer implements Customer
  getName()  -> String       // actual name
  getPlan()  -> BillingPlan  // actual plan
  isNull()   -> Boolean      return false

class NullCustomer implements Customer
  getName()  -> String       return "occupant"
  getPlan()  -> BillingPlan  return BillingPlan.basic()
  isNull()   -> Boolean      return true

class CustomerRepository
  find(id) -> Customer
    result = db.lookup(id)
    return result ?? NullCustomer()   // never return null
```

## FP shape

```
-- FP equivalent: Maybe / Option type makes absence explicit in the type
-- Null Object pattern = a default value of the same type collapsed via fold/fromMaybe

type Customer = { name: String, plan: BillingPlan }
nullCustomer :: Customer
nullCustomer = { name = "occupant", plan = BillingPlan.basic }

getCustomer :: SiteId -> Maybe Customer
resolveCustomer :: SiteId -> Customer
resolveCustomer id = fromMaybe nullCustomer (getCustomer id)
-- Callers use resolveCustomer and never deal with absence
```

## Smells fixed

- **long-conditional-chain** — a chain of `if customer == null … else …` checks is replaced by uniform method calls on an always-valid object.
- **duplicate-error-handling** — the same "handle missing customer" logic duplicated across methods is consolidated into `NullCustomer`'s method bodies.
- **primitive-obsession** — `null` is a primitive sentinel; a typed Null Object is a proper domain concept.

## Tests implied

- **Behavior preserved** — the full test suite passes; callers that formerly handled null now receive the null object and produce identical observable results.
- **Null object safety** — test every method of the null object in isolation: each returns the expected safe default and produces no exception.
- **No null at call sites** — assert that no caller of the factory/repository ever receives a null reference; the return type is always non-null.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/introduce-null-object
- https://refactoring.com/catalog/introduceSpecialCase.html
