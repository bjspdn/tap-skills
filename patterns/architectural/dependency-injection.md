---
name: dependency-injection
category: architectural
aliases: [di, inversion-of-control-container]
intent: >-
  Supply a component's dependencies from the outside rather than letting it construct or locate them itself
sources:
  - https://martinfowler.com/articles/injection.html
smells_it_fixes:
  - inappropriate-intimacy
  - hidden-dependency
  - mutable-shared-state
  - shotgun-surgery
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
composes_with:
  - factory-method
  - abstract-factory
  - strategy
  - adapter
clashes_with:
  - singleton
test_invariants:
  - "No component constructs its own collaborators — all are received via constructor, method, or property injection"
  - "Swapping a dependency for a test double requires no change to the component under test"
  - "The composition root is the only place that knows about concrete implementations"
  - "Circular dependencies are detected and rejected at wiring time, not at runtime"
---

# Dependency Injection

## Intent

Dependency Injection externalises the creation and binding of a component's collaborators so that the component depends only on abstractions, never on concrete implementations. A separate composition root — or an IoC container — wires concrete implementations to the interfaces each component declares it needs. This inverts the traditional control flow where a class instantiates its own helpers, making the dependency graph explicit, testable, and reconfigurable without modifying the components themselves.

## Structure

```
Composition Root
  │
  ├── creates ConcreteServiceA (implements ServiceA)
  ├── creates ConcreteServiceB (implements ServiceB)
  └── injects both into Client

Client
  constructor(a: ServiceA, b: ServiceB)   // depends on abstractions only
  doWork()
    this.a.operate()
    this.b.query()
```

Roles:
- **Client** — the component that needs collaborators; declares dependencies as constructor parameters (or setter/method parameters)
- **Service Interface** — the abstraction the client depends on
- **Concrete Service** — the real implementation, unknown to the client
- **Composition Root / Container** — the single place that assembles the object graph by binding interfaces to implementations
- **Injector** (optional) — framework or container that automates the wiring

## Applicability

- You want to test components in isolation by substituting real collaborators with test doubles.
- Multiple implementations of the same interface must be swappable without touching client code (e.g., production vs. development database).
- The application has a deep dependency graph that is painful to wire manually.
- You need to enforce the Dependency Inversion Principle at the architecture level.

## Consequences

**Gains**
- Testability: any dependency can be replaced with a stub, mock, or fake by passing it into the constructor.
- Loose coupling: components depend on abstractions; concrete implementations are invisible to consumers.
- Single point of assembly: the composition root is the only file that knows the full dependency graph.
- Configuration flexibility: different environments (test, staging, production) wire different implementations.

**Costs**
- Indirection: navigating from interface to implementation requires tracing through the composition root or container configuration.
- Container magic: over-reliance on auto-wiring and reflection can make the dependency graph opaque.
- Runtime errors: misconfigured containers surface wiring problems at startup rather than at compile time.
- Over-injection: components with many constructor parameters may signal a Single Responsibility violation rather than a DI success.

## OOP shape

```
// Abstraction
interface Logger
  log(message: String): void

interface UserRepository
  findById(id: UserId): User?

// Client — depends on abstractions
class UserService
  constructor(repo: UserRepository, logger: Logger)
  getUser(id: UserId): User?
    this.logger.log("fetching user " + id)
    return this.repo.findById(id)

// Composition root — the only place that knows concretions
class CompositionRoot
  static wire(): UserService
    logger = new ConsoleLogger()
    repo   = new PostgresUserRepository(connectionPool)
    return new UserService(repo, logger)
```

## FP shape

```
// Dependencies as function arguments (reader pattern)
type Logger     = String -> Effect[Unit]
type FindUserById = UserId -> Effect[Option[User]]

getUser :: Logger -> FindUserById -> UserId -> Effect[Option[User]]
getUser(log, find, id) =
  log("fetching user " ++ show(id))
  find(id)

// Composition root — partial application wires dependencies
consoleLog :: Logger
consoleLog(msg) = putStrLn("[LOG] " ++ msg)

pgFindUser :: ConnectionPool -> FindUserById
pgFindUser(pool) = id -> pool.query("SELECT ... WHERE id = ?", id)

// Wired application
app = getUser(consoleLog, pgFindUser(pool))
// app :: UserId -> Effect[Option[User]]
```

## Smells fixed

- **inappropriate-intimacy** — a component that directly instantiated a database connection or third-party SDK now only sees an interface; the concrete type is invisible.
- **hidden-dependency** — static service locators or global singletons that were called deep inside methods are replaced by explicit constructor parameters, making the dependency graph visible.
- **mutable-shared-state** — a globally accessible mutable singleton is replaced by an instance injected at construction time; scope and lifetime are controlled by the composition root.
- **shotgun-surgery** — changing a dependency's implementation (e.g., swapping a logging library) requires modifying only the composition root, not every class that uses logging.

## Tests implied

- **No self-construction** — static analysis confirms that no component outside the composition root calls `new ConcreteService()` or equivalent; all dependencies arrive via injection.
- **Test-double substitution** — unit test creates the component with a fake/stub for each dependency; no special framework setup, no real infrastructure.
- **Single composition root** — grep the codebase for concrete instantiation of service types; all hits are in one composition-root module (or container configuration file).
- **Circular dependency detection** — configure a dependency cycle (A -> B -> A); assert the container or composition root raises an error at wiring time, not at call time.

## Sources

- https://martinfowler.com/articles/injection.html
