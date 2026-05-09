---
name: replace-inheritance-with-delegation
category: refactoring
aliases: [favor-composition-over-inheritance]
intent: >-
  Replace a subclass relationship with a field holding the former superclass and explicit delegation calls
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/replaceInheritanceWithDelegation.html
smells_it_fixes:
  - refused-bequest
  - inappropriate-intimacy
  - parallel-inheritance-hierarchy
smells_it_introduces:
  - repeated-param-threading
composes_with:
  - extract-interface
  - replace-delegation-with-inheritance
clashes_with:
  - replace-delegation-with-inheritance
  - extract-subclass
  - form-template-method
test_invariants:
  - "All behavior delegated to the former superclass produces the same result as when it was inherited"
  - "The delegating class no longer exposes methods it does not need from the former superclass"
---

# Replace Inheritance with Delegation

## Intent

Inheritance implies an "is-a" relationship: a subclass is a full substitutable instance of the superclass. When a subclass uses only part of the superclass interface — or inherits behavior it doesn't want — the relationship is really "has-a": composition. Replacing the inheritance with a field that holds the former superclass and forwarding only the needed calls makes the relationship honest, prevents unwanted inherited methods from leaking through, and removes the tight coupling of inheritance. It is the inverse of Replace Delegation with Inheritance.

## Structure

Before:
```
class MyStack extends Vector {
  push(element): void { this.addElement(element) }
  pop(): Element { ... }
}
// MyStack inherits all of Vector's public methods — exposing size(), elementAt(), etc.
```

After:
```
class MyStack {
  private delegate: Vector = new Vector()
  push(element): void { this.delegate.addElement(element) }
  pop(): Element { ... }
  size(): Int { return this.delegate.size() }  // delegated explicitly
}
```

## Applicability

- The subclass uses only a small portion of the superclass's interface
- The subclass inherits methods it doesn't want callers to use (Refused Bequest)
- The "is-a" relationship is not a true substitutability — the subclass cannot be safely used wherever the superclass is expected
- The hierarchy is becoming tangled with non-taxonomic inheritance (implementation reuse rather than type substitution)

## Consequences

- **Honest interface** — only the methods explicitly delegated are visible; unwanted inherited methods are gone
- **Looser coupling** — the delegating class is not bound to the superclass's full contract
- **Forwarding boilerplate** — every needed method requires an explicit forwarding stub; can be verbose
- **Polymorphism lost** — the class no longer satisfies the superclass type; references typed to the superclass must be updated; Extract Interface can restore a shared protocol

## OOP shape

```
// Before
class Stack extends List {
  push(item): void { this.add(0, item) }
  pop(): Item      { return this.remove(0) }
  // inherits: get(), set(), add(index), remove(index), contains(), iterator()... unwanted
}

// Step 1: add delegate field
class Stack {
  private delegate: List = new ArrayList()
  push(item): void { this.delegate.add(0, item) }
  pop(): Item      { return this.delegate.remove(0) }
  isEmpty(): Boolean { return this.delegate.isEmpty() }
}
// Step 2: remove extends List
// Step 3: add explicit delegation for any methods that were called on Stack-as-List
```

## FP shape

```
// Before — module re-exports everything from a base module (implicit delegation)
export * from './list'
export const push = (item, list) => [item, ...list]

// After — explicit, selective re-export (explicit delegation)
import { isEmpty, size } from './list'
export const push = (item, list) => [item, ...list]
export const pop  = ([head, ...tail]) => ({ item: head, rest: tail })
export { isEmpty, size }  // only what the stack interface needs
```

## Smells fixed

- **refused-bequest** — a subclass that inherits methods it does not want (and cannot override away) has its unwanted inheritance removed; only chosen methods are forwarded
- **inappropriate-intimacy** — a class bound to a superclass via inheritance has intimate access to all its internals; delegation limits the exposure to the forwarded surface
- **parallel-inheritance-hierarchy** — when both hierarchies exist only because of implementation reuse, replacing inheritance with delegation in one eliminates the need for the parallel structure

## Tests implied

- **Delegated behavior identity** — assert that each explicitly forwarded method returns the same result as the corresponding method on the delegate object
- **Unwanted methods absent** — assert that methods the subclass previously inherited but did not want are no longer accessible on the refactored class

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/replaceInheritanceWithDelegation.html
