---
name: flyweight
category: structural
aliases: [cache, fine-grained]
intent: >-
  Share fine-grained objects to support large numbers of them efficiently by separating intrinsic from extrinsic state
sources:
  - https://refactoring.guru/design-patterns/flyweight
smells_it_fixes:
  - mutable-shared-state
  - primitive-obsession
  - data-clump
smells_it_introduces:
  - mutable-shared-state
  - temporal-coupling
  - unclear-naming
composes_with:
  - composite
  - factory-method
  - singleton
clashes_with:
  - prototype
test_invariants:
  - "Two requests for the same intrinsic state return the identical shared flyweight instance"
  - "Flyweight objects carry no extrinsic (context-specific) state — all context is passed at use time"
  - "Total flyweight instances created equals the number of distinct intrinsic state combinations, not the number of logical objects"
  - "Mutating one flyweight's intrinsic state is prevented — flyweights are immutable"
---

# Flyweight

## Intent

Flyweight reduces memory usage when a program must maintain a huge number of similar objects by extracting their shared, immutable state (intrinsic state) into a small pool of reusable flyweight objects. Context-specific data (extrinsic state) is passed to flyweight operations at call time rather than stored inside the object. The FlyweightFactory ensures only one instance exists per unique intrinsic state.

## Structure

```
Client
  - extrinsicState[]
  + operation(extrinsicData)
         |
         v
FlyweightFactory
  - cache: Map<IntrinsicKey, Flyweight>
  + getFlyweight(intrinsicState): Flyweight

Flyweight           (shared, immutable)
  - intrinsicState
  + operation(extrinsicState): void
```

Roles:
- **Flyweight** — stores only intrinsic (shared, immutable) state; accepts extrinsic state as parameters
- **FlyweightFactory** — returns a cached Flyweight for a given intrinsic key, creating it on first request
- **Client** — maintains extrinsic state; passes it into flyweight operations

## Applicability

- Your application must create a huge number of objects that would exhaust available memory.
- Most object state can be made extrinsic (passed in rather than stored).
- Many groups of objects can be replaced by relatively few shared objects once extrinsic state is removed.
- The application does not depend on object identity (flyweights are shared, so `a === b` may hold unexpectedly).

## Consequences

**Gains**
- Dramatic memory reduction when intrinsic state is small relative to extrinsic state.
- Fewer objects created; reduced GC pressure.

**Costs**
- CPU trade-off: recomputing or looking up extrinsic state at call time instead of reading it from the object.
- Adds complexity: clients must track extrinsic state externally.
- Flyweights must be strictly immutable — any mutable shared state is a concurrency hazard.
- Code becomes harder to read; the intrinsic/extrinsic split is non-obvious.

## OOP shape

```
// Immutable flyweight — only intrinsic state
class Flyweight
  constructor(readonly intrinsicState: IntrinsicData)
  operation(extrinsicState: ExtrinsicData): Result
    return compute(this.intrinsicState, extrinsicState)

// Factory — cache keyed by intrinsic state
class FlyweightFactory
  private cache: Map<string, Flyweight>
  getFlyweight(intrinsicState: IntrinsicData): Flyweight
    key = serialize(intrinsicState)
    if not cache.has(key):
      cache.set(key, new Flyweight(intrinsicState))
    return cache.get(key)

// Client — owns extrinsic state
class Context
  flyweight: Flyweight        // retrieved from factory
  extrinsicState: ExtrinsicData
  render(): Result
    return this.flyweight.operation(this.extrinsicState)
```

## FP shape

```
// Intrinsic state = closed-over in a partially applied function
type FlyweightFn = ExtrinsicData -> Result

makeFlyweight :: IntrinsicData -> FlyweightFn
makeFlyweight(intrinsic) =
  extrinsic -> compute(intrinsic, extrinsic)

// Factory = memoised constructor
flyweightFor = memoize(makeFlyweight)   // keyed by intrinsic key

// Usage
fw = flyweightFor(sharedIntrinsic)
result = fw(perContextExtrinsic)
```

## Smells fixed

- **primitive-obsession** — repeated duplication of the same raw data values (e.g., colour strings, glyph codes) across thousands of objects is replaced by a single shared value object.
- **data-clump** — clusters of fields that always travel together as intrinsic state are extracted into a Flyweight value type.
- **mutable-shared-state** — the pattern enforces intrinsic-state immutability, making shared-state mutation a design-time error rather than a runtime bug.

## Tests implied

- **Identity cache** — call `factory.getFlyweight(same key)` twice; assert the returned references are strictly equal.
- **No extrinsic state stored** — inspect Flyweight instance fields; assert none stores per-context data.
- **Instance count** — create N contexts with K distinct intrinsic keys (N >> K); assert factory cache size equals K.
- **Immutability** — attempt to mutate intrinsic state on a shared Flyweight; assert it is prevented (frozen, readonly, or copied).

## Sources

- https://refactoring.guru/design-patterns/flyweight
