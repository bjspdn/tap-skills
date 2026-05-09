---
name: clean-architecture
category: architectural
aliases: [onion-architecture]
intent: >-
  Organize code in concentric layers where dependencies point inward, keeping business rules independent of frameworks
sources:
  - https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
smells_it_fixes:
  - inappropriate-intimacy
  - divergent-change
  - shotgun-surgery
smells_it_introduces:
  - over-abstraction-single-variant
  - speculative-generality
  - small-class-proliferation
composes_with:
  - hexagonal
  - facade
  - strategy
  - factory-method
clashes_with:
  - singleton
test_invariants:
  - "Inner layers compile and pass tests without any outer-layer dependency"
  - "A framework change in the outermost ring does not modify any use-case or entity file"
  - "Dependency arrows in the import graph all point inward — no outward import exists"
  - "Use cases depend only on entity interfaces, never on concrete gateways"
---

# Clean Architecture

## Intent

Clean Architecture arranges a system into concentric rings — Entities, Use Cases, Interface Adapters, and Frameworks & Drivers — with a strict dependency rule: source-code dependencies may only point inward. Inner rings define abstractions; outer rings supply implementations. This ensures that the most stable and valuable parts of the system (business rules) are shielded from the most volatile parts (UI, database, web frameworks). The pattern generalises Hexagonal Architecture and Onion Architecture under a single principle.

## Structure

```
┌──────────────────────────────────────────┐
│  Frameworks & Drivers  (outermost)       │
│  ┌────────────────────────────────────┐  │
│  │  Interface Adapters                │  │
│  │  ┌──────────────────────────────┐  │  │
│  │  │  Use Cases                   │  │  │
│  │  │  ┌────────────────────────┐  │  │  │
│  │  │  │  Entities  (innermost) │  │  │  │
│  │  │  └────────────────────────┘  │  │  │
│  │  └──────────────────────────────┘  │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘

Dependency Rule: → always points inward
```

Roles:
- **Entities** — enterprise-wide business rules, domain objects, value objects
- **Use Cases** — application-specific business rules; orchestrate entities and define ports
- **Interface Adapters** — controllers, presenters, gateways — translate between use-case language and external format
- **Frameworks & Drivers** — web server, ORM, message broker, UI framework — the outermost, most replaceable ring

## Applicability

- The project is expected to outlive its current framework or infrastructure choices.
- Multiple teams work on different rings and need clear compile-time boundaries.
- Business rules are complex enough to warrant first-class isolation from delivery details.
- You need to enforce architectural constraints via module boundaries rather than convention.

## Consequences

**Gains**
- Framework independence: business rules have zero coupling to any delivery mechanism.
- Testability: entities and use cases are plain objects testable with no infrastructure.
- Deployment flexibility: the same core can be packaged as a monolith, microservice, or serverless function.
- Clear ownership: each ring has a distinct rate of change and team accountability.

**Costs**
- Boilerplate: simple features still require touching multiple layers (entity, use case, adapter, controller).
- Small-class proliferation: each boundary crossing introduces request/response DTOs and mappers.
- Over-engineering risk for small or CRUD-heavy projects where layers add ceremony without value.
- Steeper onboarding: newcomers must learn the ring model before contributing.

## OOP shape

```
// Entity (innermost)
class Invoice
  constructor(id: InvoiceId, lineItems: List[LineItem])
  total(): Money
  markPaid(): Invoice

// Use case
interface InvoiceGateway            // port — defined in use-case ring
  save(invoice: Invoice): void

class PayInvoiceUseCase
  constructor(gateway: InvoiceGateway)
  execute(request: PayInvoiceRequest): PayInvoiceResponse
    invoice = this.gateway.findById(request.invoiceId)
    paid = invoice.markPaid()
    this.gateway.save(paid)
    return PayInvoiceResponse.from(paid)

// Interface adapter
class InvoiceController
  constructor(useCase: PayInvoiceUseCase)
  handlePost(httpRequest): HttpResponse
    request = PayInvoiceRequest.fromHttp(httpRequest)
    response = this.useCase.execute(request)
    return HttpResponse.ok(response.toJson())
```

## FP shape

```
// Entity — pure functions
total :: List[LineItem] -> Money
markPaid :: Invoice -> Invoice

// Use case — function requiring gateway capabilities
type InvoiceGateway = { find: InvoiceId -> Effect[Invoice], save: Invoice -> Effect[Unit] }

payInvoice :: InvoiceGateway -> PayInvoiceRequest -> Effect[PayInvoiceResponse]
payInvoice(gw, req) =
  invoice <- gw.find(req.invoiceId)
  paid = markPaid(invoice)
  gw.save(paid)
  pure(responseFrom(paid))

// Interface adapter — translates HTTP to use-case call
handlePost :: InvoiceGateway -> HttpRequest -> Effect[HttpResponse]
handlePost(gw, httpReq) =
  req = parseRequest(httpReq)
  res <- payInvoice(gw, req)
  pure(toHttpResponse(res))
```

## Smells fixed

- **inappropriate-intimacy** — entities and use cases no longer import framework types; all knowledge of HTTP headers, SQL dialects, or ORM annotations stays in outer rings.
- **divergent-change** — a change in business rules touches only the inner rings; a change in delivery touches only the outer rings; neither triggers changes in the other.
- **shotgun-surgery** — cross-cutting concerns like "add a new field to an entity" are localised; the ripple stops at the use-case boundary instead of leaking into controllers and DB migrations simultaneously.

## Tests implied

- **Inner layers compile independently** — build the entity and use-case modules in isolation; they must compile and pass all unit tests with no outer-ring code on the classpath.
- **Framework change is contained** — replace the HTTP framework in the outermost ring; confirm zero modifications to use-case or entity source files.
- **All imports point inward** — architecture fitness function (or static analysis rule) scans the import graph and fails if any inner-ring module imports an outer-ring module.
- **Use cases depend on abstractions** — grep use-case source; every collaborator is an interface (gateway port), never a concrete class from an outer ring.

## Sources

- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
