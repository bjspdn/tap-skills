---
name: replace-type-code-with-class
category: refactoring
aliases: [type-code-to-class, enum-class]
intent: >-
  Replace an integer or string type code with a class so the type system validates legal values at compile time
sources:
  - https://refactoring.guru/replace-type-code-with-class
  - https://refactoring.com/catalog/replaceTypeCodeWithClass.html
smells_it_fixes:
  - primitive-obsession
  - magic-number
  - switch-on-type
smells_it_introduces:
  - small-class-proliferation
composes_with:
  - replace-type-code-with-subclasses
  - replace-type-code-with-state-strategy
  - replace-magic-number-with-symbolic-constant
clashes_with:
  - replace-type-code-with-subclasses
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "only valid type values can be constructed — invalid codes are rejected at the boundary"
  - "switch/if chains on the type code still work, but now operate on a typed class rather than a raw integer"
---

# Replace Type Code with Class

## Intent
A class uses an integer or string constant to represent a type (e.g., blood type, order status). Any integer could be passed; the type system provides no protection. Replace the code with a class whose instances represent the legal values. This makes invalid codes impossible to construct and prepares the ground for further behavioral refactoring.

## Structure
```
Before:
  class Person
    bloodType: Int    // 0=A, 1=B, 2=AB, 3=O
    static TYPE_A  = 0
    static TYPE_B  = 1
    static TYPE_AB = 2
    static TYPE_O  = 3

After:
  class BloodType
    static A  = BloodType("A")
    static B  = BloodType("B")
    static AB = BloodType("AB")
    static O  = BloodType("O")
    private code: String

  class Person
    bloodType: BloodType   ← typed, not Int
```

## Applicability
- A class carries an integer or string that represents one of a fixed set of types
- Invalid values can be accidentally passed because the parameter type is too broad
- The type code does NOT drive type-specific behavior yet (if it does, use Replace Type Code with Subclasses or State/Strategy)
- You want to add type-specific behavior incrementally on the new class later

## Consequences
- **Gains**: compile-time type safety; centralized valid-value set; easy to add behavior to the type later
- **Costs**: more classes; switch/conditional chains on the type are still present — they should be eliminated in a follow-on refactoring

## OOP shape
```
class BloodType
  private _code: String

  private constructor(code: String)
    _code = code

  static A  : BloodType = new BloodType("A")
  static B  : BloodType = new BloodType("B")
  static AB : BloodType = new BloodType("AB")
  static O  : BloodType = new BloodType("O")

  toString(): String = _code
  equals(other: BloodType): Boolean = _code == other._code

class Person
  bloodType: BloodType
```

## FP shape
```
// Sum type / enum
type BloodType = A | B | AB | O

// Or opaque newtype over a validated string
type BloodType = BloodType(String)

make_blood_type(s: String) -> Result<BloodType, Error> =
  match s with
  | "A" | "B" | "AB" | "O" -> Ok(BloodType(s))
  | _ -> Error("invalid blood type: " + s)
```

## Smells fixed
- **primitive-obsession**: a raw integer standing for a domain concept is replaced by an explicit domain type
- **magic-number**: integer constants (0, 1, 2, 3) are replaced by named instances with meaningful identities
- **switch-on-type**: the switch statement still exists but now operates on a constrained type; subsequent refactoring can eliminate it

## Tests implied
- Only the defined static instances can be created — no arbitrary integer can be passed as a blood type
- Equality between instances of the same code returns true; different codes return false

## Sources
- https://refactoring.guru/replace-type-code-with-class
- https://refactoring.com/catalog/replaceTypeCodeWithClass.html
