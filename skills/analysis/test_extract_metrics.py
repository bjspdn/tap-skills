#!/usr/bin/env python3
"""
test_extract_metrics.py — unittest suite for extract_metrics.py

Run:
    python3 test_extract_metrics.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent / "extract_metrics.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_script(logs_dir: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), logs_dir],
        capture_output=True,
        text=True,
    )


def write_jsonl(path: Path, lines: list) -> None:
    with path.open("w") as fh:
        for obj in lines:
            fh.write(json.dumps(obj) + "\n")


def assistant_msg(
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read: int = 0,
    cache_create: int = 0,
    content: list = None,
) -> dict:
    if content is None:
        content = []
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": content,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cache_read_input_tokens": cache_read,
                "cache_creation_input_tokens": cache_create,
            },
        },
    }


def tool_use_block(name: str = "Read") -> dict:
    return {"type": "tool_use", "name": name, "id": "toolu_abc", "input": {}}


def write_checkpoint(feature_dir: Path, completed: list, failed=None, parent_sha: str = "abc123") -> None:
    cp = {
        "completedTasks": [{"taskId": t} for t in completed],
        "failedTask": failed,
        "parentSha": parent_sha,
    }
    (feature_dir / "checkpoint.json").write_text(json.dumps(cp))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMissingDirectory(unittest.TestCase):
    def test_missing_dir_emits_empty_features(self):
        result = run_script("/tmp/__nonexistent_tap_logs__")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data, {"features": {}})
        self.assertIn("No logs found", result.stderr)


class TestEmptyDirectory(unittest.TestCase):
    def test_empty_dir_emits_empty_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(tmp)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertEqual(data, {"features": {}})


class TestSingleFeatureTokenSums(unittest.TestCase):
    def test_token_sums_are_correct(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "my-feature"
            feat.mkdir()
            # In the Claude API, input_tokens is the non-cached (raw) portion;
            # cache_read and cache_create are additive on top.
            write_jsonl(feat / "code-writer-01-foo.jsonl", [
                assistant_msg(input_tokens=100, output_tokens=20, cache_read=0,  cache_create=50),
                assistant_msg(input_tokens=200, output_tokens=30, cache_read=80, cache_create=0),
            ])
            result = run_script(tmp)
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            totals = data["features"]["my-feature"]["totals"]
            # total prompt tokens = raw(300) + cache_read(80) + cache_create(50) = 430
            self.assertEqual(totals["input_tokens"],  430)
            self.assertEqual(totals["output_tokens"], 50)
            self.assertEqual(totals["cache_read_tokens"],   80)
            self.assertEqual(totals["cache_create_tokens"], 50)
            # raw_input = sum of input_tokens fields = 300
            self.assertEqual(totals["raw_input_tokens"], 300)


class TestToolCallCounting(unittest.TestCase):
    def test_tool_calls_counted_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            write_jsonl(feat / "code-writer-01-x.jsonl", [
                # 2 tool_use blocks → 2 calls, 1 turn
                assistant_msg(content=[tool_use_block("Read"), tool_use_block("Edit")]),
                # 1 tool_use block → 1 call, 1 turn
                assistant_msg(content=[tool_use_block("Bash")]),
                # thinking block only, no tool_use — 1 turn, 0 calls
                assistant_msg(content=[{"type": "thinking", "thinking": "hmm"}]),
                # empty content → not counted as a turn
                assistant_msg(content=[]),
            ])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            totals = data["features"]["feat"]["totals"]
            self.assertEqual(totals["tool_calls"], 3)
            self.assertEqual(totals["turns"], 3)


class TestRoleInference(unittest.TestCase):
    def test_by_role_breakdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()

            # test-writer
            write_jsonl(feat / "test-writer-01-foo.jsonl", [
                assistant_msg(output_tokens=10, content=[tool_use_block()]),
            ])
            # code-writer
            write_jsonl(feat / "code-writer-01-foo.jsonl", [
                assistant_msg(output_tokens=20, content=[tool_use_block(), tool_use_block()]),
            ])
            # reviewer (dot-separated stem)
            write_jsonl(feat / "reviewer.jsonl", [
                assistant_msg(output_tokens=5),
            ])
            # debugger
            write_jsonl(feat / "debugger-reviewer.jsonl", [
                assistant_msg(output_tokens=7, content=[tool_use_block()]),
            ])

            result = run_script(tmp)
            data = json.loads(result.stdout)
            by_role = data["features"]["feat"]["by_role"]

            self.assertIsNotNone(by_role["test-writer"])
            self.assertEqual(by_role["test-writer"]["output_tokens"], 10)
            self.assertEqual(by_role["test-writer"]["tool_calls"], 1)

            self.assertIsNotNone(by_role["code-writer"])
            self.assertEqual(by_role["code-writer"]["output_tokens"], 20)
            self.assertEqual(by_role["code-writer"]["tool_calls"], 2)

            self.assertIsNotNone(by_role["reviewer"])
            self.assertEqual(by_role["reviewer"]["output_tokens"], 5)

            self.assertIsNotNone(by_role["debugger"])
            self.assertEqual(by_role["debugger"]["output_tokens"], 7)

            # refactorer never appeared
            self.assertIsNone(by_role["refactorer"])


class TestCheckpointReading(unittest.TestCase):
    def test_checkpoint_fields_populated(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            write_checkpoint(feat, completed=["task-01", "task-02", "task-03"], parent_sha="deadbeef")
            write_jsonl(feat / "code-writer-01-x.jsonl", [assistant_msg()])

            result = run_script(tmp)
            data = json.loads(result.stdout)
            f = data["features"]["feat"]
            self.assertEqual(f["tasks_completed"], 3)
            self.assertEqual(f["tasks_failed"], 0)
            self.assertEqual(f["parent_sha"], "deadbeef")


class TestMissingCheckpoint(unittest.TestCase):
    def test_null_fields_when_no_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            write_jsonl(feat / "code-writer-01-x.jsonl", [assistant_msg()])

            result = run_script(tmp)
            data = json.loads(result.stdout)
            f = data["features"]["feat"]
            self.assertIsNone(f["tasks_completed"])
            self.assertIsNone(f["tasks_failed"])
            self.assertIsNone(f["parent_sha"])


class TestMalformedJsonlLine(unittest.TestCase):
    def test_bad_line_skipped_valid_lines_processed(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            jf = feat / "code-writer-01-x.jsonl"
            with jf.open("w") as fh:
                fh.write(json.dumps(assistant_msg(output_tokens=42, content=[tool_use_block()])) + "\n")
                fh.write("THIS IS NOT JSON }{{\n")
                fh.write(json.dumps(assistant_msg(output_tokens=8)) + "\n")

            result = run_script(tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("malformed", result.stderr.lower())

            data = json.loads(result.stdout)
            totals = data["features"]["feat"]["totals"]
            self.assertEqual(totals["output_tokens"], 50)   # 42 + 8
            self.assertEqual(totals["tool_calls"], 1)


class TestCostCalculation(unittest.TestCase):
    def test_cost_matches_manual_calculation(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            # In the Claude API:
            #   input_tokens = 600_000   (raw, non-cached — billed at $3.00/MTok)
            #   cache_create = 200_000   (billed at $3.75/MTok)
            #   cache_read   = 400_000   (billed at $0.30/MTok)
            #   output_tokens= 100_000   (billed at $15.00/MTok)
            write_jsonl(feat / "code-writer-01-x.jsonl", [
                assistant_msg(
                    input_tokens=600_000,
                    output_tokens=100_000,
                    cache_read=400_000,
                    cache_create=200_000,
                ),
            ])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            cost = data["features"]["feat"]["totals"]["estimated_cost_usd"]

            expected = (
                600_000  * 3.00  / 1_000_000   # raw input
                + 200_000 * 3.75  / 1_000_000   # cache create
                + 400_000 * 0.30  / 1_000_000   # cache read
                + 100_000 * 15.00 / 1_000_000   # output
            )
            self.assertAlmostEqual(cost, expected, places=4)


class TestCacheHitRate(unittest.TestCase):
    def test_cache_hit_rate_calculation(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            # raw input_tokens=250, cache_read=750, cache_create=0
            # total_prompt = 250 + 750 = 1000
            # cache_hit_rate = 750 / 1000 = 0.75
            write_jsonl(feat / "code-writer-01-x.jsonl", [
                assistant_msg(input_tokens=250, cache_read=750),
            ])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            rate = data["features"]["feat"]["cache_hit_rate"]
            self.assertAlmostEqual(rate, 0.75, places=4)

    def test_cache_hit_rate_zero_when_no_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            write_jsonl(feat / "code-writer-01-x.jsonl", [assistant_msg()])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            self.assertEqual(data["features"]["feat"]["cache_hit_rate"], 0.0)


class TestDebuggerAndReviewerFlags(unittest.TestCase):
    def test_debugger_invoked_true_when_debugger_file_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            write_jsonl(feat / "debugger-01-oops.jsonl", [assistant_msg()])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            self.assertTrue(data["features"]["feat"]["debugger_invoked"])
            self.assertFalse(data["features"]["feat"]["reviewer_ran"])

    def test_reviewer_ran_true_when_reviewer_file_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            write_jsonl(feat / "reviewer.jsonl", [assistant_msg()])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            self.assertTrue(data["features"]["feat"]["reviewer_ran"])
            self.assertFalse(data["features"]["feat"]["debugger_invoked"])


class TestMultipleFeatures(unittest.TestCase):
    def test_each_feature_is_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            for slug, tokens in [("alpha", 100), ("beta", 200)]:
                fd = Path(tmp) / slug
                fd.mkdir()
                write_jsonl(fd / "code-writer-01-x.jsonl", [
                    assistant_msg(output_tokens=tokens),
                ])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            self.assertIn("alpha", data["features"])
            self.assertIn("beta",  data["features"])
            self.assertEqual(data["features"]["alpha"]["totals"]["output_tokens"], 100)
            self.assertEqual(data["features"]["beta"]["totals"]["output_tokens"],  200)


class TestNonJsonlFilesIgnored(unittest.TestCase):
    def test_stdin_md_and_other_files_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            feat = Path(tmp) / "feat"
            feat.mkdir()
            # .stdin.md files should be ignored
            (feat / "code-writer-01-x.stdin.md").write_text("some prompt text")
            write_jsonl(feat / "code-writer-01-x.jsonl", [
                assistant_msg(output_tokens=99),
            ])
            result = run_script(tmp)
            data = json.loads(result.stdout)
            self.assertEqual(data["features"]["feat"]["totals"]["output_tokens"], 99)


if __name__ == "__main__":
    unittest.main()
