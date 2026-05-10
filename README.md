# tap

Claude Code plugin for **TDD/Subagent-driven, design-pattern-aware development**.

Bundles a coordinated pipeline that takes a feature idea from whiteboard to merged-and-reviewed code:

- **Brainstorming + ideation** that converges on a single well-specified ticket
- **Decomposition** of the ticket into vertical-slice TDD tasks
- **Wave-parallel execution** of those tasks via dedicated phase agents (RED → GREEN → REFACTOR)
- **Independent review** of the final diff against the spec
- **Debugging** when phases fail or the reviewer finds blockers
- **Post-run analytics** over collected logs

A 97-card design-pattern catalog (GoF + Fowler refactorings) sits at plugin root and is consumed by every skill that needs to name a structural shape.

## Install

Install directly from the GitHub repo:

```bash
/plugin marketplace add bjspdn/tap-skills
/plugin install tap@tap
```

Pin to a tag:

```bash
/plugin marketplace add git@github.com:bjspdn/tap-skills.git#v0.2.0
```

Update later:

```bash
/plugin update tap
```

### Install locally

```bash
# Load plugin without installing — point at the cloned repo
claude --plugin-dir /path/to/tap-skills

# Reload after edits
/reload-plugins
```


## How to use it

The primary way to use this set of skills/agents is to first start with `/tap:into` to get a brainstorming session going. 
It will create an artefact at `.tap/tickets/<slug>/ideation.md`. That ideation.md will then be used by `/tap:convey` to decompose it into tasks at the same location. Once everything is done and settled, run `/tap:run` to run the TDD cycle.


## Versioning + releases

**Semver, automated via `bump-version.sh`.**

```bash
# Full release: bump files, roll changelog, commit, tag, push, GitHub Release
./scripts/bump-version.sh 0.3.0

# Check version sync across declared files
./scripts/bump-version.sh --check

# Check + scan repo for stale version strings
./scripts/bump-version.sh --audit
```

The script reads `.version-bump.json` for the list of files that carry a version field. It guards against empty changelogs (document changes under `[Unreleased]` in `CHANGELOG.md` before bumping) and dirty working trees.

## Skills

| Skill        | Command         | What it does                                                                                                                                                   |
| --------------| -----------------| ----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **into**     | `/tap:into`     | Brainstorming partner. Explores codebase + web in parallel, challenges assumptions, converges on a well-specified ticket at `.tap/tickets/<slug>/ideation.md`. |
| **convey**   | `/tap:convey`   | Decomposes an `ideation.md` into vertical-slice TDD task files (`task-NN-*.md`) ready for execution.                                                           |
| **run**      | `/tap:run`      | Executes decomposed tasks through a wave-parallel TDD pipeline — worktree per ticket, RED/GREEN/REFACTOR phase agents, commit trailers, auto-retry on failure. |
| **sketch**   | `/tap:sketch`   | Rapid single-behavior TDD prototype. No tickets, no worktree — runs RED/GREEN/REFACTOR directly on current branch for changes touching 1–3 files.              |
| **research** | `/tap:research` | Deep multi-hop research on any technical topic. Cross-references sources, emits structured artifact at `.tap/research/<topic-slug>.md`.                        |
| **refactor** | `/tap:refactor` | Aggressive structural refactoring targeting 80% reduction in countable lines without behavior change. Splits monoliths into focused submodules.                |
| **retro**    | `/tap:retro`    | Post-mortem of completed runs. Extracts commit trailers, classifies failures, computes per-agent metrics, builds rolling aggregate profile.                    |


## Pattern catalog API

Skills consume `patterns/` via three discovery modes (full spec in [`patterns/README.md`](patterns/README.md)):

1. **By name** — `read ${CLAUDE_PLUGIN_ROOT}/patterns/<category>/<name>.md`
2. **By smell** — query `${CLAUDE_PLUGIN_ROOT}/patterns/_index.json#smell_to_patterns[<smell-tag>]`
3. **By scan** — `grep -lr "smells_it_fixes:.*<tag>" ${CLAUDE_PLUGIN_ROOT}/patterns/` (fallback)

Each card has machine-readable frontmatter (`name`, `category`, `aliases`, `intent`, `sources`, `smells_it_fixes`, `smells_it_introduces`, `composes_with`, `clashes_with`, `test_invariants`) and a human-readable body (intent, structure, applicability, consequences, OOP shape, FP shape, smells fixed, tests implied, sources).

Adding a pattern: drop a new `<category>/<kebab-name>.md` conforming to [`patterns/_schema.md`](patterns/_schema.md) and regenerate `_index.json`.

## License

MIT
