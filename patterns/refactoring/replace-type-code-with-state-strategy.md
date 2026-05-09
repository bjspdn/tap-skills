---
name: replace-type-code-with-state-strategy
category: refactoring
aliases: [type-code-to-state, type-code-to-strategy]
intent: >-
  Replace a mutable type code with a pluggable state or strategy object so behavior can change at runtime
sources:
  - https://refactoring.guru/replace-type-code-with-state-strategy
  - https://refactoring.com/catalog/replaceTypeCodeWithStateStrategy.html
smells_it_fixes:
  - switch-on-type
  - long-conditional-chain
  - mutable-shared-state
  - primitive-obsession
smells_it_introduces:
  - indirection-overhead
  - subclass-proliferation
composes_with:
  - replace-type-code-with-subclasses
  - replace-conditional-with-polymorphism
clashes_with:
  - replace-type-code-with-subclasses
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "swapping the state/strategy object changes the dispatched behavior immediately"
  - "the type code field is eliminated from the host class"
---

# Replace Type Code with State/Strategy

## Intent
A class has a type code that drives behavior and the type can change during the object's lifetime (State variant) or the algorithm varies independently (Strategy variant). Introduce a separate class hierarchy for the type, delegate the type-specific behavior to instances of that hierarchy, and allow the host to swap its delegate at runtime. This is the variant of Replace Type Code with Subclasses for mutable types.

## Structure
```
Before:
  class Employee
    type: Int    // can change: e.g., SALESMAN promoted to MANAGER
    payAmount(): Money
      switch type: ...

After:
  interface EmployeeType
    payAmount(employee: Employee): Money

  class EngineerType implements EmployeeType ...
  class ManagerType  implements EmployeeType ...

  class Employee
    _type: EmployeeType    ← swappable at runtime
    setType(t: EmployeeType)
    payAmount(): Money
      return _type.payAmount(self)
```

## Applicability
- The type code can change at runtime (an employee is promoted; an order changes status)
- Behavior varies per type and needs to be dispatched polymorphically
- Multiple classes share the same type-code behavior (Strategy): extract it once and inject it
- Replace Type Code with Subclasses is inappropriate because the object's type is not fixed at construction

## Consequences
- **Gains**: type can change at runtime; type-specific behavior is isolated in dedicated classes; conditionals disappear
- **Costs**: more classes and indirection; the host object must expose enough of itself for the delegate to operate

## OOP shape
```
interface EmployeeType
  payAmount(emp: Employee): Money

class EngineerType implements EmployeeType
  payAmount(emp: Employee): Money = emp.basePay()

class SalesmanType implements EmployeeType
  payAmount(emp: Employee): Money = emp.basePay() + emp.commission()

class ManagerType implements EmployeeType
  payAmount(emp: Employee): Money = emp.basePay() + emp.bonus()

class Employee
  private _type: EmployeeType

  setType(t: EmployeeType): Unit
    _type = t

  payAmount(): Money
    return _type.payAmount(self)
```

## FP shape
```
// Strategy: pass behavior as a function
type PayStrategy = Employee -> Money

engineer_pay : PayStrategy = emp -> emp.base_pay
salesman_pay : PayStrategy = emp -> emp.base_pay + emp.commission
manager_pay  : PayStrategy = emp -> emp.base_pay + emp.bonus

type Employee = {
  ...,
  pay_strategy: PayStrategy   // mutable ref or passed per call
}

pay_amount(emp: Employee) = emp.pay_strategy(emp)
```

## Smells fixed
- **switch-on-type**: the switch dispatching on the mutable type code is replaced by delegation to the current state/strategy object
- **long-conditional-chain**: each conditional arm moves into its own implementation class
- **mutable-shared-state**: the type code integer is replaced by a typed state object; transitions are explicit
- **primitive-obsession**: the raw integer type code is replaced by a first-class polymorphic type

## Tests implied
- Swapping the state/strategy object causes the host object's behavior to change immediately — test before and after swap
- Each state/strategy implementation produces the same result as the corresponding branch of the original conditional

## Sources
- https://refactoring.guru/replace-type-code-with-state-strategy
- https://refactoring.com/catalog/replaceTypeCodeWithStateStrategy.html
