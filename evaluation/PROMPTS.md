# Pilot Prompts (verbatim)

Both templates were sent to fresh Claude Code subagent sessions on
2026-09-23 (host Claude Code 2.1.280, model `claude-fable-5-1`, skill
commit `1e4eb0d`). `{REPO}`, `{FIXTURE}`, and `{WORK}` were substituted with
absolute paths. The seven additional skill runs in `skill-runs/` used the
skill template with one extra request in item (b): the divergence event id.

## Skill condition

```
You are a fresh session testing a skill. Skill folder: {REPO}/skills/agent-failure-analysis

Task: analyse the recorded agent run at {FIXTURE} using the skill.

Steps:
1. Read the skill's SKILL.md and follow it exactly, including the reference files it names.
2. Use the output directory {WORK} (create it).
3. Produce report.json and report.md in that directory through the skill's workflow.

Restrictions: under {REPO} read only the skill folder and the one fixture file named above. Do not read anything else under evaluation/, tests/, docs/, or README.md, and do not read any other fixture. Do not modify anything under that repository.

Return as your final message: (a) the exact JSON output of your final check-report run, (b) the outcome status and basis, the list of finding categories, and the earliest_divergence status from your report, (c) how many check-report iterations you needed before it passed.
```

## Plain condition

```
Analyse the recorded agent run stored at {FIXTURE} (a JSON file). Explain what happened, which failures the evidence supports, which explanations remain hypotheses, what information is missing, and propose a regression test.

Write your analysis as JSON to {WORK}/report.json (create the directory), following this exact schema:

{
  "report_version": "afa-report/1",
  "skill_version": "0.1.0",
  "run_id": "<must equal the file's run_id>",
  "source": {"snapshot": "snapshot.json", "sha256": "<SHA-256 hex digest of the fixture file's bytes>"},
  "task": {
    "description_ref": {"pointer": "/task/description"},
    "criteria_status": "known | unknown",
    "tool_policy_status": "required | optional | prohibited | unknown",
    "evidence_coverage": {"events_total": 0, "events_reviewed": 0, "note": "text"}
  },
  "outcome": {
    "status": "success | failure | unknown",
    "basis": "evaluator_observation | tool_evidence | external_verified | agent_claim | none",
    "statement": "text",
    "references": [ {"event_id": "...", "pointer": "...", "excerpt": "..."} ]
  },
  "key_events": [ {"event_id": "...", "summary": "text", "references": [ ... ]} ],
  "findings": [
    {"id": "F1", "category": "<taxonomy slug>", "observation": "text", "interpretation": "text",
     "evidence_status": "established | partial | contested", "references": [ ... ]}
  ],
  "earliest_divergence": {"status": "identified | unknown", "event_id": "<required when identified>", "statement": "text", "references": [ ... ]},
  "hypotheses": [ {"id": "H1", "statement": "text", "would_confirm": "text", "would_refute": "text", "references": [ ... ]} ],
  "missing_information": [ {"item": "text", "discriminates": "text"} ],
  "remediation": {"status": "proposed | none", "statement": "text"},
  "regression_test": {"status": "proposed | none", "targets": ["F1"], "preconditions": ["text"], "inputs": ["text"], "expected_behavior": ["text"], "assertions": ["text"]}
}

Field notes: category must be one of instruction_following, tool_selection, tool_execution, reasoning_calculation, environment_provider, evaluation_task_design, other_unknown. criteria_status and tool_policy_status must match the file's success_criteria.status and tool_policy.status. events_total must equal the number of events in the file. References use event ids from the file plus RFC 6901 JSON pointers, resolved inside the named event when event_id is given (for example pointer "/content/output"), or from the file root when it is not (for example "/evaluator/observations/0/text"); an excerpt, when given, must be an exact substring of the referenced value. Compute the sha256 with `shasum -a 256` on the fixture file.

Do not read any other file under {REPO}. Do not modify anything under that repository.

Return as your final message: the outcome status and basis, the list of finding categories, and the earliest_divergence status from your report.
```

What the plain condition was not given: SKILL.md, the evidence contract,
the taxonomy definitions and their required references, the `prepare`
packet, the rule that an excerpt must be non-empty, the rule that a proposed
regression test needs targets, and the `check-report` loop.
