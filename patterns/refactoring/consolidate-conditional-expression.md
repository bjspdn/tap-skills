---
name: consolidate-conditional-expression
category: refactoring
aliases: []
intent: >-
  Merge multiple separate conditionals with the same result into one combined condition, then extract it as a method
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/consolidate-conditional-expression
  - https://refactoring.com/catalog/consolidateConditionalExpression.html
smells_it_fixes:
  - duplicate-code
  - long-conditional-chain
  - comments-as-deodorant
smells_it_introduces: []
composes_with:
  - extract-method
  - decompose-conditional
  - remove-control-flag
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass after consolidation"
  - "The merged condition produces true under exactly the same circumstances as the separate conditions did"
  - "The extracted method name communicates the shared semantics of all merged conditions"
---

# Consolidate Conditional Expression

## Intent

When several independent checks all result in the same action, they are logically one compound condition expressing a single reason. Combine them with `||` or `&&` into one condition, then Extract Method on that condition so the name reveals the shared meaning. The result replaces a sequence of "if … return X; if … return X; if … return X" with "if combinedReason() return X".

## Structure

```
before:
  method disabilityAmount(employee) -> Money
    if employee.seniority < 2         then return 0
    if employee.monthsDisabled > 12   then return 0
    if employee.isPartTime            then return 0
    return calculateDisability(employee)

after:
  method disabilityAmount(employee) -> Money
    if isIneligible(employee) then return 0
    return calculateDisability(employee)

  method isIneligible(employee) -> Boolean
    return employee.seniority < 2
        || employee.monthsDisabled > 12
        || employee.isPartTime
```

## Applicability

- Multiple consecutive guards all return (or assign) the same value.
- The checks are not independent business rules — they collectively represent one conceptual reason to exit/skip.
- No side effects exist in any of the individual conditions (pure boolean checks only).
- After consolidation, the combined condition has a name worth extracting.

## Consequences

**Gains**
- Eliminates repetition of the same outcome across multiple conditions.
- The extracted method names the underlying intent — "is ineligible" rather than listing reasons.
- Simplifies the main method to a readable policy check.

**Costs**
- If the conditions are truly independent business rules that happen to share an action, merging hides the distinction and makes future divergence harder.
- Do not consolidate if any branch has side effects or if each branch's reason should remain separately auditable.

## OOP shape

```
class DisabilityCalculator
  // Before: repeated early-return pattern
  calculate(employee) -> Money
    if employee.seniority < 2       return zeroDisability
    if employee.monthsDisabled > 12 return zeroDisability
    if employee.isPartTime          return zeroDisability
    return computeFullDisability(employee)

  // After: consolidated guard
  calculate(employee) -> Money
    if isIneligible(employee) return zeroDisability
    return computeFullDisability(employee)

  private isIneligible(employee) -> Boolean
    return employee.seniority < 2
        || employee.monthsDisabled > 12
        || employee.isPartTime
```

## FP shape

```
isIneligible :: Employee -> Bool
isIneligible e =
  e.seniority < 2 || e.monthsDisabled > 12 || e.isPartTime

calculate :: Employee -> Money
calculate e
  | isIneligible e = zeroDisability
  | otherwise      = computeFullDisability e
```

## Smells fixed

- **duplicate-code** — the repeated "return 0" or "return null" that appears after each guard is deduplicated into one exit point.
- **long-conditional-chain** — a sequence of same-result guards is collapsed into a single named condition.
- **comments-as-deodorant** — a comment like `// not eligible for disability` appears once above a merged method instead of scattered across three checks.

## Tests implied

- **Behavior preserved** — the full test suite passes; the merged condition fires under exactly the same scenarios.
- **Condition equivalence** — for any combination of `(seniority, monthsDisabled, isPartTime)` where the old code returned zero, the new `isIneligible` returns true.
- **Name matches semantics** — the extracted method name accurately describes all circumstances under which it returns true.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/consolidate-conditional-expression
- https://refactoring.com/catalog/consolidateConditionalExpression.html
