---
name: mediator
category: behavioral
aliases: [intermediary, controller]
intent: >-
  Define an object that encapsulates how a set of objects interact, reducing direct dependencies between them
sources:
  - https://refactoring.guru/design-patterns/mediator
smells_it_fixes:
  - inappropriate-intimacy
  - shotgun-surgery
  - god-class
  - mutable-shared-state
smells_it_introduces:
  - god-class
  - large-class
composes_with:
  - observer
  - facade
  - command
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "Colleagues communicate only through the mediator, never directly with each other"
  - "Removing a colleague does not require changes to other colleagues"
  - "The mediator correctly routes a notification to all registered interested colleagues"
  - "Adding a new colleague requires changes only in the mediator"
---

# Mediator

## Intent

Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and lets you vary their interaction independently. Components (colleagues) send events to the mediator; the mediator decides who else is notified and how. This centralizes complex many-to-many communication into one place.

## Structure

```
Colleague A ──notifies──> Mediator <──notifies── Colleague B
     ^                       |                        ^
     |                    routes                      |
     └────────────────────────────────────────────────┘
             (never communicate directly)

Mediator (interface)
  + notify(sender: Colleague, event: Event): void

ConcreteMediator
  - colleagueA: ColleagueA
  - colleagueB: ColleagueB
  + notify(sender, event): void { ... dispatch logic ... }

Colleague (abstract)
  - mediator: Mediator
  + triggerEvent(event): void { mediator.notify(this, event) }
```

Roles:
- **Mediator** — defines the communication contract between colleagues
- **ConcreteMediator** — implements coordination; knows all colleagues
- **Colleague** — knows only the mediator; sends/receives events through it

## Applicability

- A set of objects communicate in complex, hard-to-understand ways; many-to-many connections exist
- Reusing a component is difficult because it references too many other components
- Distributed behavior should be customizable without subclassing every participant
- GUI form logic: enabling/disabling controls based on other controls' state
- Air traffic control, chat room, event bus

## Consequences

- **Reduced coupling** — colleagues have no direct references to each other
- **Centralized control flow** — interaction logic lives in one place; easier to understand holistically
- **Easier colleague reuse** — components become more self-contained
- **Mediator becomes a god object** — all cross-component logic accumulates; can become a large-class smell
- **Single point of failure** — mediator complexity grows with every new interaction
- **Harder to test individual interactions** — must route through mediator to observe colleague behavior

## OOP shape

```
interface Mediator {
  notify(sender: Colleague, event: string): void
}

abstract class Colleague {
  constructor(protected mediator: Mediator) {}
  protected trigger(event: string): void {
    this.mediator.notify(this, event)
  }
}

class ConcreteMediator implements Mediator {
  constructor(
    private a: ColleagueA,
    private b: ColleagueB
  ) {}

  notify(sender: Colleague, event: string): void {
    if (sender === this.a && event === "changed") {
      this.b.reactToA()
    } else if (sender === this.b && event === "submitted") {
      this.a.lockDown()
    }
  }
}
```

## FP shape

```
// Mediator as a message bus / event dispatcher
type Event = { sender: string; type: string; payload: unknown }
type Handler = (event: Event) => void

// Mediator is a registry + dispatch function — no shared mutable objects
const createMediator = () => {
  const routes = new Map<string, Handler[]>()

  return {
    register: (eventType: string, handler: Handler) => {
      routes.set(eventType, [...(routes.get(eventType) ?? []), handler])
    },
    dispatch: (event: Event) => {
      (routes.get(event.type) ?? []).forEach(h => h(event))
    },
  }
}

// Colleagues publish to and subscribe from the mediator only
// No direct imports between colleague modules
```

## Smells fixed

- **inappropriate-intimacy** — colleague classes that import and call each other are decoupled; they only reference the mediator interface
- **shotgun-surgery** — adding a new interaction requires only a change in the mediator, not in every affected colleague
- **god-class** — a single component that orchestrates many others has its coordination logic extracted into an explicit mediator
- **mutable-shared-state** — shared mutable objects passed between colleagues are replaced by explicit event messages through the mediator

## Tests implied

- **No direct coupling** — inspect colleague classes for imports or references to other colleague types; none should exist
- **Correct routing** — when colleague A fires event X, assert that the mediator calls the expected method on colleague B (and only B)
- **Isolated removal** — removing or replacing colleague C requires zero changes in A or B; verify by substituting a stub for C
- **Extension locality** — adding a new colleague type and registering it with the mediator leaves existing colleagues' tests green

## Sources

- https://refactoring.guru/design-patterns/mediator
