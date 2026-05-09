---
name: composite
category: structural
aliases: [object-tree]
intent: >-
  Compose objects into tree structures to represent part-whole hierarchies and let clients treat individual objects and compositions uniformly
sources:
  - https://refactoring.guru/design-patterns/composite
smells_it_fixes:
  - long-conditional-chain
  - switch-on-type
  - duplicate-algorithm-variants
smells_it_introduces:
  - over-abstraction-single-variant
  - inappropriate-intimacy
composes_with:
  - iterator
  - visitor
  - decorator
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "A composite's operation result equals the fold of the same operation over all children"
  - "Client code operates identically on a Leaf and on a Composite of depth N"
  - "Adding or removing a child from a Composite does not require changes to Component interface or client"
  - "Leaf nodes never reference child-management methods"
---

# Composite

## Intent

Composite organises objects into tree structures where each node is either a leaf (no children) or a composite (container of components). Both kinds implement the same Component interface, so clients recursively invoke the same operation without knowing whether they are talking to a single object or a whole subtree. The pattern directly models part-whole hierarchies: file systems, UI widget trees, expression trees, scene graphs.

## Structure

```
Client ──> «interface» Component
                + operation()
                    ▲
          ┌─────────┴──────────┐
        Leaf               Composite
        + operation()      - children: Component[]
                           + operation()     // foreach child: child.operation()
                           + add(Component)
                           + remove(Component)
```

Roles:
- **Component** — common interface for both leaves and composites
- **Leaf** — has no children; performs actual work
- **Composite** — stores child Components; delegates to them
- **Client** — operates on Component; unaware of Leaf vs Composite

## Applicability

- You need to represent part-whole hierarchies of objects (trees).
- You want clients to treat individual objects and compositions of objects uniformly.
- The hierarchy is recursive in nature (e.g., directories contain files or other directories).
- You want to add new node types without changing client code.

## Consequences

**Gains**
- Client simplicity: single interface for the whole tree.
- Open/Closed: new leaf or composite types slot in without client changes.
- Natural fit for recursive algorithms (render, evaluate, serialize).

**Costs**
- Component interface may be forced to include child-management methods inappropriate for leaves (interface segregation tension).
- Over-general design makes it hard to restrict which components can be children of which composites.
- Deep trees can produce hard-to-debug stack overflows in naive recursion.

## OOP shape

```
interface Component
  operation(): Result

class Leaf implements Component
  operation(): Result
    return compute(this.value)

class Composite implements Component
  children: Component[]
  operation(): Result
    return this.children
           .map(c => c.operation())
           .reduce(combine)
  add(c: Component): void
  remove(c: Component): void
```

## FP shape

```
// Algebraic data type (recursive sum type)
type Component = Leaf(value) | Node(children: Component[])

// Fold over the tree — isomorphic to Composite.operation()
foldTree :: (LeafVal -> R) -> (R[] -> R) -> Component -> R
foldTree(leafFn, combineFn, Leaf(v))        = leafFn(v)
foldTree(leafFn, combineFn, Node(children)) =
  combineFn(children.map(foldTree(leafFn, combineFn)))
```

## Smells fixed

- **long-conditional-chain** — `if isLeaf ... else if isComposite ...` traversal logic collapses into a single recursive `operation()` call.
- **switch-on-type** — type-tag switches for tree node kinds are replaced by polymorphic dispatch on Component.
- **duplicate-algorithm-variants** — the same traversal written separately for leaves and containers is unified in one recursive implementation.

## Tests implied

- **Composite folds correctly** — build a known tree, assert `composite.operation()` equals the manually computed fold over all leaf values.
- **Uniform client interface** — write a client function accepting Component; call it with a Leaf and with a depth-3 Composite; confirm no branching needed in client.
- **Open/Closed for new types** — introduce a new Leaf subtype; verify existing Composite and client tests require zero edits.
- **Leaf has no children** — assert that Leaf does not expose or implement `add`/`remove` in any way visible to client code.

## Sources

- https://refactoring.guru/design-patterns/composite
