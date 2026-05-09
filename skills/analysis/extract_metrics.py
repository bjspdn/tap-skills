#!/usr/bin/env python3
"""
extract_metrics.py — reads TDD run logs from a .tap/logs/ directory and
emits structured JSON to stdout.

Usage:
    python3 extract_metrics.py <logs-dir>
"""

import json
import os
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Pricing constants (Sonnet 3.x/4.x blended rates, per million tokens)
# ---------------------------------------------------------------------------
PRICE_RAW_INPUT_PER_MTOK    = 3.00
PRICE_CACHE_CREATE_PER_MTOK = 3.75
PRICE_CACHE_READ_PER_MTOK   = 0.30
PRICE_OUTPUT_PER_MTOK       = 15.00


# ---------------------------------------------------------------------------
# Role inference
# ---------------------------------------------------------------------------
_ROLE_PREFIXES = [
    ("test-writer", "test-writer"),
    ("code-writer", "code-writer"),
    ("refactorer",  "refactorer"),
    ("reviewer",    "reviewer"),
    ("debugger",    "debugger"),
]

def _infer_role(filename: str) -> str:
    stem = Path(filename).stem.lower()
    # First pass: strict startswith (highest priority)
    for prefix, role in _ROLE_PREFIXES:
        if stem.startswith(prefix):
            return role
    # Second pass: substring match for "reviewer" stems like "reviewer.jsonl"
    # that didn't start with a known prefix (edge case: bare "reviewer" stem
    # already caught above, but handles e.g. "01-reviewer-notes")
    if "reviewer" in stem:
        return "reviewer"
    return "other"


# ---------------------------------------------------------------------------
# Per-role accumulator
# ---------------------------------------------------------------------------
def _empty_role_bucket() -> dict:
    return {
        "input_tokens":        0,
        "output_tokens":       0,
        "cache_read_tokens":   0,
        "cache_create_tokens": 0,
        "raw_input_tokens":    0,
        "tool_calls":          0,
        "turns":               0,
    }


# ---------------------------------------------------------------------------
# Process a single JSONL file
# ---------------------------------------------------------------------------
def _process_jsonl(path: Path, role_buckets: dict) -> None:
    role = _infer_role(path.name)
    if role not in role_buckets:
        role_buckets[role] = _empty_role_bucket()

    bucket = role_buckets[role]

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                print(
                    f"WARNING: {path}:{lineno}: malformed JSON ({exc}), skipping",
                    file=sys.stderr,
                )
                continue

            if not isinstance(obj, dict):
                continue

            if obj.get("type") != "assistant":
                continue

            message = obj.get("message")
            if not isinstance(message, dict):
                continue

            # --- token accounting ---
            usage = message.get("usage")
            if isinstance(usage, dict):
                raw   = usage.get("input_tokens", 0) or 0
                cr    = usage.get("cache_read_input_tokens", 0) or 0
                cc    = usage.get("cache_creation_input_tokens", 0) or 0
                bucket["raw_input_tokens"]    += raw
                bucket["cache_read_tokens"]   += cr
                bucket["cache_create_tokens"] += cc
                bucket["input_tokens"]        += raw + cr + cc
                bucket["output_tokens"]       += usage.get("output_tokens", 0) or 0

            # --- tool call + turn counting ---
            content = message.get("content")
            if isinstance(content, list) and content:
                bucket["turns"] += 1
                bucket["tool_calls"] += sum(
                    1 for item in content
                    if isinstance(item, dict) and item.get("type") == "tool_use"
                )


# ---------------------------------------------------------------------------
# Read checkpoint.json for a feature
# ---------------------------------------------------------------------------
def _read_checkpoint(feature_dir: Path) -> tuple:
    """Returns (tasks_completed, tasks_failed, parent_sha) — all None on missing."""
    cp_path = feature_dir / "checkpoint.json"
    if not cp_path.exists():
        return None, None, None
    try:
        with cp_path.open("r", encoding="utf-8") as fh:
            cp = json.load(fh)
        completed = cp.get("completedTasks")
        tasks_completed = len(completed) if isinstance(completed, list) else None
        failed = cp.get("failedTask")
        tasks_failed = 0 if failed is None else 1
        parent_sha = cp.get("parentSha")
        return tasks_completed, tasks_failed, parent_sha
    except Exception as exc:  # noqa: BLE001
        print(
            f"WARNING: could not read checkpoint at {cp_path}: {exc}",
            file=sys.stderr,
        )
        return None, None, None


# ---------------------------------------------------------------------------
# Process one feature directory
# ---------------------------------------------------------------------------
def _process_feature(feature_dir: Path) -> dict:
    role_buckets: dict[str, dict] = {}

    jsonl_files = sorted(feature_dir.glob("*.jsonl"))
    for jf in jsonl_files:
        try:
            _process_jsonl(jf, role_buckets)
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARNING: error reading {jf}: {exc}, skipping file",
                file=sys.stderr,
            )

    # --- aggregate totals across all roles ---
    total_input   = sum(b["input_tokens"]        for b in role_buckets.values())
    total_output  = sum(b["output_tokens"]       for b in role_buckets.values())
    total_calls   = sum(b["tool_calls"]          for b in role_buckets.values())
    total_turns   = sum(b["turns"]               for b in role_buckets.values())
    raw_input     = sum(b["raw_input_tokens"]    for b in role_buckets.values())
    cache_read    = sum(b["cache_read_tokens"]   for b in role_buckets.values())
    cache_create  = sum(b["cache_create_tokens"] for b in role_buckets.values())

    # estimated cost — each bucket is billed at its own rate
    cost = (
        raw_input    * PRICE_RAW_INPUT_PER_MTOK    / 1_000_000
        + cache_create * PRICE_CACHE_CREATE_PER_MTOK / 1_000_000
        + cache_read   * PRICE_CACHE_READ_PER_MTOK   / 1_000_000
        + total_output * PRICE_OUTPUT_PER_MTOK        / 1_000_000
    )

    # cache_hit_rate = cache_read / total_prompt_tokens  (avoid div-by-zero)
    cache_hit_rate = (cache_read / total_input) if total_input > 0 else 0.0

    # checkpoint
    tasks_completed, tasks_failed, parent_sha = _read_checkpoint(feature_dir)

    # build by_role — known roles always present, others only if seen
    known_roles = ["test-writer", "code-writer", "refactorer", "reviewer", "debugger", "other"]
    export_keys = ("input_tokens", "output_tokens", "tool_calls", "turns")
    by_role: dict = {}
    for role in known_roles:
        b = role_buckets.get(role)
        by_role[role] = {k: b[k] for k in export_keys} if b else None

    for role, bucket in role_buckets.items():
        if role not in by_role:
            by_role[role] = {k: bucket[k] for k in export_keys}

    return {
        "tasks_completed": tasks_completed,
        "tasks_failed":    tasks_failed,
        "parent_sha":      parent_sha,
        "totals": {
            "input_tokens":       total_input,
            "output_tokens":      total_output,
            "cache_read_tokens":  cache_read,
            "cache_create_tokens": cache_create,
            "raw_input_tokens":   raw_input,
            "tool_calls":         total_calls,
            "turns":              total_turns,
            "estimated_cost_usd": round(cost, 6),
        },
        "by_role": by_role,
        "cache_hit_rate":     round(cache_hit_rate, 6),
        "debugger_invoked":   "debugger" in role_buckets,
        "reviewer_ran":       "reviewer" in role_buckets,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: extract_metrics.py <logs-dir>", file=sys.stderr)
        sys.exit(1)

    logs_dir = Path(sys.argv[1])

    if not logs_dir.exists() or not logs_dir.is_dir():
        print(
            f"No logs found at {logs_dir}. Run 'tap run' first.",
            file=sys.stderr,
        )
        print(json.dumps({"features": {}}))
        sys.exit(0)

    feature_dirs = sorted(
        p for p in logs_dir.iterdir() if p.is_dir()
    )

    if not feature_dirs:
        print(json.dumps({"features": {}}))
        sys.exit(0)

    features: dict = {}
    for fd in feature_dirs:
        try:
            features[fd.name] = _process_feature(fd)
        except Exception as exc:  # noqa: BLE001
            print(
                f"WARNING: failed to process feature '{fd.name}': {exc}, skipping",
                file=sys.stderr,
            )

    print(json.dumps({"features": features}, indent=2))


if __name__ == "__main__":
    main()
