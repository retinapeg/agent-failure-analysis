import json
import subprocess
import sys

import pytest

from conftest import write_bundle


def test_valid_bundle_has_no_errors(tools, bundle):
    errors, warnings = tools.validate_bundle(bundle)
    assert errors == []
    assert warnings == []


def test_non_object_rejected(tools):
    errors, _ = tools.validate_bundle([1, 2])
    assert errors == ["bundle must be a JSON object"]


def test_missing_required_fields(tools, bundle):
    del bundle["events"]
    del bundle["provenance"]
    errors, _ = tools.validate_bundle(bundle)
    assert "missing required top-level field: events" in errors
    assert "missing required top-level field: provenance" in errors


def test_wrong_schema_version(tools, bundle):
    bundle["schema_version"] = "afa-bundle/9"
    errors, _ = tools.validate_bundle(bundle)
    assert any("schema_version" in e for e in errors)


def test_duplicate_event_ids(tools, bundle):
    bundle["events"][3]["id"] = "e2"
    errors, _ = tools.validate_bundle(bundle)
    assert any("duplicate event id 'e2'" in e for e in errors)


def test_duplicate_call_ids(tools, bundle):
    bundle["events"].append({"id": "e5", "kind": "tool_call", "content": {"call_id": "c1", "tool": "bash", "args": {}}})
    errors, _ = tools.validate_bundle(bundle)
    assert any("duplicate call_id 'c1'" in e for e in errors)


def test_result_without_call(tools, bundle):
    bundle["events"].append({"id": "e5", "kind": "tool_result", "content": {"call_id": "zzz", "ok": True, "output": ""}})
    errors, _ = tools.validate_bundle(bundle)
    assert any("no earlier tool_call" in e for e in errors)


def test_unknown_kind_is_error(tools, bundle):
    bundle["events"][0]["kind"] = "thought"
    errors, _ = tools.validate_bundle(bundle)
    assert any("unknown kind 'thought'" in e for e in errors)


def test_missing_content_field(tools, bundle):
    del bundle["events"][1]["content"]["args"]
    errors, _ = tools.validate_bundle(bundle)
    assert any("tool_call.content.args must be dict" in e for e in errors)


def test_bool_is_not_int_for_line_number(tools, bundle):
    bundle["events"] = [{"id": "L1", "kind": "log_line", "content": {"line_number": True, "text": "x"}}]
    errors, _ = tools.validate_bundle(bundle)
    assert any("line_number must be int" in e for e in errors)


def test_unknown_status_values(tools, bundle):
    bundle["tool_policy"]["status"] = "mandatory"
    bundle["evaluator"]["observations"][0]["verdict"] = "great"
    errors, _ = tools.validate_bundle(bundle)
    assert any("tool_policy.status" in e for e in errors)
    assert any("verdict" in e for e in errors)


def test_known_criteria_need_list(tools, bundle):
    bundle["success_criteria"] = {"status": "known", "criteria": []}
    errors, _ = tools.validate_bundle(bundle)
    assert any("criteria must be a non-empty array" in e for e in errors)


def test_warnings_for_unknowns_and_unpaired(tools, bundle):
    bundle["success_criteria"] = {"status": "unknown"}
    bundle["tool_policy"] = {"status": "unknown"}
    bundle["final_output"] = {"status": "unavailable"}
    bundle["evaluator"] = {"status": "unavailable"}
    bundle["events"].pop(2)  # remove the tool_result
    bundle["events"].append({"id": "e9", "kind": "error", "content": {"message": "boom"}})  # no ts
    bundle["extra_field"] = 1
    errors, warnings = tools.validate_bundle(bundle)
    assert errors == []
    joined = "\n".join(warnings)
    for needle in ("success_criteria unknown", "tool_policy unknown", "final_output unavailable",
                   "evaluator unavailable", "has no tool_result", "have no ts", "unknown top-level field"):
        assert needle in joined


def test_backwards_timestamp_warns(tools, bundle):
    bundle["events"][3]["ts"] = "2025-01-01T00:00:00Z"
    errors, warnings = tools.validate_bundle(bundle)
    assert errors == []
    assert any("earlier than the previous" in w for w in warnings)


def test_bad_timestamp_is_error(tools, bundle):
    bundle["events"][3]["ts"] = "yesterday"
    errors, _ = tools.validate_bundle(bundle)
    assert any("ts is not ISO 8601" in e for e in errors)


def test_event_limit(tools, bundle):
    errors, _ = tools.validate_bundle(bundle, max_events=3)
    assert any("over the limit of 3" in e for e in errors)


def test_unicode_round_trip(tools, bundle):
    bundle["events"][0]["content"]["text"] = "héllo — 你好 🎉 \u0000"
    errors, _ = tools.validate_bundle(bundle)
    assert errors == []


# ---- CLI

def run(tools_path, *args, cwd=None):
    return subprocess.run([sys.executable, str(tools_path), *args], capture_output=True, text=True, cwd=cwd)


def test_cli_validate_ok(tools_path, tmp_path, bundle):
    p = tmp_path / "b.json"
    write_bundle(p, bundle)
    r = run(tools_path, "validate", str(p))
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["ok"] is True and out["event_count"] == 4 and len(out["sha256"]) == 64


def test_cli_validate_malformed_json(tools_path, tmp_path):
    p = tmp_path / "b.json"
    p.write_text('{"schema_version": "afa-bundle/1", ', encoding="utf-8")
    r = run(tools_path, "validate", str(p))
    assert r.returncode == 2
    assert "not valid JSON" in r.stderr


def test_cli_validate_not_utf8(tools_path, tmp_path):
    p = tmp_path / "b.json"
    p.write_bytes(b"\xff\xfe{}")
    r = run(tools_path, "validate", str(p))
    assert r.returncode == 2
    assert "not valid UTF-8" in r.stderr


def test_cli_validate_errors_exit_1(tools_path, tmp_path, bundle):
    bundle["events"][0]["id"] = "e2"
    p = tmp_path / "b.json"
    write_bundle(p, bundle)
    r = run(tools_path, "validate", str(p))
    assert r.returncode == 1
    assert json.loads(r.stdout)["ok"] is False


def test_cli_over_limit_rejected_not_truncated(tools_path, tmp_path, bundle):
    p = tmp_path / "b.json"
    write_bundle(p, bundle)
    r = run(tools_path, "--max-bytes", "10", "validate", str(p))
    assert r.returncode == 2
    assert "over the limit" in r.stderr and "silent subset" in r.stderr


def test_cli_missing_file(tools_path, tmp_path):
    r = run(tools_path, "validate", str(tmp_path / "nope.json"))
    assert r.returncode == 2
