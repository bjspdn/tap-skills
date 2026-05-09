---
name: remove-setting-method
category: refactoring
aliases: []
intent: >-
  Make a field immutable by removing its setter and initializing it only through the constructor
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/removeSettingMethod.html
smells_it_fixes:
  - mutable-shared-state
  - temporal-coupling
smells_it_introduces: []
composes_with:
  - separate-query-from-modifier
  - replace-constructor-with-factory-method
clashes_with: []
test_invariants:
  - "The field's value set at construction time is the same value returned by its getter for the object's lifetime"
  - "No code path modifies the field after construction"
---

# Remove Setting Method

## Intent

If a field should never change after an object is created, advertising a setter invites unintended mutation. Removing the setter communicates immutability as a design intent and lets the compiler or runtime enforce it. The field is promoted to a constructor-initialized, read-only slot; callers that need a different value must construct a new object.

## Structure

Before:
```
class Person {
  private name: String
  setName(name: String): void { this.name = name }
  getName(): String { return this.name }
}
person.setName("Alice")
```

After:
```
class Person {
  private readonly name: String
  constructor(name: String) { this.name = name }
  getName(): String { return this.name }
}
new Person("Alice")
```

## Applicability

- The field is only ever set once (at construction time) after the object is initialized
- The field represents an identity or invariant attribute that should not drift over the object's lifetime
- Accidental reassignment of the field would constitute a bug, not a feature

## Consequences

- **Immutability by construction** — the object's identity fields cannot be corrupted after initialization
- **Thread safety** — immutable fields need no synchronization
- **More constructor parameters** — fields previously assigned lazily via setters must now be provided at construction; factory methods or builders may be needed for complex initialization
- **Breaking change** — callers that used the setter (even legitimately) must migrate to constructing a new instance

## OOP shape

```
// Before — field set post-construction
class Account {
  private id: AccountId
  setId(id: AccountId): void { this.id = id }
}
account.setId(newId)

// After — constructor-only initialization
class Account {
  private readonly id: AccountId
  constructor(id: AccountId) { this.id = id }
}
new Account(newId)
```

## FP shape

```
// Before — mutable record updated after construction
type Account = { id: AccountId }
const account: Account = {}
account.id = newId  // post-hoc assignment

// After — immutable record; "update" creates a new value
type Account = { readonly id: AccountId }
const account: Account = { id: newId }

// To "change" id: construct a new record
const withId = (account: Account, id: AccountId): Account =>
  ({ ...account, id })
```

## Smells fixed

- **mutable-shared-state** — identity fields that could be reassigned after construction are a source of subtle bugs; removing the setter eliminates the mutation path
- **temporal-coupling** — code that required `new Foo()` followed by `foo.setX(...)` in a specific order is replaced by a single construction expression that is always complete

## Tests implied

- **Immutability enforced** — assert that no setter method exists on the class after refactoring; a type-system check or reflection-based test confirms the field is read-only
- **Constructor sets value** — assert that `new Person("Alice").getName() === "Alice"` and that the value does not change over the object's lifetime in any test scenario

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/removeSettingMethod.html
