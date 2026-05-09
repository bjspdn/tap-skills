# Changelog

All notable changes to the tap plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-10

### Added

- **`/tap:sketch` skill** rapid single-behavior TDD prototype. Lightweight alternative to the full `into → convey → run` pipeline for changes touching ≤3 files. In-memory task spec, no worktree, no tickets on disk. Reuses TestWriter/CodeWriter/Refactorer agents with inline specs. Bounded failure handling (one Debugger retry per phase).
- **`/tap:retro` skill** post-mortem analysis of completed `/tap:run` executions. Two-layer output: ephemeral run report (`.tap/retros/<slug>-<date>.md`) + rolling aggregate profile (`.tap/retros/_profile.json`). Extracts commit trailers, classifies failures into a taxonomy, computes per-agent/per-pattern/per-gate metrics. Profile entries require ≥3 samples before reaching `established` confidence.
- **Profile contract** (`skills/retro/profile-contract.md`) reference doc defining how skills and agents consume the retro profile. Signals are advisory, never mandatory. Missing profile = no behavior change.
- **Architectural pattern cards** (7) `hexagonal`, `clean-architecture`, `repository`, `cqrs`, `event-sourcing`, `saga`, `dependency-injection`. All conform to `_schema.md`. Catalog count 90 → 97.
- **Profile consumer wiring** `into`, `convey`, `sketch`, and `run` skills read established profile signals. TestWriter, CodeWriter, and Refactorer agents accept optional `profile_note` input. PatternsDiscoverer and PatternScanner agents boost/demote patterns based on `clean_green_rate`.
- **`bump-version.sh`** config-driven release script with three modes: bump (roll changelog + commit + tag), `--check` (drift detection), `--audit` (stale version grep). Guarded by non-empty `[Unreleased]` and clean working tree.

### Changed

- **`sketch` pattern-check** now follows the full catalog discovery API: reads `README.md`, resolves aliases, reads actual cards for `composes_with`/`clashes_with`/`test_invariants`, feeds card data into RED/GREEN/REFACTOR shaping.
- **PatternScanner protocol**  renumbered steps (1→6) to accommodate profile check as step 1.
- **`_index.json`** updated with 7 architectural patterns, 7 new aliases, smell routes, bidirectional `composes_with`/`clashes_with` entries. `generated_at` set to 2026-05-10.
- `back-at-it` phase removed from `/tap:into`. 

## [0.1.0] - 2026-05-09

### Added

- Initial release: `into`, `convey`, `run`, `along`, `refactor`, `research` skills.
- 13 agents: CodeWriter, CodebaseCrossref, CodebaseScanner, Debugger, DependencyScanner, IdeationResearcher, IndependentAuditor, PatternScanner, PatternsDiscoverer, Refactorer, ResearchHopper, Reviewer, TestWriter.
- 90-card design pattern catalog (GoF creational/structural/behavioral + Fowler refactorings) with schema-driven discovery via `_index.json`.
- Wave-parallel TDD execution with saga isolation.
- Multi-hop deep research engine with domain-classified search strategies.
