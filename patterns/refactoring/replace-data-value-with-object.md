---
name: replace-data-value-with-object
category: refactoring
aliases: [value-object-extraction]
intent: >-
  Promote a primitive or simple data item to an object so behavior related to it can live alongside the data
sources:
  - https://refactoring.guru/replace-data-value-with-object
  - https://refactoring.com/catalog/replaceDataValueWithObject.html
smells_it_fixes:
  - primitive-obsession
  - data-clump
  - feature-envy
smells_it_introduces:
  - small-class-proliferation
composes_with:
  - change-value-to-reference
  - self-encapsulate-field
  - extract-class
clashes_with:
  - replace-record-with-data-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the new object is a value object: equal instances with equal data compare as equal"
  - "all formatting, validation, and parsing logic for the original data lives in the new class"
---

# Replace Data Value with Object

## Intent
A data item — a primitive or a simple field — has grown associated behavior (formatting, validation, comparison) that is scattered through the codebase. Replace it with a dedicated object that carries that behavior alongside the data. The result is a Value Object with a richer API and a single home for all related logic.

## Structure
```
Before:
  class Order
    customerName: String
    customerAreaCode: String
    customerNumber: String

After:
  class Order
    customer: Customer      ← value object

  class Customer
    name: String
    phone: PhoneNumber
    isValid(): Boolean
    format(): String
```

## Applicability
- A primitive field has formatting, parsing, or validation logic duplicated across the codebase
- Multiple fields travel together and represent a single concept (data clump)
- Comparisons or operations on the value require special logic beyond raw equality
- The value will later become a reference object shared across entities (upgrade via Change Value to Reference)

## Consequences
- **Gains**: co-locates behavior with data; eliminates duplication; makes the domain concept explicit
- **Costs**: more classes; callers must be updated; equality semantics must be defined explicitly

## OOP shape
```
// Before
class Customer
  name: String
  areaCode: String
  number: String

// After
class PhoneNumber              // value object
  areaCode: String
  number: String

  equals(other: PhoneNumber): Boolean
  toString(): String
    return "(" + areaCode + ") " + number

class Customer
  name: String
  phone: PhoneNumber           // primitive replaced
```

## FP shape
```
// Before: loose primitive
type Customer = { name: String, area_code: String, number: String }

// After: named product type with smart constructor
type PhoneNumber = { area_code: String, number: String }
make_phone(area, num) -> Result<PhoneNumber, Error>   // validates on construction
format_phone(p: PhoneNumber) -> String

type Customer = { name: String, phone: PhoneNumber }
```

## Smells fixed
- **primitive-obsession**: a raw primitive string/integer is replaced by a domain concept with its own type
- **data-clump**: fields that cluster together (area code + number) are absorbed into one named type
- **feature-envy**: scattered methods operating on the primitive migrate to the new class

## Tests implied
- Value equality holds: two instances with identical data compare equal
- All formatting, parsing, and validation logic produces the same results as the previously scattered implementations

## Sources
- https://refactoring.guru/replace-data-value-with-object
- https://refactoring.com/catalog/replaceDataValueWithObject.html
