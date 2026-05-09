---
name: observer
category: behavioral
aliases: [event-subscriber, listener, publish-subscribe]
intent: >-
  Define a one-to-many dependency so that when one object changes state, all dependents are notified automatically
sources:
  - https://refactoring.guru/design-patterns/observer
smells_it_fixes:
  - inappropriate-intimacy
  - shotgun-surgery
  - temporal-coupling
  - feature-envy
smells_it_introduces:
  - mutable-shared-state
  - temporal-coupling
composes_with:
  - mediator
  - singleton
  - command
  - strategy
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "All registered observers are notified exactly once per subject state change"
  - "Unsubscribed observers receive no further notifications"
  - "Observer notification order is consistent or explicitly documented as unordered"
  - "Subject state is fully updated before any observer is notified"
---

# Observer

## Intent

Define a one-to-many dependency between objects so that when one object (the subject) changes state, all its dependents (observers) are notified and updated automatically. Observer decouples the subject from knowing which objects depend on it; observers register and deregister themselves dynamically. The pattern is foundational to event-driven architectures, reactive UIs, and pub/sub messaging.

## Structure

```
Subject (Observable)
  - observers: Observer[]
  + subscribe(o: Observer): void
  + unsubscribe(o: Observer): void
  + notify(): void         { observers.forEach(o => o.update(this)) }
  - state: State

Observer (interface)
  + update(subject: Subject): void

ConcreteObserverA     ConcreteObserverB
  + update(subject)     + update(subject)
    { reads state }       { reads state }
```

Roles:
- **Subject / Observable** — holds state; maintains observer list; triggers notifications
- **Observer** — receives update notifications; pulls or receives current state
- **ConcreteObserver** — implements reaction logic for a specific concern
- **Client** — wires observers to subjects; manages subscription lifecycle

## Applicability

- A change in one object requires changing others, and you don't know how many objects need to change
- An object should be able to notify other objects without knowing who they are
- GUI MVC: model notifies views of data changes
- Event systems, reactive streams, domain event publishing
- Cross-cutting concerns (logging, metrics, audit) that should not be wired into domain code

## Consequences

- **Loose coupling** — subject knows only the Observer interface; concrete observers are invisible to it
- **Broadcast communication** — one state change fans out to all observers at once
- **Dynamic subscriptions** — observers can join/leave at runtime
- **Unexpected update cascades** — one observer's reaction may trigger further notifications
- **Memory leaks** — forgotten subscriptions prevent garbage collection of observers
- **Non-deterministic ordering** — notification order may vary; observers must not assume a sequence
- **Debugging difficulty** — tracing which update triggered a side effect requires following subscription graphs

## OOP shape

```
interface Observer<T> {
  update(state: T): void
}

class Subject<T> {
  private observers: Set<Observer<T>> = new Set()
  private state: T

  subscribe(o: Observer<T>): void   { this.observers.add(o) }
  unsubscribe(o: Observer<T>): void { this.observers.delete(o) }

  setState(state: T): void {
    this.state = state
    this.notify()
  }

  private notify(): void {
    for (const o of this.observers) o.update(this.state)
  }
}

class LoggingObserver implements Observer<AppState> {
  update(state: AppState): void { log(state) }
}
```

## FP shape

```
// Observer = stream / signal / reactive value
// Subject = writable signal or event emitter

// Minimal reactive cell
type Signal<T> = {
  get: () => T
  set: (val: T) => void
  subscribe: (fn: (val: T) => void) => () => void  // returns unsubscribe
}

const createSignal = <T>(initial: T): Signal<T> => {
  let value = initial
  const subs = new Set<(v: T) => void>()
  return {
    get: () => value,
    set: (v) => { value = v; subs.forEach(fn => fn(v)) },
    subscribe: (fn) => { subs.add(fn); return () => subs.delete(fn) },
  }
}

// RxJS / reactive streams: Observable.pipe(map, filter, debounce...)
// Observers are just plain functions subscribed to the stream
```

## Smells fixed

- **inappropriate-intimacy** — components that directly query each other's state on every change are replaced by a subscription model
- **shotgun-surgery** — adding a new reaction to an event requires only creating a new observer, not modifying the subject or every existing reaction
- **temporal-coupling** — the subject no longer needs to know when observers are ready; they register themselves
- **feature-envy** — logic that "polls" another object's state is replaced by a push notification via update

## Tests implied

- **Complete fanout** — after `setState`, every registered observer's `update` is called with the new state; verify with spies on all registered instances
- **Unsubscribe stops delivery** — after `unsubscribe`, a subsequent `setState` does not invoke the removed observer
- **Notification consistency** — observers receive the fully updated state; assert that reading any state field inside `update` returns post-change values
- **Ordering documentation** — if notification order matters, document and test it; otherwise assert that all observers receive the event regardless of registration order

## Sources

- https://refactoring.guru/design-patterns/observer
