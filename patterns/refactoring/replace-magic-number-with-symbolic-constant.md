---
name: replace-magic-number-with-symbolic-constant
category: refactoring
aliases: [introduce-symbolic-constant, named-constant]
intent: >-
  Replace a raw numeric literal that has a domain meaning with a named constant that makes the intent explicit
sources:
  - https://refactoring.guru/replace-magic-number-with-symbolic-constant
  - https://refactoring.com/catalog/replaceMagicLiteral.html
smells_it_fixes:
  - magic-number
  - unclear-naming
  - duplicate-algorithm-variants
smells_it_introduces:
  - over-abstraction-single-variant
composes_with:
  - replace-type-code-with-class
  - encapsulate-field
clashes_with: []
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "the constant's value equals the original literal — no accidental value change"
  - "all occurrences of the magic literal are replaced by the named constant"
---

# Replace Magic Number with Symbolic Constant

## Intent
A numeric literal appears in the code with a non-obvious meaning. A reader must reverse-engineer its intent from context. Replace it with a named constant that expresses the domain concept the number represents. Every occurrence of the literal then becomes a documentation point.

## Structure
```
Before:
  potentialEnergy = mass * 9.81 * height
  if status == 2 then ...

After:
  GRAVITATIONAL_CONSTANT = 9.81
  ORDER_STATUS_SHIPPED = 2

  potentialEnergy = mass * GRAVITATIONAL_CONSTANT * height
  if status == ORDER_STATUS_SHIPPED then ...
```

## Applicability
- A numeric literal (or string) has a domain meaning that its value alone does not communicate
- The same literal appears in multiple places (a change requires a search-and-replace hunt)
- The value is a well-known domain or physical constant that deserves a canonical name
- The number is a threshold, limit, or configuration value that may change independently of the code

## Consequences
- **Gains**: self-documenting code; single place to change the value; communicates intent to readers
- **Costs**: minor proliferation of constant names; poorly named constants can be worse than the literal

## OOP shape
```
class Physics
  static GRAVITATIONAL_ACCELERATION: Float = 9.81

class Order
  static STATUS_PENDING: Int   = 0
  static STATUS_SHIPPED: Int   = 2
  static STATUS_DELIVERED: Int = 3

  method isShipped(): Boolean
    return status == Order.STATUS_SHIPPED
```

## FP shape
```
// Module-level constants
gravitational_acceleration : Float = 9.81

// Enum-like variant names (sum type preferred, but constant is acceptable)
order_status_pending   = 0
order_status_shipped   = 2
order_status_delivered = 3

potential_energy(mass, height) =
  mass * gravitational_acceleration * height
```

## Smells fixed
- **magic-number**: the unnamed literal is replaced by a constant whose name makes its meaning unambiguous
- **unclear-naming**: code that required a comment to explain a value now has the explanation as the constant name
- **duplicate-algorithm-variants**: all uses of the same literal reference the same constant; no risk of inconsistency

## Tests implied
- The constant's value matches the original literal exactly — test any formula that uses it against a known result
- No occurrences of the original literal remain in production code — verified by a grep/search

## Sources
- https://refactoring.guru/replace-magic-number-with-symbolic-constant
- https://refactoring.com/catalog/replaceMagicLiteral.html
