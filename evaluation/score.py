#!/usr/bin/env python3
"""Score report.json files against evaluation/expected keys on the key-checkable rubric items.

Covers S1 (outcome), S4 (divergence), and the category part of S2/S3 (forbidden or missing
categories). S5, S6, S7 and the semantic half of S2 need a human reader. Prints one line per report.
Usage: python3 evaluation/score.py <report.json> [<report.json> ...]
"""
import json
import sys
from pathlib import Path

EXPECTED = Path(__file__).resolve().parent / "expected"


def fixture_for(report_path: Path) -> str:
    rid = json.loads(report_path.read_text())["run_id"]
    return rid.replace("syn-", "", 1)


def score(report_path: Path) -> dict:
    r = json.loads(report_path.read_text())
    key = json.loads((EXPECTED / f"{fixture_for(report_path)}.json").read_text())
    out = {}
    o = r["outcome"]
    cats = [f["category"] for f in r["findings"]]
    ok = False
    for allowed in key["allowed_outcomes"]:
        if o["status"] == allowed["status"] and o["basis"] in allowed["basis"]:
            if "only_with_category" in allowed and allowed["only_with_category"] not in cats:
                continue
            ok = True
    out["S1_outcome"] = "pass" if ok else f"fail ({o['status']}/{o['basis']})"
    kc = key["categories"]
    forbidden_hit = [c for c in cats if c in kc.get("forbidden", [])]
    partial_only = kc.get("partial_only", [])
    partial_viol = [f["category"] for f in r["findings"] if f["category"] in partial_only and f["evidence_status"] == "established"]
    expected_any = kc.get("expected_any", [])
    missing = expected_any and not any(c in expected_any for c in cats) and not kc.get("allow_empty")
    if forbidden_hit or partial_viol:
        out["S2_categories"] = f"fail (forbidden={forbidden_hit}, established-but-partial-only={partial_viol})"
    elif missing:
        out["S2_categories"] = f"partial (none of expected {expected_any} present; findings={cats})"
    else:
        out["S2_categories"] = "pass"
    d = r["earliest_divergence"]
    kd = key["divergence"]
    if d["status"] not in kd["allowed"]:
        out["S4_divergence"] = f"fail ({d['status']})"
    elif d["status"] == "identified" and kd["event_ids"] and d.get("event_id") not in kd["event_ids"]:
        out["S4_divergence"] = f"fail (identified at {d.get('event_id')}, key allows {kd['event_ids']})"
    elif kd.get("preferred") and d["status"] != kd["preferred"]:
        out["S4_divergence"] = f"partial ({d['status']}; key prefers {kd['preferred']})"
    else:
        out["S4_divergence"] = "pass"
    rt = r["regression_test"]["status"]
    want = key["regression_test"]
    if want == "expected":
        out["S6_regression_present"] = "pass" if rt == "proposed" else "fail (none proposed)"
    elif want == "none_expected":
        out["S6_regression_present"] = "pass" if rt == "none" else "partial (proposed although no failure is expected)"
    else:
        out["S6_regression_present"] = "pass"
    out["findings"] = cats
    return out


def main(argv):
    for p in argv:
        s = score(Path(p))
        print(f"{p}: " + " | ".join(f"{k}={v}" for k, v in s.items()))


if __name__ == "__main__":
    main(sys.argv[1:])
