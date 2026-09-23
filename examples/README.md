# Examples

Every bundle here is **synthetic**: authored by hand for this repository, with
`provenance.synthetic: true`. No real agent, model, provider, or user produced
these events. Each folder holds the input `bundle.json`, the `evidence.json`
and `snapshot.sha256` that `prepare` produced, and the `report.json` and
`report.md` that a fresh Claude Code session wrote by following the skill.
All four reports passed `check-report` with zero errors and zero warnings.

| Folder | Shows | Outcome | Findings |
|---|---|---|---|
| `calculation-mistake/` | The hero case: an evidence-backed finding with the divergence pinned to one event, and a concrete regression test. The agent's own calculator returned 3.0 and the agent wrote 2.80. | `failure` | `reasoning_calculation` |
| `provider-failure/` | A failure that is not the agent's fault. Two HTTP 503 responses; the report blames the environment, not reasoning, and keeps "would more retries have helped" as a hypothesis. | `failure` | `environment_provider` |
| `incomplete-trace/` | Abstention. The recording stops after a tool call with no result. No finding, outcome `unknown`, three hypotheses, and the list of what would discriminate them. | `unknown` | none |
| `defective-grader/` | A grader defect. The answer satisfies the stated criterion; the exact-match grader failed it over spacing. The finding is against the evaluation, not the agent. | `success` | `evaluation_task_design` |

These reports were produced by the model, checked mechanically, and labelled
by the implementing session against `evaluation/expected/`. They have not yet
been reviewed by Leo. See `evaluation/RESULTS.md`.

To reproduce one:

```bash
T=skills/agent-failure-analysis/scripts/trace_tools.py
python3 $T prepare examples/calculation-mistake/bundle.json --out /tmp/afa-demo
# ...the host model writes /tmp/afa-demo/report.json following SKILL.md...
python3 $T check-report /tmp/afa-demo/report.json --snapshot /tmp/afa-demo/snapshot.json --evidence /tmp/afa-demo/evidence.json
python3 $T render /tmp/afa-demo/report.json -o /tmp/afa-demo/report.md
```
