---
name: run
description: Executes one or more decomposed tickets through a wave-parallel TDD pipeline. One worktree per ticket; tasks group into waves by symbol-dependency inference; tasks within a wave run in parallel when their `files.create` + `files.modify` are disjoint, sequential when they overlap; each task runs three phase agents (TestWriter → CodeWriter → Refactorer) chained via git commit trailers. Orchestrator owns the worktree (create, merge, delete). Use when the user invokes `/tap-run`, says "run the tickets", "execute the pipeline", or has unfinished `.tap/tickets/<slug>/` folders with `task-*.md` files.
argument-hint: slug
---


# tap-run

Drives decomposed tickets in `.tap/tickets/<slug>/` through a wave-parallel TDD pipeline. One worktree per ticket, owned end-to-end by the orchestrator. Tasks inside a ticket are grouped into waves by symbol ownership inferred from `context[]`; wave-mates run in parallel when their file sets are disjoint and serialize when they overlap. Each task threads RED → GREEN → REFACTOR phase agents chained through git commit trailers. The canonical execution doc is the co-located [RUN_FLOW.md](RUN_FLOW.md) — this file is the trigger surface only.

## How to use this skill

1. Read [RUN_FLOW.md](RUN_FLOW.md) end-to-end before any tool call.
2. Re-skim `RUN_FLOW.md`'s `## Runbook` and `## Phase failure branches` before each wave dispatch — keeps mid-run drift out.
3. Phase agent files at `agents/{TestWriter,CodeWriter,Refactorer,Debugger,Reviewer}.md` are the contract for each subagent's behavior; do not embed their logic here.

## Constraints

1. Pass all four gates before committing; RED exempts the test gate only.
2. Each phase commits its own work with `Tap-Task`, `Tap-Phase`, `Tap-Files` trailers.
3. Wrap disk-writing gates and the `git add … && git commit …` step in `flock -w 300 <commit_lock>`.
4. Fix hook failures at the source via a new commit.
5. Resume by parsing trailers in `<parent_sha>..HEAD`; skip phases already committed.
6. Wave-mates run in parallel; wave-mates touch disjoint files.
7. Run Reviewer once per ticket when survivors ≥ 2; only Blockers trigger Debugger Shape B.
8. Orchestrator owns the worktree (create at ticket entry, integrate + delete at ticket exit).
9. Sub-agents stay inside their assigned worktree.
10. Phase agents find prior phases by trailer search in `<parent_sha>..HEAD`.
11. Tickets run in lex-slug order; tasks inside a ticket group into waves.
12. Subjects follow the exact form: `test(<task-id>): …`, `feat(<task-id>): …`, `refactor(<task-id>): …`, `fix(<scope>): …`.
13. Before each wave dispatch, read `.failure-log.json` from the worktree and inject `<failure-context>` into agent prompts for tasks whose files overlap with prior failures.
14. Before each agent dispatch, build and inject a `<calibration>` block from established `_profile.json` signals. Only `established` (≥3 samples) signals enter the block; `tentative` signals are never injected.
15. After each GREEN or REFACTOR commit, run smell-check: if the task has a pattern hint, scan the phase diff against the pattern's `smells_it_introduces` heuristics and append matches to `.smell-warnings.json`. Inject `<smell-warnings>` into the next phase agent's prompt.
16. After plan approval, create a TaskList (ticket → wave → task → phase) before opening any worktree. Update task status as phases complete. The TaskList MUST exist before step 4 begins.
17. Never prune worktrees silently. Surface stale worktree references in the plan output; prune only after engineer approves.

## Halt paths

- Dirty main repo on entry → halt before discovery; surface dirty paths.
- Quality gates unresolvable → halt before planning.
- Cycle in symbol-owner graph → halt the ticket; surface the cycle.
- Worktree create fails → mark ticket FAILED; continue to next ticket.
- Phase agent emits malformed envelope → halt ticket; leave worktree intact.
- Commit-lock timeout twice → saga-isolate the affected task; continue the wave.
- All tasks saga-isolated → ticket FAILED; cleanup worktree; continue.
- Reviewer Blockers persist after Shape B → ticket FAILED; leave worktree intact.
- Rebase conflict on integration → halt the ticket; leave worktree for inspection.

## Anti-rationalization table

Do not produce these rationalizations. If you catch yourself reasoning toward one, stop and take the correct action.

| Where              | Rationalization                                                            | Real problem                                                                                      | Correct action                                                                                                          |
|--------------------|----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Preflight          | "Working tree is mostly clean, just one untracked file"                    | Dirty state leaks into worktree or corrupts merge. "Mostly clean" is dirty                        | `git status --porcelain` must return empty. Any output = halt                                                           |
| Planning           | "Plan is straightforward, engineer will obviously approve"                 | Skips approval prompt, removes engineer's last checkpoint before execution                        | Always ask. Approval is mandatory even for single-task tickets                                                          |
| Planning           | "Only one ticket with two tasks, TaskList is overkill"                     | Skips progress tracking. No visibility into what completed, what failed, what's pending           | Always create TaskList after approval. Even single-task tickets get tracked                                              |
| Preflight          | "Stale worktrees are just garbage, safe to prune automatically"            | Silent cleanup removes references the engineer may not know about. Violates no-surprise principle | Surface stale entries in the plan. Prune only after engineer approves the plan                                           |
| Wave inference     | "These tasks don't really depend on each other, one wave is fine"          | Puts file-overlapping tasks in same wave. Parallel writes corrupt each other                      | Run the algorithm. Two tasks sharing any path NEVER share a wave — no judgment calls                                    |
| Dispatch           | "I'll dispatch tasks one at a time to be safe"                             | Serializes what should be parallel, wastes wall time, violates wave-parallel contract             | One assistant message per phase per wave. N tasks = N parallel Agent calls                                              |
| Dispatch           | "I'll fix this failure myself instead of dispatching Debugger"             | Orchestrator does agent work, bypasses Debugger's structured root-cause analysis and trailer      | Always dispatch Debugger Shape A. Orchestrator orchestrates, agents execute                                             |
| Gates              | "Tests pass, lint is just style — skip it this once"                       | Broken lint gate hides real issues. Gate exemptions are defined in the spec, not improvised       | All four gates must pass (RED exempts test gate only). No ad-hoc exemptions                                             |
| Commit lock        | "No parallel tasks right now, flock is unnecessary overhead"               | Next wave might overlap. Lock discipline must be unconditional or race conditions sneak in        | Always `flock -w 300`. Even single-task waves use the lock — consistency prevents bugs                                  |
| Trailers           | "Trailers are boilerplate, the commit message is clear enough"             | Missing trailers break resume. Next run can't skip completed phases, re-runs everything          | Every phase commit gets `Tap-Task`, `Tap-Phase`, `Tap-Files`. Non-negotiable                                            |
| --no-verify        | "Hook is failing on something irrelevant to this change"                   | Bypasses safety checks. Hook failures signal real issues that compound downstream                 | Never `--no-verify`. Fix the underlying issue, create a new commit                                                      |
| Reviewer           | "Only two survivors and they're trivial, Reviewer is overkill"             | Survivors ≥ 2 = Reviewer runs. Complexity judgment is not the orchestrator's call                 | Dispatch Reviewer when survivors ≥ 2. No exceptions based on perceived simplicity                                       |
| Reviewer blockers  | "These blockers are minor, more like warnings really"                      | Downgrades severity to skip Debugger Shape B, lets real issues into the merge                     | Blocker severity is the Reviewer's call, not the orchestrator's. Blockers trigger Shape B, always                       |
| Retro              | "Run was clean, no failures, retro won't find anything useful"             | Skips data collection. Clean runs are signal too — retro builds the profile from both             | Always invoke `Skill(tap:retro)` as the last action. No conditional skip                                                |
| Calibration        | "The profile signal is tentative but looks relevant, worth including"      | Acting on tentative data (< 3 samples) is acting on noise. Premature calibration erodes trust     | Only inject `established` signals. Log tentative signals internally; never put them in `<calibration>`                   |
| TAP_RESULT         | "Agent output looks successful, I can infer the status"                    | Infers instead of parsing. Malformed or missing envelope = halt, not guess                        | Parse the final-line `TAP_RESULT: {...}` JSON. Missing or malformed = halt ticket                                       |
| Resume             | "Fresh worktree, no prior commits to check"                                | Skips trailer parsing. If a previous run was interrupted, phases get re-run and duplicate work    | Always parse `<parent_sha>..HEAD` trailers. Empty result = fresh, not "skip the check"                                  |

## See also

- [`RUN_FLOW.md`](./RUN_FLOW.md) — co-located, canonical run flow (lifecycle,
  runbook, wave inference, dispatch, commit policy, failure + halt tables).

- `agents/{TestWriter,CodeWriter,Refactorer,Debugger,Reviewer}.md` —
  per-agent contracts.
