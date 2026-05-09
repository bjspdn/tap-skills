---
name: proxy
category: structural
aliases: [surrogate]
intent: >-
  Provide a substitute object that controls access to another object, adding behaviour before or after the real object is reached
sources:
  - https://refactoring.guru/design-patterns/proxy
smells_it_fixes:
  - inappropriate-intimacy
  - mutable-shared-state
  - temporal-coupling
  - duplicate-error-handling
smells_it_introduces:
  - over-abstraction-single-variant
  - temporal-coupling
composes_with:
  - decorator
  - adapter
  - facade
clashes_with:
  - singleton-collaborator-no-di
test_invariants:
  - "Proxy and RealSubject implement identical interfaces — client code requires no change to use either"
  - "Proxy forwards every call to RealSubject when access is granted — no silent data transformation"
  - "Proxy-specific logic (caching, auth, lazy init) is exercisable independently of RealSubject"
  - "Proxy does not expose RealSubject's reference to the client"
  - "Lazy proxy creates RealSubject at most once, on first access"
---

# Proxy

## Intent

Proxy inserts a surrogate object in front of a real subject, controlling access to it. The proxy implements the same interface as the real subject so clients are unaware of the indirection. Common applications include: lazy initialisation (virtual proxy), access control (protection proxy), remote communication abstraction (remote proxy), and transparent caching (caching proxy). Unlike Decorator, Proxy typically manages the lifecycle of the real subject itself.

## Structure

```
Client ──> «interface» Subject
                + request(): Result
                    ▲
          ┌─────────┴──────────┐
      RealSubject            Proxy
      + request()            - realSubject: RealSubject  (lazy or injected)
                             + request()
                               // pre-access logic
                               realSubject.request()
                               // post-access logic
```

Roles:
- **Subject** — interface implemented by both RealSubject and Proxy
- **RealSubject** — the object that does the real work
- **Proxy** — controls access to RealSubject; owns or lazily creates it
- **Client** — talks to Subject; unaware of whether it holds a Proxy or RealSubject

## Applicability

- **Virtual proxy**: defer expensive object creation until the object is actually needed.
- **Protection proxy**: add access control or capability checks before delegating.
- **Remote proxy**: hide network communication behind a local object (e.g., RPC stub).
- **Caching proxy**: cache expensive results and return them without hitting the real subject.
- **Logging / audit proxy**: transparently record access without changing the subject.

## Consequences

**Gains**
- Open/Closed: new access-control or caching policies without modifying RealSubject.
- Lazy initialisation defers resource cost until needed.
- Client is decoupled from RealSubject's location (local vs remote) and lifecycle.

**Costs**
- Adds a response latency layer for every method call.
- Risk of temporal coupling when proxy must synchronise lifecycle with real subject.
- Multiple proxy responsibilities in one class becomes a maintenance burden (prefer one proxy per concern or use Decorator instead).

## OOP shape

```
interface Subject
  request(args): Result

class RealSubject implements Subject
  request(args): Result
    return doWork(args)

class Proxy implements Subject
  private realSubject: RealSubject | null = null

  private getReal(): RealSubject
    if this.realSubject == null:
      this.realSubject = new RealSubject()   // lazy init
    return this.realSubject

  request(args): Result
    if not isAuthorised(args): throw AccessDenied
    result = this.getReal().request(args)
    log(args, result)
    return result
```

## FP shape

```
// Proxy = function wrapper that controls dispatch to the real fn
type SubjectFn = Args -> Result

makeProxy :: SubjectFn -> SubjectFn
makeProxy(realFn) =
  args ->
    checkAccess(args)                    // protection
    result = lazily(realFn)(args)        // virtual / caching
    audit(args, result)                  // logging
    result

// lazily = memoize first-call construction
lazily :: (() -> SubjectFn) -> SubjectFn
lazily(factory) =
  let fn = null
  args -> (fn = fn ?? factory())(args)
```

## Smells fixed

- **inappropriate-intimacy** — client code that directly managed RealSubject lifecycle (creation, teardown, null-checks) is encapsulated in the proxy.
- **mutable-shared-state** — a caching proxy centralises cache mutation behind a single controlled point rather than scattered throughout calling code.
- **temporal-coupling** — lazy proxy removes the requirement that callers initialise the real subject before any use.
- **duplicate-error-handling** — access-check or retry logic repeated across every call site is centralised in the protection or retry proxy.

## Tests implied

- **Interface parity** — verify Proxy and RealSubject are assignable to the same Subject type; no client code change required.
- **Transparent delegation** — given access is granted, assert Proxy returns exactly what RealSubject returns for the same inputs.
- **Proxy logic in isolation** — unit test access control / caching / logging with a stub RealSubject, without triggering real work.
- **Reference encapsulation** — assert no public getter exposes the internal RealSubject reference to the client.
- **Single lazy init** — call a virtual proxy's request N times; assert RealSubject constructor is invoked exactly once.

## Sources

- https://refactoring.guru/design-patterns/proxy
