---
name: strategy
category: behavioral
aliases: [policy]
intent: >-
  Define a family of algorithms, encapsulate each one, and make them interchangeable at runtime
sources:
  - https://refactoring.guru/design-patterns/strategy
smells_it_fixes:
  - long-conditional-chain
  - switch-on-type
  - duplicate-algorithm-variants
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
composes_with:
  - factory-method
  - decorator
  - observer
  - state
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "All strategy variants conform to the strategy interface contract"
  - "Context delegates without inspecting the concrete strategy type"
  - "Swapping strategies at runtime produces the behavior of the new strategy from that point forward"
  - "Context behavior is fully determined by its current strategy with no residual logic"
---

# Strategy

## Intent

Define a family of algorithms, encapsulate each one in its own class, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it. The context object holds a reference to a strategy and delegates the algorithm to it; clients can swap strategies at runtime without modifying the context.

## Structure

```
Context
  - strategy: Strategy
  + setStrategy(s: Strategy): void
  + execute(): Result  { return strategy.run(data) }

Strategy (interface)
  + run(data: Data): Result

ConcreteStrategyA       ConcreteStrategyB       ConcreteStrategyC
  + run(data): Result     + run(data): Result      + run(data): Result
  (algorithm A)           (algorithm B)            (algorithm C)
```

Roles:
- **Context** — holds a strategy reference; delegates algorithm execution; provides data access
- **Strategy** — common interface all algorithms implement
- **ConcreteStrategy** — implements one variant of the algorithm

## Applicability

- Multiple related classes differ only in their behavior
- You need to swap algorithms at runtime based on configuration, user input, or environment
- You want to isolate algorithm logic from the code that uses it
- A class has a large conditional selecting among variants of the same operation
- Sorting, compression, validation, pricing, routing, rendering — any pluggable algorithm slot

## Consequences

- **Algorithm family encapsulated** — each variant is self-contained and independently testable
- **Eliminates conditionals** — no `if/switch` on algorithm type in the context
- **Open for extension** — new algorithms added as new classes, context untouched
- **Increased objects** — one class per algorithm; trivial variants may not justify the abstraction
- **Client must know strategies** — the caller selecting a strategy needs to be aware of available options
- **Context/strategy coupling** — they must agree on the data contract; mismatches cause runtime errors

## OOP shape

```
interface SortStrategy<T> {
  sort(items: T[]): T[]
}

class QuickSort<T> implements SortStrategy<T> {
  sort(items: T[]): T[] { /* quicksort impl */ return items }
}

class MergeSort<T> implements SortStrategy<T> {
  sort(items: T[]): T[] { /* mergesort impl */ return items }
}

class Sorter<T> {
  constructor(private strategy: SortStrategy<T>) {}

  setStrategy(s: SortStrategy<T>): void { this.strategy = s }
  sort(items: T[]): T[] { return this.strategy.sort(items) }
}
```

## FP shape

```
// Strategy = higher-order function / first-class function
type SortFn<T> = (items: T[]) => T[]

const quickSort:  SortFn<number> = (items) => { /* ... */ return items }
const mergeSort:  SortFn<number> = (items) => { /* ... */ return items }
const radixSort:  SortFn<number> = (items) => { /* ... */ return items }

// Context = function that accepts a strategy as a parameter
const sortWith = <T>(strategy: SortFn<T>) =>
  (items: T[]): T[] => strategy(items)

// Runtime swap = pass a different function
const sorter = sortWith(quickSort)
const fastSorter = sortWith(radixSort)

// Strategy injection via partial application / dependency injection
const buildPipeline = (compress: CompressFn, encrypt: EncryptFn) =>
  (data: Buffer): Buffer => encrypt(compress(data))
```

## Smells fixed

- **long-conditional-chain** — a cascade of `if/else if` selecting an algorithm variant is replaced by strategy injection; the context contains no branching
- **switch-on-type** — `switch (algorithmType)` inside a method is eliminated; the selected strategy object carries its own behavior
- **duplicate-algorithm-variants** — near-identical algorithm blocks copy-pasted across callers are unified into distinct, named strategy classes

## Tests implied

- **Interface conformance** — every strategy variant passes a shared contract test that exercises the full strategy interface
- **Context opacity** — inspect context code for `instanceof` or type checks on the held strategy; there should be none
- **Runtime swap** — set strategy A, execute, assert result A; set strategy B, execute, assert result B; no residual A behavior
- **Context isolation** — context logic produces the same output for identical inputs regardless of which strategy produced that output — test context logic separately from strategy logic

## Sources

- https://refactoring.guru/design-patterns/strategy
