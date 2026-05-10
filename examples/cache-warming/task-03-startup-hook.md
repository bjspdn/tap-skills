---
id: 03-startup-hook
files:
  create:
    - src/cache/cache-warmer.ts
    - src/cache/cache-warmer.test.ts
  modify:
    - path: src/server/bootstrap.ts
      anchor: startServer
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
    path: src/cache/warming-strategy.ts
    line: 3
    signature: |
      interface WarmingStrategy {
        warm(store: CacheStore<string>): Promise<void>
      }
  - name: startServer
    path: src/server/bootstrap.ts
    line: 14
    signature: |
      export async function startServer(config: AppConfig): Promise<void>
---

# 03-startup-hook

## RED

### Action
Write a test asserting that `CacheWarmer.warm()` invokes the strategy and that `startServer` calls the warmer before binding the port.

### Example
```ts
import { describe, it, expect, vi } from "vitest"
import { CacheWarmer } from "./cache-warmer"
import { InMemoryCacheStore } from "./cache-store"

describe("CacheWarmer", () => {
  it("delegates to warming strategy and completes before returning", async () => {
    const store = new InMemoryCacheStore<string>()
    const strategy = { warm: vi.fn().mockResolvedValue(undefined) }
    const warmer = new CacheWarmer(store, strategy)

    await warmer.warm()

    expect(strategy.warm).toHaveBeenCalledWith(store)
  })

  it("logs warning and continues if strategy throws", async () => {
    const store = new InMemoryCacheStore<string>()
    const strategy = { warm: vi.fn().mockRejectedValue(new Error("timeout")) }
    const warmer = new CacheWarmer(store, strategy)

    await expect(warmer.warm()).resolves.toBeUndefined()
  })
})
```

### Verify
```sh
npx vitest run src/cache/cache-warmer.test.ts
```

### Done
Test fails because `CacheWarmer` does not exist.

## GREEN

### Action
Implement `CacheWarmer` that wraps a `CacheStore` and `WarmingStrategy`. The `warm()` method delegates to the strategy inside a try/catch that logs on failure. Wire into `startServer` before the listener bind call.

### Example
```ts
import type { CacheStore } from "./cache-store"
import type { WarmingStrategy } from "./warming-strategy"

export class CacheWarmer {
  constructor(
    private store: CacheStore<string>,
    private strategy: WarmingStrategy
  ) {}

  async warm(): Promise<void> {
    try {
      await this.strategy.warm(this.store)
    } catch (err) {
      console.warn("[cache-warmer] warming failed, continuing with cold cache:", err)
    }
  }
}
```

### Verify
```sh
npx vitest run src/cache/cache-warmer.test.ts
```

### Done
Test passes.

## REFACTOR

### Action
Extract the error-handling wrapper into a private `safeDelegation` method on `CacheWarmer`. Rename `err` to `cause` for clarity.

### Verify
```sh
npx vitest run src/cache/cache-warmer.test.ts
```

### Done
Test still passes; structure improved.
