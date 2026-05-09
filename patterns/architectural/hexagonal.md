---
name: hexagonal
category: architectural
aliases: [ports-and-adapters]
intent: >-
  Isolate core business logic from external concerns by expressing dependencies as ports and plugging in adapters
sources:
  - https://alistair.cockburn.us/hexagonal-architecture/
  - https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)
smells_it_fixes:
  - inappropriate-intimacy
  - feature-envy
  - divergent-change
  - shotgun-surgery
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
composes_with:
  - adapter
  - facade
  - strategy
  - factory-method
clashes_with:
  - singleton
test_invariants:
  - "Domain logic executes without any concrete adapter wired in"
  - "Swapping one adapter for another does not change any domain test"
  - "No import of infrastructure types appears inside the domain hexagon"
  - "Each port has at least one test double and one real adapter"
---

# Hexagonal

## Intent

Hexagonal Architecture (Ports & Adapters) structures an application so that the core domain logic sits at the center, fully decoupled from external systems. The domain defines ports — abstract contracts for the capabilities it needs (driven side) and the actions it offers (driving side). Concrete adapters implement these ports, connecting the domain to databases, UIs, message brokers, or any other external technology. The result is a codebase where the most valuable logic can be developed, tested, and reasoned about independently of delivery mechanisms.

## Structure

```
                   Driving side                     Driven side
                   (primary)                        (secondary)

   UI Adapter ──┐                              ┌── DB Adapter
  CLI Adapter ──┤── Driving Port ── DOMAIN ── Driven Port ──┤── Queue Adapter
  API Adapter ──┘   (inbound)      (core)     (outbound)    └── FS Adapter
```

Roles:
- **Domain (Hexagon)** — pure business logic, owns all rules, has no outward dependency
- **Driving Port** — interface the domain exposes to the outside (use cases, application services)
- **Driven Port** — interface the domain requires from the outside (repositories, notifiers, gateways)
- **Driving Adapter** — translates an external trigger (HTTP, CLI, event) into a driving port call
- **Driven Adapter** — implements a driven port using a concrete technology (SQL, AMQP, filesystem)

## Applicability

- The system must survive technology changes (swap database, replace queue, migrate UI framework) without rewriting business rules.
- Multiple delivery channels (REST, GraphQL, CLI, event consumer) share the same domain logic.
- You want fast, deterministic unit tests for business rules with no infrastructure in the loop.
- The domain is complex enough that coupling it to any single framework would obscure its intent.

## Consequences

**Gains**
- Technology independence: infrastructure can be replaced by changing adapters alone.
- Testability: the domain is exercised through ports with in-memory test doubles.
- Enforced separation of concerns: compile-time checks prevent domain from importing infrastructure.
- Symmetric treatment of driving and driven sides simplifies mental model.

**Costs**
- Port proliferation: every external touchpoint needs an interface and at least two implementations.
- Indirection overhead: simple CRUD paths may feel over-engineered.
- Learning curve: developers unfamiliar with the pattern may place logic in adapters.
- Risk of speculative generality if ports are defined for adapters that will never be swapped.

## OOP shape

```
// Driven port — domain defines it
interface OrderRepository
  save(order: Order): void
  findById(id: OrderId): Order?

// Driving port — application service
class PlaceOrderUseCase
  constructor(repo: OrderRepository, notifier: OrderNotifier)
  execute(cmd: PlaceOrderCommand): OrderConfirmation
    order = Order.create(cmd)
    this.repo.save(order)
    this.notifier.orderPlaced(order)
    return OrderConfirmation.from(order)

// Driven adapter — infrastructure
class PostgresOrderRepository implements OrderRepository
  save(order: Order): void  // SQL INSERT
  findById(id: OrderId): Order?  // SQL SELECT
```

## FP shape

```
// Ports as function type aliases
type SaveOrder     = Order -> Effect[Unit]
type FindOrderById = OrderId -> Effect[Option[Order]]
type NotifyOrder   = Order -> Effect[Unit]

// Use case as a function closed over port functions
placeOrder :: SaveOrder -> NotifyOrder -> PlaceOrderCommand -> Effect[OrderConfirmation]
placeOrder(save, notify, cmd) =
  order = createOrder(cmd)
  save(order)
  notify(order)
  pure(confirmationFrom(order))

// Adapter — concrete implementation
postgresSave :: ConnectionPool -> SaveOrder
postgresSave(pool) = order -> pool.execute(insertSQL, order)
```

## Smells fixed

- **inappropriate-intimacy** — domain code that directly imported database drivers or HTTP clients is replaced by port interfaces; the domain never sees infrastructure types.
- **feature-envy** — application logic that lived inside controllers or repository implementations moves into the domain hexagon where it belongs.
- **divergent-change** — changes to persistence technology no longer ripple into business rules; each concern changes for its own reasons.
- **shotgun-surgery** — a new business rule is expressed in one place (the domain) instead of scattered across controllers, repositories, and serializers.

## Tests implied

- **Domain runs without adapters** — unit tests instantiate domain objects and call use cases with in-memory stubs; no database, no network.
- **Adapter swap is invisible to domain** — integration test suite runs the same domain assertions against both the in-memory stub and a real adapter (e.g., Postgres test container).
- **No infrastructure imports in domain** — static analysis or architecture test (e.g., ArchUnit) asserts that the domain module has zero dependencies on infrastructure modules.
- **Every port has a double and a real** — test coverage report shows each port interface is implemented by at least one test double and one production adapter.

## Sources

- https://alistair.cockburn.us/hexagonal-architecture/
- https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)
