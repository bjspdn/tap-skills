---
name: cqrs
category: architectural
aliases: []
intent: >-
  Separate read and write models so each can be optimised, scaled, and evolved independently
sources:
  - https://martinfowler.com/bliki/CQRS.html
  - https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
smells_it_fixes:
  - god-class
  - divergent-change
  - large-class
smells_it_introduces:
  - over-abstraction-single-variant
  - small-class-proliferation
composes_with:
  - command
  - observer
  - mediator
  - repository
clashes_with: []
test_invariants:
  - "A command never returns domain data beyond an acknowledgement or identifier"
  - "A query never mutates state"
  - "The read model eventually reflects every accepted write"
  - "Command and query models can be deployed and scaled independently"
---

# CQRS

## Intent

Command Query Responsibility Segregation splits a single model that handles both reads and writes into two distinct models: a write model (commands) optimised for enforcing invariants and processing state transitions, and a read model (queries) optimised for serving data in the shapes consumers need. Each side can use different data stores, schemas, and scaling strategies. CQRS is particularly effective in domains where read and write workloads have very different performance profiles or where the shape of data needed for display diverges significantly from the shape needed to enforce business rules.

## Structure

```
                     ┌─────────────┐
  Client ──command──>│ Write Model │──events/sync──> Projection
                     │ (commands)  │                    │
                     └─────────────┘                    ▼
                                                 ┌────────────┐
  Client ──query──────────────────────────────>  │ Read Model  │
                                                 │ (queries)   │
                                                 └────────────┘
```

Roles:
- **Command** — intent to mutate state; validated and processed by the write model
- **Write Model** — enforces invariants, executes business rules, persists authoritative state
- **Read Model** — denormalised projection optimised for query performance
- **Projection / Synchroniser** — keeps the read model up to date (sync or async)
- **Query** — a request for data; served entirely by the read model

## Applicability

- Read and write workloads differ dramatically in volume, shape, or latency requirements.
- The domain model for writes is complex (aggregates, invariants), but read views are flat and denormalised.
- You need to scale reads independently of writes (e.g., many dashboard consumers, few order processors).
- Multiple read representations of the same data are needed (search index, analytics view, API response).

## Consequences

**Gains**
- Each model is simpler — writes enforce rules, reads serve shapes; neither carries the other's concerns.
- Independent scalability: read replicas can be added without affecting the write path.
- Flexibility to use different storage technologies for reads vs. writes.
- Cleaner domain model: aggregates focus on invariants, not on answering UI queries.

**Costs**
- Eventual consistency between write and read models must be understood and communicated to users.
- Increased infrastructure complexity: two data stores, a synchronisation mechanism, monitoring for lag.
- Small-class proliferation: separate command handlers, query handlers, DTOs, projections.
- Overkill for simple CRUD applications where read and write shapes are essentially identical.

## OOP shape

```
// Command side
class PlaceOrderCommand
  customerId: CustomerId
  items: List[LineItem]

class PlaceOrderHandler
  constructor(repo: OrderWriteRepository)
  handle(cmd: PlaceOrderCommand): OrderId
    order = Order.create(cmd.customerId, cmd.items)
    this.repo.save(order)
    return order.id

// Query side
class OrderSummaryQuery
  customerId: CustomerId

class OrderSummaryHandler
  constructor(readStore: OrderReadStore)
  handle(query: OrderSummaryQuery): List<OrderSummaryDto>
    return this.readStore.findByCustomer(query.customerId)

// Projection keeps read store in sync
class OrderProjection
  constructor(readStore: OrderReadStore)
  onOrderPlaced(event: OrderPlacedEvent): void
    this.readStore.upsert(OrderSummaryDto.from(event))
```

## FP shape

```
// Command handler — returns only an id or acknowledgement
handlePlaceOrder :: OrderWriteRepo -> PlaceOrderCommand -> Effect[OrderId]
handlePlaceOrder(repo, cmd) =
  order = createOrder(cmd.customerId, cmd.items)
  repo.save(order)
  pure(order.id)

// Query handler — pure read, no side effects on domain state
queryOrderSummary :: OrderReadStore -> CustomerId -> Effect[List[OrderSummaryDto]]
queryOrderSummary(store, custId) =
  store.findByCustomer(custId)

// Projection — maps events to read-model updates
projectOrderPlaced :: OrderReadStore -> OrderPlacedEvent -> Effect[Unit]
projectOrderPlaced(store, event) =
  store.upsert(summaryFrom(event))
```

## Smells fixed

- **god-class** — a monolithic service class that mixed query methods with mutation methods is split into focused command handlers and query handlers, each with a single responsibility.
- **divergent-change** — the write model changes when business rules evolve; the read model changes when UI needs change; neither forces a change in the other.
- **large-class** — aggregate roots bloated with query convenience methods shed that weight to the read model, keeping the write model lean.

## Tests implied

- **Commands return no domain data** — assert that every command handler's return type is void, an ID, or a simple acknowledgement; never a full domain object or DTO.
- **Queries are side-effect-free** — run a query, then verify the write model's state is unchanged; queries are pure reads.
- **Read model eventually consistent** — publish a command, wait for projection, then assert the read model reflects the change within a bounded time window.
- **Independent deployment** — build and start the read service and write service in separate processes; both health-check green independently.

## Sources

- https://martinfowler.com/bliki/CQRS.html
- https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
