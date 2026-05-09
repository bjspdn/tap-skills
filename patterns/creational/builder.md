---
name: builder
category: creational
aliases: []
intent: >-
  Separate the construction of a complex object from its representation so the same process can create different representations
sources:
  - https://refactoring.guru/design-patterns/builder
smells_it_fixes:
  - long-parameter-list
  - data-clump
  - temporal-coupling
  - telescoping-constructor
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - composite
  - factory-method
clashes_with: []
test_invariants:
  - "A product built via Builder contains exactly the parts that were specified through builder calls"
  - "Calling build() on a fresh builder with no configuration yields a valid default product"
  - "Builder step order does not affect the final product when steps are independent"
  - "The Director, when present, reproduces the same product configuration on every invocation"
  - "The same builder interface can produce structurally distinct representations of the same concept"
---

# Builder

## Intent

Builder separates the step-by-step construction of a complex object from the representation it produces. A Director orchestrates a sequence of builder steps; concrete Builders implement those steps to assemble different representations. The client receives a finished product only by calling the terminal `build()` step, which means the object is always fully initialised when handed over.

## Structure

```
<<interface>> Builder
  + reset()        : void
  + setPartA(v)    : void
  + setPartB(v)    : void
  + setPartC(v)    : void

ConcreteBuilder1 implements Builder
  - product : Product1
  + build()  : Product1

ConcreteBuilder2 implements Builder
  - product : Product2
  + build()  : Product2

Director
  - builder : Builder
  + construct() : void   ← calls builder steps in order

Product1
Product2
```

## Applicability

- Constructing an object requires many steps, some optional, some ordered.
- The same construction process must yield different representations.
- A constructor with many parameters (especially optional ones) has become unreadable.
- You need fine-grained control over the construction process.

## Consequences

**Gains**
- Eliminates telescoping constructors and multi-flag parameter lists.
- Construction and representation are decoupled: change one without touching the other.
- Unfinished objects are never exposed; `build()` is the single exit point.
- Director can encapsulate reusable construction recipes.

**Costs**
- Adds builder class(es) per product — more moving parts for simple objects.
- Builder interface must be updated whenever the product gains a new part.
- Mutable intermediate state inside the builder can be surprising.

## OOP shape

```
interface HouseBuilder
  method setWalls(count: int)     : HouseBuilder   // fluent optional
  method setRoof(type: RoofType)  : HouseBuilder
  method setGarage(has: bool)     : HouseBuilder
  method build()                  : House

class ConcreteHouseBuilder implements HouseBuilder
  private state: PartialHouse
  method setWalls(count)  → mutate state; return this
  method setRoof(type)    → mutate state; return this
  method setGarage(has)   → mutate state; return this
  method build()          → validate state; return House(state)

class Director
  constructor(builder: HouseBuilder)
  method constructLuxuryHouse() : void
    builder.setWalls(4).setRoof(GABLED).setGarage(true)
  method constructSimpleHouse() : void
    builder.setWalls(4).setRoof(FLAT).setGarage(false)
```

## FP shape

In FP the builder is a record of configuration accumulated through a chain of transforms, terminated by a finaliser. Often implemented as an immutable record updated via `with` expressions, or a fold over a list of configuration operations.

```
type HouseConfig = {
  walls  : int    = 4
  roof   : Roof   = FLAT
  garage : bool   = false
}

// Each "step" is a plain function HouseConfig → HouseConfig
withWalls  : int → (HouseConfig → HouseConfig)
withRoof   : Roof → (HouseConfig → HouseConfig)
withGarage : bool → (HouseConfig → HouseConfig)

buildHouse : HouseConfig → House

// Usage: compose steps, then apply finaliser
luxuryHouse =
  buildHouse(
    withGarage(true)(
      withRoof(GABLED)(
        withWalls(4)(defaultConfig)
      )
    )
  )
```

## Smells fixed

- **long-parameter-list** — A constructor like `new House(4, GABLED, true, 2, RED, ...)` becomes a readable chain of named builder calls.
- **data-clump** — Parameters that always travel together (wall count + material + height) are encapsulated inside builder steps.
- **temporal-coupling** — Code that previously had to call setters in a specific order before calling `render()` is replaced by a builder that validates completeness at `build()`.
- **telescoping-constructor** — Multiple overloaded constructors for different optional combinations collapse into one builder interface with optional steps.

## Tests implied

- **Step fidelity** — Each builder step is independently exercised; assert the corresponding part appears in the final product.
- **Default product validity** — `new ConcreteBuilder().build()` produces a valid, usable product without any configuration calls.
- **Step order independence** — Where steps are logically independent, apply them in different orders; assert identical products result.
- **Director reproducibility** — Call `director.constructX()` twice on fresh builders; assert both resulting products are equivalent.
- **Cross-builder representation** — Use two concrete builders with the same Director recipe; assert the two products differ in representation but encode the same logical concept.

## Sources

- https://refactoring.guru/design-patterns/builder
