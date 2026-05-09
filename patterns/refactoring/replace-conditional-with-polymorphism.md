---
name: replace-conditional-with-polymorphism
category: refactoring
aliases: []
intent: >-
  Move each conditional branch into an overriding method on a subclass or type-case variant, eliminating the switch/if chain
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/replace-conditional-with-polymorphism
  - https://refactoring.com/catalog/replaceConditionalWithPolymorphism.html
smells_it_fixes:
  - switch-on-type
  - long-conditional-chain
  - duplicate-algorithm-variants
  - shotgun-surgery
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - strategy
  - factory-method
  - extract-method
clashes_with:
  - replace-nested-conditional-with-guard-clauses
test_invariants:
  - "Behavior preserved — all existing tests still pass after replacing the conditional"
  - "Each subclass/variant handles exactly the case that its corresponding branch handled"
  - "The base method contains no remaining conditional that discriminates on type"
---

# Replace Conditional With Polymorphism

## Intent

A conditional that switches on an object's type or category to select different behavior is a sign that the varying behavior belongs in the objects themselves. Move each branch into an overriding method on the appropriate subclass. The caller then invokes the method polymorphically, eliminating the conditional entirely. Adding new cases becomes adding a new subclass rather than editing a conditional — a structural improvement in the Open/Closed sense.

## Structure

```
before:
  method getSpeed(bird) -> Number
    switch bird.type
      case EUROPEAN:      return baseSpeed()
      case AFRICAN:       return baseSpeed() - loadFactor() * bird.numberOfCoconuts
      case NORWEGIAN_BLUE: return bird.isNailed ? 0 : baseSpeed() * bird.voltage * 0.9

after:
  abstract class Bird
    abstract getSpeed() -> Number
    baseSpeed() -> Number  // shared

  class EuropeanBird extends Bird
    getSpeed() -> Number   return baseSpeed()

  class AfricanBird extends Bird
    getSpeed() -> Number   return baseSpeed() - loadFactor() * numberOfCoconuts

  class NorwegianBlueBird extends Bird
    getSpeed() -> Number   return isNailed ? 0 : baseSpeed() * voltage * 0.9
```

## Applicability

- A conditional checks the type or category of an object and performs different actions for each case.
- The same switch/if chain appears in multiple methods — each is a separate site for the same type-discriminating logic.
- New types are expected in the future, and each addition currently requires editing every conditional site.
- The varying behavior is inherent to the object's identity, not contextual caller behavior.

## Consequences

**Gains**
- Eliminates type-dispatching conditionals entirely.
- Adding a new case requires a new class, not editing existing code (Open/Closed Principle).
- Each variant's behavior is encapsulated in one place.
- Reduces shotgun-surgery: when behavior changes for one type, exactly one class changes.

**Costs**
- Introduces a class hierarchy — overkill if there are only two cases or if the hierarchy will not grow.
- Factory infrastructure is needed to instantiate the correct subclass.
- Deep inheritance hierarchies can obscure behavior; prefer Strategy (composition) when the behavior is a policy rather than identity.

## OOP shape

```
// Before: dispatcher method
class Bird
  getSpeed() -> Number
    switch this.type
      case PARROT:  return parrotSpeed()
      case SWALLOW: return swallowSpeed()
      // more cases…

// After: polymorphic dispatch
abstract class Bird
  abstract getSpeed() -> Number

class Parrot extends Bird
  getSpeed() -> Number  // parrot-specific logic

class Swallow extends Bird
  getSpeed() -> Number  // swallow-specific logic

// Caller: no change needed — polymorphic dispatch is transparent
bird.getSpeed()
```

## FP shape

```
-- FP equivalent: pattern match on a tagged union / sum type
data Bird = Parrot ParrotData | Swallow SwallowData | NorwegianBlue NorwegianData

getSpeed :: Bird -> Speed
getSpeed (Parrot d)       = parrotSpeed d
getSpeed (Swallow d)      = swallowSpeed d
getSpeed (NorwegianBlue d) = norwegianSpeed d

-- Adding a new bird: add a new constructor and a new clause — analogous to adding a subclass.
-- Exhaustiveness checking replaces runtime type errors.
```

## Smells fixed

- **switch-on-type** — a `switch bird.type` or `if type == X … else if type == Y` chain is the canonical trigger for this refactoring.
- **long-conditional-chain** — each branch dispatches to type-specific behavior; moving it into the type itself eliminates the chain.
- **duplicate-algorithm-variants** — the same switch appears in multiple methods; after polymorphism, each variant's behavior lives once in its class.
- **shotgun-surgery** — adding a new type currently requires editing every switch; after polymorphism, only one new class is needed.

## Tests implied

- **Behavior preserved** — the full test suite passes; each subclass/variant produces the result its original branch produced.
- **Type-case parity** — for each former branch, there is a corresponding subclass whose `getSpeed()` (or equivalent) returns an identical value given the same inputs.
- **No residual conditional** — the base class or calling code contains no `if/switch` discriminating on type; static analysis or review confirms this.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/replace-conditional-with-polymorphism
- https://refactoring.com/catalog/replaceConditionalWithPolymorphism.html
