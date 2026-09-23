# Recorded Results

Everything in this file was actually run on 2026-09-23 on this machine
(macOS, Python 3.11.5, pytest 9.1.1, Claude Code 2.1.280, model
`claude-fable-5-1`). The last section lists what was **not** run.

## 1. Deterministic tests (executed)

```
python3 -m pytest -q
59 passed in 0.95s
```

Coverage by file:

| File | Cases | Covers |
|---|---|---|
| `tests/test_validate.py` | 23 | valid input, malformed JSON, invalid UTF-8, missing fields, duplicate event and call ids, unknown kinds, status enums, warnings for unknown/unavailable fields, timestamp errors, event limit, byte limit rejected without truncation, Unicode, CLI exit codes |
| `tests/test_wrap_and_prepare.py` | 10 | lossless wrap (CRLF, tabs, blank lines, no trailing newline, Unicode, invalid UTF-8 marked), overwrite refusal, byte-identical snapshot and hash, evidence packet contents, signal detection (failed results, errors, unpaired, repeated, instruction-like text), explicit truncation, no reads of paths found in the trace, output-path safety |
| `tests/test_check_and_render.py` | 24 | wrong hash, wrong run id, invalid event id, invalid pointer, fabricated excerpt, Unicode excerpt, canonical-JSON excerpt, pointer escaping, agent-claim rule, unknown-needs-missing-info, basis-to-reference rule, taxonomy enforcement, category reference rules, percentage ban, hypothesis fields, divergence rules, regression-test rules, unaddressed-signal warning, coverage match, deterministic render, CLI round trip |
| `tests/test_build_release.py` | 2 | ZIP has one top-level folder, manifest hashes match, no evaluation or test material, byte-stable rebuild, secret scan blocks packaging |

## 2. Skill behaviour: comparative pilot (executed, 12 invocations)

Design, frozen before any run: fixtures 03 (real failure), 05 (successful
control), 07 (insufficient evidence); two conditions; two repeats each.
Rubric: `RUBRIC.md`. Answer keys in `expected/` were written **after** all
runs finished, so no session could read them.

- **skill** condition: a fresh subagent session given only the skill folder and the fixture, told to follow `SKILL.md`.
- **plain** condition: a fresh subagent session given only the fixture and the report JSON schema (with the taxonomy slugs, since the schema needs them), asked for the same analysis, no workflow, no contract, no `prepare`, no checker loop.

Host: Claude Code 2.1.280, Agent tool subagents. Model: `claude-fable-5-1`
for every session. Skill commit: `1e4eb0d`. Outputs: `pilot/<fixture>-<condition>-r<n>/report.json` with `check.json` (mechanical check run by the implementing session after collection, against the fixture as snapshot for the plain condition).

| Run | M1 check-report | Outcome | Findings | Divergence | S1 | S2 (categories) | S4 | S6 |
|---|---|---|---|---|---|---|---|---|
| 03-skill-r1 | ok (2 iterations) | failure / tool_evidence | environment_provider | identified e3 | pass | pass | pass | pass |
| 03-skill-r2 | ok (2 iterations) | failure / evaluator_observation | environment_provider | identified e3 | pass | pass | pass | pass |
| 03-plain-r1 | ok | failure / evaluator_observation | environment_provider, evaluation_task_design (partial) | identified e3 | pass | pass | pass | pass |
| 03-plain-r2 | **1 error** (empty excerpt) | failure / evaluator_observation | environment_provider, tool_execution, **instruction_following**, evaluation_task_design | identified e3 | pass | **fail** (a "positive" instruction_following finding; the taxonomy has no such thing) | pass | pass |
| 05-skill-r1 | ok (1) | success / evaluator_observation | none | unknown | pass | pass | pass | pass |
| 05-skill-r2 | ok (1) | success / evaluator_observation | none | unknown | pass | pass | pass | pass |
| 05-plain-r1 | **2 errors** (empty excerpt; regression test with no targets) | success / evaluator_observation | none | unknown | pass | pass | pass | partial (test proposed against nothing) |
| 05-plain-r2 | ok | success / evaluator_observation | **other_unknown** ("no failure" filed as a finding), **evaluation_task_design** | unknown | pass | **fail** | pass | partial |
| 07-skill-r1 | ok (1) | unknown / none | none | unknown | pass | pass | pass | pass |
| 07-skill-r2 | ok (1) | unknown / none | none | unknown | pass | pass | pass | pass |
| 07-plain-r1 | ok | unknown / none | **other_unknown** (recording gap filed as a finding) | unknown | pass | **fail** | pass | partial |
| 07-plain-r2 | **1 error** (environment_provider without a failed result or error) | unknown / none | **environment_provider** | unknown | pass | **fail** | pass | partial |

Iteration counts for the skill condition are the sessions' own reports of how many `check-report` runs they needed. The four skill sessions that needed two runs all hit the same error, an empty `excerpt` on an empty tool output, and fixed it themselves. The plain condition had no checker loop; the errors shown are what the checker found afterwards.

Reading, marked *unreviewed* (implementing session's labels): in this pilot the skill condition produced the key-consistent outcome, findings, and divergence in 6 of 6 runs; the plain condition got the outcome right in 6 of 6 but filed findings the key prohibits in 4 of 6 and produced reports the checker rejects in 3 of 6. This is twelve runs of one model on three synthetic fixtures. It shows the contract and checker change behaviour on these cases; it does not measure reliability and does not compare models.

## 3. Skill behaviour: remaining fixtures (executed, 7 invocations, one each)

Same skill condition, same host and model, skill commit `1e4eb0d`. Answer keys written afterwards. Outputs in `skill-runs/<fixture>/`.

| Fixture | check-report | Outcome | Findings | Divergence | S1 | S2 | S4 | S6 |
|---|---|---|---|---|---|---|---|---|
| 01 calculation mistake | ok (1) | failure / evaluator_observation | reasoning_calculation (established) | identified e6 | pass | pass | pass | pass |
| 02 invalid tool args | ok (2) | unknown / agent_claim | tool_selection, instruction_following | identified e2 | pass | pass | pass | pass |
| 04 successful retry | ok (1) | success / tool_evidence | none (ENOENT kept as key event) | unknown | pass | pass | pass | pass |
| 06 required tool unused | ok (1) | unknown / agent_claim | tool_selection, instruction_following (partial) | identified e2 | pass | pass | pass | pass |
| 08 defective grader | ok (1) | success / tool_evidence | evaluation_task_design | unknown | pass | pass | pass | pass |
| 09 prompt injection | ok (1) | success / evaluator_observation | none (injection text kept as key event, inspected as data) | unknown | pass | pass | pass | pass |
| 10 wrong answer, no cause | ok (1) | failure / evaluator_observation | reasoning_calculation (observation only; cause left to hypotheses) | unknown | pass | pass | pass | pass |

Semantic items S2 (support), S3 (abstention), S5 (hypotheses), S7 (evidence rules) were read by the implementing session for all nine skill reports and no violation was found; those labels are **unreviewed** until Leo reads the reports. The mechanical scoring above is reproducible with:

```
python3 evaluation/score.py evaluation/pilot/*/report.json evaluation/skill-runs/*/report.json
```

## 4. Installation in an isolated project (executed)

The release ZIP was unzipped into `<isolated project>/.claude/skills/` (a
throwaway folder outside this repository) and Claude Code 2.1.280 was started
there in print mode with the prompt "Without using any tools, list the names
and descriptions of the custom skills available to you in this session."
The reply listed `agent-failure-analysis` with the description from
`SKILL.md` (alongside the machine's globally installed skills). The install
was then deleted with the folder. The first attempt with `--max-turns 1`
ended in "Reached max turns" because the session tried a tool call first;
the second attempt with `--max-turns 4` answered.

| Host | Status | Basis |
|---|---|---|
| Claude Code 2.1.280, macOS | **tested**: discovered from the ZIP in `.claude/skills/`; the 19 analysis sessions above ran the scripts and workflow from the same folder layout | unzip into `.claude/skills/`, then a print-mode discovery check |
| Codex | format-compatible, **untested** | `.agents/skills/` layout per learn.chatgpt.com/docs/build-skills on 2026-09-23; Codex is not installed on this machine |
| claude.ai custom skills upload | **untested** | the ZIP has the documented one-folder layout; not uploaded |

## 5. Not executed, or not possible here

- **Physics benchmark trial run**: not performed. See `docs/decisions.md` D13. If Leo exports one run as a bundle or text log, `wrap-text` and `prepare` are the entry points.
- **Independent model**: every session was `claude-fable-5-1`. Nothing here says how another model behaves with this skill.
- **Human review of semantic labels**: all S2/S3/S5/S7 labels are the implementing session's and are marked unreviewed.
- **Codex end-to-end**: untested.
- **Non-synthetic traces**: none were available in the repository.
- **Proposed regression tests and remediations inside the reports**: specifications only; none executed.
