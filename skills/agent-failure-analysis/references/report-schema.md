# Report (`afa-report/1`)

`report.json` is the canonical analysis. `report.md` is rendered from it by
`trace_tools.py render` and carries no information the JSON lacks.

References use the format in `evidence-contract.md` section 2.

```json
{
  "report_version": "afa-report/1",
  "skill_version": "0.1.0",
  "run_id": "<must equal snapshot run_id>",
  "source": {"snapshot": "snapshot.json", "sha256": "<must equal snapshot hash>"},
  "task": {
    "description_ref": {"pointer": "/task/description"},
    "criteria_status": "known | unknown",
    "tool_policy_status": "required | optional | prohibited | unknown",
    "evidence_coverage": {"events_total": 0, "events_reviewed": 0, "note": "text"}
  },
  "outcome": {
    "status": "success | failure | unknown",
    "basis": "evaluator_observation | tool_evidence | criteria_match | external_verified | agent_claim | none",
    "statement": "text",
    "references": [ {"event_id": "...", "pointer": "...", "excerpt": "..."} ]
  },
  "key_events": [
    {"event_id": "...", "summary": "text", "references": [ ... ]}
  ],
  "findings": [
    {
      "id": "F1",
      "category": "<taxonomy slug>",
      "observation": "text",
      "interpretation": "text",
      "evidence_status": "established | partial | contested",
      "references": [ ... ]
    }
  ],
  "earliest_divergence": {
    "status": "identified | unknown",
    "event_id": "<required when identified>",
    "statement": "text",
    "references": [ ... ]
  },
  "hypotheses": [
    {
      "id": "H1",
      "statement": "text",
      "would_confirm": "text",
      "would_refute": "text",
      "references": [ ... ]
    }
  ],
  "missing_information": [
    {"item": "text", "discriminates": "text"}
  ],
  "remediation": {"status": "proposed | none", "statement": "text"},
  "regression_test": {
    "status": "proposed | none",
    "targets": ["F1"],
    "preconditions": ["text"],
    "inputs": ["text"],
    "expected_behavior": ["text"],
    "assertions": ["text"]
  }
}
```

## Checks performed by `check-report`

Errors (report rejected):
- Wrong `report_version`; `run_id` or `sha256` differing from the snapshot.
- Any enumerated field outside its allowed values; any taxonomy slug not in the taxonomy.
- Any reference whose event id, pointer, or excerpt does not resolve exactly, or whose excerpt is empty.
- `outcome.basis` whose required reference kind is absent: `evaluator_observation` needs `/evaluator`, `tool_evidence` needs a `tool_result` event, `criteria_match` needs `/success_criteria` (status `known`) plus `/final_output` or an `assistant_message`, `external_verified` needs `/provenance`.
- `outcome.status` not `unknown` with basis `agent_claim` or `none`, or with no references.
- A finding with no references, an empty observation, or references that do not meet its category's required kinds.
- `earliest_divergence` identified without an existing `event_id` and references.
- A hypothesis missing `would_confirm` or `would_refute`.
- `outcome.status` unknown with empty `missing_information`.
- `regression_test` proposed with any empty list or with `targets` naming unknown finding ids.
- Numeric percentages in `outcome.statement`, finding interpretations, or hypothesis statements.

Warnings (report accepted, reviewer should look):
- Signal events from `evidence.json` that no reference cites (when `--evidence` is supplied).
- `regression_test.targets` naming a hypothesis rather than a finding.
- `events_reviewed` below `events_total`.
- A finding or `tool_evidence` basis whose references are `log_line` events: the event-kind rule cannot be applied to unstructured lines, so the reviewer must check the excerpts.

Every check-report run prints: *"Reference validity confirms that cited
locations and excerpts exist in the snapshot. It does not confirm that any
interpretation follows from them."*
