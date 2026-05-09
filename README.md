# tap

Claude Code plugin for **TDD-driven development with subagent spawns**.

Bundles skills + agents that drive a red → green → refactor cycle, delegating each phase to a focused subagent.

---

## Status

Early scaffold. Skills + agents land next.

## Install

This plugin is **not** on the official Anthropic marketplace. Install directly from GitHub:

```bash
/plugin marketplace add <owner>/tap
/plugin install tap@tap
```

Pin to a tag:

```bash
/plugin marketplace add git@github.com:<owner>/tap.git#v0.1.0
```

Update later:

```bash
/plugin update tap
```

---

## Repo layout

Repo root **is** the plugin. No nested `tap/` subdirectory.

```
tap/
├── .claude-plugin/
│   ├── plugin.json          # manifest (required)
│   └── marketplace.json     # marketplace listing (for self-distribution)
├── skills/
│   └── <skill-name>/
│       └── SKILL.md
├── agents/
│   └── <agent-name>.md
├── hooks/
│   └── hooks.json           # optional
├── RELEASE-NOTES.md
└── README.md
```

Only `plugin.json` lives in `.claude-plugin/`. Skills + agents at root.

---

## Manifest

`.claude-plugin/plugin.json` schema:

```json
{
  "name": "tap",
  "description": "TDD-driven development plugin with subagent spawns",
  "version": "0.1.0",
  "author": { "name": "Ben" },
  "repository": "https://github.com/<owner>/tap",
  "license": "MIT"
}
```

`name` defines skill namespace: `/tap:<skill>`. Independent of dir name but kept in sync for sanity.

---

## Versioning + releases

**Manual semver, mirrored by git tag.**

- Bump `version` in `plugin.json`
- Tag commit: `git tag v0.1.0 && git push --tags`
- Cut GitHub Release with notes from `RELEASE-NOTES.md`

Rules:

- Set `version` explicitly → users update only on bump
- Omit `version` → commit SHA = version → every push = new update for subscribers
- Auto-update opt-in per-marketplace; kill switch: `DISABLE_AUTOUPDATER` env var

Reference for release flow: [obra/superpowers](https://github.com/obra/superpowers) — manual semver tags, GitHub Releases, `RELEASE-NOTES.md`. No release-please / semantic-release automation.

---

## Subagent spawning from skills

Skills delegate via natural prompt. No explicit API call.

`skills/red-phase/SKILL.md`:

```markdown
---
description: Red phase. Spawns test-writer agent.
---
# Red Phase

> @test-writer Write failing test for [feature]. No implementation.
```

`agents/test-writer.md`:

```markdown
---
name: test-writer
description: Writes failing unit tests for TDD workflows
model: claude-opus-4.7-20250805
maxTurns: 10
---
You are a test-first specialist. Write only failing tests.
```

Claude auto-invokes subagents on `@<agent-name>` references or context match against the agent description.

---

## Local dev

```bash
# Load plugin without installing
claude --plugin-dir /home/ben/Documents/projects/tap

# Reload after edits
/reload-plugins
```

Multi-plugin local load:

```bash
claude --plugin-dir ./tap --plugin-dir ./other-plugin
```

---

## Distribution

Three install paths users can use:

```bash
# GitHub shorthand (requires marketplace.json in repo)
/plugin marketplace add owner/repo

# Any git URL, optional tag pin
/plugin marketplace add https://gitlab.com/co/plugins.git
/plugin marketplace add git@github.com:user/repo.git#v1.0.0

# Hosted marketplace.json
/plugin marketplace add https://example.com/marketplace.json
```

Install: `/plugin install tap@tap`

---

## References

- [Claude Code plugins guide](https://code.claude.com/docs/en/plugins.md)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference.md)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces.md)
- [Discover + install plugins](https://code.claude.com/docs/en/discover-plugins.md)
- [Custom subagents](https://code.claude.com/docs/en/sub-agents.md)
- [Superpowers — release flow reference](https://github.com/obra/superpowers)
- [TDD Guard — TDD plugin reference](https://github.com/nizos/tdd-guard)
- [anthropics/skills — official skill examples](https://github.com/anthropics/skills)

---

## License

MIT
