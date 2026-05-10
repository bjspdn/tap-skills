#!/usr/bin/env bash
set -euo pipefail

# Schema validation for the tap plugin.
# Checks structural integrity of markdown frontmatter + JSON files.
# Dependencies: bash, jq, grep, find (no external tools).

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAIL=0

pass() { printf "  \033[32mPASS\033[0m %s\n" "$1"; }
fail() { printf "  \033[31mFAIL\033[0m %s — %s\n" "$1" "$2"; FAIL=1; }

# Extract YAML frontmatter value (between --- fences). Returns empty if missing.
frontmatter_has() {
  local file="$1" field="$2"
  sed -n '/^---$/,/^---$/p' "$file" | grep -q "^${field}:"
}

printf "\n\033[1m[patterns] Checking pattern cards…\033[0m\n"
REQUIRED_PATTERN_FIELDS=(name category smells_it_fixes test_invariants)
while IFS= read -r card; do
  rel="${card#"$ROOT"/}"
  for field in "${REQUIRED_PATTERN_FIELDS[@]}"; do
    if ! frontmatter_has "$card" "$field"; then
      fail "$rel" "missing frontmatter field: $field"
    fi
  done
done < <(find "$ROOT/patterns" -path "*/*/*.md" -not -name "README.md" -not -name "_schema.md")
# Only report pass if no failures in this section
[[ $FAIL -eq 0 ]] && pass "all pattern cards have required frontmatter"

printf "\n\033[1m[patterns/_index.json] Checking index integrity…\033[0m\n"
INDEX="$ROOT/patterns/_index.json"
if ! jq empty "$INDEX" 2>/dev/null; then
  fail "_index.json" "invalid JSON"
else
  pass "_index.json is valid JSON"
  # Check every pattern .md has an entry in by_category
  PREV_FAIL=$FAIL
  while IFS= read -r card; do
    slug="$(basename "$card" .md)"
    cat_dir="$(basename "$(dirname "$card")")"
    if ! jq -e ".by_category[\"$cat_dir\"] | index(\"$slug\")" "$INDEX" >/dev/null 2>&1; then
      fail "patterns/$cat_dir/$slug.md" "present on disk but missing from _index.json by_category.$cat_dir"
    fi
  done < <(find "$ROOT/patterns" -path "*/*/*.md" -not -name "README.md" -not -name "_schema.md")
  [[ $FAIL -eq $PREV_FAIL ]] && pass "all pattern files have matching _index.json entries"

  # Check every entry in by_category has a matching .md on disk
  PREV_FAIL=$FAIL
  for cat in $(jq -r '.by_category | keys[]' "$INDEX"); do
    for slug in $(jq -r ".by_category[\"$cat\"][]" "$INDEX"); do
      if [[ ! -f "$ROOT/patterns/$cat/$slug.md" ]]; then
        fail "_index.json" "by_category.$cat lists '$slug' but patterns/$cat/$slug.md does not exist"
      fi
    done
  done
  [[ $FAIL -eq $PREV_FAIL ]] && pass "all _index.json entries have matching files on disk"
fi

printf "\n\033[1m[agents] Checking agent specs…\033[0m\n"
REQUIRED_AGENT_FIELDS=(name description tools model)
PREV_FAIL=$FAIL
for agent in "$ROOT"/agents/*.md; do
  [[ -f "$agent" ]] || continue
  rel="${agent#"$ROOT"/}"
  for field in "${REQUIRED_AGENT_FIELDS[@]}"; do
    if ! frontmatter_has "$agent" "$field"; then
      fail "$rel" "missing frontmatter field: $field"
    fi
  done
done
[[ $FAIL -eq $PREV_FAIL ]] && pass "all agent specs have required frontmatter"

printf "\n\033[1m[skills] Checking SKILL.md files…\033[0m\n"
REQUIRED_SKILL_FIELDS=(name description)
PREV_FAIL=$FAIL
while IFS= read -r skill; do
  rel="${skill#"$ROOT"/}"
  for field in "${REQUIRED_SKILL_FIELDS[@]}"; do
    if ! frontmatter_has "$skill" "$field"; then
      fail "$rel" "missing frontmatter field: $field"
    fi
  done
done < <(find "$ROOT/skills" -name "SKILL.md")
[[ $FAIL -eq $PREV_FAIL ]] && pass "all SKILL.md files have required frontmatter"

printf "\n\033[1m[schemas] Checking JSON schemas…\033[0m\n"
SCHEMA="$ROOT/schemas/session-resume.schema.json"
if [[ ! -f "$SCHEMA" ]]; then
  fail "schemas/session-resume.schema.json" "file not found"
elif ! jq empty "$SCHEMA" 2>/dev/null; then
  fail "schemas/session-resume.schema.json" "invalid JSON"
else
  pass "session-resume.schema.json is valid JSON"
fi

printf "\n\033[1m[examples] Checking example files…\033[0m\n"
PREV_FAIL=$FAIL
while IFS= read -r ex; do
  rel="${ex#"$ROOT"/}"
  if [[ ! -s "$ex" ]]; then
    fail "$rel" "file is empty"
  fi
done < <(find "$ROOT/examples" -type f)
[[ $FAIL -eq $PREV_FAIL ]] && pass "all example files are non-empty"

printf "\n"
if [[ $FAIL -ne 0 ]]; then
  printf "\033[31mValidation failed.\033[0m\n\n"
  exit 1
else
  printf "\033[32mAll checks passed.\033[0m\n\n"
  exit 0
fi
