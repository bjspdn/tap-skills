---
title: Cache warming on startup
---

# Cache warming on startup: Design intent

## Intent

First request after service boot hits cold config reads for every key. Add eager cache warming during startup so all config entries are pre-loaded before the HTTP listener binds.

## Context

- `ConfigService` is the sole reader of config values today; callers invoke `get(key)` which hits the backing store each time (`src/config/config-service.ts:23`)
- A `CacheStore` interface already exists for session data (`src/cache/cache-store.ts:5`) -- reusable shape
- `startServer()` in `src/server/bootstrap.ts:14` runs lifecycle hooks sequentially before binding the port -- integration point for warming

## Approach

```
PATTERN: Strategy (warming algorithm is swappable)
  WHAT: A family of warming algorithms behind a common interface, selected at config time.
  HERE: WarmingStrategy interface with FullWarm and PriorityWarm implementations; injected into the startup hook.
FLOW:
  1. Server bootstrap calls CacheWarmer.warm() before binding port
  2. CacheWarmer delegates to the injected WarmingStrategy
  3. Strategy reads config keys from the backing store and populates CacheStore
  4. On completion, bootstrap proceeds to bind the listener
INVARIANTS:
  - Warming completes before the listener accepts connections
  - A failed warm does not prevent startup -- log error and continue with cold cache
SEAMS:
  - WarmingStrategy interface -- swappable for tests (NoOpStrategy)
  - CacheStore interface -- in-memory stub for unit tests
OPEN:
  - Timeout for warming -- defer to planner
```

## Signatures

```ts
interface CacheStore<V> {
  get(key: string): V | undefined
  set(key: string, value: V, ttl?: number): void
  has(key: string): boolean
}

interface WarmingStrategy {
  warm(store: CacheStore<string>): Promise<void>
}
```

## Constraints

- Warming must complete in under 5 seconds or abort with a warning
- No new external dependencies -- use existing backing store client
- CacheStore is generic; config warming uses `CacheStore<string>`

## Boundaries

- Not changing how `ConfigService.get()` reads from the cache after startup
- Not adding cache invalidation or TTL refresh during runtime
- Not warming caches other than config

## Considered & rejected

- Lazy warming on first miss -- adds latency to the first real request per key; defeats the purpose
- Background warming after port bind -- requests can arrive before warming completes
