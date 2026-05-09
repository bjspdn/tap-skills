---
name: adapter
category: structural
aliases: [wrapper]
intent: >-
  Convert the interface of a class into another interface clients expect, enabling incompatible interfaces to work together
sources:
  - https://refactoring.guru/design-patterns/adapter
  - https://en.wikipedia.org/wiki/Adapter_pattern
smells_it_fixes:
  - inappropriate-intimacy
  - feature-envy
  - divergent-change
smells_it_introduces:
  - speculative-generality
composes_with:
  - facade
  - decorator
  - bridge
clashes_with:
  - inappropriate-intimacy
test_invariants:
  - "Adapter translates every call on the target interface to the correct adaptee method"
  - "Client never references adaptee type directly"
  - "Adapter does not alter observable behaviour — same inputs produce same outputs"
  - "Swapping one adaptee for another behind the same adapter leaves client tests unchanged"
---

# Adapter

## Intent

Adapter wraps an existing class (the adaptee) so it conforms to an interface the client expects (the target). This lets incompatible classes collaborate without modifying either side. The pattern is especially useful when integrating third-party libraries, legacy subsystems, or any code whose interface cannot be changed.

## Structure

```
Client ──uses──> «interface» Target
                      ▲
                 Adapter
                   - adaptee: Adaptee
                   + request() → adaptee.specificRequest()

Adaptee
  + specificRequest()
```

Roles:
- **Target** — the interface the client knows
- **Adaptee** — the existing class with the incompatible interface
- **Adapter** — implements Target, delegates to Adaptee
- **Client** — works only with the Target interface

## Applicability

- You want to use an existing class but its interface does not match what you need.
- You are integrating a third-party or legacy component you cannot modify.
- You need several existing subclasses to gain a common interface without subclassing each one.
- You are wrapping a data-format or protocol mismatch between subsystems.

## Consequences

**Gains**
- Single Responsibility: translation logic lives in one place.
- Open/Closed: new adaptees can be introduced without touching the client.
- Reduces coupling between client and concrete implementation.

**Costs**
- Adds an indirection layer; can be confusing if the adaptee interface is very similar to the target.
- Object adapter (composition) cannot override adaptee behaviour; class adapter (inheritance) can but is less flexible.
- May tempt speculative abstraction when there is only one adaptee.

## OOP shape

```
interface Target
  operation(): Result

class Adaptee          // third-party / legacy — do not modify
  specificOperation(): LegacyResult

class Adapter implements Target
  constructor(adaptee: Adaptee)
  operation(): Result
    raw = this.adaptee.specificOperation()
    return translate(raw)          // mapping logic here
```

## FP shape

```
// Adapter as a translation function that closes over the adaptee fn
adaptFn :: (LegacyInput -> LegacyResult) -> (Input -> Result)
adaptFn(legacyFn) =
  input -> translate(legacyFn(toLegacyInput(input)))

// Usage
targetFn = adaptFn(adaptee.specificOperation)
client(targetFn)
```

## Smells fixed

- **inappropriate-intimacy** — client code that reached into adaptee internals to massage data is replaced by a clean delegation boundary.
- **feature-envy** — logic that lived in the client to compensate for a wrong interface moves into the adapter where it belongs.
- **divergent-change** — when the adaptee API changes, only the adapter changes; client is insulated.

## Tests implied

- **Adapter translates every call** — for each method on Target, assert that invoking it on the Adapter triggers the correct adaptee method with correctly mapped arguments.
- **Client never references adaptee type** — static analysis / type-checker confirms no import of Adaptee in client module.
- **Same inputs, same outputs** — property test: `adapter.operation(x) == directAdaptee(x)` for all sampled inputs.
- **Swappable adaptee** — integration test: substitute a stub adaptee, confirm client tests pass without change.

## Sources

- https://refactoring.guru/design-patterns/adapter
- https://en.wikipedia.org/wiki/Adapter_pattern
