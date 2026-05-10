#!/bin/bash
# Context pressure monitor for tap skills.
# Reads last assistant turn's token usage from transcript.
# Thresholds grounded on 200K effective budget regardless of model window.

# Only fire in repos with an active .tap/ directory
[ -d ".tap" ] || exit 0

INPUT=$(cat)
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path')

if [ ! -f "$TRANSCRIPT" ]; then
  exit 0
fi

# Extract last assistant turn's input token total (= context window usage that turn)
LAST_USAGE=$(tac "$TRANSCRIPT" | grep -m1 '"role":"assistant"' || true)

if [ -z "$LAST_USAGE" ]; then
  exit 0
fi

INPUT_TOKENS=$(echo "$LAST_USAGE" | jq '
  (.message.usage.input_tokens // 0) +
  (.message.usage.cache_creation_input_tokens // 0) +
  (.message.usage.cache_read_input_tokens // 0)
' 2>/dev/null)

if [ -z "$INPUT_TOKENS" ] || [ "$INPUT_TOKENS" = "null" ]; then
  exit 0
fi

# Thresholds: 200K effective budget
if [ "$INPUT_TOKENS" -gt 150000 ]; then
  PRESSURE="high"
elif [ "$INPUT_TOKENS" -gt 100000 ]; then
  PRESSURE="moderate"
else
  PRESSURE="nominal"
fi

# Only inject at moderate+ to avoid noise
if [ "$PRESSURE" = "nominal" ]; then
  exit 0
fi

# Inline rules per level — no file lookup needed
if [ "$PRESSURE" = "high" ]; then
  RULES="Near-silent. Status updates only (e.g. 'Wave 2 complete. 3/3 green.'). All substance via artifact files + git trailers. Never echo agent output inline. Never restate task specs or ideation content. Never narrate agent dispatch."
else
  RULES="Emit decisions to artifact files. Conversation gets one-line summaries only. No restating prior context. No inline justification unless user asks. Agent dispatch silent — surface only conflicts needing user input."
fi

echo "{\"additionalContext\": \"CONTEXT_PRESSURE: $PRESSURE (${INPUT_TOKENS}t / 200K budget). ${RULES} User questions override — answer fully, then return to constrained mode.\"}"
