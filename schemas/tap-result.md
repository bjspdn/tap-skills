# TAP_RESULT Envelope Contract

The TAP_RESULT envelope is the structured output every tap agent emits on its final line of stdout. The orchestrator parses this line to determine run outcome.

## Format

The very last line of stdout MUST be a single `TAP_RESULT:` line — a JSON object on one line, prefixed by `TAP_RESULT: `. Nothing comes after it.

```
TAP_RESULT: {"status":"<status>","data":{...}}
```

## Constraints

- Emit exactly one `TAP_RESULT:` line per run, immediately before exiting.
- Place it as the FINAL line of stdout. Follow it with nothing — no trailing prose, no trailing newline content, no fenced code block, no follow-up explanation.
- Format the JSON as single-line, strictly valid: double-quoted strings, no trailing commas, no comments.
- Escape newlines as `\n` inside JSON strings for multi-line content (reasons, embedded stderr, notes, evidence excerpts).
- The orchestrator treats missing, malformed, or non-final envelopes as a fatal failure.

## Status values

Three possible statuses:

| Status | Meaning |
|--------|---------|
| `ok` (or `pass` for Reviewer) | Agent completed successfully — committed, skipped on resume, or passed audit |
| `failed` (or `fail` for Reviewer) | Agent encountered a recoverable failure — phase gate red, test still failing, blockers found |
| `gave_up` | Agent cannot proceed — missing input, design conflict, scope violation |

## Generic shape

```json
{"status":"ok","data":{...}}
{"status":"failed","data":{...}}
{"status":"gave_up","data":{"reason":"<why the task cannot proceed>"}}
```

Each agent extends the `data` object with agent-specific fields (status shapes, phase identifiers, file lists, etc.). See the individual agent spec for the exact `data` contract per status value.
