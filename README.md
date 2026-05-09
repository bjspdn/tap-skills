# tap

Claude Code plugin for **TDD-driven, design-pattern-aware development with subagent spawning**.

Bundles a coordinated pipeline that takes a feature idea from whiteboard to merged-and-reviewed code:

- **Brainstorming + ideation** that converges on a single well-specified ticket
- **Decomposition** of the ticket into vertical-slice TDD tasks
- **Wave-parallel execution** of those tasks via dedicated phase agents (RED → GREEN → REFACTOR)
- **Independent review** of the final diff against the spec
- **Recovery** when phases fail or the reviewer finds blockers
- **Aggressive structural refactoring** as a separate, opt-in pass
- **Whiteboard-style guidance** when the human is the one writing code
- **Deep research** into libraries, algorithms, or protocols when a knowledge gap surfaces
- **Post-run analytics** over collected logs

A 90-card design-pattern catalog (GoF + Fowler refactorings) sits at plugin root and is consumed by every skill that needs to name a structural shape.


## Install

This plugin is **not** on the official Anthropic marketplace. Install directly from the GitHub repo:

```bash
/plugin marketplace add bjspdn/tap-skills
/plugin install tap@tap
```

Pin to a tag:

```bash
/plugin marketplace add git@github.com:bjspdn/tap-skills.git#v0.1.0
```

Update later:

```bash
/plugin update tap
```


## How to use it

The primary way to use this set of skills/agent is to first start with `/tap:into` to get a brainstorming session going. 
It will create an artefact at `.tap/tickets/<slug>/ideation.md`. That ideation.md will then be used by `/tap:convey` to decompose it into tasks at the same location. Once everything is done and settled, run `/tap:run` to run the TDD cycle.


## Versioning + releases

**Manual semver, mirrored by git tag.**

- Bump `version` in `plugin.json`.
- Tag the commit: `git tag v0.1.0 && git push --tags`.
- Cut a GitHub Release with notes drawn from `CHANGELOG.md`.


## Subagent spawning from skills — how it actually works

A skill is a markdown file at `skills/<name>/SKILL.md`. An agent is a markdown file at `agents/<Name>.md`. To spawn an agent from inside a skill, the skill's body includes a literal `Agent(...)` invocation template that Claude follows when running the skill. Claude is the one issuing the actual tool call; the skill body is the recipe.

**Agent file** (from `agents/TestWriter.md`):

```markdown
---
name: TestWriter
description: Writes the failing test for one TDD task — RED phase. Spawned by the /tap-run skill — do not invoke directly.
tools: Read, Edit, Write, Bash, Glob, Grep
model: sonnet
effort: low
---

# TestWriter — RED phase

You write the failing test for one TDD task. You commit the test alone, no implementation. ...
```

**Skill template that spawns it** (from `skills/into/SKILL.md`, simplified):

````markdown
Agent(
  subagent_type: "Explore",
  description: "<3-5 word task summary>",
  prompt: "Research <topic> for <reason> with the WebSearch & WebFetch tools.
           Use the [dorks](dorks.md) for query construction.
           Cross-reference findings across sources.
           ---
           Return your findings following this structure: ..."
)
````

When Claude runs the skill, it parses that template, substitutes the slots, and emits an actual `Agent` tool call with the same shape. The agent file's frontmatter `name` field is what `subagent_type` matches against.

This pattern is used throughout the plugin:

- `skills/into/SKILL.md` — spawns multiple `Explore` and `general-purpose` agents in parallel during ideation
- `skills/convey/SKILL.md` — spawns dependency-scan + pattern-scan + independent-audit agents
- `skills/research/SKILL.md` — spawns 1–3 hop agents per research iteration
- `skills/run/SKILL.md` — orchestrates `TestWriter`, `CodeWriter`, `Refactorer`, `Reviewer`, `Debugger` per task per wave (orchestration logic in the colocated `RUN_FLOW.md`)

The fan-out + fan-in pattern (parallel `Agent` tool uses in a single message, then join on results) is how the wave-parallel execution actually achieves parallelism.

---

## Local dev

```bash
# Load plugin without installing — point at the cloned repo
claude --plugin-dir /path/to/tap-skills

# Reload after edits
/reload-plugins
```

Multi-plugin local load:

```bash
claude --plugin-dir ./tap-skills --plugin-dir ./other-plugin
```


## Distribution

Three install paths users can choose between:

```bash
# GitHub shorthand (requires marketplace.json in the repo)
/plugin marketplace add owner/repo

# Any git URL, optional tag pin
/plugin marketplace add https://gitlab.com/co/plugins.git
/plugin marketplace add git@github.com:user/repo.git#v1.0.0

# Hosted marketplace.json
/plugin marketplace add https://example.com/marketplace.json
```

Then: `/plugin install <plugin-name>@<marketplace-name>`.

For this repo: `/plugin marketplace add bjspdn/tap-skills` then `/plugin install tap@tap`.


## Pattern catalog API

Skills consume `patterns/` via three discovery modes (full spec in [`patterns/README.md`](patterns/README.md)):

1. **By name** — `read ${CLAUDE_PLUGIN_ROOT}/patterns/<category>/<name>.md`
2. **By smell** — query `${CLAUDE_PLUGIN_ROOT}/patterns/_index.json#smell_to_patterns[<smell-tag>]`
3. **By scan** — `grep -lr "smells_it_fixes:.*<tag>" ${CLAUDE_PLUGIN_ROOT}/patterns/` (fallback)

Each card has machine-readable frontmatter (`name`, `category`, `aliases`, `intent`, `sources`, `smells_it_fixes`, `smells_it_introduces`, `composes_with`, `clashes_with`, `test_invariants`) and a human-readable body (intent, structure, applicability, consequences, OOP shape, FP shape, smells fixed, tests implied, sources).

Adding a pattern: drop a new `<category>/<kebab-name>.md` conforming to [`patterns/_schema.md`](patterns/_schema.md) and regenerate `_index.json`.

## License

MIT
