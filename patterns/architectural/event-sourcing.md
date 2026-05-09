---
name: event-sourcing
category: architectural
aliases: []
intent: >-
  Persist state as an append-only sequence of domain events rather than mutable current-state snapshots
sources:
  - https://martinfowler.com/eaaDev/EventSourcing.html
smells_it_fixes:
  - mutable-shared-state
  - temporal-coupling
smells_it_introduces:
  - over-abstraction-single-variant
  - large-class
composes_with:
  - cqrs
  - command
  - observer
  - memento
clashes_with: []
test_invariants:
  - "Replaying all events from an empty state reproduces the current aggregate state exactly"
  - "The event store is append-only — no event is ever modified or deleted"
  - "Each event is self-describing and carries all data needed to reconstruct the state change"
  - "Aggregate state can be rebuilt from any point-in-time snapshot plus subsequent events"
---

# Event Sourcing

## Intent

Event Sourcing captures every change to application state as an immutable domain event appended to a log. Instead of storing only the current state, the system stores the full history of state transitions. Current state is derived by replaying events from the beginning (or from a snapshot). This gives the system a complete audit trail, enables temporal queries ("what was the state last Tuesday?"), and supports rebuilding read models or projections from the authoritative event stream.

## Structure

```
Command ──> Aggregate ──> Event(s) ──append──> Event Store
                                                   │
                                          replay / subscribe
                                                   │
                                    ┌──────────────┼──────────────┐
                                    ▼              ▼              ▼
                              Read Model     Analytics       Audit Log
                              Projection     Projection
```

Roles:
- **Event** — immutable record of something that happened, expressed in past tense (OrderPlaced, PaymentReceived)
- **Event Store** — append-only log that persists events in order
- **Aggregate** — applies a command by emitting events; rebuilds its state by replaying its own events
- **Projection** — subscribes to events and maintains a derived read model
- **Snapshot** (optional) — periodic checkpoint of aggregate state to speed up replay

## Applicability

- Audit and compliance requirements demand a full history of every state change.
- The domain benefits from temporal queries or the ability to rewind and replay state.
- You need to build multiple, independent read models from the same source of truth.
- CQRS is already in use and you want an authoritative event stream to feed projections.
- Debugging production issues requires knowing exactly what sequence of events led to the current state.

## Consequences

**Gains**
- Complete audit trail: every state change is recorded with its payload and timestamp.
- Temporal queries: reconstruct the state of any aggregate at any point in time.
- Decoupled projections: new read models can be created by replaying the existing event stream.
- Natural fit with CQRS: events bridge the write model to read-model projections.

**Costs**
- Event schema evolution: changing event shapes requires versioning and upcasting strategies.
- Replay time grows with event count; snapshots add implementation complexity.
- Eventual consistency: projections lag behind the event store; UI must handle stale reads.
- Steeper learning curve: developers must think in events rather than mutable state.
- Storage growth: the event log grows indefinitely; archival and compaction policies are needed.

## OOP shape

```
// Event
class OrderPlacedEvent
  orderId: OrderId
  customerId: CustomerId
  items: List[LineItem]
  occurredAt: Timestamp

// Aggregate
class Order
  - state: OrderState
  + static rehydrate(events: List[Event]): Order
      order = new Order()
      events.forEach(e -> order.apply(e))
      return order
  + place(cmd: PlaceOrderCommand): List[Event]
      validate(cmd)
      return [OrderPlacedEvent(cmd)]
  - apply(event: Event): void
      match event
        OrderPlacedEvent -> this.state = OrderState.placed(event)
        OrderShippedEvent -> this.state = this.state.ship(event)

// Event Store
interface EventStore
  append(aggregateId: AggregateId, events: List[Event], expectedVersion: Int): void
  load(aggregateId: AggregateId): List[Event]
```

## FP shape

```
// Events as a union type
type OrderEvent
  = OrderPlaced { orderId, customerId, items, occurredAt }
  | OrderShipped { orderId, carrier, occurredAt }
  | OrderCancelled { orderId, reason, occurredAt }

// State reconstruction via fold
type OrderState = { status, items, ... }

applyEvent :: OrderState -> OrderEvent -> OrderState
applyEvent(state, OrderPlaced(e))   = { status: "placed", items: e.items, ... }
applyEvent(state, OrderShipped(e))  = { ...state, status: "shipped" }
applyEvent(state, OrderCancelled(e)) = { ...state, status: "cancelled" }

rehydrate :: List[OrderEvent] -> OrderState
rehydrate = foldl(applyEvent, emptyState)

// Command handler emits events
placeOrder :: PlaceOrderCmd -> OrderState -> Either[Error, List[OrderEvent]]
placeOrder(cmd, state) =
  if state.status != "empty" then Left(AlreadyPlaced)
  else Right([OrderPlaced { ... }])
```

## Smells fixed

- **mutable-shared-state** — instead of mutating a single row in place (where concurrent updates can conflict silently), each state change is a new immutable event appended to the log; conflicts are detected by version checks.
- **temporal-coupling** — the explicit event sequence captures causality; replaying events in order guarantees correct state reconstruction, eliminating hidden dependencies on execution timing.

## Tests implied

- **Replay reproduces state** — given a known list of events, assert that replaying them onto an empty aggregate produces the expected current state. Property test: for any valid command sequence, replay(events(commands)) == finalState.
- **Append-only store** — attempt to update or delete an existing event; assert the operation is rejected or not exposed by the API.
- **Self-describing events** — deserialise each event type from its serialised form; assert all fields are present and no external context is required to interpret the event.
- **Snapshot + tail replay** — take a snapshot at event N, replay events N+1..M, assert the result matches a full replay from event 1..M.

## Sources

- https://martinfowler.com/eaaDev/EventSourcing.html
