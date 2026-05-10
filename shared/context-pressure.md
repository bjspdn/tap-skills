# Context Pressure Protocol

A `UserPromptSubmit` hook injects a `CONTEXT_PRESSURE` signal every turn based on real token counts from the transcript. Skills adapt verbosity accordingly.

## Pressure Levels

Thresholds are grounded on a 200K effective budget regardless of actual model window size. Attention quality degrades well before the window fills — these thresholds keep skills disciplined early.

| Level      | Trigger          | Behavior                                                                                                                                                                                                                                     |
|------------|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `nominal`  | < 100K tokens    | Full prose. Inline examples. Conversational exploration. Verbose agent outputs in conversation when useful.                                                                                                                                  |
| `moderate` | 100K–150K tokens | Emit decisions to artifact files. Conversation gets one-line summaries only. No restating prior context. No inline justification unless user asks. Agent outputs consumed silently — surface only conflicts or decisions needing user input. |
| `high`     | > 150K tokens    | Near-silent. Status updates only ("Wave 2 complete. 3/3 green."). All substance flows through artifact files and git trailers. Never echo agent output inline. Never restate task specs.                                                     |

## Default Postures (when no signal present)

If the hook is not installed or emits no signal, skills fall back to their natural posture:

| Skill                 | Default posture |
|-----------------------|-----------------|
| into                  | nominal         |
| research (standalone) | nominal         |
| convey                | moderate        |
| sketch                | moderate        |
| retro                 | moderate        |
| research (callable)   | moderate        |
| refactor              | moderate        |
| run                   | high            |

## Rules

1. **Artifacts over conversation.** At `moderate`+, substance belongs in files (`.tap/tickets/`, `.tap/research/`, `.tap/retros/`), not conversation. Conversation carries status, decisions, and failures only.
2. **No restating.** Never repeat what an artifact already says. The user wrote ideation.md — don't echo it back. The agent emitted TAP_RESULT — don't paste it inline.
3. **Summaries scale down.** At `nominal`: full paragraph summaries OK. At `moderate`: one line per item. At `high`: counts and status codes only.
4. **User questions override.** If the user asks "why did you do X?", answer fully regardless of pressure level. Then return to constrained mode.
5. **Agent dispatch stays silent at moderate+.** Don't narrate "I'm now dispatching the DependencyScanner agent..." — just do it. Surface only results that need user action.

## Anti-rationalization

| Rationalization                                                     | Real problem                                                               | Correct action                                                                   |
|---------------------------------------------------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| "User should see this reasoning so they understand my decisions"    | Burning context on process narration nobody asked for                      | Write to artifact. One-line summary in conversation. User reads file if curious. |
| "I need to restate the task spec so it's fresh in context"          | Agent reads task file from disk — restating wastes tokens for zero benefit | Trust the file. Reference it by path, don't inline it.                           |
| "This is important enough to be verbose even at high pressure"      | Nothing is important enough to fill the window and lose early context      | Compress. If truly critical, write to a file and tell user where to look.        |
| "I'm only slightly over the threshold, moderate rules are overkill" | Thresholds exist because gradual drift is invisible until it's too late    | Respect the level. No exceptions. No "just this once."                           |
