---
name: remove-control-flag
category: refactoring
aliases: []
intent: >-
  Replace a boolean control-flag variable used to break out of loops or conditionals with break, return, or continue
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/remove-control-flag
  - https://refactoring.com/catalog/removeControlFlag.html
smells_it_fixes:
  - mutable-shared-state
  - long-method
  - unclear-naming
smells_it_introduces: []
composes_with:
  - extract-method
  - replace-nested-conditional-with-guard-clauses
  - consolidate-conditional-expression
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass after removing the flag"
  - "The loop or conditional exits at the same logical point as when the flag was set"
  - "No boolean flag variable remains to track exit conditions"
---

# Remove Control Flag

## Intent

A boolean variable that is set to `true` inside a loop or conditional to signal "we are done" is a manual reimplementation of `break`, `return`, or `continue`. These language constructs communicate exit intent directly and visibly; the flag hides it behind a mutation and deferred check. Replace the flag-set with the appropriate control-flow statement and delete the flag.

## Structure

```
before:
  found = false
  for each person in people
    if not found
      if person == "Don"
        sendAlert()
        found = true
      if person == "John"
        sendAlert()
        found = true

after:
  for each person in people
    if person == "Don" || person == "John"
      sendAlert()
      break
```

## Applicability

- A boolean variable is initialized before a loop, set to `true` (or `false`) inside it, and checked as the loop continuation condition or inside the loop body.
- The flag's only purpose is to signal early exit — it carries no semantic meaning beyond "stop".
- The language supports `break`, `return`, or `continue` (i.e., virtually all modern languages).

## Consequences

**Gains**
- The control flow intent is immediately visible at the exit point instead of being communicated via a flag checked later.
- Removes a mutable variable whose sole purpose is to defer a decision.
- Simplifies the loop body; the nesting level often decreases.

**Costs**
- If structured programming disciplines forbid multiple exit points, this refactoring violates the preference — a trade-off between ideology and clarity.
- When the flag also carries information (not just "done?"), it may need to remain or be replaced with a richer return value.

## OOP shape

```
class PersonScanner
  // Before
  scan(people)
    found = false
    for person in people
      if not found
        if person == targetPerson
          doSomething(person)
          found = true

  // After
  scan(people)
    for person in people
      if person == targetPerson
        doSomething(person)
        break
```

## FP shape

```
-- FP uses early return via pattern matching or Maybe — no mutable flag exists
-- Before (flag translated to accumulator)
scan :: [Person] -> IO ()
scan [] = return ()
scan (p:ps)
  | p == target = doSomething p   -- implicit stop via non-recursion
  | otherwise   = scan ps

-- After (same — idiomatic FP never had the flag to begin with)
-- The refactoring enforces the same discipline in imperative code.
```

## Smells fixed

- **mutable-shared-state** — the flag is a mutation whose effect is a delayed conditional; replacing it with `break`/`return` eliminates the mutation.
- **long-method** — removing flag initialization, flag-check wrapper, and flag-set typically shaves several lines and one indentation level.
- **unclear-naming** — names like `done`, `found`, `exitLoop` communicate nothing about *why* exiting is warranted; `break` placed at the exit point does.

## Tests implied

- **Behavior preserved** — the full test suite passes; the loop exits at the same iteration as before.
- **Same logical exit point** — trace the control flow: the refactored loop exits on the same element that caused the flag to be set.
- **No residual flag** — static analysis confirms the boolean variable no longer exists.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/remove-control-flag
- https://refactoring.com/catalog/removeControlFlag.html
