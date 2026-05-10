# Research Template

Use this template for all research artifacts. Adapt section depth to the topic,
but preserve structural order. Sections marked `(conditional)` are included or
swapped based on the research mode (project-bound vs pure-knowledge).

---

```markdown
> **Topic:** [Research topic] | **Domain:** [domain classification] | **Mode:** project-bound | pure-knowledge | **Date:** [date] | **Hops:** [N]
> **Stack:** [language + framework] *(project-bound only — omit for pure-knowledge)*

---

## Question

[1-2 sentences framing the research question. What specifically are we trying
to understand?]

---

## TL;DR

[3-5 bullet points summarizing the key findings. A reader who stops here should
have the essential answer. Each bullet states a finding and its confidence level.]

---

## Findings

What authoritative sources converge on. Each finding is graded.

### [Finding name]

**Confidence:** Established | Probable | Uncertain
**Sources:** [inline source links]

[Description of the finding. What it is, why it matters, when it applies.
Specific enough to act on — not "RNG is important for games" but "Mersenne
Twister has a period of 2^19937-1 but fails BigCrush statistical tests;
xoshiro256** passes all tests and is faster on modern hardware".]

### [Next finding...]

[Repeat as needed. Typically 3-8 findings per research topic.]

---

## Competing Approaches

*(Conditional — include only when genuine disagreement exists across sources.)*

Areas where sources have not converged — multiple valid approaches coexist.

### [Approach A] vs [Approach B]

| Dimension           | [Approach A] | [Approach B] |
|---------------------|--------------|--------------|
| When to use         |              |              |
| Tradeoff            |              |              |
| Adoption signal     |              |              |
| Key advocate/source |              |              |

[Brief analysis of when each approach fits. No recommendation — present the
decision factors.]

---

## Codebase Alignment

*(Conditional — project-bound only. Omit entirely for pure-knowledge research.)*

How the current project relates to research findings.

### Follows

| Finding        | Evidence                     |
|----------------|------------------------------|
| [Finding name] | `file:line` — [what it does] |

### Diverges

| Finding        | Current Approach                 | Evidence    |
|----------------|----------------------------------|-------------|
| [Finding name] | [What the codebase does instead] | `file:line` |

### Absent

| Finding        | Where It Would Apply                             |
|----------------|--------------------------------------------------|
| [Finding name] | [Which part of the codebase this is relevant to] |

### Local Conventions

[Patterns the codebase uses that the research didn't cover — project-specific
idioms worth preserving or questioning.]

---

## Source Agreement

*(Conditional — pure-knowledge only. Omit entirely for project-bound research.)*

How sources relate to each other on key claims.

### Consensus

| Finding        | Agreeing Sources     |
|----------------|----------------------|
| [Finding name] | [source1], [source2] |

### Contradictions

| Finding | Source A says | Source B says | Likely reason                      |
|---------|---------------|---------------|------------------------------------|
| [Claim] | [Position]    | [Position]    | [version diff, context diff, etc.] |

### Single-source claims

| Finding | Source | Note                          |
|---------|--------|-------------------------------|
| [Claim] | [URL]  | Confidence capped at Probable |

---

## Confidence Map

| Claim           | Confidence                         | Source Count | Recency              |
|-----------------|------------------------------------|--------------|----------------------|
| [Claim summary] | Established / Probable / Uncertain | [N]          | [newest source year] |

---

## Open Questions

[Questions that research could not resolve — genuine disagreement, topic too
new for consensus, or answer depends on context only the user can provide.]

- [Question 1]
- [Question 2]

---

## Sources

| Source | Type                                                        | Relevance                  |
|--------|-------------------------------------------------------------|----------------------------|
| [URL]  | docs / RFC / paper / spec / blog / discussion / repo / wiki | [one-line why it mattered] |
```

---

## Template Notes

- **TL;DR is mandatory.** The research artifact may be consumed by `tap-into`
  mid-ideation — the TL;DR lets it extract the essentials without reading the
  full document.
- **Confidence grading is mandatory per finding.** Established = 2+ authoritative
  sources agree. Probable = 1 authoritative or 2+ community sources. Uncertain =
  conflicting or single community source.
- **Codebase Alignment is mandatory for project-bound research.** Research without
  grounding in the actual project is trivia. The alignment section makes it
  actionable. Omit for pure-knowledge research.
- **Source Agreement is mandatory for pure-knowledge research.** Without a codebase
  to ground against, cross-referencing sources against each other is how rigor is
  maintained. Omit for project-bound research.
- **Never include both Codebase Alignment and Source Agreement.** They are mutually
  exclusive based on mode.
- **No recommendations.** The artifact presents what exists and what sources say.
  Design decisions happen in `tap-into`, not here.
- **Line count target:** 150-400 lines. Under 150 suggests shallow research.
  Over 400 suggests scope creep — split into multiple research artifacts.
- **Competing Approaches section is conditional.** Only include when genuine
  disagreement exists across sources. If there's clear consensus, skip it.