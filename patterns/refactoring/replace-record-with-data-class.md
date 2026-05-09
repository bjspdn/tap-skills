---
name: replace-record-with-data-class
category: refactoring
aliases: [record-to-class, dumb-data-class]
intent: >-
  Replace a legacy record or struct with a proper class so behavior can be added to the data over time
sources:
  - https://refactoring.guru/replace-record-with-data-class
  - https://refactoring.com/catalog/replaceRecordWithDataClass.html
smells_it_fixes:
  - primitive-obsession
  - data-clump
  - feature-envy
smells_it_introduces:
  - data-class
  - small-class-proliferation
composes_with:
  - replace-data-value-with-object
  - encapsulate-field
  - encapsulate-collection
clashes_with:
  - replace-array-with-object
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the new class exposes the same fields as the original record with equivalent get/set semantics"
  - "the class can be instantiated without any behavioral logic and used as a dumb data holder initially"
---

# Replace Record with Data Class

## Intent
An interface with an external system or legacy code returns a plain record (struct, dictionary, or raw data container) with no behavior. Create a proper class to wrap it. The class initially acts as a dumb data holder, but it gives you a home for future behavior and type safety that a raw record cannot provide.

## Structure
```
Before:
  record = fetchRow()   // returns { name: "Alice", age: 30, email: "..." }
  print(record["name"])

After:
  class Person
    name: String
    age: Int
    email: String

  person = Person.fromRecord(fetchRow())
  print(person.name)
```

## Applicability
- An external system, database query, or legacy API returns untyped or weakly typed records
- A struct or dictionary is passed around the codebase and behaviour accumulates outside it
- You intend to add validation, formatting, or business logic to the data in the near future
- Type safety and IDE assistance are desired for data that was previously accessed by string keys

## Consequences
- **Gains**: type-safe field access; named home for future behavior; easier refactoring of field names
- **Costs**: initial class is a data class with no behavior — a temporary state that should be improved; requires mapping from the external record format

## OOP shape
```
// External record (untyped, from DB / API)
raw = { "name": "Alice", "age": 30 }

// New data class
class Person
  name: String
  age: Int

  static fromRecord(r: Map<String, Any>): Person
    return Person(name=r["name"], age=r["age"])

  // behavior can be added here later
  isAdult(): Boolean
    return age >= 18
```

## FP shape
```
// Before: raw map / associative structure
raw: Map<String, Any>
name = map_get(raw, "name")

// After: typed record with smart constructor
type Person = { name: String, age: Int }

from_record(raw: Map<String, Any>) -> Result<Person, Error> =
  Ok({ name: map_get!(raw, "name"), age: int_parse!(map_get!(raw, "age")) })

// Additional functions can be added to the module
is_adult(p: Person) = p.age >= 18
```

## Smells fixed
- **primitive-obsession**: raw maps/structs used as domain objects are replaced by typed classes
- **data-clump**: fields that cluster into a concept get a proper named type
- **feature-envy**: methods that operated on the raw record and lived outside it can migrate into the new class

## Tests implied
- The new class can be constructed from the same raw record data and its fields return the expected values
- Field access by name is type-safe — invalid field names fail at compile time, not runtime

## Sources
- https://refactoring.guru/replace-record-with-data-class
- https://refactoring.com/catalog/replaceRecordWithDataClass.html
