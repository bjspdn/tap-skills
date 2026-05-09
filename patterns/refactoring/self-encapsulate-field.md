---
name: self-encapsulate-field
category: refactoring
aliases: [use-accessor-internally]
intent: >-
  Access a field only through getter/setter methods even within its own class, enabling subclass override of access
sources:
  - https://refactoring.guru/self-encapsulate-field
  - https://refactoring.com/catalog/selfEncapsulateField.html
smells_it_fixes:
  - inappropriate-intimacy
  - mutable-shared-state
smells_it_introduces:
  - accessor-noise
  - over-abstraction-single-variant
composes_with:
  - encapsulate-field
  - replace-data-value-with-object
  - extract-class
clashes_with:
  - encapsulate-field
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "all internal direct field references are replaced by accessor calls"
  - "subclasses can override the getter to change access behavior without modifying the parent"
---

# Self Encapsulate Field

## Intent
Direct field access inside a class makes subclassing fragile — a subclass cannot intercept field reads or writes. Replace all internal references to the field with calls to a getter and setter. This gives subclasses a hook point and centralizes access logic (lazy init, validation, notification) in one place.

## Structure
```
Before:
  class Item
    _price: Money

    method discounted(): Money
      return _price * 0.9          ← direct access

After:
  class Item
    _price: Money

    get price(): Money             ← accessor
      return _price

    set price(v: Money)            ← mutator
      _price = v

    method discounted(): Money
      return price * 0.9           ← via accessor
```

## Applicability
- A class will be subclassed and subclasses may need to override field access (e.g., lazy initialization)
- Access to a field requires non-trivial logic such as validation, caching, or event notification
- Preparing a field to be moved or replaced with a computed value
- The field is part of a superclass hierarchy where different subclasses store it differently

## Consequences
- **Gains**: subclass hook point; centralized access logic; eases future replacement of the field
- **Costs**: adds accessor boilerplate within the same class; can obscure the fact that a field is local state

## OOP shape
```
class Item
  private _price: Money

  protected get price(): Money
    return _price

  protected set price(v: Money)
    _price = v

  method discounted(): Money
    return price * 0.9   // uses getter, not _price

// Subclass can override
class SpecialItem extends Item
  override get price(): Money
    return _price * launchDiscountFactor
```

## FP shape
```
// FP equivalent: pass an accessor function rather than the field itself
type ItemConfig = {
  get_price: () -> Money,
  set_price: Money -> Unit
}

discounted(cfg: ItemConfig) -> Money =
  cfg.get_price() * 0.9

// Default config uses a simple ref
make_item(price: Money) -> ItemConfig =
  ref = mutable(price)
  { get_price: () -> deref(ref), set_price: v -> set(ref, v) }
```

## Smells fixed
- **inappropriate-intimacy**: internal direct field access is replaced by the class's own public contract, which subclasses can safely override
- **mutable-shared-state**: all mutations route through the setter, providing a single place to add guards or notifications

## Tests implied
- All internal access paths use the accessor — verify no direct field references remain in the class body
- A subclass that overrides the getter sees its version called when the parent's methods execute

## Sources
- https://refactoring.guru/self-encapsulate-field
- https://refactoring.com/catalog/selfEncapsulateField.html
