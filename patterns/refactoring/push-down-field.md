---
name: push-down-field
category: refactoring
aliases: []
intent: >-
  Move a field from the superclass to only those subclasses that actually use it
sources:
  - https://refactoring.guru/refactoring/techniques/dealing-with-generalization
  - https://refactoring.com/catalog/pushDownField.html
smells_it_fixes:
  - speculative-generality
  - refused-bequest
  - large-class
smells_it_introduces: []
composes_with:
  - push-down-method
  - extract-subclass
clashes_with:
  - pull-up-field
test_invariants:
  - "The field is accessible on subclasses that use it and inaccessible on those that don't"
  - "Field values are preserved for instances of the subclasses that received it"
---

# Push Down Field

## Intent

A field declared on the superclass that is only used by a subset of subclasses is misplaced. It misleads readers into thinking the field is universally relevant and makes the superclass carry state it should not own. Moving the field down to only the subclasses that use it makes the hierarchy more accurate and prevents unintended access from unrelated subclasses.

## Structure

Before:
```
class Employee {
  protected quota: Money  // only Salesman uses this
}
class Salesman extends Employee { }
class Engineer extends Employee { }
```

After:
```
class Employee { }
class Salesman extends Employee {
  private quota: Money
}
class Engineer extends Employee { }
```

## Applicability

- The field is only referenced in a subset of subclasses
- Other subclasses either never read/write the field or set it to a meaningless default
- A previous pull-up was overly aggressive and the field does not belong at the general level

## Consequences

- **Accurate ownership** — the field's location reflects where it is actually needed
- **Reduced superclass weight** — fewer fields on the superclass means a lighter, more focused contract
- **Possible duplicate fields** — if pushed to multiple subclasses, two separate field declarations exist; accept this if the semantics genuinely differ per subclass
- **Visibility may narrow** — a `protected` field on the superclass becomes `private` on each subclass, which is the desired tightening

## OOP shape

```
// Before
class Employee {
  protected quota: Money     // irrelevant for Engineer
  protected skill: String    // irrelevant for Salesman
}
class Salesman extends Employee { }
class Engineer extends Employee { }

// After
class Employee { }
class Salesman extends Employee {
  private quota: Money
}
class Engineer extends Employee {
  private skill: String
}
```

## FP shape

```
// Before — shared record carries fields not used by all variants
type Employee = { name: String; quota: Money; skill: String }

// After — per-variant records carry only relevant fields
type Employee = { name: String }
type Salesman = Employee & { quota: Money }
type Engineer = Employee & { skill: String }
```

## Smells fixed

- **speculative-generality** — a field added to the superclass anticipating future use by all subclasses but only used by one is speculative; pushing it down removes the phantom generality
- **refused-bequest** — subclasses that inherit a field they never read or write are silently carrying dead state; push-down removes the unwanted inheritance
- **large-class** — a superclass accumulating fields for narrow subclass use cases is unnecessarily large; push-down trims it

## Tests implied

- **Field accessible in receiving subclass** — assert that the subclass that received the field reads and writes it correctly after the push-down
- **Field absent from non-receiving subclasses** — assert that non-receiving subclasses do not have a field of the same name (via reflection or type check)

## Sources

- https://refactoring.guru/refactoring/techniques/dealing-with-generalization
- https://refactoring.com/catalog/pushDownField.html
