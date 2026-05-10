---
id: 02-warming-strategy
files:
  create:
    - src/cache/warming-strategy.ts
    - src/cache/warming-strategy.test.ts
  modify: []
context:
  - name: CacheStore
    path: src/cache/cache-store.ts
    line: 1
    signature: |
      interface CacheStore<V> {
        get(key: string): V | undefined
        set(key: string, value: V, ttl?: number): void
        has(key: string): boolean
      }
  - name: WarmingStrategy
    new: true
    signature: |
      interface WarmingStrategy {
        warm(store: CacheStore<string>): Promise<void>
      }
  - name: FullWarmStrategy
    new: true
    signature: |
      class FullWarmStrategy implements WarmingStrategy {
        constructor(private loader: () => Promise<Record<string, string>>)
        warm(store: CacheStore<string>): Promise<void>
      }
---

# 02-warming-strategy

## RED

### Action
Write a test asserting that `FullWarmStrategy.warm()` populates the store with all entries returned by the loader function.

### Example
```ts
import { describe, it, expect, vi } from "vitest"
import { FullWarmStrategy } from "./warming-strategy"
import { InMemoryCacheStore } from "./cache-store"

describe("FullWarmStrategy", () => {
  it("populates store with all loader entries", async () => {
    const loader = vi.fn().mockResolvedValue({ "db.host": "localhost", "db.port": "5432" })
    const store = new InMemoryCacheStore<string>()
    const strategy = new FullWarmStrategy(loader)

    await strategy.warm(store)

    expect(store.get("db.host")).toBe("localhost")
    expect(store.get("db.port")).toBe("5432")
    expect(loader).toHaveBeenCalledOnce()
  })
})
```

### Test invariants
- "All strategy variants conform to the strategy interface contract"
- "Context delegates without inspecting the concrete strategy type"
- "Swapping strategies at runtime produces the behavior of the new strategy from that point forward"

### Verify
```sh
npx vitest run src/cache/warming-strategy.test.ts
```

### Done
Test fails because `FullWarmStrategy` does not exist.

## GREEN

### Pattern hint
Compose using Strategy (see `patterns/behavioral/strategy.md`). The warming algorithm is encapsulated behind `WarmingStrategy`; context (`CacheWarmer`) delegates without type-checking the variant.

### Action
Implement `WarmingStrategy` interface and `FullWarmStrategy` class. The strategy iterates loader output and calls `store.set()` for each entry.

### Example
```ts
import type { CacheStore } from "./cache-store"

export interface WarmingStrategy {
  warm(store: CacheStore<string>): Promise<void>
}

export class FullWarmStrategy implements WarmingStrategy {
  constructor(private loader: () => Promise<Record<string, string>>) {}

  async warm(store: CacheStore<string>): Promise<void> {
    const entries = await this.loader()
    for (const [key, value] of Object.entries(entries)) {
      store.set(key, value)
    }
  }
}
```

### Verify
```sh
npx vitest run src/cache/warming-strategy.test.ts
```

### Done
Test passes.

## REFACTOR

### Action
No refactoring needed -- GREEN followed pattern, structure is adequate.

### Verify
```sh
npx vitest run src/cache/warming-strategy.test.ts
```

### Done
Test still passes.
