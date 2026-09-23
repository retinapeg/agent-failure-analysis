#!/usr/bin/env python3
"""Compare report.json files with the retrospective keys in evaluation/expected.

The keys were written after the runs by the implementing session; they are development labels,
not independent ground truth. This script checks outcome, category membership, divergence, and
whether a regression test is present. A key-prohibited category can be a placement error (a true
non-failure filed as a finding) or an unsupported diagnosis; only a reader can tell which.
Usage: python3 evaluation/score.py [--keys DIR] <report.json> [<report.json> ...]
"""
import json
import sys
from pathlib import Path

EXPECTED = Path(__file__).resolve().parent / "expected"


def fixture_for(report_path: Path) -> str:
    rid = json.loads(report_path.read_text())["run_id"]
    return rid.replace("syn-", "", 1)


def score(report_path: Path, keys: Path = EXPECTED) -> dict:
    r = json.loads(report_path.read_text())
    key = json.loads((keys / f"{fixture_for(report_path)}.json").read_text())
    out = {}
    o = r["outcome"]
    cats = [f["category"] for f in r["findings"]]
    ok = False
    for allowed in key["allowed_outcomes"]:
        if o["status"] == allowed["status"] and o["basis"] in allowed["basis"]:
            if "only_with_category" in allowed and allowed["only_with_category"] not in cats:
                continue
            ok = True
    out["outcome_vs_key"] = "pass" if ok else f"fail ({o['status']}/{o['basis']})"
    kc = key["categories"]
    forbidden_hit = [c for c in cats if c in kc.get("forbidden", [])]
    partial_only = kc.get("partial_only", [])
    partial_viol = [f["category"] for f in r["findings"] if f["category"] in partial_only and f["evidence_status"] == "established"]
    expected_any = kc.get("expected_any", [])
    missing = expected_any and not any(c in expected_any for c in cats) and not kc.get("allow_empty")
    if forbidden_hit or partial_viol:
        out["key_prohibited_category"] = f"fail (forbidden={forbidden_hit}, established-but-partial-only={partial_viol})"
    elif missing:
        out["key_prohibited_category"] = f"partial (none of expected {expected_any} present; findings={cats})"
    else:
        out["key_prohibited_category"] = "pass"
    d = r["earliest_divergence"]
    kd = key["divergence"]
    if d["status"] not in kd["allowed"]:
        out["divergence_vs_key"] = f"fail ({d['status']})"
    elif d["status"] == "identified" and kd["event_ids"] and d.get("event_id") not in kd["event_ids"]:
        out["divergence_vs_key"] = f"fail (identified at {d.get('event_id')}, key allows {kd['event_ids']})"
    elif kd.get("preferred") and d["status"] != kd["preferred"]:
        out["divergence_vs_key"] = f"partial ({d['status']}; key prefers {kd['preferred']})"
    else:
        out["divergence_vs_key"] = "pass"
    rt = r["regression_test"]["status"]
    want = key["regression_test"]
    if want == "expected":
        out["regression_present_vs_key"] = "pass" if rt == "proposed" else "fail (none proposed)"
    elif want == "none_expected":
        out["regression_present_vs_key"] = "pass" if rt == "none" else "partial (proposed although no failure is expected)"
    else:
        out["regression_present_vs_key"] = "pass"
    out["findings"] = cats
    return out


def main(argv):
    keys = EXPECTED
    if argv and argv[0] == "--keys":
        keys = Path(argv[1])
        argv = argv[2:]
    for p in argv:
        s = score(Path(p), keys)
        print(f"{p}: " + " | ".join(f"{k}={v}" for k, v in s.items()))


if __name__ == "__main__":
    main(sys.argv[1:])
