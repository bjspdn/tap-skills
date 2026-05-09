---
name: add-parameter
category: refactoring
aliases: []
intent: >-
  Add a parameter to a method so it can receive information it currently cannot access
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/addParameter.html
smells_it_fixes:
  - feature-envy
  - inappropriate-intimacy
smells_it_introduces:
  - long-parameter-list
composes_with:
  - introduce-parameter-object
  - parameterize-method
clashes_with:
  - remove-parameter
test_invariants:
  - "Behavior is identical for all callers that pass the same value the method previously derived internally"
  - "New parameter is used; dead-code analysis shows no unused parameter"
---

# Add Parameter

## Intent

When a method needs information it cannot obtain from its current parameters or object state, add a parameter to supply that information. This is a simple structural change — the method contract grows by one input. Prefer it as a stepping stone toward larger refactorings rather than as an end in itself, because every added parameter increases caller burden.

## Structure

Before:
```
class Report {
  generate(): Document
}

caller.report.generate()
```

After:
```
class Report {
  generate(format: Format): Document
}

caller.report.generate(Format.PDF)
```

## Applicability

- A method needs data that only the caller knows
- The data cannot be derived from existing parameters or from the object's own fields without inappropriate coupling
- You are midway through a larger refactoring (e.g. Parameterize Method) that requires widening the signature first

## Consequences

- **Increased expressiveness** — the method can now serve more contexts
- **Increased caller burden** — every call site must supply the new argument
- **Risk of long parameter list** — repeated additions accumulate; apply Introduce Parameter Object if the list grows beyond 3–4 items
- **Breaks existing API** — public methods require callers outside the codebase to be updated or a default overload provided

## OOP shape

```
// Before
class Scheduler {
  nextSlot(): TimeSlot { /* uses fixed internal clock */ }
}

// After
class Scheduler {
  nextSlot(from: Instant): TimeSlot { /* caller supplies reference time */ }
}

// Transitional shim while migrating callers
class Scheduler {
  nextSlot(from: Instant = Instant.now()): TimeSlot { ... }
}
```

## FP shape

```
// Before — function closes over global/implicit state
const nextSlot = () => computeFrom(globalClock)

// After — explicit parameter; function is pure
const nextSlot = (from: Instant): TimeSlot => computeFrom(from)

// Partial application restores zero-arg convenience at boundary
const nextSlotFromNow = () => nextSlot(Instant.now())
```

## Smells fixed

- **feature-envy** — when the method reached into another object to get data, passing the data directly reduces cross-object coupling
- **inappropriate-intimacy** — a method that accessed a collaborator's internals to extract one value can instead receive that value as a parameter

## Tests implied

- **Behavioral identity** — for each existing call site, verify that passing the value the method previously derived yields identical output
- **Parameter is exercised** — at least one test passes a non-default value and asserts a different result, confirming the parameter is not dead

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/addParameter.html
