---
id: 01-cache-store
files:
  create:
    - src/cache/cache-store.ts
    - src/cache/cache-store.test.ts
  modify: []
context:
  - name: CacheStore
    new: true
    signature: |
      interface CacheStore<V> {
        get(key: string): V | undefined
        set(key: string, value: V, ttl?: number): void
        has(key: string): boolean
      }
---

# 01-cache-store

## RED

### Action
Write a test asserting that `set` followed by `get` returns the stored value, and `get` on an unknown key returns `undefined`.

### Example
```ts
import { describe, it, expect } from "vitest"
import { InMemoryCacheStore } from "./cache-store"

describe("InMemoryCacheStore", () => {
  it("returns stored value after set", () => {
    const store = new InMemoryCacheStore<string>()
    store.set("db.host", "localhost")
    expect(store.get("db.host")).toBe("localhost")
  })

  it("returns undefined for unknown key", () => {
    const store = new InMemoryCacheStore<string>()
    expect(store.get("missing")).toBeUndefined()
  })
})
```

### Test invariants
- "Two calls to the accessor method return the same instance (reference equality)"
- "The single instance satisfies the full interface contract of the underlying type"

### Verify
```sh
npx vitest run src/cache/cache-store.test.ts
```

### Done
Test fails because `InMemoryCacheStore` does not exist.

## GREEN

### Pattern hint
Compose using Singleton (see `src/cache/cache-store.ts` -- single shared cache instance per process). Evidence: neighboring session cache uses module-level singleton export.

### Action
Implement `InMemoryCacheStore` as a class satisfying `CacheStore<V>`. Use a `Map` internally. Export both the interface and the class.

### Example
```ts
export interface CacheStore<V> {
  get(key: string): V | undefined
  set(key: string, value: V, ttl?: number): void
  has(key: string): boolean
}

export class InMemoryCacheStore<V> implements CacheStore<V> {
  private store = new Map<string, V>()
  get(key: string): V | undefined { return this.store.get(key) }
  set(key: string, value: V): void { this.store.set(key, value) }
  has(key: string): boolean { return this.store.has(key) }
}
```

### Verify
```sh
npx vitest run src/cache/cache-store.test.ts
```

### Done
Test passes.

## REFACTOR

### Action
No refactoring needed -- GREEN followed pattern, structure is adequate.

### Verify
```sh
npx vitest run src/cache/cache-store.test.ts
```

### Done
Test still passes.
