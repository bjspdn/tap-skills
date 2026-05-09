---
name: prototype
category: creational
aliases: [clone]
intent: >-
  Specify the kinds of objects to create using a prototypical instance, and create new objects by copying that prototype
sources:
  - https://refactoring.guru/design-patterns/prototype
smells_it_fixes:
  - repeated-construction-ceremony
  - inappropriate-intimacy
  - switch-on-type
smells_it_introduces:
  - mutable-shared-state
  - shallow-copy-aliasing
composes_with:
  - composite
  - decorator
  - factory-method
  - abstract-factory
clashes_with: []
test_invariants:
  - "A cloned object is equal in value to its prototype but is a distinct identity (different reference)"
  - "Mutating a clone does not affect the prototype or any sibling clone"
  - "Deep clone includes all nested objects; no shared mutable references remain between original and copy"
  - "The clone operation is available through a uniform interface regardless of concrete type"
---

# Prototype

## Intent

Prototype lets you copy existing objects without depending on their concrete classes. Each object exposes a `clone()` method that knows how to reproduce itself; the client simply calls `clone()` on a pre-configured prototype instead of constructing a new object from scratch. This is particularly valuable when object construction is expensive or when the exact class of an object is unknown at compile time.

## Structure

```
<<interface>> Prototype
  + clone() : Prototype

ConcretePrototypeA implements Prototype
  - field1, field2, ...
  + clone() : ConcretePrototypeA   ← deep-copies own state

ConcretePrototypeB implements Prototype
  - fieldX, fieldY, ...
  + clone() : ConcretePrototypeB

PrototypeRegistry (optional)
  - prototypes : Map<key, Prototype>
  + get(key) : Prototype   ← returns clone of stored prototype
  + register(key, proto)

Client
  uses Prototype interface only
```

## Applicability

- Classes to instantiate are specified at run time (e.g. by dynamic loading).
- Instances of a class can have only one of a few combinations of state; cloning pre-configured prototypes is more convenient than manual construction.
- Object construction is costly (deep graph, I/O, computation) and a copy is cheaper.
- You want to build a product by assembling parts that can themselves be prototyped.

## Consequences

**Gains**
- Hides concrete product classes from the client.
- Lets you clone complex or partially-configured objects without knowing their type.
- Alternative to subclassing: vary behaviour by substituting prototype instances.
- Pre-built prototypes can serve as reusable templates.

**Costs**
- Implementing `clone()` correctly for deep graphs with circular references is non-trivial.
- Shallow copy (copying only top-level fields) leads to shared mutable sub-objects — a subtle source of bugs.
- Cloning objects with external resources (file handles, DB connections) requires special handling.

## OOP shape

```
interface Prototype
  method clone() : Prototype

class Shape implements Prototype
  field color : Color
  field position : Point
  // ... other value-like fields

  constructor copy(other: Shape)          // copy constructor
    this.color    = other.color           // value copy
    this.position = other.position.copy() // deep copy of mutable field

  method clone() : Shape
    return new Shape copy(this)

class Circle extends Shape
  field radius : float
  method clone() : Circle
    return new Circle copy(this)          // includes radius

class PrototypeRegistry
  field store : Map<String, Prototype>
  method register(key, proto) : void
  method get(key) : Prototype
    return store[key].clone()
```

## FP shape

In FP, prototyping maps naturally to record copy / `with` expressions. A "prototype" is a default record value; a "clone" is a shallow or deep structural copy, often with field overrides.

```
type Shape = { color: Color, position: Point, radius: Float }

// Default prototype value
defaultCircle : Shape = { color=RED, position=origin, radius=1.0 }

// "Clone with overrides" is a record update expression
cloneAt : Shape → Point → Shape
cloneAt proto pos = { ...proto, position = pos }

// Registry is a plain map from key to default value
registry : Map<String, Shape>
make : String → Shape
make key = registry[key]   // structural copy on retrieval in immutable setting
```

## Smells fixed

- **repeated-construction-ceremony** — When creating many similar objects requires the same long sequence of setters/constructors, replacing it with `prototype.clone()` (plus targeted overrides) removes the duplication.
- **inappropriate-intimacy** — Client code that digs into an object's internals to replicate it manually is replaced by the object's own `clone()` method.
- **switch-on-type** — Branching on type to decide which constructor to call is replaced by a registry lookup that returns the correctly-typed clone.

## Tests implied

- **Value equality, reference inequality** — Assert `clone == original` (value) but `clone !== original` (identity); they are distinct objects.
- **Mutation isolation** — Mutate a field on the clone; assert the prototype's corresponding field is unchanged, and vice versa.
- **Deep copy completeness** — For a prototype with nested mutable objects, assert no shared references exist between original and clone at any depth.
- **Uniform clone interface** — Invoke `clone()` through the `Prototype` interface reference (not the concrete type); assert the returned object is the correct concrete type.

## Sources

- https://refactoring.guru/design-patterns/prototype
