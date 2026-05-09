---
name: remove-middle-man
category: refactoring
aliases: [remove-delegation-wrapper]
intent: >-
  Delete a class that does nothing but forward calls, letting clients talk directly to the real object
sources:
  - https://refactoring.guru/remove-middle-man
  - https://refactoring.com/catalog/removeMiddleMan.html
smells_it_fixes:
  - middle-man
  - speculative-generality
  - dead-code
smells_it_introduces:
  - inappropriate-intimacy
  - long-chained-navigation
composes_with:
  - inline-class
  - move-method
clashes_with:
  - hide-delegate
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "clients receive identical results calling the real object directly"
  - "the former middle-man class has no remaining delegation methods after the refactoring"
---

# Remove Middle Man

## Intent
A class has grown to contain mostly delegation methods that simply forward to another object. The delegation layer adds indirection with no value. Remove it and let clients call the real object directly. This is the inverse of Hide Delegate.

## Structure
```
Before:
  Client → Person.getManager()
  Person
    getManager(): Person
      return department.getManager()    // pure delegation

After:
  Client → Person.getDepartment().getManager()
  // or Client holds direct reference to Department
```

## Applicability
- A server class's public API is dominated by methods that do nothing but forward to a delegate
- The delegate's interface has stabilized and clients can absorb its changes without harm
- The indirection layer was added defensively but the anticipated change never materialized
- After several rounds of Hide Delegate have accumulated too many pass-through methods

## Consequences
- **Gains**: removes unnecessary indirection; server class shrinks; real collaborator is directly accessible
- **Costs**: clients now depend on the delegate's type; changes to the delegate propagate directly to all clients; Law of Demeter is weakened

## OOP shape
```
// Before
class Person
  getManager(): Person          // only delegates
    return department.getManager()

class Client
  method work(person: Person)
    return person.getManager()

// After
class Person
  getDepartment(): Department   // expose the real delegate

class Client
  method work(person: Person)
    return person.getDepartment().getManager()
```

## FP shape
```
// Before: opaque wrapper function
get_manager(person) = person.department.manager   // hidden

// After: clients compose accessors directly
person |> get_department |> department_manager
// the wrapper function is deleted
```

## Smells fixed
- **middle-man**: the class that existed only to forward calls is dissolved
- **speculative-generality**: delegation wrapper added "just in case" the interface would change, never used
- **dead-code**: pure pass-through methods that add no logic are removed

## Tests implied
- All clients receive the same results calling the real object directly as they did through the former wrapper
- The former wrapper class retains no delegation methods — verify by grepping for the pattern

## Sources
- https://refactoring.guru/remove-middle-man
- https://refactoring.com/catalog/removeMiddleMan.html
