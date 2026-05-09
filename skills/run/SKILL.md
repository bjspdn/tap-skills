---
name: run
description: Executes one or more decomposed tickets through a wave-parallel TDD pipeline. One worktree per ticket; tasks group into waves by symbol-dependency inference; tasks within a wave run in parallel when their `files.create` + `files.modify` are disjoint, sequential when they overlap; each task runs three phase agents (TestWriter → CodeWriter → Refactorer) chained via git commit trailers. Orchestrator owns the worktree (create, merge, delete). Use when the user invokes `/tap-run`, says "run the tickets", "execute the pipeline", or has unfinished `.tap/tickets/<slug>/` folders with `task-*.md` files.
---

# tap-run

Drives decomposed tickets in `.tap/tickets/<slug>/` through a wave-parallel TDD pipeline. One worktree per ticket, owned end-to-end by the orchestrator. Tasks inside a ticket are grouped into waves by symbol ownership inferred from `context[]`; wave-mates run in parallel when their file sets are disjoint and serialize when they overlap. Each task threads RED → GREEN → REFACTOR phase agents chained through git commit trailers. The canonical execution doc is the co-located [RUN_FLOW.md](RUN_FLOW.md) — this file is the trigger surface only.

## How to use this skill

1. Read [RUN_FLOW.md](RUN_FLOW.md) end-to-end before any tool call.
2. Re-skim `RUN_FLOW.md`'s `## Runbook` and `## Phase failure branches` before each wave dispatch — keeps mid-run drift out.
3. Phase agent files at `agents/{TestWriter,CodeWriter,Refactorer,Debugger,Reviewer}.md` are the contract for each subagent's behavior; do not embed their logic here.

## Hard rules

1. Orchestrator owns the worktree (create at ticket entry, integrate + delete at ticket exit).
2. Sub-agents stay inside their assigned worktree.
3. Tickets run in lex-slug order; tasks inside a ticket group into waves.
4. Wave-mates run in parallel; wave-mates touch disjoint files.
5. Phase agents find prior phases by trailer search in `<parent_sha>..HEAD`.
6. Each phase commits its own work with `Tap-Task`, `Tap-Phase`, `Tap-Files` trailers.
7. Subjects follow the exact form: `test(<task-id>): …`, `feat(<task-id>): …`, `refactor(<task-id>): …`, `fix(<scope>): …`.
8. All four gates green before commit; RED exempts the test gate only.
9. Disk-writing gates and the `git add … && git commit …` step run under `flock -w 300 <commit_lock>`.
10. Resume by parsing trailers in `<parent_sha>..HEAD`; phases already committed are skipped.
11. Hook failures get fixed at root cause via a new commit.
12. Reviewer runs once per ticket when survivors ≥ 2; only Blockers trigger Debugger Shape B.

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

## See also

- [`RUN_FLOW.md`](./RUN_FLOW.md) — co-located, canonical run flow (lifecycle,
  runbook, wave inference, dispatch, commit policy, failure + halt tables).

- `agents/{TestWriter,CodeWriter,Refactorer,Debugger,Reviewer}.md` —
  per-agent contracts.
