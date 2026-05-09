#!/usr/bin/env bash
set -euo pipefail

# bump-version.sh — version coordinator for the tap plugin
#
# Usage:
#   bump-version.sh <X.Y.Z>   Bump files, roll changelog, commit, tag, push & GitHub Release
#   bump-version.sh --check    Report current versions across files, detect drift
#   bump-version.sh --audit    Run check + grep repo for stale/undeclared version strings
#
# Requires: jq, git, gh (optional — for GitHub Releases)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG="$ROOT_DIR/.version-bump.json"
CHANGELOG="$ROOT_DIR/CHANGELOG.md"

# ─── Colors ───────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# ─── Helpers ──────────────────────────────────────────────────────────────────

die()  { echo -e "${RED}error:${RESET} $*" >&2; exit 1; }
info() { echo -e "${CYAN}→${RESET} $*"; }
ok()   { echo -e "${GREEN}✓${RESET} $*"; }
warn() { echo -e "${YELLOW}⚠${RESET} $*"; }

check_deps() {
  command -v jq  >/dev/null 2>&1 || die "jq is required but not installed"
  command -v git >/dev/null 2>&1 || die "git is required but not installed"
  [[ -f "$CONFIG" ]] || die ".version-bump.json not found at $ROOT_DIR"
}

# Convert dot-path like "plugins.0.version" → jq path ".plugins[0].version"
dot_to_jq() {
  local path=".$1"
  # Replace .N (digit segments) with [N]
  echo "$path" | sed -E 's/\.([0-9]+)/[\1]/g'
}

# Read current version from a JSON file at a given field path
read_version() {
  local file="$ROOT_DIR/$1"
  local jq_path
  jq_path=$(dot_to_jq "$2")
  [[ -f "$file" ]] || die "file not found: $1"
  jq -r "$jq_path" "$file"
}

# Write version to a JSON file at a given field path
write_version() {
  local file="$ROOT_DIR/$1"
  local jq_path new_version="$3"
  jq_path=$(dot_to_jq "$2")
  local tmp
  tmp=$(mktemp)
  jq "$jq_path = \"$new_version\"" "$file" > "$tmp" && mv "$tmp" "$file"
}

# Validate semver format
validate_semver() {
  [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || die "invalid semver: $1 (expected X.Y.Z)"
}

# Get file count from config
file_count() {
  jq '.files | length' "$CONFIG"
}

# Get file path at index
file_path_at() {
  jq -r ".files[$1].path" "$CONFIG"
}

# Get field at index
file_field_at() {
  jq -r ".files[$1].field" "$CONFIG"
}

# ─── --check ──────────────────────────────────────────────────────────────────

cmd_check() {
  info "checking versions across declared files..."
  echo

  local count drift=0 first_version=""
  count=$(file_count)

  for ((i = 0; i < count; i++)); do
    local path field version
    path=$(file_path_at "$i")
    field=$(file_field_at "$i")
    version=$(read_version "$path" "$field")

    if [[ -z "$first_version" ]]; then
      first_version="$version"
    fi

    if [[ "$version" != "$first_version" && -n "$first_version" ]]; then
      warn "$path ($field) = ${BOLD}$version${RESET}  ← drift!"
      drift=1
    else
      ok "$path ($field) = ${BOLD}$version${RESET}"
    fi
  done

  echo
  if [[ $drift -eq 1 ]]; then
    die "version drift detected — files are out of sync"
  else
    ok "all files at ${BOLD}v$first_version${RESET}"
  fi

  # Check git tag alignment
  if git tag -l "v$first_version" | grep -q "v$first_version"; then
    ok "git tag v$first_version exists"
  else
    warn "git tag v$first_version does not exist"
  fi
}

# ─── --audit ──────────────────────────────────────────────────────────────────

cmd_audit() {
  cmd_check
  echo

  local count first_version=""
  count=$(file_count)

  # Get current version from first file
  local path field
  path=$(file_path_at 0)
  field=$(file_field_at 0)
  first_version=$(read_version "$path" "$field")

  info "auditing repo for undeclared references to ${BOLD}$first_version${RESET}..."

  # Build exclude args from config
  local -a exclude_args=()
  local excludes
  excludes=$(jq -r '.audit.exclude[]' "$CONFIG" 2>/dev/null || true)
  while IFS= read -r ex; do
    [[ -n "$ex" ]] && exclude_args+=(--exclude-dir="$ex" --exclude="$ex")
  done <<< "$excludes"

  # Also exclude declared files (they're supposed to have the version)
  for ((i = 0; i < count; i++)); do
    local p
    p=$(file_path_at "$i")
    exclude_args+=(--exclude="$(basename "$p")")
  done

  # Escape dots for regex, use word boundaries to avoid partial matches like <0.0-1.0>
  local escaped_version
  escaped_version=$(echo "$first_version" | sed 's/\./\\./g')
  local hits
  hits=$(cd "$ROOT_DIR" && grep -rnP "(?<![.\d-])${escaped_version}(?![.\d-])" "${exclude_args[@]}" . 2>/dev/null || true)

  if [[ -n "$hits" ]]; then
    warn "found undeclared version references:"
    echo "$hits" | while IFS= read -r line; do
      echo "  $line"
    done
  else
    ok "no undeclared version references found"
  fi
}

# ─── bump ─────────────────────────────────────────────────────────────────────

cmd_bump() {
  local new_version="$1"
  validate_semver "$new_version"

  # Get current version
  local current_version
  current_version=$(read_version "$(file_path_at 0)" "$(file_field_at 0)")

  if [[ "$current_version" == "$new_version" ]]; then
    die "version is already $new_version"
  fi

  # Check git tag doesn't already exist
  if git tag -l "v$new_version" | grep -q "v$new_version"; then
    die "git tag v$new_version already exists"
  fi

  # Guard: check [Unreleased] section is not empty
  info "checking changelog..."
  local unreleased_content
  unreleased_content=$(sed -n '/^## \[Unreleased\]/,/^## \[/{ /^## \[/d; p; }' "$CHANGELOG" | sed '/^$/d')
  if [[ -z "$unreleased_content" ]]; then
    die "[Unreleased] section in CHANGELOG.md is empty — document changes before releasing"
  fi
  ok "changelog has unreleased content"

  # Check working tree is clean
  if [[ -n "$(git -C "$ROOT_DIR" status --porcelain)" ]]; then
    die "working tree is dirty — commit or stash changes first"
  fi

  # Show what we're doing
  echo
  echo -e "${BOLD}Bumping:${RESET} v$current_version → v$new_version"
  echo

  # 1. Update version in all declared files
  local count
  count=$(file_count)
  for ((i = 0; i < count; i++)); do
    local path field
    path=$(file_path_at "$i")
    field=$(file_field_at "$i")
    write_version "$path" "$field" "$new_version"
    ok "updated $path"
  done

  # 2. Roll changelog: [Unreleased] → [X.Y.Z] - YYYY-MM-DD
  local today
  today=$(date +%Y-%m-%d)
  local new_header="## [$new_version] - $today"

  # Replace the [Unreleased] header, keep content, add fresh [Unreleased] above
  sed -i "s/^## \[Unreleased\]$/## [Unreleased]\n\n${new_header}/" "$CHANGELOG"
  ok "rolled changelog → [$new_version] - $today"

  # 3. Git commit
  local files_to_stage=("$CHANGELOG")
  for ((i = 0; i < count; i++)); do
    files_to_stage+=("$(file_path_at "$i")")
  done

  (cd "$ROOT_DIR" && git add "${files_to_stage[@]}")
  (cd "$ROOT_DIR" && git commit -m "$(cat <<EOF
release: v$new_version

Co-Authored-By: Claude <claude@anthropic.com>
EOF
  )")
  ok "committed release"

  # 4. Git tag
  (cd "$ROOT_DIR" && git tag -a "v$new_version" -m "Release v$new_version")
  ok "tagged v$new_version"

  # 5. Push commits + tags
  local branch
  branch=$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)
  (cd "$ROOT_DIR" && git push origin "$branch" --tags)
  ok "pushed to origin/$branch with tags"

  # 6. Create GitHub Release with changelog content
  if command -v gh >/dev/null 2>&1; then
    # Extract release notes for this version from changelog
    local release_notes
    release_notes=$(sed -n "/^## \[$new_version\]/,/^## \[/{/^## \[/d; p;}" "$CHANGELOG")

    (cd "$ROOT_DIR" && gh release create "v$new_version" \
      --title "v$new_version" \
      --notes "$release_notes")
    ok "created GitHub Release v$new_version"
  else
    warn "gh CLI not found — skipping GitHub Release creation"
    echo "  Create manually: gh release create v$new_version"
  fi

  echo
  echo -e "${GREEN}${BOLD}Released v$new_version${RESET}"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

check_deps

case "${1:-}" in
  --check)
    cmd_check
    ;;
  --audit)
    cmd_audit
    ;;
  --help|-h|"")
    echo "Usage: bump-version.sh <X.Y.Z> | --check | --audit"
    echo
    echo "  <X.Y.Z>   Bump version, roll changelog, commit, tag, push & release"
    echo "  --check    Report current versions, detect drift"
    echo "  --audit    Check + grep for stale version strings"
    ;;
  *)
    cmd_bump "$1"
    ;;
esac
