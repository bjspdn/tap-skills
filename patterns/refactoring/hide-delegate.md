---
name: hide-delegate
category: refactoring
aliases: [introduce-delegation]
intent: >-
  Add a delegation method on a server object so clients don't need to know about the server's internal delegates
sources:
  - https://refactoring.guru/hide-delegate
  - https://refactoring.com/catalog/hideDelegate.html
smells_it_fixes:
  - inappropriate-intimacy
  - long-chained-navigation
  - feature-envy
smells_it_introduces:
  - middle-man
  - accessor-noise
composes_with:
  - extract-class
  - move-method
clashes_with:
  - remove-middle-man
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "clients no longer reference the delegate class directly through the server"
  - "delegation method on server returns the same result as the chained call did"
---

# Hide Delegate

## Intent
A client reaches through one object to access a second object's features — violating the Law of Demeter. Add a method on the first object that wraps the delegate call. The client now only depends on the direct server, not on the server's internal collaborator. This is the inverse of Remove Middle Man.

## Structure
```
Before:
  client → manager.getDepartment().getManager()

After:
  client → manager.getManager()    // delegates internally
  Manager
    getDepartment(): Department    // hidden from client
    getManager(): Person           // new delegation method
      return department.getManager()
```

## Applicability
- A client navigates a chain of object references to reach a service (train-wreck code)
- A class is frequently changed and its clients should be insulated from that change
- The delegate object is an implementation detail that should not leak into the API
- Enforcing the Law of Demeter on a server's public interface

## Consequences
- **Gains**: clients are decoupled from the delegate's interface; changes to the delegate don't propagate to clients
- **Costs**: the server class grows a delegation method for every delegate feature clients need; risk of becoming a middle man

## OOP shape
```
// Before
class Client
  method work(person: Person)
    dept = person.getDepartment()
    manager = dept.getManager()

// After
class Person
  getDepartment(): Department      // may become private/package
  getManager(): Person             // new wrapper
    return department.getManager()

class Client
  method work(person: Person)
    manager = person.getManager()  // single hop
```

## FP shape
```
// Before: composed accessors expose intermediate types
get_dept_manager = person -> department -> manager

// After: opaque accessor hides the intermediate step
get_manager(person) = person |> get_department |> get_dept_manager
// exported API exposes only get_manager; get_department is module-private
```

## Smells fixed
- **inappropriate-intimacy**: client no longer reaches into the server's private delegate
- **long-chained-navigation**: train-wreck call chain is collapsed to a single hop
- **feature-envy**: logic that navigated chains to perform work is now encapsulated in the owning class

## Tests implied
- The new delegation method returns the same value as the old chained access — test with the same fixtures
- No client module imports or references the delegate class directly after the refactoring

## Sources
- https://refactoring.guru/hide-delegate
- https://refactoring.com/catalog/hideDelegate.html
