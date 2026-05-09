---
name: push-down-method
category: refactoring
aliases: []
intent: >-
  Move a method from the superclass to only those subclasses that actually use it
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/pushDownMethod.html
smells_it_fixes:
  - speculative-generality
  - refused-bequest
  - large-class
smells_it_introduces:
  - duplicate-algorithm-variants
composes_with:
  - push-down-field
  - extract-subclass
clashes_with:
  - pull-up-method
test_invariants:
  - "Each subclass that receives the pushed-down method behaves identically to when the method was on the superclass"
  - "Subclasses that did not need the method no longer have access to it"
---

# Push Down Method

## Intent

When a method on the superclass is relevant to only one (or a subset) of its subclasses, it does not belong at the general level. It implies either a missed specialization or a leftover from a previous refactoring. Moving the method down to the subclasses that actually use it removes noise from the superclass interface and makes the class hierarchy more honest about where behavior lives.

## Structure

Before:
```
class Employee {
  quota(): Money  // only Salesman uses this
}
class Salesman extends Employee { }
class Engineer extends Employee { }
```

After:
```
class Employee { }
class Salesman extends Employee {
  quota(): Money
}
class Engineer extends Employee { }
```

## Applicability

- The method is only relevant to one or a few subclasses, not the full hierarchy
- The superclass is accumulating methods that do not apply to all subclasses
- Subclasses that don't use the method throw `NotImplemented` or return a default null/zero — a Refused Bequest smell

## Consequences

- **Cleaner superclass interface** — methods not relevant to all subclasses are removed from the general contract
- **Possible duplication** — if pushed down to multiple subclasses, the body may be duplicated; accept this if the subclass semantics genuinely differ, otherwise prefer keeping it higher
- **Polymorphic access lost** — code that references the method via a superclass-typed variable can no longer compile; requires a cast or interface extraction
- **Prerequisite for Extract Subclass** — pushing down a cluster of methods is often the first step before extracting a new specialized subclass

## OOP shape

```
// Before
class Employee {
  abstract quota(): Money  // only meaningful for Salesman
}
class Engineer extends Employee {
  quota(): Money { throw NotImplemented() }  // refused bequest
}
class Salesman extends Employee {
  quota(): Money { return this._quota }
}

// After
class Employee { }  // no quota
class Engineer extends Employee { }
class Salesman extends Employee {
  quota(): Money { return this._quota }
}
```

## FP shape

```
// Before — quota function on general Employee union
type Employee = Salesman | Engineer
const quota = (e: Employee): Money => {
  if (e.kind === 'salesman') return e.quota
  throw Error('not a salesman')  // refused bequest
}

// After — quota only on Salesman type
type Salesman = { kind: 'salesman'; quota: Money }
const salesmanQuota = (s: Salesman): Money => s.quota
```

## Smells fixed

- **speculative-generality** — a method placed on the superclass "in case subclasses need it" but only one does is speculative; pushing it down removes the pretense
- **refused-bequest** — subclasses that inherit a method they don't use (returning null or throwing) have their bequest refused; the method is pushed to where it is actually wanted
- **large-class** — a superclass accumulating methods for narrow subclass use cases grows unnecessarily; push-down trims it back

## Tests implied

- **Behavioral equivalence** — assert that the subclass that received the method produces the same output as it did when the method was on the superclass
- **Superclass access removed** — assert that accessing the method via a superclass-typed reference is a compile-time error (not a runtime error) after the push-down

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/pushDownMethod.html
