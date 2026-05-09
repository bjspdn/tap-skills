---
name: facade
category: structural
aliases: []
intent: >-
  Provide a simplified interface to a complex subsystem, reducing client coupling to its internals
sources:
  - https://refactoring.guru/design-patterns/facade
smells_it_fixes:
  - inappropriate-intimacy
  - feature-envy
  - long-parameter-list
  - god-class
smells_it_introduces:
  - over-abstraction-single-variant
  - god-class
composes_with:
  - adapter
  - mediator
  - abstract-factory
clashes_with:
  - inappropriate-intimacy
test_invariants:
  - "Client achieves its use case by calling only Facade methods — no direct subsystem imports"
  - "Facade delegates all actual work to subsystem classes — contains no domain logic itself"
  - "Subsystem classes remain individually testable without the Facade"
  - "Replacing a subsystem implementation does not change the Facade's public interface"
---

# Facade

## Intent

Facade provides a single, simplified entry-point to a complex subsystem containing many interdependent classes. It does not encapsulate the subsystem — clients can still reach individual classes if they need fine-grained control — but it dramatically reduces the surface area that most clients need. Facade is the canonical pattern for building layered architectures and SDK wrappers.

## Structure

```
Client ──> Facade
           + simpleOperation()
             ┌──────────────────────────┐
             │  SubsystemA.step1()      │
             │  SubsystemB.step2(x)     │
             │  SubsystemC.finalize()   │
             └──────────────────────────┘
                   Subsystem classes
```

Roles:
- **Facade** — knows which subsystem classes to involve and in what order; delegates all work
- **Subsystem classes** — implement actual functionality; unaware of the Facade
- **Client** — talks to Facade for common use cases; may still access subsystem directly when needed

## Applicability

- You want to provide a simple interface to a complex subsystem.
- You are building a layered architecture and want to define entry points to each layer.
- The subsystem has too many moving parts for typical clients to orchestrate themselves.
- You want to decouple clients from subsystem internals so the subsystem can evolve freely.

## Consequences

**Gains**
- Isolates clients from subsystem complexity.
- Promotes loose coupling between layers.
- Simplifies most client code to a handful of calls.

**Costs**
- Facade can become a god-class if all subsystem orchestration funnels through one object.
- Risk of hiding complexity rather than managing it — thin facades that just forward calls add indirection with no benefit.
- Subsystem changes may still ripple through Facade if the orchestration logic is tightly coupled.

## OOP shape

```
// Subsystem classes — complex, interdependent, do real work
class SubsystemA
  step1(config): IntermediateResult

class SubsystemB
  step2(input: IntermediateResult): ProcessedResult

class SubsystemC
  finalize(result: ProcessedResult): Output

// Facade — orchestrates the subsystem for common workflows
class Facade
  constructor(a: SubsystemA, b: SubsystemB, c: SubsystemC)

  simpleOperation(config): Output
    r1 = this.a.step1(config)
    r2 = this.b.step2(r1)
    return this.c.finalize(r2)
```

## FP shape

```
// Subsystem = independent functions
subsystemA :: Config -> IntermediateResult
subsystemB :: IntermediateResult -> ProcessedResult
subsystemC :: ProcessedResult -> Output

// Facade = composed pipeline
facadeOp :: Config -> Output
facadeOp = subsystemC << subsystemB << subsystemA
// (or explicit pipe: input -> subsystemC(subsystemB(subsystemA(input))))
```

## Smells fixed

- **inappropriate-intimacy** — client code that directly orchestrated multiple subsystem classes is centralised in the Facade.
- **feature-envy** — client logic that "envied" subsystem internals to stitch calls together moves into the Facade where it belongs.
- **long-parameter-list** — repeated multi-parameter subsystem setup sequences become a single Facade call with sensible defaults.
- **god-class** — a client class that grew by absorbing subsystem knowledge is relieved of that orchestration.

## Tests implied

- **Client uses only Facade** — integration test: confirm no client module imports subsystem class types directly.
- **Facade is purely delegating** — unit test: mock all subsystem classes; assert Facade invokes each in correct order with correct arguments and returns the final result.
- **Subsystem independently testable** — subsystem unit tests run without any Facade instance or import.
- **Interface stable under subsystem change** — swap a subsystem implementation behind the Facade; assert the Facade's public API signature and observable output contract remain unchanged.

## Sources

- https://refactoring.guru/design-patterns/facade
