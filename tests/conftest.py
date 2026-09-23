import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS_PATH = REPO / "skills" / "agent-failure-analysis" / "scripts" / "trace_tools.py"
FIXTURES = REPO / "evaluation" / "fixtures"


def _load_tools():
    spec = importlib.util.spec_from_file_location("trace_tools", TOOLS_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["trace_tools"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def tools():
    return _load_tools()


@pytest.fixture
def tools_path():
    return TOOLS_PATH


MINIMAL_BUNDLE = {
    "schema_version": "afa-bundle/1",
    "run_id": "t-001",
    "task": {"description": "Print hello", "constraints": ["Do not write files"]},
    "success_criteria": {"status": "known", "criteria": ["stdout contains 'hello'"]},
    "tool_policy": {"status": "optional", "tools": ["bash"]},
    "events": [
        {"id": "e1", "kind": "user_message", "ts": "2026-01-01T00:00:00Z", "content": {"text": "Please print hello"}},
        {"id": "e2", "kind": "tool_call", "ts": "2026-01-01T00:00:01Z",
         "content": {"call_id": "c1", "tool": "bash", "args": {"cmd": "echo hello"}}},
        {"id": "e3", "kind": "tool_result", "ts": "2026-01-01T00:00:02Z",
         "content": {"call_id": "c1", "ok": True, "output": "hello\n"}},
        {"id": "e4", "kind": "assistant_message", "ts": "2026-01-01T00:00:03Z", "content": {"text": "Done: printed hello."}},
    ],
    "final_output": {"status": "available", "text": "Done: printed hello."},
    "evaluator": {"status": "available", "observations": [{"id": "o1", "text": "stdout was 'hello'", "verdict": "pass"}]},
    "provenance": {"source": "unit test", "synthetic": True},
}


@pytest.fixture
def bundle():
    return copy.deepcopy(MINIMAL_BUNDLE)


def write_bundle(path: Path, bundle: dict) -> bytes:
    data = (json.dumps(bundle, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    path.write_bytes(data)
    return data


def minimal_report(bundle: dict, sha256: str) -> dict:
    return {
        "report_version": "afa-report/1",
        "skill_version": "0.1.0",
        "run_id": bundle["run_id"],
        "source": {"snapshot": "snapshot.json", "sha256": sha256},
        "task": {
            "description_ref": {"pointer": "/task/description", "excerpt": "Print hello"},
            "criteria_status": "known",
            "tool_policy_status": "optional",
            "evidence_coverage": {"events_total": 4, "events_reviewed": 4, "note": "All events reviewed."},
        },
        "outcome": {
            "status": "success",
            "basis": "evaluator_observation",
            "statement": "The evaluator observed the expected stdout.",
            "references": [{"pointer": "/evaluator/observations/0/verdict", "excerpt": "pass"},
                           {"event_id": "e3", "pointer": "/content/output", "excerpt": "hello"}],
        },
        "key_events": [{"event_id": "e2", "summary": "bash echo hello", "references": []}],
        "findings": [],
        "earliest_divergence": {"status": "unknown", "statement": "No divergence: the run succeeded.", "references": []},
        "hypotheses": [],
        "missing_information": [],
        "remediation": {"status": "none"},
        "regression_test": {"status": "none"},
    }
