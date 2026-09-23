import copy
import hashlib
import json
import subprocess
import sys

from conftest import minimal_report, write_bundle


def sha(bundle):
    return hashlib.sha256((json.dumps(bundle, indent=2, ensure_ascii=False) + "\n").encode()).hexdigest()


def check(tools, bundle, report, evidence=None):
    return tools.check_report(report, bundle, sha(bundle), evidence)


def test_minimal_report_passes(tools, bundle):
    errors, warnings = check(tools, bundle, minimal_report(bundle, sha(bundle)))
    assert errors == [] and warnings == []


def test_wrong_hash_rejected(tools, bundle):
    rep = minimal_report(bundle, "0" * 64)
    errors, _ = check(tools, bundle, rep)
    assert any("sha256 does not match" in e for e in errors)


def test_wrong_run_id_rejected(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["run_id"] = "other"
    errors, _ = check(tools, bundle, rep)
    assert any("run_id" in e for e in errors)


def test_invalid_event_reference(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"]["references"].append({"event_id": "e99"})
    errors, _ = check(tools, bundle, rep)
    assert any("event_id 'e99' does not exist" in e for e in errors)


def test_invalid_pointer(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"]["references"].append({"event_id": "e3", "pointer": "/content/nope"})
    errors, _ = check(tools, bundle, rep)
    assert any("does not resolve" in e for e in errors)


def test_fabricated_excerpt_rejected(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"]["references"][1]["excerpt"] = "goodbye"
    errors, _ = check(tools, bundle, rep)
    assert any("excerpt not found" in e and "'goodbye'" in e for e in errors)


def test_excerpt_must_be_exact_including_unicode(tools, bundle):
    bundle["events"][3]["content"]["text"] = "Fertig — 完了 ✓"
    rep = minimal_report(bundle, sha(bundle))
    rep["key_events"][0]["references"] = [{"event_id": "e4", "pointer": "/content/text", "excerpt": "完了 ✓"}]
    errors, _ = check(tools, bundle, rep)
    assert errors == []
    rep["key_events"][0]["references"] = [{"event_id": "e4", "pointer": "/content/text", "excerpt": "完了 ✗"}]
    errors, _ = check(tools, bundle, rep)
    assert any("excerpt not found" in e for e in errors)


def test_excerpt_against_non_string_uses_canonical_json(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["key_events"][0]["references"] = [{"event_id": "e2", "pointer": "/content/args", "excerpt": '{"cmd":"echo hello"}'}]
    errors, _ = check(tools, bundle, rep)
    assert errors == []


def test_pointer_escaping(tools, bundle):
    bundle["events"][1]["content"]["args"] = {"a/b": "v", "c~d": "w"}
    rep = minimal_report(bundle, sha(bundle))
    rep["key_events"][0]["references"] = [{"event_id": "e2", "pointer": "/content/args/a~1b", "excerpt": "v"},
                                          {"event_id": "e2", "pointer": "/content/args/c~0d", "excerpt": "w"}]
    errors, _ = check(tools, bundle, rep)
    assert errors == []


def test_agent_claim_cannot_support_success(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"]["basis"] = "agent_claim"
    errors, _ = check(tools, bundle, rep)
    assert any("cannot rest on basis 'agent_claim'" in e for e in errors)
    rep["outcome"]["status"] = "unknown"
    rep["missing_information"] = [{"item": "verification", "discriminates": ""}]
    errors, _ = check(tools, bundle, rep)
    assert errors == []


def test_unknown_outcome_needs_missing_information(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"].update({"status": "unknown", "basis": "none"})
    errors, _ = check(tools, bundle, rep)
    assert any("requires at least one missing_information" in e for e in errors)


def test_basis_must_match_reference_kind(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"]["basis"] = "tool_evidence"
    rep["outcome"]["references"] = [{"pointer": "/evaluator/observations/0/verdict"}]
    errors, _ = check(tools, bundle, rep)
    assert any("tool_evidence requires a reference to a tool_result" in e for e in errors)


def _finding(cat, refs, **kw):
    f = {"id": "F1", "category": cat, "observation": "obs", "interpretation": "", "evidence_status": "established",
         "references": refs}
    f.update(kw)
    return f


def test_taxonomy_enforced(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["findings"] = [_finding("hallucination", [{"event_id": "e4"}])]
    errors, _ = check(tools, bundle, rep)
    assert any("not in the taxonomy" in e for e in errors)


def test_finding_without_references_rejected(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["findings"] = [_finding("tool_execution", [])]
    errors, _ = check(tools, bundle, rep)
    assert any("at least one reference is required" in e for e in errors)


def test_category_reference_rules(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    # tool_execution must cite a tool_result or error
    rep["findings"] = [_finding("tool_execution", [{"event_id": "e4"}])]
    errors, _ = check(tools, bundle, rep)
    assert any("needs a reference to a tool_result or error" in e for e in errors)
    rep["findings"] = [_finding("tool_execution", [{"event_id": "e3"}])]
    errors, _ = check(tools, bundle, rep)
    assert errors == []
    # environment_provider must cite a *failed* result or error
    rep["findings"] = [_finding("environment_provider", [{"event_id": "e3"}])]
    errors, _ = check(tools, bundle, rep)
    assert any("failed tool_result or error" in e for e in errors)
    # instruction_following needs rule + act
    rep["findings"] = [_finding("instruction_following", [{"pointer": "/tool_policy/status"}])]
    errors, _ = check(tools, bundle, rep)
    assert any("instruction_following" in e for e in errors)
    rep["findings"] = [_finding("instruction_following", [{"pointer": "/tool_policy/status"}, {"event_id": "e4"}])]
    errors, _ = check(tools, bundle, rep)
    assert errors == []
    # evaluation_task_design needs task/criteria/evaluator
    rep["findings"] = [_finding("evaluation_task_design", [{"event_id": "e4"}])]
    errors, _ = check(tools, bundle, rep)
    assert any("evaluation_task_design" in e for e in errors)


def test_percentages_forbidden(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["outcome"]["statement"] = "I am 85% sure."
    errors, _ = check(tools, bundle, rep)
    assert any("percentage" in e for e in errors)
    rep = minimal_report(bundle, sha(bundle))
    rep["hypotheses"] = [{"id": "H1", "statement": "90% likely a timeout", "would_confirm": "x", "would_refute": "y"}]
    errors, _ = check(tools, bundle, rep)
    assert any("percentage" in e for e in errors)


def test_hypothesis_needs_confirm_and_refute(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["hypotheses"] = [{"id": "H1", "statement": "s", "would_confirm": "", "would_refute": "y"}]
    errors, _ = check(tools, bundle, rep)
    assert any("would_confirm" in e for e in errors)


def test_divergence_identified_requires_event(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["earliest_divergence"] = {"status": "identified", "statement": "s", "references": []}
    errors, _ = check(tools, bundle, rep)
    assert any("existing event_id" in e for e in errors)
    assert any("at least one reference" in e for e in errors)


def test_regression_test_rules(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["findings"] = [_finding("tool_execution", [{"event_id": "e3"}])]
    rep["regression_test"] = {"status": "proposed", "targets": ["F9"], "preconditions": ["p"], "inputs": ["i"],
                              "expected_behavior": ["e"], "assertions": []}
    errors, _ = check(tools, bundle, rep)
    assert any("target 'F9'" in e for e in errors)
    assert any("assertions must be a non-empty" in e for e in errors)
    rep["hypotheses"] = [{"id": "H1", "statement": "s", "would_confirm": "c", "would_refute": "r"}]
    rep["regression_test"].update({"targets": ["H1"], "assertions": ["a"]})
    errors, warnings = check(tools, bundle, rep)
    assert errors == []
    assert any("targets hypothesis 'H1'" in w for w in warnings)


def test_unaddressed_signal_warns(tools, bundle):
    bundle["events"].append({"id": "e5", "kind": "error", "content": {"message": "boom"}})
    rep = minimal_report(bundle, sha(bundle))
    rep["task"]["evidence_coverage"]["events_total"] = 5
    rep["task"]["evidence_coverage"]["events_reviewed"] = 5
    ev = tools.build_evidence(bundle, sha(bundle), [])
    errors, warnings = check(tools, bundle, rep, ev)
    assert errors == []
    assert any("signal event 'e5' is never referenced" in w for w in warnings)
    rep["key_events"].append({"event_id": "e5", "summary": "an error after completion", "references": []})
    _, warnings = check(tools, bundle, rep, ev)
    assert warnings == []


def test_coverage_must_match(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["task"]["evidence_coverage"]["events_total"] = 3
    errors, _ = check(tools, bundle, rep)
    assert any("events_total must be 4" in e for e in errors)


def test_render_is_deterministic_and_complete(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["findings"] = [_finding("tool_execution", [{"event_id": "e3", "pointer": "/content/output", "excerpt": "hello"}],
                                interpretation="Recovered.")]
    rep["hypotheses"] = [{"id": "H1", "statement": "s", "would_confirm": "c", "would_refute": "r"}]
    rep["missing_information"] = [{"item": "m", "discriminates": "H1"}]
    rep["remediation"] = {"status": "proposed", "statement": "fix"}
    rep["regression_test"] = {"status": "proposed", "targets": ["F1"], "preconditions": ["p"], "inputs": ["i"],
                              "expected_behavior": ["e"], "assertions": ["a"]}
    a = tools.render_markdown(rep)
    b = tools.render_markdown(copy.deepcopy(rep))
    assert a == b
    for needle in ("# Agent Run Analysis", "## Outcome", "**SUCCESS**", "### F1: `tool_execution`", "Recovered.",
                   "## Earliest evidenced divergence", "### H1", "**Would refute:** r", "- m Discriminates: H1",
                   "specification, not executed", "`ev:e3 /content/output` \"hello\"", tools.REFERENCE_NOTICE,
                   sha(bundle)):
        assert needle in a, needle


def test_cli_check_and_render(tools_path, tmp_path, bundle):
    p = tmp_path / "b.json"
    write_bundle(p, bundle)
    work = tmp_path / "w"
    r = subprocess.run([sys.executable, str(tools_path), "prepare", str(p), "--out", str(work)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    digest = json.loads(r.stdout)["sha256"]
    rep = minimal_report(bundle, digest)
    (work / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    r = subprocess.run([sys.executable, str(tools_path), "check-report", str(work / "report.json"), "--snapshot",
                        str(work / "snapshot.json"), "--evidence", str(work / "evidence.json")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    out = json.loads(r.stdout)
    assert out["ok"] is True and out["notice"].startswith("Reference validity confirms")
    r = subprocess.run([sys.executable, str(tools_path), "render", str(work / "report.json"), "-o", str(work / "report.md")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    md = (work / "report.md").read_text(encoding="utf-8")
    assert "**SUCCESS**" in md
    # a bad report exits 1 and the notice is still printed
    rep["source"]["sha256"] = "0" * 64
    (work / "report.json").write_text(json.dumps(rep), encoding="utf-8")
    r = subprocess.run([sys.executable, str(tools_path), "check-report", str(work / "report.json"), "--snapshot",
                        str(work / "snapshot.json")], capture_output=True, text=True)
    assert r.returncode == 1
    assert "Reference validity" in json.loads(r.stdout)["notice"]


def test_render_refuses_non_report(tools_path, tmp_path):
    p = tmp_path / "x.json"
    p.write_text("{}", encoding="utf-8")
    r = subprocess.run([sys.executable, str(tools_path), "render", str(p)], capture_output=True, text=True)
    assert r.returncode == 2


def test_criteria_match_basis_allows_success_without_tools_or_evaluator(tools, bundle):
    bundle["events"] = [{"id": "e1", "kind": "user_message", "content": {"text": "Capital of Australia?"}},
                        {"id": "e2", "kind": "assistant_message", "content": {"text": "Canberra"}}]
    bundle["success_criteria"] = {"status": "known", "criteria": ["Answer is Canberra"]}
    bundle["final_output"] = {"status": "available", "text": "Canberra"}
    bundle["evaluator"] = {"status": "unavailable"}
    rep = minimal_report(bundle, sha(bundle))
    rep["task"]["evidence_coverage"].update({"events_total": 2, "events_reviewed": 2})
    rep["key_events"] = []
    refs = [{"pointer": "/success_criteria/criteria/0", "excerpt": "Answer is Canberra"},
            {"pointer": "/final_output/text", "excerpt": "Canberra"}]
    rep["outcome"] = {"status": "success", "basis": "criteria_match", "statement": "Answer matches the criterion.", "references": refs}
    errors, warnings = check(tools, bundle, rep)
    assert errors == [] and warnings == []
    # every other basis is rejected for this bundle
    for basis in ("tool_evidence", "evaluator_observation", "external_verified", "agent_claim", "none"):
        rep["outcome"]["basis"] = basis
        errors, _ = check(tools, bundle, rep)
        assert any("outcome" in e for e in errors), basis
    # criteria_match needs known criteria and both reference kinds
    rep["outcome"]["basis"] = "criteria_match"
    rep["outcome"]["references"] = [{"pointer": "/final_output/text", "excerpt": "Canberra"}]
    errors, _ = check(tools, bundle, rep)
    assert any("requires a reference into /success_criteria" in e for e in errors)
    rep["outcome"]["references"] = refs
    bundle["success_criteria"] = {"status": "unknown"}
    rep["task"]["criteria_status"] = "unknown"
    errors, _ = check(tools, bundle, rep)
    assert any("requires success_criteria.status 'known'" in e for e in errors)


def test_log_line_references_warn_instead_of_fail(tools):
    raw = b"task: fetch page\ntool_call http_get url=https://x\nERROR http_get: connection reset by peer\nagent: could not fetch\n"
    lb = tools.wrap_text(raw, "log1", "fetch page", "test", True)
    lb["success_criteria"] = {"status": "known", "criteria": ["page content reported"]}
    digest = sha(lb)
    rep = minimal_report(lb, digest)
    rep["task"] = {"description_ref": {"pointer": "/task/description"}, "criteria_status": "known",
                   "tool_policy_status": "unknown", "evidence_coverage": {"events_total": 4, "events_reviewed": 4, "note": "all"}}
    rep["key_events"] = []
    rep["outcome"] = {"status": "unknown", "basis": "none", "statement": "cannot tell", "references": []}
    rep["missing_information"] = [{"item": "result", "discriminates": ""}]
    refs = [{"event_id": "L3", "pointer": "/content/text", "excerpt": "connection reset"},
            {"event_id": "L2", "pointer": "/content/text", "excerpt": "http_get"}]
    for cat in ("tool_execution", "environment_provider", "reasoning_calculation", "instruction_following"):
        rep["findings"] = [{"id": "F1", "category": cat, "observation": "line 3 shows a connection reset",
                            "interpretation": "", "evidence_status": "partial", "references": refs}]
        errors, warnings = check(tools, lb, rep)
        assert errors == [], (cat, errors)
        assert any("log_line" in w and "Reviewer must check" in w for w in warnings), cat
    # tool_evidence basis on log lines: warning, not error
    rep["findings"] = []
    rep["outcome"] = {"status": "failure", "basis": "tool_evidence", "statement": "reset", "references": refs}
    rep["missing_information"] = []
    errors, warnings = check(tools, lb, rep)
    assert errors == []
    assert any("tool_evidence rests on unstructured log_line" in w for w in warnings)


def test_empty_excerpt_rejected(tools, bundle):
    rep = minimal_report(bundle, sha(bundle))
    rep["key_events"][0]["references"] = [{"event_id": "e3", "pointer": "/content/output", "excerpt": ""}]
    errors, _ = check(tools, bundle, rep)
    assert any("excerpt must not be empty" in e for e in errors)
