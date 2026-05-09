---
name: repository
category: architectural
aliases: [data-access-object, dao]
intent: >-
  Mediate between domain and data-mapping layers using a collection-like interface for accessing domain objects
sources:
  - https://martinfowler.com/eaaCatalog/repository.html
smells_it_fixes:
  - duplicate-code
  - feature-envy
  - shotgun-surgery
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
composes_with:
  - facade
  - factory-method
  - strategy
  - adapter
clashes_with: []
test_invariants:
  - "Domain objects are retrieved and persisted without the domain knowing the storage mechanism"
  - "Query logic is encapsulated inside the repository, not scattered across callers"
  - "Substituting an in-memory repository for a database-backed one does not break any domain test"
  - "Repository interface exposes domain language, not SQL or storage primitives"
---

# Repository

## Intent

Repository provides a collection-oriented abstraction over data storage, presenting domain objects as if they lived in an in-memory collection. Callers add, remove, and query objects through a domain-centric interface; the repository translates these operations into whatever persistence mechanism lies beneath — SQL, document store, file system, or remote API. This shields the domain from data-access concerns and centralises query logic.

## Structure

```
Client ──uses──> «interface» Repository<T>
                       ▲
                 ConcreteRepository<T>
                   - dataSource: DataSource
                   + findById(id): T?
                   + findAll(spec: Specification): List<T>
                   + save(entity: T): void
                   + remove(entity: T): void

Domain objects never reference DataSource
```

Roles:
- **Repository interface** — domain-facing contract using domain types (entities, value objects, specifications)
- **Concrete Repository** — implements the interface using a specific storage technology
- **Specification** (optional) — encapsulated query criteria expressed in domain terms
- **Client** — domain service or use case that consumes the repository

## Applicability

- Multiple parts of the application need to query the same aggregate root, and you want to avoid duplicating query logic.
- The domain model should remain ignorant of how and where data is stored.
- You anticipate changing storage technology or want to test business logic with an in-memory store.
- Complex query criteria need to be composable and reusable across use cases.

## Consequences

**Gains**
- Single Responsibility: all persistence logic for an aggregate lives in one place.
- Domain purity: domain objects contain no persistence annotations or SQL.
- Testability: in-memory repository implementations make domain tests fast and deterministic.
- Substitutability: swapping storage technology requires only a new concrete repository.

**Costs**
- Can become a "god repository" if too many query methods accumulate without pruning.
- Over-abstraction risk when the application is a thin CRUD layer with no real domain logic.
- Specification pattern adds complexity; simpler apps may not need composable queries.
- May hide performance characteristics of the underlying store (N+1 queries, missing indexes).

## OOP shape

```
interface OrderRepository
  findById(id: OrderId): Order?
  findByCustomer(customerId: CustomerId): List<Order>
  save(order: Order): void
  remove(order: Order): void

class SqlOrderRepository implements OrderRepository
  constructor(connection: DbConnection)
  findById(id: OrderId): Order?
    row = this.connection.query("SELECT ... WHERE id = ?", id)
    return row ? mapToOrder(row) : null
  save(order: Order): void
    this.connection.execute("INSERT ... ON CONFLICT UPDATE ...", toRow(order))

class InMemoryOrderRepository implements OrderRepository
  - store: Map<OrderId, Order>
  findById(id: OrderId): Order?
    return this.store.get(id)
  save(order: Order): void
    this.store.set(order.id, order)
```

## FP shape

```
// Repository as a record of effectful functions
type OrderRepo =
  { findById:     OrderId -> Effect[Option[Order]]
  , findByCust:   CustomerId -> Effect[List[Order]]
  , save:         Order -> Effect[Unit]
  , remove:       Order -> Effect[Unit]
  }

// In-memory implementation
inMemoryRepo :: Ref[Map[OrderId, Order]] -> OrderRepo
inMemoryRepo(ref) =
  { findById  = id   -> ref.get |> map(_.get(id))
  , findByCust = cid -> ref.get |> map(_.values.filter(_.customerId == cid))
  , save      = o    -> ref.update(_.put(o.id, o))
  , remove    = o    -> ref.update(_.remove(o.id))
  }

// Use case consumes the record
placeOrder :: OrderRepo -> PlaceOrderCmd -> Effect[Confirmation]
placeOrder(repo, cmd) =
  order = createOrder(cmd)
  repo.save(order)
  pure(confirm(order))
```

## Smells fixed

- **duplicate-code** — scattered SQL queries or data-access snippets that appeared in multiple services are consolidated behind a single repository method.
- **feature-envy** — service classes that reached into raw database connections and mapped rows themselves now delegate to the repository, which owns the mapping.
- **shotgun-surgery** — when the storage schema changes, only the concrete repository implementation changes; domain services and use cases remain untouched.

## Tests implied

- **Storage-agnostic domain** — domain tests inject an in-memory repository; they never start a database. All domain assertions pass.
- **Query encapsulation** — no caller constructs raw queries; static analysis confirms that SQL/NoSQL query strings appear only inside concrete repository files.
- **Swappable implementation** — the same integration test suite runs against both in-memory and real-database repository implementations with identical results.
- **Domain-language interface** — repository method signatures use domain types (OrderId, CustomerId) not storage primitives (string, int, row).

## Sources

- https://martinfowler.com/eaaCatalog/repository.html
