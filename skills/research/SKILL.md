---
name: research
description: "Deep, multi-hop research on any technical topic — libraries, frameworks, algorithms, game systems, protocols, math, or software patterns. Cross-references sources and emits a structured research artifact at `.tap/research/<topic-slug>-<YYYY-MM-DD>.md`"
---

## Context pressure

Follow the protocol in [shared/context-pressure.md](../../shared/context-pressure.md).
Default posture when no signal present: **nominal** (standalone) / **moderate** (callable)

# Deep Research

Multi-hop research engine for any technical topic — libraries, frameworks,
game engines, algorithms, math, protocols, standards, and software patterns.
Adapts search strategy to the domain. Grounds findings in project context
when one exists, stands alone when it doesn't.

Operates in two modes:
- **Standalone**: invoked directly, produces `.tap/research/<topic-slug>.md`
- **Callable**: invoked mid-conversation by `tap:into` or `tap-convey` when a
  knowledge gap surfaces. Returns findings to the calling context.

## References

- [Web Search Reference](${CLAUDE_PLUGIN_ROOT}/dorks.md) — Brave Search operators, domain filtering, query patterns by domain
- [Research Template](research-template.md) — output artifact structure

## Constraints (critical)

1. **Scope queries to their context.** When a project context exists, include
   the detected language, framework, and dependencies. When researching a
   pure-knowledge topic (algorithms, math, game theory), scope to the domain
   instead. "Mersenne Twister PRNG properties" not "random number generation".
   "ECS architecture in Bevy 0.15" not "game architecture".
2. **Surface gaps honestly rather than filling them with fabricated claims.** If
   a search returns nothing authoritative, say so.
3. **Prioritize authoritative sources.** Official docs > RFCs/specs/papers >
   widely-cited blog posts > community discussions. StackOverflow answers are
   evidence of community practice, not authoritative design guidance.
4. **Cover new ground with each hop.** If a hop returns information already
   captured, that is a convergence signal — stop.
5. **Cross-reference sources.** Every claim cross-referenced against at least
   one other source. When a project context exists, also cross-reference
   findings against the codebase.
6. **Output a file, not chat.** Standalone mode always emits
   `.tap/research/<topic-slug>.md`. Callable mode returns structured findings
   to the calling agent.

---

## Phase: context-detection

**Purpose**: Build a context block that scopes all subsequent research queries. For project-bound topics, detect the stack. For pure-knowledge topics, derive context from the user's prompt.

### Step: classify

Determine the research mode from the user's topic:
- **Project-bound**: topic relates to a library, framework, or pattern
  used in the current codebase → proceed to manifest scan.
- **Pure-knowledge**: topic is domain knowledge not tied to this project
  (algorithms, math, game theory, protocol specs) → skip manifest,
  build context from user prompt.

### Step: manifest

(Project-bound only) Read the project manifest — `package.json`,
`Cargo.toml`, `go.mod`, `pyproject.toml`, `build.gradle`, `pom.xml`,
or equivalent. Extract:
- Primary language and version
- Framework (e.g., Next.js 15, Bevy 0.15, Axum 0.8)
- Key dependencies relevant to the research topic
- Toolchain signals (bundler, test runner, linter)

### Step: build-context

Produce a `<context>` block that every subsequent search agent receives:

```xml
<context>
  <mode>project-bound | pure-knowledge</mode>
  <!-- project-bound fields (include when mode=project-bound) -->
  <language>TypeScript 5.x</language>
  <framework>Next.js 15 (App Router)</framework>
  <runtime>Node 22 / Bun 1.x</runtime>
  <key_deps>zod, drizzle-orm, tailwindcss</key_deps>
  <relevant_deps><!-- deps directly related to topic --></relevant_deps>
  <!-- pure-knowledge fields (include when mode=pure-knowledge) -->
  <domain>game-systems | algorithms | math | protocols | hardware | other</domain>
  <scope><!-- user-provided constraints, e.g. "2D physics, no external deps" --></scope>
</context>
```

This block is injected into every Explore agent prompt.

## Phase: research-loop

**Purpose**: Iterative multi-hop research. Each hop searches, analyzes findings, identifies gaps, and decides whether to continue or converge. Hard cap: 5 hops. Typical: 3.

### Step: classify-domain

Before hop 1, classify the topic to select the right search strategy.
Use the `<context>` block from the detection phase.

Domain classifications and their search strategies:
- **library-framework**: official docs, changelog, GitHub issues/discussions,
  migration guides, API references, benchmark comparisons.
  Authoritative domains: docs sites, GitHub repos, release notes.
- **algorithm-math**: academic papers, reference implementations, Wikipedia,
  Wolfram MathWorld, textbook references, complexity analyses.
  Authoritative domains: arxiv.org, wikipedia.org, mathworld.wolfram.com,
  algorithm visualization sites, university course materials.
- **game-systems**: engine documentation, GDC talks/slides, game dev wikis,
  engine source code, community tutorials with benchmarks.
  Authoritative domains: engine docs (docs.godotengine.org, bevyengine.org,
  docs.unity3d.com), gamedeveloper.com, gdcvault.com.
- **protocol-standard**: RFCs, specification documents, reference
  implementations, conformance test suites, IETF/W3C/IEEE publications.
  Authoritative domains: rfc-editor.org, w3.org, ietf.org, ieee.org.
- **software-patterns**: same as original behavior — conventions, ecosystem
  patterns, idiomatic practices scoped to the stack.
  Authoritative domains: language/framework docs, refactoring.guru,
  martinfowler.com, style guides.

The domain drives which `site:` dorks and source-quality rankings the
hop agents use. Multiple domains can apply (e.g., "ECS pattern in Bevy"
= game-systems + software-patterns).

### Step: hop

Each hop spawns 1-3 concurrent ResearchHopper agents depending on how many
distinct threads need pursuing. Hop 1 is always broad. Subsequent hops
are targeted at gaps identified by the previous hop's analysis.

```text
Agent(
  subagent_type: "ResearchHopper",
  description: "{topic} — hop {N}: {angle}",
  prompt: "
    context_block: {context_block}
    classified_domain: {classified_domain}
    topic: {topic}
    angle: {specific_angle_for_this_hop}
    prior_findings: {summary_of_what_previous_hops_found}
    hop_n: {N}
  "
)
```

### Step: analysis

After each hop's agents return, the main agent:
1. Merges findings, deduplicates, resolves conflicts between sources.
2. Updates a running `<knowledge_state>`:
   - **Established**: claims supported by 2+ authoritative sources
   - **Probable**: claims from 1 authoritative source or 2+ community sources
   - **Uncertain**: single community source or conflicting information
   - **Unknown**: identified gaps with no findings yet
3. Checks termination criteria (see below).
4. If continuing, formulates specific angles for the next hop based on
   the **Unknown** and **Uncertain** items.

### Step: termination

Stop the loop when ANY of these are true:
- **Convergence**: the last hop's agents all returned
  `<convergence_signal>yes</convergence_signal>` with no new **Established**
  or **Probable** claims added to `<knowledge_state>`.
- **Hard cap**: 5 hops completed.
- **Saturation**: the **Unknown** list is empty or contains only questions
  that search cannot answer (e.g., "what should we choose" — that is a
  design decision, not a research question).
- **Diminishing returns**: the last hop moved items from **Unknown** to
  **Uncertain** but not to **Probable** or **Established** — further hops
  are unlikely to improve confidence.

## Phase: crossref

**Purpose**: Cross-reference findings. For project-bound topics, ground findings in the codebase. For pure-knowledge topics, cross-reference sources against each other for agreement and contradiction.

### Step: route

Check the `<context>` block's `<mode>`:
- **project-bound** → run Step: codebase-scan
- **pure-knowledge** → run Step: source-crossref

### Step: codebase-scan

(Project-bound only)

```text
Agent(
  subagent_type: "CodebaseCrossref",
  description: "Cross-reference {topic} with codebase",
  prompt: "
    topic: {topic}
    context_block: {context_block}
    final_knowledge_state: {final_knowledge_state}
  "
)
```

### Step: source-crossref

(Pure-knowledge only)

The main agent reviews the `<knowledge_state>` and for each
**Established** and **Probable** finding:
1. Identifies which sources agree on the claim.
2. Flags contradictions between sources — note what each source says.
3. Notes where a claim has only a single source (weaker evidence).

Produce a `<crossref>` block:

```xml
<crossref>
  <agreement finding="<claim>" sources="url1, url2">
    Sources converge on this point.
  </agreement>
  <contradiction finding="<claim>">
    <source url="url1">Says X</source>
    <source url="url2">Says Y</source>
    <note>Why they disagree (different versions, different contexts, etc.)</note>
  </contradiction>
  <single_source finding="<claim>" source="url">
    Only one source found. Confidence capped at Probable.
  </single_source>
</crossref>
```

No agent spawned — this is a synthesis step by the main agent.

## Phase: synthesis

**Purpose**: Produce the research artifact. In standalone mode, emit a file. In callable mode, return structured findings to the calling context.

### Step: write

Compile `<knowledge_state>` and `<crossref>` into the output artifact
following the [research template](research-template.md).
Write to `.tap/research/<topic-slug>.md`.

The slug is derived from the topic: lowercase, hyphens for spaces,
no special characters. e.g., "branded types" → `branded-types`,
"error handling with thiserror" → `error-handling-thiserror`.

### Step: self-review

After writing, verify:
- Every **Established** claim cites at least 2 sources
- Every **Probable** claim cites at least 1 source
- Every **Uncertain** claim is flagged as such
- Codebase cross-references include file:line evidence (project-bound only)
- Source cross-references flag contradictions (pure-knowledge only)
- No claims without source attribution
- No recommendations — findings and conventions only (the user decides
  what to adopt)
- The document answers the original research question

If gaps exist, fix inline.

## Callable mode

When invoked by `tap:into` or `tap-convey` mid-conversation:
1. Skip the file emission step.
2. Run phases `context-detection` → `research-loop` → `crossref` as normal.
3. Return the `<knowledge_state>` and `<crossref>` blocks directly to the
   calling agent instead of writing a file.
4. The calling agent integrates findings into its own workflow (ideation,
   task decomposition, etc.).
5. If the calling agent later requests a persisted artifact, run the
   `synthesis` phase at that point.

## Anti-rationalization table

Do not produce these rationalizations. If you catch yourself reasoning toward one, stop and take the correct action.

| Where | Rationalization | Real problem | Correct action |
|---|---|---|---|
| Context detection | "Topic is straightforward, skip manifest scan" | Misses framework version, key deps, runtime — queries land on wrong version's docs | Always run context detection. Even "simple" topics need version-scoped queries |
| Classify domain | "This is just a library question" | Misclassifies domain, uses wrong search strategy and authority ranking | Map to specific domain(s). Many topics span two (e.g., "ECS in Bevy" = game-systems + software-patterns). Get it right before hop 1 |
| Hop 1 | "First result answers the question fully" | Stops at 1 source, no cross-reference. Single-source claims cap at Probable, not Established | Every Established claim needs 2+ sources. One result is a starting point, not a conclusion |
| Hop N | "This blog post is authoritative enough" | Weak source quality. Community blog ≠ official docs ≠ RFC | Follow authority ranking: official docs > specs/papers > cited blogs > community. A blog is evidence of practice, not authoritative guidance |
| Hop N | "Sources agree, cross-referencing is redundant" | Agreement doesn't mean correctness. Sources may share the same upstream misconception | Cross-reference every claim. Agreement from independent sources is evidence. Agreement from sources citing each other is one data point |
| Termination | "3 hops is enough for any topic" | Premature convergence. Complex topics need 4-5 hops to reach Established confidence | Check termination criteria: convergence signal, saturation, diminishing returns. Hop count alone is not a termination criterion |
| Termination | "Remaining unknowns are edge cases, not worth another hop" | Declares unknowns unimportant to avoid another hop. The user might care about those edges | Surface remaining Unknowns explicitly. Let the user decide if they matter. Don't triage on their behalf |
| Crossref | "No codebase context, skip cross-referencing entirely" | Pure-knowledge mode still requires source-vs-source cross-referencing for contradictions | Route correctly: project-bound → codebase scan, pure-knowledge → source crossref. Neither mode skips crossref |
| Synthesis | "Findings are clear, self-review is a formality" | Skips verification that every claim has source attribution and confidence labels | Run self-review mechanically. Check every Established claim for 2+ sources, every Probable for 1+, every Uncertain flagged. Not optional |
| Synthesis | "I'll note this recommendation since it's obvious" | Research skill does not recommend — it presents findings. Recommendations are the user's or tap:into's job | Present what exists. Distinguish fact, convention, opinion, constraint. Never pick a winner |

## Constraints (general)

- Scope every search query to its context. Project-bound: include
  language/framework. Pure-knowledge: include domain terminology.
  Generic queries waste hops.
- Prefer fewer, higher-quality sources over many shallow ones. Three
  authoritative findings beat ten Reddit threads.
- Judge recency relative to the domain's rate of change. A 2021 blog
  post about Next.js 12 conventions may be actively harmful for a
  Next.js 15 project. A 2019 paper on a stable algorithm is fine.
- Distinguish between fact (verified by multiple sources), convention
  (community consensus), opinion (individual preference), and constraint
  (language/framework/domain limitation). Label each.
- Present what exists, what the sources say, and what the codebase does
  (when applicable). The user or `tap:into` decides what to adopt.
- When research reveals genuine disagreement (e.g., two competing
  approaches, conflicting benchmarks), present both with their tradeoffs.
  Let the caller pick a winner.
