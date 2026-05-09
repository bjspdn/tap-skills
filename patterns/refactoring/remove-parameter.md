---
name: remove-parameter
category: refactoring
aliases: []
intent: >-
  Remove a parameter that is no longer used by the method body to shrink the caller contract
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/removeParameter.html
smells_it_fixes:
  - long-parameter-list
  - dead-code
smells_it_introduces: []
composes_with:
  - rename-method
  - introduce-parameter-object
clashes_with:
  - add-parameter
test_invariants:
  - "Behavior is identical before and after the parameter is dropped"
  - "No call site passes a value that was silently discarded before the refactoring"
---

# Remove Parameter

## Intent

A parameter that is never used inside the method body adds noise to the signature and misleads callers into believing the value influences the result. Removing it reduces cognitive load at every call site and shrinks the surface area of the method's contract. It is the symmetric inverse of Add Parameter.

## Structure

Before:
```
class Printer {
  print(document: Document, unused: Boolean): void
}
```

After:
```
class Printer {
  print(document: Document): void
}
```

## Applicability

- Static analysis confirms the parameter is never read inside the method body
- The parameter was added speculatively ("we might need this later") but never used
- A previous refactoring left the parameter orphaned
- The parameter is only used in polymorphic siblings — consider whether the base contract actually needs it

## Consequences

- **Simpler call sites** — callers no longer need to manufacture and pass a value they don't understand
- **Honest signature** — the method contract accurately reflects its information needs
- **Breaks API** — removing a public parameter forces callers outside the codebase to update; provide a shim or deprecation window if needed
- **Polymorphism concern** — if overrides in subclasses do use the parameter, remove only with care; the base signature drives the contract

## OOP shape

```
// Before — orphaned flag never read
class EmailSender {
  send(message: Message, debug: Boolean): void {
    smtp.deliver(message)  // debug unused
  }
}

// After
class EmailSender {
  send(message: Message): void {
    smtp.deliver(message)
  }
}
```

## FP shape

```
// Before — parameter is ignored
const send = (message: Message, _debug: Boolean): void =>
  smtp.deliver(message)

// After — honest arity
const send = (message: Message): void =>
  smtp.deliver(message)
```

## Smells fixed

- **long-parameter-list** — each unused parameter silently inflates the list; removal shrinks it back toward the minimum necessary contract
- **dead-code** — a parameter that is always ignored is a dead input; its removal is a direct application of dead-code elimination

## Tests implied

- **Behavioral identity** — the full test suite passes without change after the parameter is removed
- **No silent discard** — confirm via call-site audit that no caller was relying on a side effect triggered by passing a specific value (unlikely but possible in dynamic languages)

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/removeParameter.html
