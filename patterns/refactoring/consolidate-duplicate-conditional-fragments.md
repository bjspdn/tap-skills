---
name: consolidate-duplicate-conditional-fragments
category: refactoring
aliases: []
intent: >-
  Move code that appears in every branch of a conditional outside the conditional so it executes unconditionally
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/consolidate-duplicate-conditional-fragments
  - https://refactoring.com/catalog/consolidateDuplicateConditionalFragments.html
smells_it_fixes:
  - duplicate-code
  - long-conditional-chain
smells_it_introduces: []
composes_with:
  - consolidate-conditional-expression
  - extract-method
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass after consolidation"
  - "The moved statement executes exactly once regardless of which branch would have been taken"
  - "No branch retains a copy of the moved statement"
---

# Consolidate Duplicate Conditional Fragments

## Intent

When the same statement appears at the end (or start) of every branch of an `if-then-else`, it is not truly conditional — it always executes. Move it outside the conditional, before or after, as appropriate. This removes unnecessary duplication and clarifies that the statement is independent of the branching logic.

## Structure

```
before:
  if isSpecialDeal()
    total = price * 0.95
    send(total)
  else
    total = price * 0.98
    send(total)     // send() duplicated in both branches

after:
  if isSpecialDeal()
    total = price * 0.95
  else
    total = price * 0.98
  send(total)       // moved after the conditional
```

## Applicability

- An identical statement (or sequence of statements) appears in all branches of a conditional.
- Moving the statement before/after the conditional does not change observable behavior — ordering must be safe.
- The duplication is mechanical: the same call with the same arguments in each branch.

## Consequences

**Gains**
- Eliminates obvious duplication; the conditional narrows to what is genuinely different per branch.
- Makes the unconditional nature of the shared statement explicit.
- Reduces the risk of branches diverging when the shared statement is updated.

**Costs**
- Requires confidence that moving the statement preserves ordering semantics (no interleaved side effects).
- If the statement's behavior depends on state set within a branch, it cannot be safely moved.

## OOP shape

```
class Sale
  // Before
  process(isSpecial) -> void
    if isSpecial
      total = price * 0.95
      sendInvoice(total)      // duplicated
    else
      total = price * 0.98
      sendInvoice(total)      // duplicated

  // After
  process(isSpecial) -> void
    if isSpecial then total = price * 0.95
    else              total = price * 0.98
    sendInvoice(total)        // consolidated
```

## FP shape

```
-- Before
process isSpecial price =
  if isSpecial
    then let t = price * 0.95 in sendInvoice t
    else let t = price * 0.98 in sendInvoice t

-- After
process isSpecial price =
  let total = if isSpecial then price * 0.95 else price * 0.98
  in  sendInvoice total
```

## Smells fixed

- **duplicate-code** — identical statements duplicated across every conditional branch are collapsed to a single unconditional occurrence.
- **long-conditional-chain** — each branch shrinks to only the part that is genuinely conditional, making the intent of the branching clearer.

## Tests implied

- **Behavior preserved** — the full test suite passes; the moved statement executes in both the true and false path.
- **Executes exactly once** — a spy or side-effect counter on the moved statement confirms it fires exactly once per call regardless of branch.
- **No branch residual** — code inspection confirms neither branch retains a copy of the moved statement.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/consolidate-duplicate-conditional-fragments
- https://refactoring.com/catalog/consolidateDuplicateConditionalFragments.html
