# tap — Project Instructions

## Changelog

- Update `CHANGELOG.md` under `## [Unreleased]` when making notable changes (new features, bug fixes, breaking changes, refactors).
- Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format: `### Added`, `### Changed`, `### Fixed`, `### Removed`.
- Bold the item name, then describe: `- **Thing** description of what and why.`
- Don't bump versions manually — use `./scripts/bump-version.sh <X.Y.Z>`.

## Releases

- `./scripts/bump-version.sh <X.Y.Z>` — full release: roll changelog, commit, tag, push, GitHub Release.
- `./scripts/bump-version.sh --check` — verify version sync across files.
- `./scripts/bump-version.sh --audit` — check + scan for stale version strings.
- Bump will refuse if `[Unreleased]` is empty or working tree is dirty.
