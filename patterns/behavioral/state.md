---
name: state
category: behavioral
aliases: [objects-for-states]
intent: >-
  Allow an object to alter its behavior when its internal state changes, appearing to change its class
sources:
  - https://refactoring.guru/design-patterns/state
smells_it_fixes:
  - long-conditional-chain
  - switch-on-type
  - large-class
  - mutable-shared-state
smells_it_introduces:
  - speculative-generality
  - shotgun-surgery
composes_with:
  - strategy
  - singleton
  - flyweight
clashes_with:
  - god-class
test_invariants:
  - "The context delegates all state-dependent behavior to the current state object"
  - "A transition leaves the context in exactly the target state, no more"
  - "State-specific behavior is unreachable from states that do not allow it"
  - "Context class contains no conditional logic branching on its own state field"
---

# State

## Intent

Allow an object to alter its behavior when its internal state changes. The object will appear to change its class. State-specific behavior is extracted into separate state classes; the context object delegates all behavior to the current state and swaps the state object when a transition occurs. This eliminates large conditional blocks that branch on an internal status flag.

## Structure

```
Context
  - state: State
  + request(): void   { state.handle(this) }
  + setState(s: State): void

State (interface)
  + handle(context: Context): void

ConcreteStateA                 ConcreteStateB
  + handle(context): void        + handle(context): void
    { do A behavior;               { do B behavior;
      context.setState(new B()) }    context.setState(new A()) }
```

Roles:
- **Context** — maintains a reference to the current state; clients interact with context only
- **State** — declares the interface for state-specific behavior
- **ConcreteState** — implements behavior for one state; may trigger transitions

## Applicability

- An object's behavior depends on its state and must change at runtime
- Operations have large multi-part conditionals that branch on state flags or enums
- Finite state machines: order lifecycle, TCP connections, vending machines, UI wizard flows
- State transitions need to be explicit and auditable
- When adding a new state should not require modifying existing state classes

## Consequences

- **Localizes state-specific behavior** — each state class encapsulates one mode's logic
- **Explicit transitions** — state changes are visible and traceable
- **Open/Closed for states** — new states added without touching context or other states (if transitions are managed by states themselves)
- **Increased class count** — one class per state; may be overkill for simple two-state toggles
- **Transition ownership ambiguity** — context or state can own transitions; inconsistency causes bugs
- **Shared-state risk** — if state objects are singletons, they must be stateless themselves

## OOP shape

```
interface State {
  handle(context: Context): void
}

class Context {
  private state: State

  constructor(initial: State) { this.state = initial }
  setState(s: State): void    { this.state = s }
  request(): void             { this.state.handle(this) }
}

class IdleState implements State {
  handle(ctx: Context): void {
    // idle behavior
    ctx.setState(new ProcessingState())
  }
}

class ProcessingState implements State {
  handle(ctx: Context): void {
    // processing behavior
    ctx.setState(new IdleState())
  }
}
```

## FP shape

```
// State machine as a pure data + transition function
type StateName = "idle" | "processing" | "done" | "error"

type Transition<Input, S extends StateName> = {
  next: S
  sideEffect?: (input: Input) => void
}

type Machine<Input> = {
  [S in StateName]: (input: Input) => Transition<Input, StateName>
}

// Each state is a function: input => next state + side effects
// No class; no mutable flag; transition table is data
const machine: Machine<AppEvent> = {
  idle:       (e) => e.type === "start" ? { next: "processing" } : { next: "idle" },
  processing: (e) => e.type === "done"  ? { next: "done" }       : { next: "error" },
  done:       (_) => ({ next: "done" }),
  error:      (_) => ({ next: "idle" }),
}

// XState / Redux reducers follow this exact shape
```

## Smells fixed

- **long-conditional-chain** — a cascade of `if (state === "X") ... else if (state === "Y")` in every method is replaced by polymorphic dispatch to state objects
- **switch-on-type** — `switch (this.status)` blocks across multiple methods collapse; each case becomes its own state class
- **large-class** — a context class bloated with all state-specific branches is decomposed into focused state classes
- **mutable-shared-state** — a raw status flag mutated across many methods is replaced by a controlled state-object swap through `setState`

## Tests implied

- **Pure delegation** — calling `context.request()` in a given state invokes exactly the current state's `handle`; verify no conditional logic in context
- **Transition completeness** — after a triggering event, `context` holds the exact expected target state; assert with `instanceof` or identity check
- **Unreachable behavior** — assert that calling a state-specific operation when in an incompatible state raises an explicit error or no-ops (never silently executes)
- **Context stays clean** — grep the context class for `switch`/`if (this.state ===` patterns; there should be none

## Sources

- https://refactoring.guru/design-patterns/state
