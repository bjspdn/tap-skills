---
name: replace-exception-with-test
category: refactoring
aliases: [replace-exception-with-conditional]
intent: >-
  Replace an exception thrown for an avoidable condition with a guard check that prevents the exceptional state
sources:
  - https://refactoring.guru/refactoring/techniques/simplifying-method-calls
  - https://refactoring.com/catalog/replaceExceptionWithTest.html
smells_it_fixes:
  - duplicate-error-handling
smells_it_introduces: []
composes_with:
  - separate-query-from-modifier
  - replace-error-code-with-exception
clashes_with:
  - replace-error-code-with-exception
test_invariants:
  - "The guard check prevents the exception from being thrown for all inputs the caller can test in advance"
  - "The exception path still exists for truly unexpected conditions not checkable by the caller"
---

# Replace Exception with Test

## Intent

Exceptions should signal truly exceptional, unexpected conditions — not ordinary control flow. When a caller can trivially test whether a condition is safe before calling a method, using an exception to signal that condition is an abuse of the mechanism: it is expensive, hides intent, and trains developers to ignore exceptions. Replace such exceptions with a conditional check (guard) that the caller executes before invoking the method.

## Structure

Before:
```
try {
  value = table.get(key)
} catch (KeyNotFoundException e) {
  value = defaultValue
}
```

After:
```
value = table.containsKey(key) ? table.get(key) : defaultValue
```

## Applicability

- The caller can check for the exceptional condition before the call without significant cost or race conditions
- The condition is an expected variant of normal operation (e.g. a key might not be in a map), not a programming error
- The exception is being used as a control-flow mechanism rather than a true error signal
- The check is idempotent and the state cannot change between the check and the method call (in single-threaded or lock-guarded contexts)

## Consequences

- **Clearer intent** — a conditional check reads as "if available, use it" rather than "try and catch the absence"
- **Better performance** — avoids exception construction and stack unwinding on the common path
- **Honest control flow** — the conditional branch is visible at the call site; exceptions are invisible control flow
- **TOCTOU risk** — in concurrent code, the state may change between the check and the use; a try/catch is sometimes the only safe option
- **Exception still needed** — the method should still throw for callers that skip the guard or for conditions the caller cannot check

## OOP shape

```
// Before — using exception for flow
class ResourcePool {
  get(id: ResourceId): Resource  // throws ResourceNotFoundException
}
try {
  resource = pool.get(id)
} catch (ResourceNotFoundException e) {
  resource = pool.allocate()
}

// After — check before call
class ResourcePool {
  contains(id: ResourceId): Boolean
  get(id: ResourceId): Resource
}
resource = pool.contains(id) ? pool.get(id) : pool.allocate()
```

## FP shape

```
// Before — exception-as-control-flow
const getOrDefault = <K, V>(map: Map<K, V>, key: K, def: V): V => {
  try { return map.get(key) }  // throws if absent
  catch { return def }
}

// After — test before access
const getOrDefault = <K, V>(map: Map<K, V>, key: K, def: V): V =>
  map.has(key) ? map.get(key) : def

// FP-idiomatic: return an Option/Maybe and fold
const getOpt = <K, V>(map: Map<K, V>, key: K): Option<V> =>
  map.has(key) ? Some(map.get(key)) : None

getOpt(map, key).getOrElse(defaultValue)
```

## Smells fixed

- **duplicate-error-handling** — every call site wrapping the same try/catch for a predictable absence is replaced by a single guard pattern, centralizing the "missing" case handling

## Tests implied

- **Guard prevents exception** — assert that when the condition is safe (key present, resource allocated), calling through the guard never throws
- **Exception still fires for unexpected** — assert that the method still throws when called without the guard and the condition is not met, confirming the exception path is preserved for truly unexpected callers

## Sources

- https://refactoring.guru/refactoring/techniques/simplifying-method-calls
- https://refactoring.com/catalog/replaceExceptionWithTest.html
