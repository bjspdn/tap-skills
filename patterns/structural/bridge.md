---
name: bridge
category: structural
aliases: [handle-body]
intent: >-
  Decouple an abstraction from its implementation so that the two can vary independently
sources:
  - https://refactoring.guru/design-patterns/bridge
smells_it_fixes:
  - god-class
  - divergent-change
  - shotgun-surgery
  - long-conditional-chain
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
composes_with:
  - abstract-factory
  - strategy
  - adapter
clashes_with:
  - template-method
test_invariants:
  - "Abstraction delegates all implementation work to its Implementor — no logic duplicated across both hierarchies"
  - "Abstraction and Implementor hierarchies vary independently — adding a new Implementor requires no change to Abstraction subclasses"
  - "Client depends only on the Abstraction interface, never on a concrete Implementor"
  - "Switching Implementors at runtime leaves Abstraction state consistent"
---

# Bridge

## Intent

Bridge separates an abstraction (what something does) from its implementation (how it does it) into two independent class hierarchies linked by composition. Unlike inheritance — which permanently binds abstraction and implementation — Bridge lets you swap or extend either side without touching the other. The typical trigger is a Cartesian-product class explosion caused by two orthogonal dimensions of variation.

## Structure

```
Client
  |
Abstraction ──────────────> «interface» Implementor
  + operation()                + operationImpl()
  - impl: Implementor               ▲
       ▲                   ┌────────┴────────┐
  RefinedAbstraction   ConcreteImplA    ConcreteImplB
  + feature()
```

Roles:
- **Abstraction** — high-level control layer; holds reference to Implementor
- **RefinedAbstraction** — extends Abstraction with additional operations
- **Implementor** — interface for low-level platform/technology operations
- **ConcreteImplementor** — platform-specific implementation of Implementor

## Applicability

- You want to avoid a permanent binding between abstraction and implementation (e.g., to switch at runtime).
- Both abstraction and implementation should be extensible via subclassing, independently.
- Changes to the implementation should not affect client code.
- You face a class explosion from combining two orthogonal dimensions (e.g., Shape × RenderingEngine).

## Consequences

**Gains**
- Eliminates combinatorial class explosion from two independent variation axes.
- Open/Closed: extend either hierarchy without modifying the other.
- Implementation details hidden from client; can be swapped at runtime.

**Costs**
- Introduces indirection; harder to trace control flow.
- Overkill when one of the two dimensions has only one variant.
- Initial design requires correct identification of the two orthogonal axes.

## OOP shape

```
interface Implementor
  operationImpl(data): Result

class ConcreteImplA implements Implementor
  operationImpl(data): Result  // platform A

class ConcreteImplB implements Implementor
  operationImpl(data): Result  // platform B

abstract class Abstraction
  constructor(impl: Implementor)
  operation(): Result
    return this.impl.operationImpl(this.prepare())
  abstract prepare(): Data

class RefinedAbstraction extends Abstraction
  feature(): Result
    // orchestrates via this.impl
```

## FP shape

```
// Implementor = function type
type Impl = Data -> Result

// Abstraction = higher-order function closed over impl
makeAbstraction :: Impl -> (Input -> Result)
makeAbstraction(impl) =
  input -> impl(prepare(input))

// Concrete impls
implA: Impl = data -> ...
implB: Impl = data -> ...

// Compose
absWithA = makeAbstraction(implA)
absWithB = makeAbstraction(implB)
```

## Smells fixed

- **god-class** — a single class handling both high-level orchestration and low-level platform details is split along the abstraction/implementation axis.
- **divergent-change** — changes to the rendering engine no longer touch the shape hierarchy and vice versa.
- **shotgun-surgery** — adding a new platform no longer requires editing every abstraction subclass.
- **long-conditional-chain** — `if platform == X` branches inside abstraction methods are replaced by polymorphic dispatch to the Implementor.

## Tests implied

- **No logic duplication** — assert that Abstraction's `operation` contains no platform-specific branching; all variation lives in ConcreteImplementors.
- **Independent extension** — add a new ConcreteImplementor, verify all existing Abstraction tests pass without change.
- **Client isolation** — confirm client module imports no concrete Implementor type.
- **Runtime swap** — inject ImplA, capture output; swap to ImplB, confirm Abstraction's orchestration logic is unchanged (only results differ per impl contract).

## Sources

- https://refactoring.guru/design-patterns/bridge
