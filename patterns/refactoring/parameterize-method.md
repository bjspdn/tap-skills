---
name: parameterize-method
category: refactoring
aliases: []
intent: >-
  Merge several methods that do similar things by extracting the differing literal values into parameters
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/parameterizeMethod.html
smells_it_fixes:
  - duplicate-algorithm-variants
  - long-method
smells_it_introduces:
  - long-parameter-list
composes_with:
  - add-parameter
  - replace-parameter-with-explicit-methods
clashes_with:
  - replace-parameter-with-explicit-methods
test_invariants:
  - "Each former method's behavior is reproduced by calling the unified method with the appropriate argument"
  - "The unified method rejects or handles invalid argument values at least as well as the original methods did"
---

# Parameterize Method

## Intent

When several methods perform the same computation but differ only in a literal value — a constant, a threshold, a string label — they should be unified into a single method that accepts that value as a parameter. This eliminates duplicate logic and makes the family of behaviors extensible without adding new methods. It is the inverse of Replace Parameter with Explicit Methods.

## Structure

Before:
```
class Raise {
  tenPercentRaise(): void
  fivePercentRaise(): void
}
```

After:
```
class Raise {
  raise(percentage: Number): void
}
```

## Applicability

- Two or more methods differ only in a literal constant embedded in otherwise identical logic
- The varying value comes from a well-defined domain (a percentage, a multiplier, an enum value)
- The number of variants is open-ended or expected to grow
- The parameter values form a continuous or large discrete range (avoid when there are only 2–3 boolean-like states — prefer Replace Parameter with Explicit Methods instead)

## Consequences

- **Reduced duplication** — one body replaces N near-identical bodies
- **Open for extension** — new variants require no new methods, only new call-site arguments
- **Weaker type safety** — an unconstrained numeric parameter accepts invalid inputs that named methods would have rejected at the type level
- **Reduced discoverability** — IDEs list one method instead of N named entry points; argument intent may be unclear without IDE hints

## OOP shape

```
// Before
class Employee {
  fivePercentRaise(): void  { this.salary *= 1.05 }
  tenPercentRaise(): void   { this.salary *= 1.10 }
  fifteenPercentRaise(): void { this.salary *= 1.15 }
}

// After
class Employee {
  raise(factor: Decimal): void {
    this.salary *= (1 + factor)
  }
}
// Callers: employee.raise(0.05), employee.raise(0.10)
```

## FP shape

```
// Before
const fivePercentRaise  = (salary) => salary * 1.05
const tenPercentRaise   = (salary) => salary * 1.10

// After — unified with partial application for named variants
const raise = (factor: Decimal) => (salary: Decimal): Decimal =>
  salary * (1 + factor)

const fivePercentRaise  = raise(0.05)
const tenPercentRaise   = raise(0.10)
```

## Smells fixed

- **duplicate-algorithm-variants** — N methods share an identical algorithm body with only a literal constant differing; the literal is hoisted into a parameter and the bodies collapse into one
- **long-method** — when a large method contains multiple literal-gated branches covering the same logic at different magnitudes, parameterization collapses those branches

## Tests implied

- **Per-variant equivalence** — for each original method, assert that calling `raise(X)` with the formerly hardcoded value yields the same result the original method returned
- **Invalid input handling** — assert that the unified method handles or rejects values outside the intended domain (e.g. negative raise factor)

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/parameterizeMethod.html
