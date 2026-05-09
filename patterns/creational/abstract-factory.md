---
name: abstract-factory
category: creational
aliases: [kit]
intent: >-
  Provide an interface for creating families of related objects without specifying their concrete classes
sources:
  - https://refactoring.guru/design-patterns/abstract-factory
smells_it_fixes:
  - switch-on-type
  - long-conditional-chain
  - inappropriate-intimacy
  - scattered-platform-variants
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - factory-method
  - singleton
  - prototype
clashes_with: []
test_invariants:
  - "All products returned by one factory belong to the same family and are mutually compatible"
  - "Client code depends only on abstract factory and product interfaces, never on concrete classes"
  - "Swapping one concrete factory for another produces a complete, self-consistent product family"
  - "No factory method on AbstractFactory is left unimplemented in any concrete factory"
---

# Abstract Factory

## Intent

Abstract Factory provides an interface for producing families of related or dependent objects without specifying their concrete classes. A concrete factory encapsulates the choice of product family; the client works exclusively through the abstract interfaces. This guarantees that products from one factory are always compatible with each other, while keeping the client ignorant of which family is in use.

## Structure

```
<<interface>> AbstractFactory
  + createProductA() : AbstractProductA
  + createProductB() : AbstractProductB

ConcreteFactory1 implements AbstractFactory
  + createProductA() : ProductA1
  + createProductB() : ProductB1

ConcreteFactory2 implements AbstractFactory
  + createProductA() : ProductA2
  + createProductB() : ProductB2

<<interface>> AbstractProductA
ProductA1 implements AbstractProductA
ProductA2 implements AbstractProductA

<<interface>> AbstractProductB
ProductB1 implements AbstractProductB
ProductB2 implements AbstractProductB

Client
  - factory : AbstractFactory
  uses AbstractProductA, AbstractProductB
```

## Applicability

- A system must be independent of how its products are created and composed.
- A system must work with multiple families of products, one family at a time.
- You want to enforce that products from the same family are always used together.
- You are building a library and want to reveal only interfaces, not implementations.

## Consequences

**Gains**
- Compatibility guarantee: products from the same factory are always a coherent family.
- Isolates concrete classes from client code.
- Easy family substitution: swap the factory object to switch the entire product suite.
- Supports Open/Closed for new families (add a factory subclass without touching existing code).

**Costs**
- Adding a new product kind requires changes to AbstractFactory and every concrete factory.
- Large interface surface: even if a client only needs one product, the full factory must be implemented.
- Can feel heavy-handed when only one family will ever exist.

## OOP shape

```
interface AbstractFactory
  method createButton() : Button
  method createCheckbox() : Checkbox

interface Button
  method render() : void

interface Checkbox
  method render() : void

class MacFactory implements AbstractFactory
  method createButton() : Button  → return MacButton()
  method createCheckbox() : Checkbox  → return MacCheckbox()

class WinFactory implements AbstractFactory
  method createButton() : Button  → return WinButton()
  method createCheckbox() : Checkbox  → return WinCheckbox()

class Application
  constructor(factory: AbstractFactory)
    this.button = factory.createButton()
    this.checkbox = factory.createCheckbox()
```

## FP shape

An abstract factory maps to a record/struct of factory functions, one per product kind. A concrete factory is a value of that record type.

```
type UIFactory = {
  createButton  : () => Button
  createCheckbox: () => Checkbox
}

macFactory : UIFactory = {
  createButton   = () => makeMacButton()
  createCheckbox = () => makeMacCheckbox()
}

winFactory : UIFactory = {
  createButton   = () => makeWinButton()
  createCheckbox = () => makeWinCheckbox()
}

function buildApp(factory: UIFactory) : App
  button   = factory.createButton()
  checkbox = factory.createCheckbox()
  ...
```

## Smells fixed

- **switch-on-type** — Branching on a platform/theme tag to select which widget class to build is eliminated; the factory object carries the family choice.
- **long-conditional-chain** — Nested conditionals choosing among product variants collapse into a single factory substitution at the composition root.
- **inappropriate-intimacy** — Client code reaching into platform-specific construction details is severed by the abstract interface boundary.
- **scattered-platform-variants** — Product creation logic spread across many sites is consolidated into one factory class per family.

## Tests implied

- **Family coherence** — Instantiate each concrete factory; assert that `createProductA()` and `createProductB()` return objects from the same family (e.g. both Mac, both Win).
- **Client interface isolation** — Client test references only `AbstractFactory`, `Button`, `Checkbox`; any import of a concrete factory or product is a red flag.
- **Full factory swap** — Replace `MacFactory` with `WinFactory` in the client; assert overall behaviour changes correctly with no client-code edits.
- **No unimplemented methods** — Every method on `AbstractFactory` is overridden in every concrete factory; a missing override is a test failure.

## Sources

- https://refactoring.guru/design-patterns/abstract-factory
