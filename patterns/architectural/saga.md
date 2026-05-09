---
name: saga
category: architectural
aliases: [process-manager]
intent: >-
  Coordinate a multi-step business transaction across services using a sequence of local transactions with compensating actions
sources:
  - https://microservices.io/patterns/data/saga.html
smells_it_fixes:
  - god-class
  - long-method
  - temporal-coupling
  - duplicate-error-handling
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
composes_with:
  - command
  - state
  - observer
  - mediator
clashes_with: []
test_invariants:
  - "Every step has a corresponding compensating action that undoes its effect"
  - "If any step fails, all previously completed steps are compensated in reverse order"
  - "The saga reaches a terminal state (completed or fully compensated) for every possible failure scenario"
  - "Each local transaction is atomic — partial step execution does not occur"
---

# Saga

## Intent

A Saga manages a long-running business process that spans multiple services or bounded contexts, where a single distributed transaction (two-phase commit) is impractical or impossible. It decomposes the process into a sequence of local transactions, each paired with a compensating action. If a step fails, the saga executes compensating actions for all previously completed steps in reverse order, bringing the system back to a consistent state. Sagas can be orchestrated (a central coordinator directs each step) or choreographed (each service reacts to events and triggers the next step).

## Structure

```
Orchestrator variant:

  Saga Orchestrator
    step1() ──> Service A ──ok──> step2() ──> Service B ──ok──> step3() ──> Service C
                                                                  │
                                                               fail
                                                                  │
                                              compensate2() <─────┘
                                                  │
                                           compensate1() <── done (rolled back)

Choreography variant:

  Service A ──event──> Service B ──event──> Service C
       ▲                                      │
       └────── compensating events ◄──────────┘ (on failure)
```

Roles:
- **Saga Orchestrator** (orchestration) — central coordinator that drives the step sequence and triggers compensations on failure
- **Participant / Step** — a service or module that executes one local transaction and exposes a compensating action
- **Compensating Action** — a semantic undo for a completed step (e.g., refund payment, release reservation)
- **Saga State** — tracks which steps have completed and which need compensation

## Applicability

- A business process spans multiple services or bounded contexts that cannot share a single ACID transaction.
- Each step must be independently committable but the overall process must be logically atomic.
- Compensating actions are semantically meaningful (cancel reservation, issue refund, restore inventory).
- You need visibility into the progress of long-running processes for monitoring and debugging.

## Consequences

**Gains**
- Avoids distributed transactions: each service uses its own local transaction with no two-phase commit.
- Explicit failure handling: compensating actions make rollback logic visible and testable.
- Supports long-running processes that may span minutes, hours, or days.
- Orchestrator variant provides a single place to see the entire process flow.

**Costs**
- Compensating actions are not always a perfect undo (e.g., a sent email cannot be unsent; only a correction email can follow).
- Increased complexity: every step doubles the implementation surface (forward + compensate).
- Intermediate inconsistency: between steps, the system is in a partially completed state visible to other readers.
- Choreography variant can become hard to follow when many services react to many events.
- Testing all failure permutations requires combinatorial effort.

## OOP shape

```
// Saga step definition
class SagaStep
  action: () -> StepResult
  compensate: () -> void

// Orchestrator
class OrderSaga
  constructor(steps: List[SagaStep])
  execute(): SagaOutcome
    completed = []
    for step in this.steps
      result = step.action()
      if result.failed
        completed.reverse().forEach(s -> s.compensate())
        return SagaOutcome.rolledBack(result.error)
      completed.add(step)
    return SagaOutcome.completed()

// Concrete steps
reserveInventory = SagaStep(
  action:     () -> inventoryService.reserve(orderId, items),
  compensate: () -> inventoryService.releaseReservation(orderId)
)
chargePayment = SagaStep(
  action:     () -> paymentService.charge(orderId, amount),
  compensate: () -> paymentService.refund(orderId, amount)
)
```

## FP shape

```
// A step is a pair of effectful functions
type SagaStep = { action: Effect[StepResult], compensate: Effect[Unit] }

// Run saga: fold over steps, accumulating compensation stack
runSaga :: List[SagaStep] -> Effect[SagaOutcome]
runSaga(steps) = go(steps, [])
  where
    go([], _compensations) = pure(Completed)
    go(step :: rest, compensations) =
      result <- step.action
      case result of
        Ok    -> go(rest, step.compensate :: compensations)
        Fail(e) -> sequence(compensations) >> pure(RolledBack(e))

// Usage
orderSaga = runSaga([reserveInventory, chargePayment, scheduleShipment])
```

## Smells fixed

- **god-class** — a monolithic transaction coordinator that handled every step, error case, and rollback inline is decomposed into discrete, testable saga steps with explicit compensations.
- **long-method** — a single method that orchestrated the entire multi-service process is replaced by a declarative step list, each step a focused unit.
- **temporal-coupling** — the saga makes step ordering explicit and enforces it; hidden dependencies on execution sequence become visible in the step chain.
- **duplicate-error-handling** — scattered try/catch blocks that attempted ad-hoc rollback in each caller are replaced by systematic compensation logic in the saga runner.

## Tests implied

- **Every step has a compensation** — assert that the saga definition contains a compensating action for each forward action; no step is left without a rollback path.
- **Failure triggers reverse compensation** — simulate failure at step N; assert that steps N-1 through 1 are compensated in reverse order and the saga reports a rolled-back outcome.
- **All paths reach terminal state** — for each possible step failure point (including step 1 and the last step), run the saga and assert it reaches either "completed" or "fully compensated."
- **Steps are atomic** — verify that each step either fully completes or fully fails; no partial side effects leak from a failed step.

## Sources

- https://microservices.io/patterns/data/saga.html
