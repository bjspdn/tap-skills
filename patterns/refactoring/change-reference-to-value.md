---
name: change-reference-to-value
category: refactoring
aliases: [reference-to-value-object]
intent: >-
  Convert a reference object that has no shared-identity requirement into an immutable value object
sources:
  - https://refactoring.guru/change-reference-to-value
  - https://refactoring.com/catalog/changeReferenceToValue.html
smells_it_fixes:
  - mutable-shared-state
  - temporal-coupling
  - inappropriate-intimacy
smells_it_introduces:
  - copy-overhead
composes_with:
  - replace-data-value-with-object
  - change-value-to-reference
clashes_with:
  - change-value-to-reference
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the converted object is immutable: any 'mutation' returns a new instance"
  - "equal attribute values imply equal objects: value equality holds"
---

# Change Reference to Value

## Intent
A reference object has no real need for shared identity. Every use creates its own copy anyway, making sharing an accidental complexity. Convert it to an immutable value object — equality based on attributes, no registry, no lifecycle. This is the inverse of Change Value to Reference and the prerequisite for thread-safe data sharing.

## Structure
```
Before:
  Currency
    _code: String
    setCode(code: String)    ← mutable

  order.currency = new Currency()
  order.currency.setCode("USD")

After:
  Currency                   ← immutable value object
    code: String             ← set at construction only
    equals(other): Boolean   ← value equality
    hashCode(): Int

  order.currency = Currency("USD")
```

## Applicability
- A reference object is small, conceptually a value, and is never shared intentionally across aggregate boundaries
- The object has no meaningful lifecycle beyond the object that owns it
- Thread safety or functional-style reasoning is desired — immutable values are trivially safe
- Equality is based on attribute values, not object identity

## Consequences
- **Gains**: immutability eliminates shared mutable state hazards; safe to copy, cache, and share across threads; simple equality semantics
- **Costs**: "updates" must replace the entire object; if the object is large, copy overhead grows; all holders must be updated to use the new copy

## OOP shape
```
// Before — mutable reference object
class Currency
  _code: String
  setCode(c: String): Unit
    _code = c
  getCode(): String
    return _code

// After — immutable value object
class Currency
  code: String               // final / val

  constructor(code: String)
    self.code = code

  equals(other: Currency): Boolean
    return code == other.code

  hashCode(): Int
    return hash(code)

  withCode(newCode: String): Currency
    return Currency(newCode)   // returns new instance
```

## FP shape
```
// Plain immutable record — the default FP shape
type Currency = { code: String }

// Equality is structural by default in most FP languages
usd = { code: "USD" }
eur = { code: "EUR" }

// "Update" returns a new record
update_code(c: Currency, code: String) = { c | code: code }
```

## Smells fixed
- **mutable-shared-state**: mutability is removed; copies can be freely made without coordination
- **temporal-coupling**: callers no longer need to mutate the object after construction in a specific order
- **inappropriate-intimacy**: holders no longer need to track whether they own a unique instance or a shared one

## Tests implied
- Two instances with identical attributes compare as equal and produce the same hash code
- Calling any "update" method returns a new instance; the original instance is unchanged

## Sources
- https://refactoring.guru/change-reference-to-value
- https://refactoring.com/catalog/changeReferenceToValue.html
