---
name: health
description: Validates the integrity of the `.tap/` directory structure, detects stale worktrees, orphaned lockfiles, incomplete tickets, stale branches, and profile corruption. Reports a summary table and offers safe auto-repair with user confirmation. Use when the user invokes `/tap:health`, says "check tap health", "validate .tap", "clean up tap", "any stale worktrees", or wants to diagnose issues with their `.tap/` state.
---

## Context pressure

Follow the protocol in [shared/context-pressure.md](../../shared/context-pressure.md).
Default posture when no signal present: **nominal**

# tap-health

Diagnostic and repair tool for the `.tap/` directory. Runs a fixed set of integrity checks, surfaces a summary table, and offers auto-repair for safe fixes. Never auto-repairs without explicit user confirmation.

## Phase: preflight

### Purpose

Verify `.tap/` exists and resolve the repository root.

### Step: locate

1. Resolve `$REPO_ROOT`:
   ```
   git rev-parse --show-toplevel
   ```

2. Check that `$REPO_ROOT/.tap/` exists. If it does not, halt immediately:

   > "No `.tap/` directory found at repository root. Nothing to check."

3. Record which standard subdirectories exist:
   - `.tap/tickets/`
   - `.tap/tickets/done/`
   - `.tap/worktrees/`
   - `.tap/retros/`
   - `.tap/research/`

Missing subdirectories are not failures — they indicate features that haven't been used yet. Record them as informational.

### Done

Repository root resolved, `.tap/` confirmed present. Proceed to checks.

## Phase: checks

### Purpose

Run each diagnostic check independently. Collect results as `(check_name, status, detail)` tuples where status is one of: OK, WARN, FAIL.

### Step: directory-structure

Check that `.tap/` contains at least the expected subdirectories. For each standard subdirectory:

- Present → OK
- Absent → WARN with detail "not yet created"

This check never produces FAIL — missing dirs are expected for fresh projects.

### Step: stale-worktrees

Detect worktree directories that exist on disk but are not registered with git.

1. List directories under `.tap/worktrees/` (if the directory exists):
   ```
   ls -d .tap/worktrees/*/ 2>/dev/null
   ```

2. Get registered worktrees:
   ```
   git worktree list --porcelain
   ```

3. For each directory under `.tap/worktrees/`, check whether its absolute path appears in the registered worktree list.

4. A directory present on disk but absent from `git worktree list` is stale.

- No stale worktrees → OK "all worktrees registered"
- Stale worktrees found → WARN with list of stale paths
- `.tap/worktrees/` does not exist → OK "no worktrees directory"

Mark stale worktrees as **repairable**: `git worktree prune` + remove the directory.

### Step: orphaned-lockfiles

Detect `.lock` files with no active process holding them.

1. Find all lockfiles:
   ```
   find .tap/ -name "*.lock" -type f
   ```

2. For each lockfile, test whether any process holds it:
   ```
   flock -n <lockfile> true && echo "orphaned" || echo "active"
   ```
   If `flock -n` succeeds (exit 0), no process holds the lock — it is orphaned.

- No lockfiles → OK "no lockfiles present"
- All lockfiles active → OK "all lockfiles held by active processes"
- Orphaned lockfiles found → WARN with list of orphaned paths

Mark orphaned lockfiles as **repairable**: delete them.

### Step: ticket-integrity

Validate tickets have required structure.

1. For each directory under `.tap/tickets/` (excluding `done/`):
   - Check `ideation.md` exists. Missing → WARN "missing ideation.md"
   - Check at least one `task-*.md` file exists. Missing → WARN "no task files"
   - For each `task-*.md`, verify it has non-empty content (size > 0 bytes). Empty → WARN "empty task file: <filename>"

2. For each directory under `.tap/tickets/done/`:
   - Same checks as above, but missing task files are only informational (old tickets may predate current conventions).

- All tickets valid → OK "N active, M completed — all well-formed"
- Issues found → WARN with list of specific problems
- `.tap/tickets/` does not exist → OK "no tickets directory"

Ticket issues are **not repairable** — they require human judgment.

### Step: stale-branches

Detect `tap-*` branches with no corresponding active ticket.

1. List all local branches matching `tap-*`:
   ```
   git branch --list "tap-*" --format="%(refname:short)"
   ```

2. List all active ticket slugs (directory names under `.tap/tickets/`, excluding `done/`).

3. A branch is stale if its slug (the part after `tap-`) does not match any active ticket slug AND does not match any slug under `.tap/tickets/done/` from the last 7 days (by directory mtime).

- No `tap-*` branches → OK "no tap branches"
- All branches have matching tickets → OK "all branches active"
- Stale branches found → WARN with list of branch names

Mark stale branches as **repairable**: `git branch -d <branch>` (safe delete — refuses if unmerged).

### Step: stale-session-checkpoint

Detect a leftover `SESSION_RESUME.json` from a dead or interrupted `tap:run` session.

1. Check if `$REPO_ROOT/.tap/SESSION_RESUME.json` exists.
   - Does not exist → OK "no session checkpoint"
   - Exists → read and parse as JSON.

2. If JSON parsing fails → WARN "SESSION_RESUME.json is not valid JSON — likely corrupt"

3. If valid JSON, read the `updated_at` field and compute age:
   - Age ≤ 24 hours → WARN "active session checkpoint (updated <age> ago for ticket '<ticket_slug>'). A tap:run may be in progress, or the session died recently. Run `/tap:run` to resume or start fresh."
   - Age > 24 hours → WARN "stale session checkpoint (updated <age> ago for ticket '<ticket_slug>'). Likely from a dead session. Run `/tap:run` to resume or delete `.tap/SESSION_RESUME.json` manually."

- File absent → OK
- File present, age ≤ 24h → WARN (may be active)
- File present, age > 24h → WARN (likely stale)

Mark stale checkpoints (age > 24h) as **repairable**: delete `.tap/SESSION_RESUME.json`.

### Step: profile-integrity

Validate the retro profile file.

1. Check if `.tap/retros/_profile.json` exists:
   - Does not exist → OK "no profile yet (retro not run)"
   - Exists but empty (0 bytes) → FAIL "profile file is empty"
   - Exists with content → parse as JSON

2. If JSON parsing fails → FAIL "profile is not valid JSON"

3. If JSON is valid, check for expected top-level keys (`agent_performance`, `pattern_signals`, `gate_signals`). Missing keys are WARN, not FAIL — the profile schema may evolve.

- Valid JSON with expected keys → OK "profile valid"
- Valid JSON with missing keys → WARN "missing keys: <list>"
- Invalid JSON or empty → FAIL with detail

Profile issues are **not auto-repairable** — corrupt JSON requires manual inspection or a fresh retro run.

### Done

All checks complete. Proceed to reporting.

## Phase: report

### Purpose

Surface findings in a readable summary table and offer repairs.

### Step: summary-table

Present results as a markdown table:

```
| Check               | Status | Detail                             |
|---------------------|--------|------------------------------------|
| Directory structure | OK     | 5/5 subdirectories present         |
| Stale worktrees     | WARN   | 2 stale: .tap/worktrees/foo, ...   |
| Orphaned lockfiles  | OK     | no lockfiles present               |
| Ticket integrity    | OK     | 3 active, 7 completed              |
| Stale branches      | WARN   | tap-old-feature (no active ticket) |
| Session checkpoint  | WARN   | stale (updated 3 days ago, ticket 'foo') |
| Profile integrity   | OK     | profile valid                      |
```

### Step: repair-offer

If any check produced repairable WARN/FAIL results, present the repair actions grouped by check:

```
Repairable issues found:

1. Stale worktrees (2):
   - .tap/worktrees/foo → will run: git worktree prune && rm -rf .tap/worktrees/foo
   - .tap/worktrees/bar → will run: git worktree prune && rm -rf .tap/worktrees/bar

2. Stale branches (1):
   - tap-old-feature → will run: git branch -d tap-old-feature

Apply all repairs? (yes / pick individually / skip)
```

Wait for explicit user confirmation before executing any repair. If the user picks individually, present each repair one at a time.

If no repairable issues exist, state: "No repairs needed."

### Step: execute-repairs

For each confirmed repair, execute the command and report success or failure inline:

- Success: checkmark + command
- Failure: surface the error output, do not retry

After all repairs, re-run only the affected checks to confirm resolution. Surface the updated status.

### Done

Health check complete. Summary delivered, repairs applied (if any).

## Constraints

- **Wait for explicit user confirmation before modifying anything.** The diagnostic phase is read-only.
- **Use `git branch -d` (safe delete) for branch removal.** If deletion fails due to unmerged state, report it and move on.
- **Only remove worktree directories that `git worktree list` does not reference.**
- **Test lockfiles non-destructively.** `flock -n <file> true` tests without acquiring. If it succeeds, the lock is free. If it fails, a process holds it — leave it alone.
- **Keep the entire health check local.** No fetching, no pushing, no network calls.
- **Produce identical reports on consecutive runs** (minus any repairs applied on the first run).

## Anti-rationalization table

Do not produce these rationalizations. If you catch yourself reasoning toward one, stop and take the correct action.

| Where             | Rationalization                                                 | Real problem                                                                   | Correct action                                                                               |
|-------------------|-----------------------------------------------------------------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| Stale worktrees   | "Directory looks important, might be in use"                    | Trusts intuition over `git worktree list`. If git doesn't track it, it's stale | Check the registered list. Present is present, absent is absent. No guessing                 |
| Orphaned locks    | "Process might come back, better leave the lock"                | `flock -n` succeeded — no process holds it. Dead locks block future runs       | If `flock -n` succeeds, the lock is orphaned. Offer removal                                  |
| Repair offer      | "These are all safe, I'll just fix them without asking"         | Violates user-confirmation rule. "Safe" is the user's call, not the agent's    | Always ask. Present the exact commands. Wait for yes/no                                      |
| Stale branches    | "Branch might have useful work, I'll skip it"                   | `git branch -d` already refuses unmerged branches. The safety net is built in  | Offer the deletion. Let git's own safety mechanism decide. Report refusal if it happens      |
| Profile integrity | "JSON is almost valid, I can fix the syntax"                    | Auto-editing profile risks data loss. Profile is a rolling aggregate           | Report the error. Suggest re-running `/tap:retro` to regenerate. Never hand-edit             |
| Missing dirs      | "I should create the missing subdirectories proactively"        | User may not need all features. Empty dirs add noise                           | Report as informational. Do not create directories — they appear naturally when features run |
| Ticket integrity  | "Empty task file is probably a placeholder, not a real problem" | Placeholders rot. A task file with no content will confuse `/tap:run`          | Report it. Let the user decide if it's intentional                                           |
