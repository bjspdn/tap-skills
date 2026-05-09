---
name: substitute-algorithm
category: refactoring
aliases: []
intent: >-
  Replace the body of a method with a cleaner algorithm that produces the same results
sources:
  - https://refactoring.guru/refactoring/techniques/composing-methods/substitute-algorithm
  - https://refactoring.com/catalog/substituteAlgorithm.html
smells_it_fixes:
  - duplicate-algorithm-variants
  - long-method
  - unclear-naming
smells_it_introduces:
  - speculative-generality
composes_with:
  - extract-method
  - replace-method-with-method-object
clashes_with: []
test_invariants:
  - "Behavior preserved — all existing tests still pass with the new algorithm"
  - "New algorithm produces identical outputs for the full input domain, including edge cases"
  - "New algorithm is demonstrably simpler or more readable than the original"
---

# Substitute Algorithm

## Intent

Sometimes there is a better way to do the same thing. If you discover a clearer, simpler, or more library-aligned algorithm that produces identical results, replace the old body wholesale rather than incrementally patching it. This is distinct from incremental refactoring: you are replacing the logic, not restructuring it. A thorough test suite is essential — it defines "identical results" precisely.

## Structure

```
before:
  method foundPerson(people) -> String
    for i = 0 to people.length
      if people[i] == "Don"   then return "Don"
      if people[i] == "John"  then return "John"
      if people[i] == "Kent"  then return "Kent"
    return ""

after:
  method foundPerson(people) -> String
    candidates = ["Don", "John", "Kent"]
    return people.find(p -> candidates.contains(p)) ?? ""
```

## Applicability

- You know a simpler algorithm that is provably equivalent and better understood by the team.
- A method evolved through patches and is now harder to read than a clean rewrite would be.
- A library function now exists that replaces hand-rolled logic — standard collection ops, date math, etc.
- The existing algorithm has performance characteristics that a known alternative improves.

## Consequences

**Gains**
- The replacement algorithm may be shorter, clearer, and closer to the language's idiomatic style.
- Library-based replacements gain maintenance, correctness, and performance benefits for free.
- Removes subtly buggy hand-rolled logic.

**Costs**
- Requires a comprehensive test suite — without one, "same behavior" is a guess.
- The new algorithm must handle all edge cases the old one handled, including undocumented ones encoded in existing tests.
- A wholesale rewrite loses the incremental safety of small refactoring steps.

## OOP shape

```
class PersonFinder
  // Before: imperative scan
  foundPerson(people) -> String
    for each person in people
      if person == "Don"  return "Don"
      if person == "John" return "John"
      if person == "Kent" return "Kent"
    return ""

  // After: declarative with membership check
  foundPerson(people) -> String
    known = Set { "Don", "John", "Kent" }
    return people.firstOrDefault(p -> known.contains(p)) ?? ""
```

## FP shape

```
-- Before: explicit recursion / pattern match per name
foundPerson :: [Person] -> Maybe Person
foundPerson [] = Nothing
foundPerson (p:ps)
  | p `elem` ["Don","John","Kent"] = Just p
  | otherwise = foundPerson ps

-- After: higher-order standard library
foundPerson :: [Person] -> Maybe Person
foundPerson people = find (`elem` ["Don","John","Kent"]) people
```

## Smells fixed

- **duplicate-algorithm-variants** — when the same search/transform logic is expressed in multiple places in slightly different forms, substituting each with a canonical implementation eliminates divergence.
- **long-method** — a hand-rolled loop doing what a library function does in one line; substitution collapses the length.
- **unclear-naming** — an imperative algorithm hides its intent in control flow; a declarative substitute names the operation directly.

## Tests implied

- **Behavior preserved** — the full test suite passes unchanged; this is the only verification needed for a pure substitution.
- **Edge-case coverage** — before substituting, verify the test suite exercises empty inputs, single-element inputs, missing values, and boundary conditions to ensure the new algorithm handles them identically.
- **Demonstrable simplicity** — the new algorithm should be inspectable and obviously correct in fewer lines or cognitive steps than the original.

## Sources

- https://refactoring.guru/refactoring/techniques/composing-methods/substitute-algorithm
- https://refactoring.com/catalog/substituteAlgorithm.html
