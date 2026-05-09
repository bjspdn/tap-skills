---
name: split-temporary-variable
category: refactoring
aliases: []
intent: >-
  Give each distinct usage of a temporary variable its own variable with a name matching its role
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/split-temporary-variable
  - https://refactoring.com/catalog/splitVariable.html
smells_it_fixes:
  - mutable-shared-state
  - unclear-naming
  - long-method
smells_it_introduces: []
composes_with:
  - extract-variable
  - replace-temp-with-query
  - extract-method
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass after splitting"
  - "Each variable is assigned exactly once after the split"
  - "Each variable name accurately describes its sole purpose"
---

# Split Temporary Variable

## Intent

A temporary variable is being assigned multiple times across the body of a method, each assignment serving a different purpose. Reusing the same name for different conceptual roles confuses readers and prevents further refactoring. Assign each role its own clearly named variable. This is a prerequisite for Extract Method in any method where a single temp is smuggling multiple computations under one name.

## Structure

```
before:
  temp = 2 * (height + width)    // perimeter
  print(temp)
  temp = height * width           // area — same name, different concept!
  print(temp)

after:
  perimeter = 2 * (height + width)
  print(perimeter)
  area = height * width
  print(area)
```

## Applicability

- A temporary variable is assigned more than once and each assignment has a different semantic purpose.
- A loop-accumulator variable is fine when it serves one role throughout; do not split those.
- You want to extract a method but a multi-role temp blocks clean parameter handoff.
- A reader must trace assignments backwards to understand what the variable holds at any given point.

## Consequences

**Gains**
- Each variable carries one unambiguous meaning — the name correctly labels the value for the rest of its scope.
- Enables further refactoring: single-assignment temps can be inlined or promoted to query methods.
- Eliminates the need to trace reassignments to understand current value.

**Costs**
- Increases declared-variable count, though each variable is shorter-lived.
- Purely mechanical split — the real win comes when names are chosen well.

## OOP shape

```
method calculateGeometry(height, width)
  // Before: temp reused for unrelated values
  temp = 2 * (height + width)
  print("Perimeter: " + temp)
  temp = height * width
  print("Area: " + temp)

  // After: each role has its own name
  perimeter = 2 * (height + width)
  print("Perimeter: " + perimeter)
  area = height * width
  print("Area: " + area)
```

## FP shape

```
-- In FP, immutable let-bindings are already split by construction
calculateGeometry :: Height -> Width -> IO ()
calculateGeometry h w =
  let perimeter = 2 * (h + w)
      area      = h * w
  in  print perimeter >> print area
-- The smell does not exist in idiomatic FP; this refactoring enforces the same discipline in imperative code.
```

## Smells fixed

- **mutable-shared-state** — a temp reassigned with an unrelated value is a local form of mutable state; splitting enforces single-assignment discipline.
- **unclear-naming** — a generic name like `temp` or `result` reused across purposes gives the reader no signal about current semantics.
- **long-method** — after splitting, each variable's scope shrinks, making logical sections easier to identify and extract.

## Tests implied

- **Behavior preserved** — the full test suite passes; outputs at every print/return point remain identical.
- **Single assignment** — static analysis or code review confirms each new variable is written exactly once.
- **Name accuracy** — each variable's name describes its value at every point of use.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/split-temporary-variable
- https://refactoring.com/catalog/splitVariable.html
