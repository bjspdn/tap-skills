---
name: chain-of-responsibility
category: behavioral
aliases: [cor, chain-of-command]
intent: >-
  Pass a request along a chain of handlers; each handler decides to process it or forward it
sources:
  - https://refactoring.guru/design-patterns/chain-of-responsibility
  - https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern
smells_it_fixes:
  - long-conditional-chain
  - switch-on-type
  - god-class
smells_it_introduces:
  - speculative-generality
  - temporal-coupling
composes_with:
  - command
  - composite
  - decorator
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "A request handled by one handler is not passed further down the chain"
  - "A request unhandled by all handlers reaches the terminal condition without error"
  - "Handlers can be reordered without changing individual handler logic"
  - "Adding a new handler does not require modifying existing handlers"
---

# Chain of Responsibility

## Intent

Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it. Each handler in the chain decides independently whether to process the request or forward it to the successor.

## Structure

```
Client
  |
  v
Handler (abstract)
  - successor: Handler
  + handle(request): void
       |
  [can process?] --yes--> process()
       |
      no
       v
  successor.handle(request)

ConcreteHandlerA  ConcreteHandlerB  ConcreteHandlerC
   extends Handler
```

Roles:
- **Handler** — defines the interface for handling requests; holds optional successor reference
- **ConcreteHandler** — processes requests it is responsible for; forwards the rest
- **Client** — initiates the request to any handler in the chain

## Applicability

- More than one object may handle a request and the handler is not known a priori
- You want to issue a request to one of several objects without specifying the receiver explicitly
- The set of objects that can handle a request should be specified dynamically
- Middleware pipelines, event bubbling, permission/auth guard chains, log-level filtering

## Consequences

- **Reduced coupling** — sender is decoupled from receiver; neither knows the full chain structure
- **Flexible chain composition** — handlers added, removed, or reordered at runtime
- **Single Responsibility** — each handler knows only its own concern
- **No guarantee of handling** — a request may fall off the end of the chain unhandled
- **Harder to trace** — debugging requires following the chain to find which handler acted
- **Temporal coupling risk** — order of handlers may have hidden dependencies

## OOP shape

```
interface Handler {
  setSuccessor(handler: Handler): void
  handle(request: Request): Response | null
}

abstract class BaseHandler implements Handler {
  private successor: Handler | null

  setSuccessor(handler: Handler): void { ... }

  handle(request: Request): Response | null {
    if (this.successor) return this.successor.handle(request)
    return null
  }
}

class ConcreteHandlerA extends BaseHandler {
  handle(request: Request): Response | null {
    if (canHandle(request)) return process(request)
    return super.handle(request)
  }
}
```

## FP shape

```
type Handler<Req, Res> = (req: Req, next: () => Res | null) => Res | null

// Chain composed via reduce — each handler wraps the next
const chain = (handlers: Handler[]): Handler =>
  handlers.reduceRight(
    (next, handler) => (req) => handler(req, () => next(req)),
    (_req) => null
  )

// Middleware-style: (req, next) => result
const authHandler: Handler = (req, next) =>
  isAuthenticated(req) ? next() : null
```

## Smells fixed

- **long-conditional-chain** — a sequence of `if/else if` dispatching on request type is replaced by a composed chain of single-responsibility handlers
- **switch-on-type** — `switch (request.type)` blocks collapse; each case becomes its own handler class
- **god-class** — a monolithic dispatcher that knows every processing rule is decomposed into focused handlers

## Tests implied

- **Request handled once** — when a handler processes a request, the chain stops; verify successor is not called after a successful handle
- **Graceful fall-through** — a request no handler recognizes returns the defined null/default without throwing
- **Order independence of logic** — each handler's internal logic produces the same output regardless of its position in the chain
- **Open extension** — inserting a new handler into the chain does not require touching existing handler code

## Sources

- https://refactoring.guru/design-patterns/chain-of-responsibility
- https://en.wikipedia.org/wiki/Chain-of-responsibility_pattern
