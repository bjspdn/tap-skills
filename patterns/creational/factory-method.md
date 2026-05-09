---
name: factory-method
category: creational
aliases: [virtual-constructor]
intent: >-
  Define an interface for creating an object, but let subclasses decide which class to instantiate
sources:
  - https://refactoring.guru/design-patterns/factory-method
smells_it_fixes:
  - switch-on-type
  - long-conditional-chain
  - shotgun-surgery
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - abstract-factory
  - template-method
  - prototype
clashes_with:
  - singleton
test_invariants:
  - "The factory method returns an object that satisfies the Product interface"
  - "Concrete creators override the factory method without changing the surrounding algorithm"
  - "Client code depends only on the Product interface, never on a concrete product class"
  - "Adding a new product type requires no changes to existing creator or client code"
---

# Factory Method

## Intent

Factory Method defines a method for creating objects, but defers the instantiation decision to subclasses. The creator provides a skeletal algorithm that calls its own factory method; each subclass plugs in a different concrete product. This decouples the client from the specific class it needs to instantiate and makes the creation point a stable extension seam.

## Structure

```
Creator
  + factoryMethod() : Product   ← overridden by subclasses
  + operation()                  ← calls factoryMethod() internally

ConcreteCreatorA extends Creator
  + factoryMethod() : ProductA

ConcreteCreatorB extends Creator
  + factoryMethod() : ProductB

<<interface>> Product
ConcreteProductA implements Product
ConcreteProductB implements Product
```

## Applicability

- You cannot anticipate the class of objects your code must create.
- You want subclasses to specify the objects they create.
- You have a library of creators and want to provide a hook for users to extend what gets built.
- A class delegates responsibility to one of several helper subclasses, and you want to localise the knowledge of which helper is used.

## Consequences

**Gains**
- Eliminates tight coupling between creator and concrete products.
- Single Responsibility: product creation code lives in one place per variant.
- Open/Closed: add new products by adding new subclasses, not editing existing ones.

**Costs**
- Class hierarchy grows: every new product requires a new creator subclass.
- Can feel over-engineered when only one product type will ever exist.
- Indirection makes the instantiation path harder to trace.

## OOP shape

```
interface Product
  method doWork() : void

abstract class Creator
  abstract method factoryMethod() : Product   // subclasses override
  method operation() : void
    p = this.factoryMethod()
    p.doWork()

class ConcreteCreatorA extends Creator
  override method factoryMethod() : Product
    return new ConcreteProductA()

class ConcreteCreatorB extends Creator
  override method factoryMethod() : Product
    return new ConcreteProductB()
```

## FP shape

Factory Method maps to a higher-order function that accepts a constructor/factory function as a parameter, or to a module parameterised by a make function.

```
type ProductMaker<T extends Product> = () => T

function operation(make: ProductMaker) : void
  p = make()
  p.doWork()

// Callers inject the specific factory:
operation(() => makeProductA())
operation(() => makeProductB())
```

## Smells fixed

- **switch-on-type** — Branching on a type tag to decide which class to construct is replaced by polymorphic dispatch through the factory method.
- **long-conditional-chain** — A chain of `if/else` deciding how to build objects collapses into distinct creator subclasses.
- **shotgun-surgery** — When a new product must be wired up everywhere a type check lives, Factory Method centralises that registration to one subclass.

## Tests implied

- **Product interface conformance** — Invoke `factoryMethod()` on every concrete creator; assert the returned object satisfies the Product interface contract (responds to expected messages).
- **Creator algorithm isolation** — Call `operation()` and verify it completes correctly without the test knowing which concrete product was created.
- **Client independence** — Client test code must reference only `Creator` and `Product` types; any import of a concrete product class is a test smell.
- **Extension without modification** — Adding `ConcreteCreatorC` in a test should not require editing any existing creator or client source.

## Sources

- https://refactoring.guru/design-patterns/factory-method
