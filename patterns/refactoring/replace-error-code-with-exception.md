---
name: replace-error-code-with-exception
category: refactoring
aliases: []
intent: >-
  Replace a special return value that signals failure with an exception so error paths are explicit and unignorable
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/replaceErrorCodeWithException.html
smells_it_fixes:
  - duplicate-error-handling
  - unclear-naming
smells_it_introduces:
  - temporal-coupling
composes_with:
  - replace-exception-with-test
  - separate-query-from-modifier
clashes_with:
  - replace-exception-with-test
test_invariants:
  - "The method throws the expected exception type under the error condition, not return the error code"
  - "Callers that previously checked the return code are replaced by exception handlers or the check is moved to a guard"
---

# Replace Error Code with Exception

## Intent

A method that returns a special value (−1, null, an enum sentinel) to signal failure relies on every caller to check and handle that signal. Callers that forget to check silently propagate the error. Throwing an exception makes the error path impossible to ignore: uncaught exceptions terminate the operation visibly rather than silently continuing in a broken state. Use checked exceptions for recoverable conditions and unchecked for programming errors.

## Structure

Before:
```
result = object.withdraw(amount)
if (result == -1) handleError()
else useResult(result)
```

After:
```
try {
  object.withdraw(amount)
  // success path
} catch (InsufficientFundsError e) {
  handleError(e)
}
```

## Applicability

- The method returns a sentinel value to indicate failure and callers routinely forget or inconsistently handle it
- The error condition is genuinely exceptional — not an ordinary control-flow branch
- The language supports exceptions
- The method is called from many sites and centralizing error handling is desirable

## Consequences

- **Unignorable errors** — uncaught exceptions propagate up the call stack; silent failure is eliminated
- **Cleaner success path** — the success path is not littered with null/error checks
- **Separation of concerns** — error handling is isolated to catch blocks rather than interleaved with normal logic
- **Performance overhead** — exception construction and stack unwinding can be expensive in hot paths; not appropriate as normal control flow
- **Misuse risk** — over-use of exceptions for ordinary conditions (see Replace Exception with Test) blurs the signal/noise ratio

## OOP shape

```
// Before — error code return
class Account {
  withdraw(amount: Money): Int {  // returns -1 on insufficient funds
    if (amount > this.balance) return -1
    this.balance -= amount
    return 0
  }
}
if (account.withdraw(100) == -1) { ... }

// After — exception
class Account {
  withdraw(amount: Money): void {
    if (amount > this.balance) throw InsufficientFundsException(amount)
    this.balance -= amount
  }
}
try { account.withdraw(100) }
catch (InsufficientFundsException e) { ... }
```

## FP shape

```
// Before — nullable/sentinel return
const withdraw = (amount: Money, account: Account): Account | null =>
  amount > account.balance ? null : { ...account, balance: account.balance - amount }

// FP idiomatic: use a Result/Either type instead of exceptions
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E }

const withdraw = (amount: Money, account: Account): Result<Account, InsufficientFunds> =>
  amount > account.balance
    ? { ok: false, error: { kind: 'insufficient-funds', needed: amount } }
    : { ok: true,  value: { ...account, balance: account.balance - amount } }
```

## Smells fixed

- **duplicate-error-handling** — every caller duplicating `if (result == -1)` checks is replaced by a single exception handler at an appropriate level
- **unclear-naming** — a return value of `-1` or `null` communicates nothing about why it failed; a named exception type (e.g. `InsufficientFundsException`) names the failure condition

## Tests implied

- **Exception thrown on error** — assert that calling the method with an invalid input throws the named exception, not returns a sentinel
- **Success path unchanged** — assert that valid inputs produce the same result as before and do not throw

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/replaceErrorCodeWithException.html
