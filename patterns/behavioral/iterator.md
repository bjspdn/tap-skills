---
name: iterator
category: behavioral
aliases: [cursor]
intent: >-
  Provide a way to sequentially access elements of a collection without exposing its underlying representation
sources:
  - https://refactoring.guru/design-patterns/iterator
smells_it_fixes:
  - inappropriate-intimacy
  - feature-envy
  - duplicate-algorithm-variants
smells_it_introduces:
  - speculative-generality
composes_with:
  - composite
  - factory-method
  - memento
  - visitor
clashes_with:
  - god-class
test_invariants:
  - "Iterating a collection visits every element exactly once"
  - "Two independent iterators over the same collection do not interfere with each other"
  - "hasNext returns false exactly when no elements remain"
  - "Calling next when exhausted raises an error or returns a defined sentinel"
---

# Iterator

## Intent

Provide a sequential access interface over a collection's elements without exposing the collection's internal structure. The iterator object tracks traversal state, allowing multiple independent traversals to proceed simultaneously. Clients traverse elements using a uniform interface regardless of whether the collection is an array, tree, graph, or stream.

## Structure

```
Client
  |
  uses
  |
  v
Iterator (interface)
  + hasNext(): bool
  + next(): Element
  + reset(): void      // optional

ConcreteIterator
  - collection: ConcreteCollection
  - position: int
  implements Iterator

Iterable (interface)
  + createIterator(): Iterator

ConcreteCollection implements Iterable
  + createIterator(): Iterator { return new ConcreteIterator(this) }
```

Roles:
- **Iterator** — traversal interface (hasNext, next)
- **ConcreteIterator** — holds traversal state for a specific collection type
- **Iterable / Aggregate** — declares the factory method for creating iterators
- **Client** — traverses via Iterator interface only; unaware of collection internals

## Applicability

- You need to traverse a collection without knowing its concrete type (list, tree, graph, hash table)
- Multiple simultaneous traversals over the same collection are needed
- You want a uniform traversal API across heterogeneous collections
- Lazy traversal of large or infinite sequences (generators, streams, database cursors)

## Consequences

- **Single Responsibility** — traversal logic is separated from collection storage logic
- **Open/Closed** — new collection types get new iterators without touching client code
- **Parallel traversals** — each iterator instance holds its own position state
- **Simplified client code** — no index arithmetic or internal structure knowledge needed
- **Overhead for simple arrays** — wrapping direct indexed access in an iterator object can be wasteful
- **Snapshot vs live** — iterators may see or miss concurrent mutations depending on implementation

## OOP shape

```
interface Iterator<T> {
  hasNext(): boolean
  next(): T
}

interface Iterable<T> {
  iterator(): Iterator<T>
}

class ListIterator<T> implements Iterator<T> {
  private index = 0
  constructor(private items: T[]) {}

  hasNext(): boolean { return this.index < this.items.length }
  next(): T {
    if (!this.hasNext()) throw new Error("exhausted")
    return this.items[this.index++]
  }
}

class NumberList implements Iterable<number> {
  constructor(private data: number[]) {}
  iterator(): Iterator<number> { return new ListIterator(this.data) }
}
```

## FP shape

```
// Iterators are generators / lazy sequences
function* rangeIter(start: number, end: number): Generator<number> {
  for (let i = start; i < end; i++) yield i
}

// Tree traversal as a generator — structure hidden from caller
function* inorder<T>(node: TreeNode<T> | null): Generator<T> {
  if (!node) return
  yield* inorder(node.left)
  yield node.value
  yield* inorder(node.right)
}

// Infinite sequence with lazy take
const naturals = function*() { let n = 0; while (true) yield n++ }
const take = <T>(n: number, iter: Iterable<T>): T[] => {
  const result: T[] = []
  for (const x of iter) { result.push(x); if (result.length === n) break }
  return result
}

// Composition: map/filter over iterables are iterator transformers
const mapIter = <A, B>(iter: Iterable<A>, f: (a: A) => B): Iterable<B> => ({
  [Symbol.iterator]: function*() { for (const x of iter) yield f(x) }
})
```

## Smells fixed

- **inappropriate-intimacy** — client code that reaches into collection internals (array indices, linked-list node pointers) is replaced by the iterator interface
- **feature-envy** — traversal logic duplicated in multiple consumers is centralized in the iterator class
- **duplicate-algorithm-variants** — the same traversal spelled out differently across callers is unified under one iterator type

## Tests implied

- **Complete coverage** — collect all elements via `next()` calls; the resulting set equals the collection's elements with no omissions or duplicates
- **Iterator independence** — two iterators created from the same collection can be advanced independently without one affecting the other's position
- **Exhaustion contract** — after the last `next()`, `hasNext()` is false; a subsequent `next()` throws or returns the defined sentinel
- **Error on overrun** — calling `next()` when `hasNext()` is false produces a defined, observable error state

## Sources

- https://refactoring.guru/design-patterns/iterator
