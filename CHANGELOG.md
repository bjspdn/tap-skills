# Changelog

All notable changes to the tap plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Pattern-hint validation (CodeWriter + Refactorer)** soft check that reads the pattern card's `clashes_with` and `composes_with` frontmatter when a task has a `### Pattern hint`, surfaces warnings in TAP_RESULT for the Reviewer without blocking the commit.
- **`test_invariants` pipeline** pattern-level behavioral guarantees now flow from PatternScanner through convey emission (`### Test invariants` under `## RED`) into TestWriter, which incorporates them as mandatory assertions in RED tests.
- After ideation finishes, propose the user to either:
  - A: Run the `/tap:run` directly in the session.
  - B: Instruct the user to run `/tap:run <feature>` in a separate session.
- Immediately call `/tap:retro` after a run is over.
- **`tap:into` RUN_FLOW.md** operational source of truth with full lifecycle digraph, 16-step runbook, four named checkpoints (CP:UNDERSTAND, CP:SYNTHESIS, CP:APPROACHES, CP:PRESENTATION), bidirectional understanding↔ideation loops, decompose-then-pick flow, two-pass convergence gate (agent mechanical pre-check + human subjective confirm), and ConvergenceChecker dispatch shape.
- **`tap:into` anti-rationalization table** 12 named lazy shortcuts the agent must not produce, each with the real problem and correct action.
- **`tap:run` anti-rationalization table** 14 named shortcuts covering preflight through retro — prevents the orchestrator from skipping gates, inferring TAP_RESULT, serializing parallel dispatch, or doing agent work itself.
- **`tap:convey` anti-rationalization table** 14 named shortcuts covering ingestion through emission — prevents skipping dependency/pattern scans, horizontal slicing, vague REFACTOR actions, placeholder tokens, and skipping the independent audit.
- **`tap:retro` pattern smell cross-reference** new `cross-reference-pattern-smells` analysis step correlates a pattern card's `smells_it_introduces` against the run's failure taxonomy, recording matches as `pattern_smell_correlation` entries in the run report and accumulating them in `_profile.json`'s `pattern_signals.smell_correlations`.
- **`tap:refactor` anti-rationalization table** 11 named shortcuts covering discover through report — prevents counting non-countable lines, scattering vs reducing, modifying tests, renaming for brevity, and inflating reported numbers.
- **`tap:research` anti-rationalization table** 10 named shortcuts covering context detection through synthesis — prevents premature convergence, weak source acceptance, skipping cross-referencing, and making recommendations.
- **`tap:retro` anti-rationalization table** 10 named shortcuts covering discovery through surface-findings — prevents skipping clean runs, inflating confidence, inventing correlations, and presenting tentative signals as actionable.

### Changed

- **`tap:refactor` SKILL.md** converted XML `<phase>` tags to markdown `## Phase:` headings for structural consistency with other skills.

- **`tap:run` profile enrichment** expanded dispatch paragraph to include `pattern_signals` alongside `agent_performance` and `gate_signals`, with per-agent-type specifics (TestWriter gets test_invariants, CodeWriter gets clean_green_rate, Refactorer gets refactor-success signals).
- Changed `IdeationResearcher.md` model to haiku.
- Changed `PatternDiscovered.md` model to sonnet/medium.
- `user` -> `engineer` framing.
- **`tap:into` SKILL.md** slimmed from 239 to 37 lines — all procedural logic moved to RUN_FLOW.md. General rules trimmed to four actionable constraints, vibes removed.


## [0.3.0] - 2026-05-10

### Changed

- Removed trace of old `config.json` file.
- Removed `/tap:along` skill.

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
