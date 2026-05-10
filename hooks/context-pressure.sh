#!/bin/bash
# Context pressure monitor for tap skills.
# Reads last assistant turn's token usage from transcript.
# Thresholds grounded on 200K effective budget regardless of model window.

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

echo "{\"additionalContext\": \"CONTEXT_PRESSURE: $PRESSURE (${INPUT_TOKENS}t / 200K budget). Follow shared/context-pressure.md protocol.\"}"
