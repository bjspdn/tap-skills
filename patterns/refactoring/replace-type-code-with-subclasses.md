---
name: replace-type-code-with-subclasses
category: refactoring
aliases: [subclass-per-type]
intent: >-
  Replace a type code that drives conditional behavior with a subclass hierarchy, moving each branch into its own class
sources:
  - https://refactoring.guru/replace-type-code-with-subclasses
  - https://refactoring.com/catalog/replaceTypeCodeWithSubclasses.html
smells_it_fixes:
  - switch-on-type
  - long-conditional-chain
  - primitive-obsession
smells_it_introduces:
  - subclass-proliferation
  - inheritance-rigidity
composes_with:
  - replace-type-code-with-class
  - replace-conditional-with-polymorphism
  - replace-type-code-with-state-strategy
clashes_with:
  - replace-type-code-with-state-strategy
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "each subclass overrides the type-dispatched methods and produces the same result as the corresponding conditional branch"
  - "the type code field is eliminated from the parent class"
---

# Replace Type Code with Subclasses

## Intent
A class uses a type code to select between different behaviors in multiple conditional chains. Create a subclass for each type, override the variant-specific methods in each subclass, and let polymorphism dispatch the behavior. This eliminates the conditionals and sets up for Replace Conditional with Polymorphism. Use this when the type code affects behavior and the object type does not change at runtime.

## Structure
```
Before:
  class Employee
    type: Int   // 0=ENGINEER, 1=SALESMAN, 2=MANAGER
    payAmount(): Money
      switch type:
        ENGINEER:   ...
        SALESMAN:   ...
        MANAGER:    ...

After:
  abstract class Employee
    abstract payAmount(): Money

  class Engineer extends Employee
    payAmount(): Money  ← engineer logic

  class Salesman extends Employee
    payAmount(): Money  ← salesman logic

  class Manager extends Employee
    payAmount(): Money  ← manager logic
```

## Applicability
- A class has a type code that drives conditional branches across multiple methods
- The object's type does not change after construction (it is immutable with respect to its type)
- There are few types and the type set is stable (won't grow frequently)
- Behavior, not just data, differs between types — otherwise use Replace Type Code with Class

## Consequences
- **Gains**: eliminates type-code conditionals; each class has a single behavioral reason to exist; easy to add new behavior via new overrides
- **Costs**: type must be fixed at construction; if types need to change at runtime, use Replace Type Code with State/Strategy instead; subclass count grows

## OOP shape
```
abstract class Employee
  abstract payAmount(): Money
  abstract isPrivileged(): Boolean

  static create(type: Int): Employee
    switch type:
      ENGINEER:  return Engineer()
      SALESMAN:  return Salesman()
      MANAGER:   return Manager()

class Engineer extends Employee
  payAmount(): Money = basePay()
  isPrivileged(): Boolean = false

class Manager extends Employee
  payAmount(): Money = basePay() + bonus()
  isPrivileged(): Boolean = true
```

## FP shape
```
// Sum type: each variant is a constructor
type Employee = Engineer | Salesman | Manager

pay_amount(e: Employee) -> Money =
  match e with
  | Engineer  -> base_pay(e)
  | Salesman  -> base_pay(e) + commission(e)
  | Manager   -> base_pay(e) + bonus(e)
```

## Smells fixed
- **switch-on-type**: each switch branch migrates to a subclass override, and the switch disappears
- **long-conditional-chain**: chains of if/else on the type code are replaced by polymorphic dispatch
- **primitive-obsession**: the integer type code is eliminated; the object's class is the type discriminant

## Tests implied
- Each subclass's overridden method returns the same value as the corresponding branch of the original conditional
- The type code field no longer exists on the parent class — no references remain

## Sources
- https://refactoring.guru/replace-type-code-with-subclasses
- https://refactoring.com/catalog/replaceTypeCodeWithSubclasses.html
