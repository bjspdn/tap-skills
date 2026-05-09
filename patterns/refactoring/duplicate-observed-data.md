---
name: duplicate-observed-data
category: refactoring
aliases: [separate-domain-from-ui]
intent: >-
  Copy GUI-layer data into a domain object and keep them synchronized, separating domain logic from presentation
sources:
  - https://refactoring.guru/duplicate-observed-data
  - https://refactoring.com/catalog/duplicateObservedData.html
smells_it_fixes:
  - inappropriate-intimacy
  - divergent-change
  - god-class
smells_it_introduces:
  - synchronization-coupling
  - observer-complexity
composes_with:
  - extract-class
  - change-value-to-reference
clashes_with:
  - inline-class
test_invariants:
  - "behavior preserved — all existing tests still pass"
  - "domain object data is always consistent with the UI widget after any user interaction"
  - "domain logic can be exercised without instantiating any UI components"
---

# Duplicate Observed Data

## Intent
Domain behavior is tangled inside UI event handlers and widget state. Extract the domain data into a separate domain object, then hook the UI and domain together with an observer (or equivalent notification) so changes in either direction stay synchronized. The domain is now testable without the UI.

## Structure
```
Before:
  IntervalWindow (GUI class)
    startField: TextField
    endField: TextField
    lengthField: TextField
    // domain calculation inline in event handlers

After:
  IntervalWindow (GUI only)
    startField, endField, lengthField
    observes → Interval

  Interval (domain object)
    start: Number
    end: Number
    length: Number
    calculateLength()
    // fires notification on change
```

## Applicability
- Domain logic lives inside UI classes (forms, windows, controllers) and cannot be unit-tested without a GUI
- A class changed for both UI reasons and domain reasons (divergent change)
- Applying MVC, MVP, or similar presentation-separation pattern
- Preparing domain classes for reuse outside the UI context

## Consequences
- **Gains**: domain logic is independently testable; UI and domain evolve separately; multiple UI views can share one domain object
- **Costs**: bidirectional synchronization adds complexity; observer/event infrastructure must be introduced; data is duplicated in two places

## OOP shape
```
// Domain object (no UI imports)
class Interval implements Observable
  start: Number
  end: Number
  length: Number

  setStart(v: Number)
    start = v
    calculateLength()
    notifyObservers()

  calculateLength()
    length = end - start

// GUI class
class IntervalWindow implements Observer
  domain: Interval
  startField: TextField

  onStartChanged(event)
    domain.setStart(parse(startField.text))

  update()             // Observer callback
    startField.text = domain.start.toString()
```

## FP shape
```
// Domain: pure functions over a plain record
type Interval = { start: Number, end: Number, length: Number }

calculate_length(i: Interval) -> Interval =
  { i | length: i.end - i.start }

// UI layer: subscribes to a reactive signal / atom
interval_signal = atom(make_interval(0, 0))

// View renders from signal; user actions update signal
on_start_change(new_start) =
  swap!(interval_signal, i -> calculate_length({ i | start: new_start }))
```

## Smells fixed
- **inappropriate-intimacy**: domain logic entangled with widget state is extracted into its own object
- **divergent-change**: the UI class no longer changes for domain reasons; the domain class no longer changes for UI reasons
- **god-class**: a monolithic UI class that also owns domain computation is split along the presentation/domain boundary

## Tests implied
- Domain object calculations produce correct results without any UI instantiation
- After a UI event updates the domain object, the domain object's state matches what the UI sent

## Sources
- https://refactoring.guru/duplicate-observed-data
- https://refactoring.com/catalog/duplicateObservedData.html
