---
name: introduce-foreign-method
category: refactoring
aliases: [client-method-on-foreign-class]
intent: >-
  Add a method to a client class that acts as if it belonged to an unmodifiable server class
sources:
  - https://refactoring.guru/introduce-foreign-method
  - https://refactoring.com/catalog/introduceForeignMethod.html
smells_it_fixes:
  - feature-envy
  - repeated-param-threading
  - primitive-obsession
smells_it_introduces:
  - scattered-delegation
  - comment-as-marker
composes_with:
  - introduce-local-extension
  - move-method
clashes_with:
  - extract-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the foreign method takes the server instance as its first parameter and produces the same result as any duplicated inline logic"
  - "all duplicates of the logic are replaced by calls to the single foreign method"
---

# Introduce Foreign Method

## Intent
A server class you cannot modify needs an additional method. Create that method in the client class, passing the server instance as the first parameter. This consolidates what would otherwise be scattered inline logic into one named operation. When many such methods accumulate, upgrade to Introduce Local Extension.

## Structure
```
Before:
  class Client
    method process()
      // inline date arithmetic repeated in multiple places
      nextDay = Date(serverDate.year, serverDate.month, serverDate.day + 1)

After:
  class Client
    method process()
      nextDay = nextDay(serverDate)

    // foreign method — comment marks intent
    // Should be on Date if we could modify it
    private method nextDay(date: Date): Date
      return Date(date.year, date.month, date.day + 1)
```

## Applicability
- A server class is from a library, framework, or team boundary you cannot modify
- The missing behavior is needed in only one client class (otherwise use Introduce Local Extension)
- Duplicated inline logic across a client class that properly belongs on the server type
- A quick pragmatic fix when full extension is disproportionate

## Consequences
- **Gains**: eliminates duplicated inline logic; names the operation clearly; easy to migrate later
- **Costs**: the method lives in the wrong class — must be documented with a comment; if the need spreads to other clients, each will re-implement it
- **Upgrade path**: when three or more clients need the same foreign method, apply Introduce Local Extension

## OOP shape
```
// Server class (unmodifiable)
class Date
  year: Int
  month: Int
  day: Int

// Client class
class ReportGenerator
  // Foreign method — belongs on Date
  private nextDay(date: Date): Date
    return Date(date.year, date.month, date.day + 1)

  method generate(startDate: Date)
    reportDate = nextDay(startDate)
    ...
```

## FP shape
```
// Server module is closed
// Client module defines a local extension function
// date_utils (client-side)
next_day(date) = { date | day: date.day + 1 }

// Marked with a doc comment: "belongs in date module"
```

## Smells fixed
- **feature-envy**: scattered inline logic that reaches into a server type is consolidated into one named operation
- **repeated-param-threading**: the server instance is passed as a clean first argument rather than woven through duplication
- **primitive-obsession**: raw date arithmetic inline is replaced by a named semantic operation

## Tests implied
- The foreign method returns the same value as the previously inlined logic — test with representative inputs
- Every former duplication site now calls the single foreign method — no inline copies remain

## Sources
- https://refactoring.guru/introduce-foreign-method
- https://refactoring.com/catalog/introduceForeignMethod.html
