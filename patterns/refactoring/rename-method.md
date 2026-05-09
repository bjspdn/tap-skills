---
name: rename-method
category: refactoring
aliases: [rename-function]
intent: >-
  Change a method's name to better communicate its purpose and eliminate the need for comments
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/renameMethod.html
smells_it_fixes:
  - unclear-naming
  - comments-as-deodorant
smells_it_introduces: []
composes_with:
  - extract-method
  - introduce-parameter-object
clashes_with: []
test_invariants:
  - "Behavior is identical before and after the rename"
  - "All call sites compile and pass against the new name"
---

# Rename Method

## Intent

A method name that does not reveal its intent forces readers to inspect the body to understand what it does. Renaming the method to reflect its true purpose removes this cognitive overhead and makes the code self-documenting. The transformation is purely nominal — no logic changes.

## Structure

Before:
```
class Customer {
  getThem(): List
}
```

After:
```
class Customer {
  getOutstandingInvoices(): List
}
```

## Applicability

- The method name is an abbreviation, acronym, or internal jargon not shared by the domain
- A comment is required at the call site to explain what the method does
- The method was named for its implementation rather than its intent
- The codebase has adopted a new ubiquitous language and old names no longer match

## Consequences

- **Improved readability** — the name becomes documentation; comments at call sites can be removed
- **Alignment with domain language** — bridging code and business vocabulary reduces translation overhead
- **Merge conflicts during transition** — rename must be atomic across all call sites to avoid broken builds
- **IDE assistance required at scale** — manual rename in large codebases is error-prone; use automated rename tooling

## OOP shape

```
// Step 1: introduce new name, delegate from old
class Foo {
  newName(): Result { ... }
  oldName(): Result { return this.newName() }  // deprecated shim
}

// Step 2: migrate all callers to newName()
// Step 3: remove oldName()
```

## FP shape

```
// Before
const gt = (xs) => xs.filter(x => x.status === 'outstanding')

// After — rename to reflect intent
const getOutstandingInvoices = (invoices) =>
  invoices.filter(invoice => invoice.status === 'outstanding')

// In FP: rebind the name; the function value is unchanged
```

## Smells fixed

- **unclear-naming** — a cryptic name like `getThem` or `calc` is replaced with a name that reads as a sentence fragment at the call site
- **comments-as-deodorant** — inline `// gets outstanding invoices` comments above every call become redundant once the method is properly named

## Tests implied

- **Behavioral identity** — run the full test suite against both the old and new name (via a temporary shim) to confirm zero behavioral change
- **Call-site coverage** — every call site referencing the old name is updated; a compile-error or grep-zero confirms no stale references remain

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/renameMethod.html
