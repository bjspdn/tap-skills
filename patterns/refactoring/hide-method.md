---
name: hide-method
category: refactoring
aliases: []
intent: >-
  Reduce a method's visibility to the minimum access level required by its actual callers
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/hideMethod.html
smells_it_fixes:
  - speculative-generality
  - inappropriate-intimacy
smells_it_introduces: []
composes_with:
  - remove-setting-method
  - extract-method
clashes_with: []
test_invariants:
  - "All callers that existed before the visibility reduction still compile and pass"
  - "No caller outside the intended scope can reference the method after the change"
---

# Hide Method

## Intent

A method that is more visible than necessary expands the public API surface of a class, inviting callers to depend on internals and making future changes riskier. Reducing visibility to the narrowest level that satisfies all legitimate callers shrinks the API contract and signals that the method is an implementation detail rather than a stable interface. The transformation is structural only — no logic changes.

## Structure

Before:
```
class Account {
  public adjustBalance(amount: Money): void  // only called internally
}
```

After:
```
class Account {
  private adjustBalance(amount: Money): void
}
```

## Applicability

- Static analysis or a codebase-wide search confirms no external caller references the method
- The method is a helper used only within its own class or package
- A previous refactoring left a method public that no longer needs to be

## Consequences

- **Smaller public API** — fewer methods are part of the stable contract; future changes are cheaper
- **Encapsulation enforced** — internal implementation details cannot be accidentally depended on
- **Compile-time breakage** — if a caller was missed, the visibility reduction produces an immediate compile error, which is the desired discovery mechanism
- **Test access friction** — unit tests that directly call private helpers will break; prefer testing through the public interface

## OOP shape

```
// Before — overly broad visibility
class BankAccount {
  public credit(amount: Money): void  { this.adjustBalance(+amount) }
  public debit(amount: Money): void   { this.adjustBalance(-amount) }
  public adjustBalance(delta: Money): void { this.balance += delta }  // should be private
}

// After
class BankAccount {
  public credit(amount: Money): void  { this.adjustBalance(+amount) }
  public debit(amount: Money): void   { this.adjustBalance(-amount) }
  private adjustBalance(delta: Money): void { this.balance += delta }
}
```

## FP shape

```
// Before — helper exported from module, implicitly public
export const adjustBalance = (delta: Money, account: Account): Account =>
  ({ ...account, balance: account.balance + delta })

// After — not exported; internal to module
const adjustBalance = (delta: Money, account: Account): Account =>
  ({ ...account, balance: account.balance + delta })

export const credit = (amount: Money, account: Account): Account =>
  adjustBalance(+amount, account)
export const debit  = (amount: Money, account: Account): Account =>
  adjustBalance(-amount, account)
```

## Smells fixed

- **speculative-generality** — a method made public "in case someone needs it later" but never used externally is a speculative API; hiding it removes the phantom contract
- **inappropriate-intimacy** — when external classes call internal helper methods, reducing visibility forces callers to use the intended public interface

## Tests implied

- **Call-site exhaustiveness** — compile the codebase after the visibility reduction; zero compile errors confirms no callers were missed
- **Behavior unchanged** — run the full test suite; because the method's logic is unchanged, all existing tests should pass without modification

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/hideMethod.html
