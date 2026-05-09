---
name: singleton
category: creational
aliases: []
intent: >-
  Ensure a class has only one instance and provide a global access point to it
sources:
  - https://refactoring.guru/design-patterns/singleton
smells_it_fixes:
  - mutable-shared-state
  - duplicate-resource-initialisation
  - uncoordinated-global-access
smells_it_introduces:
  - mutable-shared-state
  - god-class
  - speculative-generality
  - hidden-dependency
  - temporal-coupling
composes_with:
  - abstract-factory
  - facade
clashes_with:
  - factory-method
  - prototype
test_invariants:
  - "Two calls to the accessor method return the same instance (reference equality)"
  - "Instance is created at most once, even under concurrent access"
  - "Singleton state mutated in one test does not leak into subsequent tests"
  - "The single instance satisfies the full interface contract of the underlying type"
---

# Singleton

## Intent

Singleton ensures a class has exactly one instance and provides a global point of access to it. The class controls its own instantiation by hiding its constructor and exposing a static accessor method that returns the same instance on every call. It is primarily used to manage shared resources — configuration, connection pools, caches — where multiple instances would cause conflicts or waste.

## Structure

```
class Singleton
  - instance : Singleton   ← static, private
  - constructor()          ← private; prevents external construction

  + getInstance() : Singleton   ← static; creates on first call, returns cached thereafter
  + businessOperation() : void
```

### Variants

**Lazy initialisation** — instance created on first `getInstance()` call. Requires thread-safe guard in concurrent environments.

**Eager initialisation** — instance created at class-load time. Thread-safe by default; creation cost paid regardless of use.

**Double-checked locking** — lazy creation with a double-checked lock to reduce synchronisation overhead in hot paths.

**Holder / initialisation-on-demand** — static inner class holds the instance; JVM class-loading guarantees thread safety without explicit locking.

## Applicability

- Exactly one object is needed to coordinate across the system (e.g. a logger, config store, or device driver).
- Shared state must be tightly controlled; multiple instances would lead to conflicts or inconsistency.
- You need lazy initialisation with a guarantee of single creation.

## Consequences

**Gains**
- Guarantees a single instance; prevents accidental duplication of stateful resources.
- Provides a well-known global access point.
- Instance is created only when first needed (lazy variant).

**Costs**
- Introduces global mutable state — one of the most common sources of hard-to-trace bugs.
- Violates Single Responsibility: the class manages both its own business logic and its own lifecycle.
- Hides dependencies: callers reach in globally rather than declaring the dependency explicitly.
- Makes unit testing hard: shared state bleeds between tests; mocking requires workarounds.
- Concurrency requires careful implementation; naïve lazy initialisation is not thread-safe.
- Breaks in multi-process or distributed contexts where "one instance" becomes meaningless.

## OOP shape

```
class Singleton
  private static field instance : Singleton | null = null
  private constructor()   // prevents external new

  public static method getInstance() : Singleton
    if instance == null
      instance = new Singleton()
    return instance

  public method doWork() : void
    // business logic

// Usage (no constructor visible to caller):
s = Singleton.getInstance()
s.doWork()
```

## FP shape

In FP, Singleton maps to a module-level value or a memoised nullary function. Shared state is made explicit through a managed effect (e.g. `IORef`, `Ref`, `State` monad) rather than hidden in a class field.

```
// Module-level singleton value (eager, pure)
val config : Config = loadConfigFromEnv()

// Memoised factory (lazy)
val getConnection : () => Connection = memoize(() => openConnection(config))

// Shared mutable state made explicit via effect type
type AppEnv = { dbRef: Ref<Connection>, logRef: Ref<Logger> }

// Consumers receive the env explicitly — no global reach-in
function processRequest(env: AppEnv, req: Request) : IO<Response>
```

## Smells fixed

- **duplicate-resource-initialisation** — Multiple parts of the codebase each constructing their own DB connection or config object is resolved by routing all access through the single instance.
- **uncoordinated-global-access** — Scattered access to a shared resource without a coordination point is centralised behind `getInstance()`.
- **mutable-shared-state** — Paradoxically, Singleton also *introduces* this smell; it *fixes* uncontrolled duplication of the state, but does not eliminate the mutability risk.

## Tests implied

- **Same-instance guarantee** — Call `getInstance()` twice; assert `result1 === result2` (reference equality).
- **Single construction** — Spy on or count constructor invocations; assert it fires at most once across multiple `getInstance()` calls.
- **Test isolation** — If tests mutate singleton state, assert a reset mechanism exists and is exercised in teardown so state does not bleed between tests.
- **Interface conformance** — Assert the returned singleton satisfies the full interface expected by its consumers.

## Sources

- https://refactoring.guru/design-patterns/singleton
