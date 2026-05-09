---
name: into
description: Brainstorming partner that drives deep discussion about an idea before any code is written. Through natural conversation, explores the codebase and the web in parallel, challenges assumptions, and converges on a single well-specified ticket with structured description. Use when user invokes `/tap-into`, says "brainstorm", "let's think through X", "scope this out", "I want to build X but let's talk first", or has a `.tap/` directory and a feature ask they want to explore before committing.
---

## Phase: back-at-it

**Purpose**: Stress-test that new feature idea of their.

Run this command `git log --since=1.week --oneline | wc -l`. If the number is superior or equal to 100, proceed with this phase, otherwise go directly to Phase: understanding.

Always surface this phase when the number is over or equal to 100 AND when the user is discussing a feature implementation. If the count is under 100 or when the user is talking about refactoring, fixing or documenting something, stay silent and move on to Phase: understanding.

### Step: aftermath

Ask the user why a new feature again, because he's got `echo "$(git log --since=1.week --oneline | wc -l) commits since last week"`, maybe they should slow the fuck down a little.
Ask the user what is the purpose of this new feature? Probe them to tell you if it has added value at all.

### Step: wait

Wait. Let the user answers your questions before you continue.
If the user comes to the conclusion that indeed this new feature is not needed, you can close this ideation session and invoke the Skill(refactor) instead; a good refactoring session can always be great. Otherwise, if the feature really has added value, proceed with the next phase: Phase: understanding.

## Phase: understanding

### Purpose

Understand the current project's context. First, follow the steps, wait for each Agent to finish their explorations, then ask questions to the user one at the time to refine the idea provided.

Once you understand what you're building, present the design intent & wait for the user's approval before continuing to the Phase: ideation.

You can spawn as many Agents of each of these types as you want: Step: websearch, Step: codebase_exploration & Step: patterns_discovery, depending on the complexity. If for example you need 2 "codebase_exploration" agents, 2 "patterns_discovery" agents & 2 "websearch" agents for a feature, that's fine. It doesn't have to be locked at specifically 3 agents.
Each and everyone of them should be contained to their own tasks:

### Step: websearch

```text
Agent(
  subagent_type: "IdeationResearcher",
  description: "Research {topic}",
  prompt: "
    topic: {topic}
    reason: {reason}
    context_seed: <if applicable, brief seed from codebase findings or prior agent output>
  "
)
```
Query construction uses [dorks](${CLAUDE_PLUGIN_ROOT}/dorks.md).

### Step: codebase_exploration

```text
Agent(
  subagent_type: "CodebaseScanner",
  description: "Scan codebase for {topic}",
  prompt: "
    topic: {topic}
    seed_files: <optional, comma-separated paths the conversation already surfaced>
  "
)
```

### Step: patterns_discovery

```text
Agent(
  subagent_type: "PatternsDiscoverer",
  description: "Pattern scan for {topic}",
  prompt: "
    topic: {topic}
    seed_files: <comma-separated paths from prior agent output>
    lang: <primary language of the topic area>
  "
)
```

### Step: synthesis

After all websearch / codebase_exploration / patterns_discovery agents return, cross-reference their outputs and flag contradictions explicitly. Common contradiction shapes:

- patterns_discovery recommends pattern X; codebase_exploration shows pattern X is not used in repo
- websearch finds community recommends approach A; codebase_exploration shows neighbors use approach B
- patterns_discovery surfaces an anti-pattern in the topic area; the user's stated approach reproduces it

For each contradiction, surface to the user as a multi-choice question: "Agents disagree on {topic}. Source X says <claim X>, source Y says <claim Y>. Which holds for this feature?" Resolve before moving to Phase: ideation.

If zero contradictions found, state that explicitly and proceed.

### Step: assumption-audit

List every premise the user stated during the back-at-it / understanding conversation as a bullet. For each premise, mark one of:
- `verified` — codebase or web findings confirm it
- `contradicted` — findings show it is false (surface to user, force re-evaluation)
- `unverifiable` — no source either way (surface to user, ask if a quick spike is needed before ideation)

Examples of premises to audit: "X is impossible without Y", "we already use pattern Z", "library W doesn't support this", "the team agreed to constraint C".

Do not skip this step. Bad ideations land on top of unaudited premises.

#### Done

This phase ends when every agent has returned consistent data across all three steps AND Step: synthesis has run (contradictions resolved or explicitly stated as none) AND Step: assumption-audit has run (every premise marked verified / contradicted / unverifiable).

## Phase: ideation

**Purpose**: Deep conversation & collaboration with the user to create a ideation.md file that crystallize every decision made.

Based on the findings returned by Step: websearch, Step: codebase_exploration & Step: patterns_discovery, proceed with the ideation by writing a new ticket following the [ideation template](ideation-template.md) at `.tap/tickets/{slug}/ideation.md`. You don't have all the information yet, that is to be expected. The ideation will help filling in the gaps.
Do not invent informations that you don't yet have because false information is worse than no information at all. Do no rush convergence on this phase.

### Step: assess

Assess the scope first before asking any questions because if a description maps to multiple independent systems, it will need to be decomposed further. Scope that is too wide is to be decomposed into smaller sub-scope.

### Step: decomposition

If a scope is too large for a single ticket, help the user decompose into sub-tickets through the normal Ideation flow. Each scope gets its own ticket & tap run lifecycle.

**Stub deferred tickets immediately.** Once the user confirms the decomposition, create a minimal `ideation.md` for each deferred ticket BEFORE diving into the first ticket's full ideation. This ensures nothing falls through the cracks — `ls .tap/tickets/` always shows the full roadmap.

Stub format:
```markdown
# [<Feature Name>]: Design intent

<!-- TODO: Full ideation pending — run /tap-into to complete -->

## Intent
<one-line description of what this ticket delivers>

## Depends on
- <slug of prerequisite ticket(s)>

## Context (from decomposition)
- <bullet points captured during the scope discussion>
- <relevant findings from the exploration agents>
- <key constraints or decisions that affect this ticket>
```

The stub is intentionally minimal — it preserves context from the decomposition discussion without inventing design decisions. The full ideation happens later via a separate `/tap-into` session.

### Step: questioning

Ask questions one at the time. Prefer multiple choices questions, but free-form questions are alright aswell. If a {topic} needs more exploration, break it into subsequent questions. Focus on understanding: purpose, constrainst, and what "done" should look like.

### Step: approaches

When exploring {approach}, propose 2-5 different approaches with trade-offs for each.
Present them like the following:
```markdown
  [{0N}]: <approach title>
    - <approach description>
    - Tradeoffs:
      - <tradeoff one>
      - <tradeoff two>
      - <tradeoff n>
    - Recommanded <approach title>: <why>
```

### Step: two-impl-check

After the user picks an approach, ask yourself: could two engineers reading this approach produce two materially different implementations that both satisfy the description? If yes, the approach has a hole. Walk through the FLOW step-by-step and identify which step admits multiple valid interpretations. Tighten the wording, pin the choice, or surface as an `OPEN:` decision. Repeat until the approach reads as one implementation, not a family.

### Step: presentation

Once you believe that you understand the design, surface it to the user. for each section, scale the explanation based on its complexity and propose design patterns surfaced in Step: patterns_discovery that could match.
For each section, ask if its looks right or not.
Each section should cover architecture, components and/or modules, data flow, how errors are handled and test cases.
This is the step where you have to be ready to go back and forth with the user until you've converged.  That's to be expected.

#### Done

Before invoking Next step, run the convergence check. Surface this checklist to the user verbatim and require explicit "yes" on each row before emitting the final ticket:

- [ ] `## Approach` — `PATTERN:` named (not blank)
- [ ] `## Approach` — `FLOW:` has ≥3 numbered steps
- [ ] `## Approach` — `INVARIANTS:` has ≥1 entry
- [ ] `## Signatures` — filled OR explicitly marked N/A in the conversation
- [ ] `## Error design` — filled OR explicitly marked N/A in the conversation
- [ ] `## Constraints` — non-empty
- [ ] `## Boundaries` — non-empty
- [ ] Two-implementations check passed (see Step: two-impl-check)
- [ ] Synthesis check passed (see Step: synthesis)

If any row is "no", loop back to the relevant step. Once every row is "yes", proceed to Next step.

## Ideation flow

General flow of the ideation process:
```dot
  digraph ideation_flow {
    rankdir=TB;
    node [fontname="Helvetica"];
    "Synthesize Explore results\n(websearch + codebase + patterns)" [shape=box];
    "Draft ticket skeleton\n(known sections only,\nno invented info)" [shape=box];
    "Gaps in required sections?" [shape=diamond];
    "Ask clarifying questions\n" [shape=box];
    "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" [shape=box];
    "User picks approach?" [shape=diamond];
    "Fill ## Intent, ## Context,\n## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries" [shape=box];
    "Two-implementations test\n(can two valid builds satisfy?)" [shape=diamond];
    "Tighten ambiguity\n(pin the choice)" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Emit ticket to\n.tap/tickets/<slug>/ideation.md" [shape=box];
    "ticket self-review\n(schema + ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources)" [shape=box];
    "Issues found?" [shape=diamond];
    "Fix inline" [shape=box];
    "User reviews ticket?" [shape=diamond];
    "Emit final ticket emission following the [ideation template](ideation-template.md)" [shape=doublecircle];
    "Synthesize Explore results\n(websearch + codebase + patterns)"
      -> "Draft ticket skeleton\n(known sections only,\nno invented info)"
      -> "Gaps in required sections?";
    "Gaps in required sections?" -> "Ask clarifying questions\n" [label="yes"];
    "Ask clarifying questions\n" -> "Gaps in required sections?";
    "Gaps in required sections?" -> "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" [label="no"];
    "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" -> "User picks approach?";
    "User picks approach?" -> "Propose 2-3 approaches\n(grounded in patterns scan +\nneighboring conventions)" [label="reject all,\nmore options"];
    "User picks approach?" -> "Fill ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources" [label="picks one"];
    "Fill ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries" -> "Two-implementations test\n(can two valid builds satisfy?)";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Emit ticket to\n.tap/tickets/<slug>/ideation.md" [label="yes"];
    "Emit ticket to\n.tap/tickets/<slug>/ideation.md"
      -> "ticket self-review\n(schema + ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources)"
      -> "Issues found?";
    "Issues found?" -> "Fix inline" [label="yes"];
    "Fix inline" -> "ticket self-review\n(schema + ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources)";
    "Issues found?" -> "User reviews ticket?" [label="no"];
    "User reviews ticket?" -> "Fill ## Approach, ## Signatures,\n## Error design, ## Constraints,\n## Boundaries, ## Open decisions,\n## Considered & rejected, ## Failure modes,\n## Sources" [label="changes requested"];
    "User reviews ticket?" -> "Emit final ticket emission following the [ideation template](ideation-template.md)" [label="approved"];
  }
```

The final state is a fully fledged ticket containing everyting that has been discussed here.

## General rules

These rules apply accross all phases & steps:
  - Always ask one question at a time because more than one question will overwhelm the user.
  - Always prefer multi-choice questions over free-from questions because they're easier to answer.
  - Always validate incrementally because this is a slow process. A proper laid out design will produce better result than an poorly laid out one.
  - Always value flexibity because the phases & steps can be interchangeable. Structured ideas will surface from chaos. Going back & forth is expecteed.
  - Always value simplicity over over-engineered ideations because elegance emerge from simple & readable code, not over-engineered code. Good code is not measured by how many lines it contains.

## Next step

Once in this section, immediately invoke Skill(convey, {slug}) where `{slug}` is the ticket slug from the ideation just completed.
