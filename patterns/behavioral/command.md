---
name: command
category: behavioral
aliases: [action, transaction]
intent: >-
  Encapsulate a request as an object, enabling parameterization, queuing, logging, and undo/redo
sources:
  - https://refactoring.guru/design-patterns/command
smells_it_fixes:
  - long-parameter-list
  - duplicate-error-handling
  - temporal-coupling
  - inappropriate-intimacy
smells_it_introduces:
  - speculative-generality
  - over-abstraction-single-variant
composes_with:
  - composite
  - memento
  - chain-of-responsibility
  - observer
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "Executing a command produces the same observable side-effect as calling the operation directly"
  - "An undoable command followed by undo leaves state identical to before execute"
  - "Commands can be serialized and replayed to reproduce the same outcome"
  - "The invoker never inspects command internals to decide how to invoke it"
---

# Command

## Intent

Turn a request into a standalone object that contains all information about the request — the receiver, the method to call, and the arguments. This decouples the object that invokes the operation from the one that knows how to perform it, and enables deferred execution, undo/redo, queueing, logging, and macro composition.

## Structure

```
Client ──creates──> ConcreteCommand
                        |
Invoker ──calls──> Command.execute()
                        |
                        v
                    Receiver.action()

Command (interface)
  + execute(): void
  + undo(): void        // optional

ConcreteCommand
  - receiver: Receiver
  - params: ...
  + execute(): void  { receiver.action(params) }
  + undo(): void     { receiver.rollback(params) }
```

Roles:
- **Command** — declares the execution interface
- **ConcreteCommand** — binds a receiver and parameters; implements execute/undo
- **Receiver** — knows how to perform the actual work
- **Invoker** — holds and fires commands without knowing their concrete type
- **Client** — creates and wires commands

## Applicability

- Operations need to be parameterized, queued, scheduled, or logged
- Undo/redo functionality is required
- Transactional behavior (all-or-nothing groups of operations)
- GUI actions, macro recording, job queues, event sourcing
- Decoupling UI layer from business logic

## Consequences

- **Decoupled invoker/receiver** — invoker is ignorant of receiver internals
- **Undo/redo** — commands store state needed to reverse themselves
- **Composability** — macro commands (Composite) aggregate smaller commands
- **Audit log** — command history doubles as an event log
- **Class proliferation** — one class per operation can lead to many small classes
- **Complexity** — simple direct calls become wrapped objects; overhead for trivial cases

## OOP shape

```
interface Command {
  execute(): void
  undo(): void
}

class ConcreteCommand implements Command {
  constructor(
    private receiver: Receiver,
    private params: Params
  ) {}

  execute(): void { this.receiver.doWork(this.params) }
  undo(): void    { this.receiver.undoWork(this.params) }
}

class Invoker {
  private history: Command[] = []

  run(cmd: Command): void {
    cmd.execute()
    this.history.push(cmd)
  }

  undoLast(): void {
    this.history.pop()?.undo()
  }
}
```

## FP shape

```
// A command is simply a closure capturing its arguments
type Command = () => void
type UndoableCommand = { execute: () => void; undo: () => void }

// Factory produces commands from data
const makeDeleteCommand = (store: Store, id: Id): UndoableCommand => {
  const snapshot = store.get(id)
  return {
    execute: () => store.delete(id),
    undo:    () => store.put(id, snapshot),
  }
}

// History stack is just an array of UndoableCommand
const runWithUndo = (history: UndoableCommand[], cmd: UndoableCommand) => {
  cmd.execute()
  return [...history, cmd]
}
```

## Smells fixed

- **long-parameter-list** — instead of passing many arguments through call sites, they are captured inside the command object at construction time
- **duplicate-error-handling** — retry/rollback logic lives once in the invoker rather than scattered across callers
- **temporal-coupling** — execution can be deferred to any point after construction, removing tight time coupling between creation and invocation
- **inappropriate-intimacy** — the invoker no longer needs to know receiver internals; the command object mediates

## Tests implied

- **Execute equivalence** — `command.execute()` produces the same state change as calling `receiver.action(params)` directly
- **Undo symmetry** — `execute()` then `undo()` leaves the system in its pre-execute state
- **Replay determinism** — serializing and replaying a command sequence reproduces identical final state
- **Invoker opacity** — the invoker holds only `Command` references; it cannot call receiver methods directly

## Sources

- https://refactoring.guru/design-patterns/command
