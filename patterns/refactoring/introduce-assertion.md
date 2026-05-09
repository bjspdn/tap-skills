---
name: introduce-assertion
category: refactoring
aliases: []
intent: >-
  Make an implicit assumption about program state explicit by adding an assertion that documents and enforces the precondition
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/introduce-assertion
  - https://refactoring.com/catalog/introduceAssertion.html
smells_it_fixes:
  - comments-as-deodorant
  - unclear-naming
  - duplicate-error-handling
smells_it_introduces: []
composes_with:
  - replace-nested-conditional-with-guard-clauses
  - remove-control-flag
  - extract-method
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass; assertions do not fire in valid scenarios"
  - "The assertion fires immediately and visibly when its assumed condition is violated"
  - "Each assertion documents a precondition or invariant that was previously only implied by comments or convention"
---

# Introduce Assertion

## Intent

Code often relies on assumptions — a value must be positive, a list must not be empty, a pointer must be non-null — that are expressed only in comments or silently assumed without any check. Replace these implicit assumptions with explicit assertions. An assertion makes the contract visible to readers, provides a loud failure at the site of the violated assumption (rather than a cryptic failure downstream), and acts as living executable documentation of what the code requires to function correctly.

## Structure

```
before:
  method getExpenseLimit() -> Money
    // assume either project or billing account is present
    return expenseLimit != null
      ? expenseLimit
      : primaryProject.getMemberExpenseLimit()

after:
  method getExpenseLimit() -> Money
    assert expenseLimit != null || primaryProject != null
    return expenseLimit != null
      ? expenseLimit
      : primaryProject.getMemberExpenseLimit()
```

## Applicability

- A piece of code will fail in a confusing way if a certain precondition does not hold, and that precondition is currently undocumented.
- A comment says "we can assume X here" — the comment should be an assertion.
- A conditional checks for a "this should never happen" case — an assertion is clearer than a silent return or a thrown exception for truly impossible states.
- You are documenting an invariant for future maintainers during a refactoring pass.

## Consequences

**Gains**
- Assumptions become executable and visible — they fail loudly at the exact point of violation.
- Removes the need for defensive handling of states that should be impossible.
- Aids debugging: the assertion fires at the origin of a problem, not at the downstream symptom.
- Assertions disabled in production typically have zero performance cost in assertion-supporting runtimes.

**Costs**
- Assertions should not be used to handle expected runtime errors (invalid user input, network failures) — use exceptions for those.
- In languages where assertions are disabled in production builds, callers may rely on the check only in development.
- Over-asserting clutters code with checks on things that cannot realistically fail.

## OOP shape

```
class ExpenseCalculator
  expenseLimit: Money?
  primaryProject: Project?

  // Before: assumption implicit
  getExpenseLimit() -> Money
    // one of these must be set
    return expenseLimit ?? primaryProject.getMemberExpenseLimit()

  // After: assumption explicit
  getExpenseLimit() -> Money
    assert expenseLimit != null || primaryProject != null,
      "ExpenseCalculator requires either an expenseLimit or a primaryProject"
    return expenseLimit ?? primaryProject.getMemberExpenseLimit()
```

## FP shape

```
-- FP equivalent: encode the precondition in the type (NonEmpty, Positive, etc.)
-- When types are insufficient, use an assertion function:

getExpenseLimit :: Maybe Money -> Maybe Project -> Money
getExpenseLimit expenseLimit project =
  assert (isJust expenseLimit || isJust project)
         "One of expenseLimit or project must be present"
    $ fromMaybe
        (memberExpenseLimit (fromJust project))
        expenseLimit

-- Preferred FP form: use smart constructors that make the invalid state unrepresentable.
```

## Smells fixed

- **comments-as-deodorant** — a comment saying "we assume X" becomes an `assert X` — same information, enforced rather than merely noted.
- **unclear-naming** — an assertion's message documents the invariant by name, replacing vague comments about what "must be true here".
- **duplicate-error-handling** — multiple defensive null-checks for a condition that should never be null are replaced by one assertion at the canonical entry point.

## Tests implied

- **Behavior preserved** — all existing valid-scenario tests pass; no assertion fires in normal execution paths.
- **Assertion fires on violation** — a test deliberately violates the precondition and asserts that the assertion error (not a silent wrong result or a downstream NullPointerException) is raised.
- **Precondition documented** — the assertion message clearly states the violated contract so the error is immediately actionable.

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-conditional-expressions/introduce-assertion
- https://refactoring.com/catalog/introduceAssertion.html
