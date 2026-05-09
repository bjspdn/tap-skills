---
name: visitor
category: behavioral
aliases: [double-dispatch]
intent: >-
  Separate an algorithm from the object structure it operates on, letting new operations be added without modifying elements
sources:
  - https://refactoring.guru/design-patterns/visitor
smells_it_fixes:
  - switch-on-type
  - inappropriate-intimacy
  - shotgun-surgery
  - divergent-change
smells_it_introduces:
  - shotgun-surgery
  - speculative-generality
composes_with:
  - composite
  - iterator
  - interpreter
clashes_with:
  - god-class
test_invariants:
  - "Each element type dispatches to its own dedicated visitor method"
  - "Adding a new visitor does not require modifying any element class"
  - "A visitor accumulates results only through its own state, not by mutating elements"
  - "Double dispatch: the method invoked depends on both the visitor type and the element type"
---

# Visitor

## Intent

Represent an operation to be performed on elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates. Elements expose an `accept(visitor)` method; the visitor implements a `visit` overload per element type. This achieves double dispatch: the operation chosen depends on both the visitor's concrete type and the element's concrete type.

## Structure

```
Element (interface)
  + accept(v: Visitor): void

ConcreteElementA          ConcreteElementB
  + accept(v): void           + accept(v): void
    { v.visitA(this) }          { v.visitB(this) }

Visitor (interface)
  + visitA(elem: ConcreteElementA): void
  + visitB(elem: ConcreteElementB): void

ConcreteVisitor1          ConcreteVisitor2
  + visitA(a): void           + visitA(a): void
  + visitB(b): void           + visitB(b): void

ObjectStructure
  - elements: Element[]
  + accept(v: Visitor): void { elements.forEach(e => e.accept(v)) }
```

Roles:
- **Element** — declares `accept(visitor)`; concrete elements call the matching visitor method
- **Visitor** — declares a `visit` method per element type; encapsulates one operation
- **ConcreteVisitor** — implements the operation for each element type
- **ObjectStructure** — iterates elements and dispatches the visitor

## Applicability

- An object structure contains many distinct element types and you need to perform several unrelated operations on them
- Operations on the structure change frequently; element classes should stay stable
- Reporting, serialization, pretty-printing, validation, metrics — multiple passes over the same AST or object graph
- Adding new operations to a class hierarchy whose source you own but want to keep clean
- When the type hierarchy is closed (known and stable) but operations are open-ended

## Consequences

- **New operations without touching elements** — add a new visitor class; zero element code changes
- **Related operations grouped** — all type-specific logic for one operation lives in one visitor class
- **Breaking the encapsulation** — visitors need access to element internals; elements may need to expose more state
- **Adding new element types is hard** — every existing visitor must add a new `visit` method; breaks existing visitors
- **Double dispatch overhead** — two virtual method calls per element visit; minor but measurable in hot paths
- **Accumulation via visitor state** — visitors can accumulate results across the structure naturally

## OOP shape

```
interface Visitor {
  visitCircle(c: Circle): void
  visitRectangle(r: Rectangle): void
  visitTriangle(t: Triangle): void
}

interface Shape {
  accept(v: Visitor): void
}

class Circle implements Shape {
  accept(v: Visitor): void { v.visitCircle(this) }
}

class Rectangle implements Shape {
  accept(v: Visitor): void { v.visitRectangle(this) }
}

class AreaCalculator implements Visitor {
  total = 0
  visitCircle(c: Circle): void      { this.total += Math.PI * c.radius ** 2 }
  visitRectangle(r: Rectangle): void { this.total += r.width * r.height }
  visitTriangle(t: Triangle): void   { this.total += 0.5 * t.base * t.height }
}
```

## FP shape

```
// Visitor = pattern matching / exhaustive switch over an ADT
type Shape =
  | { kind: "circle";    radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle";  base: number;  height: number }

// Each "visitor" is a function — exhaustive match guarantees all types handled
const area = (shape: Shape): number => {
  switch (shape.kind) {
    case "circle":    return Math.PI * shape.radius ** 2
    case "rectangle": return shape.width * shape.height
    case "triangle":  return 0.5 * shape.base * shape.height
  }
}

const perimeter = (shape: Shape): number => {
  switch (shape.kind) {
    case "circle":    return 2 * Math.PI * shape.radius
    case "rectangle": return 2 * (shape.width + shape.height)
    case "triangle":  return shape.base + shape.height + /* hypotenuse */ 0
  }
}

// New operation = new function; shape ADT unchanged
// TypeScript exhaustiveness checking enforces complete coverage
```

## Smells fixed

- **switch-on-type** — a `switch (element.type)` inside an operation class is replaced by per-type visitor methods with compile-time exhaustiveness checking
- **inappropriate-intimacy** — operations that must inspect element internals are gathered into dedicated visitor classes rather than scattered across the structure
- **shotgun-surgery** — adding a new operation currently requires modifying every element class; with Visitor, only a new visitor class is added
- **divergent-change** — element classes that change for multiple unrelated operational reasons are stabilized; operations move to visitors

## Tests implied

- **Per-type dispatch** — for each element type, verify that `accept(visitor)` calls the exact matching `visitX` method on the visitor and no other
- **No element mutation** — after a visitor traversal, assert that all element fields are unchanged; visitor accumulates into its own state only
- **Exhaustive coverage** — a new element type added to the hierarchy fails to compile (or fails a test) if any existing visitor does not implement the corresponding `visit` method
- **Double dispatch correctness** — swap both the visitor type and the element type independently; the invoked method changes in both dimensions

## Sources

- https://refactoring.guru/design-patterns/visitor
