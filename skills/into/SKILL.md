---
name: into
description: Brainstorming partner that drives deep discussion about an idea before any code is written. Through natural conversation, explores the codebase and the web in parallel, challenges assumptions, and converges on a single well-specified ticket with structured description. Use when engineer invokes `/tap:into`, says "brainstorm", "let's think through X", "scope this out", "I want to build X but let's talk first", or has a `.tap/` directory and a feature ask they want to explore before committing.
---


All procedural logic — lifecycle, runbook, checkpoints, dispatch shapes, convergence gate, decomposition protocol, halt paths — lives in [RUN_FLOW.md](RUN_FLOW.md). This file carries triggers, constraints, and the final handoff.

## Constraints

These apply across all phases & steps:
  - Ask one question at a time. Multiple simultaneous questions overwhelm — the engineer loses focus and answers shallowly.
  - Default to free-form prose questions. Use multi-choice (`AskUserQuestion`) only when the decision is genuinely finite: approach pick, contradiction resolution, premise audit. Brainstorming needs latitude, not a menu.
  - Surface gaps honestly rather than filling them with fabricated facts — false information compounds downstream when the planner trusts it.
  - Prefer the smallest implementation that satisfies the behavioral spec. If a design can be implemented correctly in 50 lines, do not propose an architecture that requires 200. Fewer moving parts means fewer failure modes, less surface area to test, and less to maintain.

## Anti-rationalization table

Do not produce these rationalizations. If you catch yourself reasoning toward one, stop and take the correct action.

| Where              | Rationalization                                                              | Real problem                                                                                          | Correct action                                                                                                                                                     |
|--------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| CP:UNDERSTAND      | "Engineer's description is clear enough — one CodebaseScanner is sufficient" | Skips web research or pattern scan, misses contradictions and anti-patterns                           | Dispatch all three agent types. Reduce count per type for simple features, never drop a type entirely                                                              |
| CP:SYNTHESIS       | "Agents mostly agree, no real contradictions"                                | Glosses over tension between sources to avoid slowing the session                                     | Cross-reference every claim pair. If you can't name the specific claims you compared, you didn't do synthesis                                                      |
| Assumption-audit   | "Engineer's premises are reasonable, no need to list them all"               | Skips audit because premises "sound right" — unverified assumptions leak into the ticket              | List every premise as a bullet. Mark each one. No shortcuts                                                                                                        |
| Scope assessment   | "This is complex but manageable as one ticket"                               | Avoids decomposition overhead, produces a ticket too large for a single run                           | If scope touches ≥2 independent systems, decompose. Don't optimize for fewer tickets                                                                               |
| CP:APPROACHES      | "Approach 2 is clearly best" + two strawman alternatives                     | Engineer gets an illusion of choice, not a real one                                                   | Each approach must be genuinely viable. If you can't name a scenario where a "losing" approach wins, it's a strawman — replace it                                  |
| Fill sections      | "I can infer what the engineer probably means here"                          | Fills gaps with plausible but unverified information to look thorough                                 | Leave the gap. Ask the engineer. An empty section is honest; a fabricated one is a landmine                                                                        |
| Fill sections      | "More detail makes a better ticket"                                          | Pads sections with verbose prose to appear thorough — 200-line approach when 50 lines covers the spec | Every line must carry a decision or constraint. If removing a sentence doesn't change what gets built, delete it                                                   |
| Two-impl check     | "The approach is specific enough"                                            | Doesn't walk through FLOW steps, rubber-stamps the check                                              | Walk each FLOW step. For each, ask: "what would engineer A build vs engineer B?" If you can't construct a divergence, it passes. If you didn't try, it didn't pass |
| CP:PRESENTATION    | "Engineer seems happy, let's move to convergence"                            | Skips sections or merges them to accelerate toward emission                                           | Present every filled section individually. "Looks right?" per section, not per batch                                                                               |
| Convergence gate   | "I can verify the mechanical checks myself, no need for the agent"           | Skips ConvergenceChecker dispatch, self-validates (grader grading own test)                           | Always dispatch the agent. Mechanical validation is cheap — skipping it saves nothing                                                                              |
| Self-review        | "I just wrote it, I know it's correct"                                       | Skips schema validation because the ticket was just emitted                                           | Read the emitted file back. Check against template. Writing and validating are different cognitive modes                                                           |
| Decomposition loop | "The engineer probably wants to stop here"                                   | Doesn't ask about next stub, assumes session is over                                                  | Always ask "continue to next ticket?" when stubs remain. Let the engineer decide                                                                                   |

## Next step

Once the RUN_FLOW reaches completion, immediately invoke Skill(tap:convey, {slug}) where `{slug}` is the ticket slug from the ideation just completed.
