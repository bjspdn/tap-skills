---
name: decorator
category: structural
aliases: [wrapper, smart-reference]
intent: >-
  Attach additional responsibilities to an object dynamically by wrapping it, as a flexible alternative to subclassing
sources:
  - https://refactoring.guru/design-patterns/decorator
smells_it_fixes:
  - god-class
  - large-class
  - speculative-generality
  - duplicate-algorithm-variants
smells_it_introduces:
  - temporal-coupling
  - over-abstraction-single-variant
composes_with:
  - composite
  - strategy
  - chain-of-responsibility
clashes_with:
  - template-method
test_invariants:
  - "A decorator forwards every method on the component interface to the wrapped component"
  - "Decorators are composable in any order; stacking N decorators applies all N behaviours"
  - "Removing a decorator layer leaves the wrapped component unchanged"
  - "Client code treats a decorated object identically to an undecorated one"
  - "Each decorator adds exactly one responsibility — no decorator mixes multiple cross-cutting concerns"
---

# Decorator

## Intent

Decorator wraps a component object inside another object that implements the same interface, adding behaviour before or after delegating to the wrapped component. Wrappers can be stacked arbitrarily, composing behaviours at runtime without altering the original class or creating a combinatorial subclass hierarchy. It is the primary pattern for cross-cutting concerns such as logging, caching, validation, and compression.

## Structure

```
Client ──> «interface» Component
                + operation(): Result
                    ▲
          ┌─────────┴──────────┐
    ConcreteComponent      BaseDecorator
    + operation()          - wrapped: Component
                           + operation() → wrapped.operation()
                               ▲
                  ┌────────────┴────────────┐
           DecoratorA                  DecoratorB
           + operation()               + operation()
             // before hook              // after hook
             wrapped.operation()         wrapped.operation()
             // after hook               // before hook
```

Roles:
- **Component** — interface shared by concrete components and decorators
- **ConcreteComponent** — the real object being decorated
- **BaseDecorator** — holds the wrapped Component; delegates by default
- **ConcreteDecorator** — overrides operation to add behaviour

## Applicability

- You want to add responsibilities to individual objects, not an entire class.
- Extension by subclassing is impractical due to a combinatorial explosion of feature combinations.
- You need to be able to add and remove responsibilities at runtime.
- Cross-cutting concerns (logging, auth, caching) should be composable independently.

## Consequences

**Gains**
- Single Responsibility: each decorator handles exactly one concern.
- Open/Closed: new behaviour via new decorator, no class modification.
- Flexible runtime composition; behaviours can be stacked in any order.

**Costs**
- Many small wrapper objects; hard to debug deep stacks.
- Order dependency: stacking order matters and is not enforced by the type system.
- Identity checks (`instanceof`) break when an object is wrapped.

## OOP shape

```
interface Component
  operation(): Result

class ConcreteComponent implements Component
  operation(): Result
    return coreResult

abstract class BaseDecorator implements Component
  constructor(wrapped: Component)
  operation(): Result
    return this.wrapped.operation()   // default: pure delegation

class LoggingDecorator extends BaseDecorator
  operation(): Result
    log("before")
    result = super.operation()
    log("after", result)
    return result

class CachingDecorator extends BaseDecorator
  operation(): Result
    if cache.has(key): return cache.get(key)
    result = super.operation()
    cache.set(key, result)
    return result
```

## FP shape

```
// Decorator = function transformer (middleware / higher-order function)
type Op = Input -> Result

withLogging :: Op -> Op
withLogging(op) = input ->
  log("before", input)
  result = op(input)
  log("after", result)
  result

withCaching :: Cache -> Op -> Op
withCaching(cache, op) = input ->
  cache.getOrSet(input, () -> op(input))

// Compose decorators via function composition
decorated = withLogging(withCaching(cache, coreOp))
```

## Smells fixed

- **god-class** — a bloated class accumulating logging, caching, validation, and business logic is decomposed into a lean core plus focused decorators.
- **large-class** — each cross-cutting concern extracted into its own decorator reduces overall class size.
- **speculative-generality** — unused feature flags or switch-enabled behaviours in a single class are replaced by opt-in decorators applied only where needed.
- **duplicate-algorithm-variants** — the same before/after hook logic copy-pasted across multiple operations is centralised in a single decorator.

## Tests implied

- **Full delegation** — for each interface method, assert that a bare BaseDecorator forwards arguments and return value unchanged to the wrapped component.
- **Stackable** — apply DecoratorA then DecoratorB; verify both A's and B's side effects are observed in the correct order.
- **Non-destructive removal** — unwrap a decorator and assert the inner component's state is unaffected.
- **Client transparency** — confirm that a function accepting Component works identically on ConcreteComponent and on a wrapped stack.
- **Single responsibility** — assert that each ConcreteDecorator class touches at most one observable concern (e.g., only logs, only caches).

## Sources

- https://refactoring.guru/design-patterns/decorator
