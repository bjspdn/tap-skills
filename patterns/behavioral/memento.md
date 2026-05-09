---
name: memento
category: behavioral
aliases: [snapshot, token]
intent: >-
  Capture and externalise an object's internal state so it can be restored later without violating encapsulation
sources:
  - https://refactoring.guru/design-patterns/memento
smells_it_fixes:
  - inappropriate-intimacy
  - mutable-shared-state
  - temporal-coupling
smells_it_introduces:
  - speculative-generality
  - large-class
composes_with:
  - command
  - iterator
  - prototype
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "Restoring from a memento returns the originator to exactly the state captured at save time"
  - "The caretaker cannot read or modify memento internals"
  - "Creating a memento does not alter the originator's current state"
  - "Successive save/restore cycles are independent; restoring one does not corrupt others"
---

# Memento

## Intent

Without violating encapsulation, capture and externalise an object's internal state into a memento object so the object can be restored to that state later. The originator is the only class that can write to and read from a memento; the caretaker stores mementos but treats them as opaque tokens. This enables undo/redo, checkpointing, and transaction rollback without leaking private state.

## Structure

```
Originator
  - state: State
  + save(): Memento        { return new Memento(this.state) }
  + restore(m: Memento)    { this.state = m.getState() }

Memento
  - state: State           // private — only Originator can read
  + getState(): State      // package/friend access in OOP languages

Caretaker
  - history: Memento[]
  + doSomething(): void    { history.push(originator.save()); originator.mutate() }
  + undo(): void           { originator.restore(history.pop()) }
```

Roles:
- **Originator** — the object whose state is saved; creates and consumes mementos
- **Memento** — opaque snapshot of originator state; ideally immutable
- **Caretaker** — requests saves, stores mementos, triggers restores; never inspects memento contents

## Applicability

- Undo/redo in editors, drawing tools, games
- Transaction rollback — save state before a risky operation
- Checkpointing long-running processes
- Snapshotting for testing or debugging (before/after assertion)
- When direct state exposure (getter/setter explosion) would violate encapsulation

## Consequences

- **Encapsulation preserved** — originator's internals never exposed to caretaker
- **Simple undo/redo** — caretaker maintains a stack of mementos; undo = pop + restore
- **Memory cost** — deep or frequent snapshots of large objects are expensive
- **Language-dependent encapsulation** — many languages lack friend/package-private access; memento internals may leak
- **Stale references** — if state contains live objects (not copies), mementos may not be truly isolated

## OOP shape

```
class Memento {
  // Only Originator accesses this — enforced via friend class or package privacy
  private constructor(private readonly state: DeepReadonly<State>) {}

  static create(state: State): Memento { return new Memento(deepCopy(state)) }
  getState(): State { return deepCopy(this.state) }  // defensive copy on read
}

class Originator {
  private state: State

  mutate(change: Change): void { applyChange(this.state, change) }
  save(): Memento { return Memento.create(this.state) }
  restore(m: Memento): void { this.state = m.getState() }
}

class Caretaker {
  private history: Memento[] = []

  constructor(private originator: Originator) {}

  checkpoint(): void { this.history.push(this.originator.save()) }
  undo(): void {
    const m = this.history.pop()
    if (m) this.originator.restore(m)
  }
}
```

## FP shape

```
// State is immutable by default — every mutation returns a new snapshot
type State = Readonly<{ ... }>

// "Memento" is just the previous state value — no special class needed
type History<S> = S[]

const save = <S>(history: History<S>, current: S): History<S> =>
  [...history, current]

const undo = <S>(history: History<S>): [History<S>, S | undefined] => {
  const prev = history[history.length - 1]
  return [history.slice(0, -1), prev]
}

// Redux-style: state is always a snapshot; time-travel = index into history array
// Immutable data structures make save/restore O(1) with structural sharing
```

## Smells fixed

- **inappropriate-intimacy** — code that reads/writes originator private fields externally to save state is replaced by the save/restore API
- **mutable-shared-state** — multiple parties mutating shared state are replaced by explicit snapshot tokens passed through the caretaker
- **temporal-coupling** — operations that depended on performing a save at exactly the right moment are made explicit through the save/restore contract

## Tests implied

- **Round-trip fidelity** — `originator.restore(originator.save())` leaves state byte-for-byte equal to the pre-save state
- **Caretaker opacity** — the caretaker test suite holds only `Memento` references; it must not access any state fields on them
- **Non-mutating save** — calling `save()` does not alter the originator's observable behavior before and after; verify with pre/post state equality
- **History independence** — saving at points T1 and T2, then restoring T1, restores T1's state — not T2's; verify with distinct snapshots

## Sources

- https://refactoring.guru/design-patterns/memento
