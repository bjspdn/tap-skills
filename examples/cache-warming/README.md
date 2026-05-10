# Worked example: cache warming on startup

This example shows what tap produces at each pipeline stage for a feature request:
**"Add cache warming on startup for the config service."**

| File                          | Pipeline stage | Produced by   |
|-------------------------------|----------------|---------------|
| `ideation.md`                 | Brainstorm     | `/tap:into`   |
| `task-01-cache-store.md`      | Decompose      | `/tap:convey` |
| `task-02-warming-strategy.md` | Decompose      | `/tap:convey` |
| `task-03-startup-hook.md`     | Decompose      | `/tap:convey` |
| `commits.md`                  | Execute        | `/tap:run`    |
| `retro-snippet.md`            | Post-mortem    | `/tap:retro`  |

All artifacts are synthetic but structurally accurate -- they match the formats the real pipeline emits.
