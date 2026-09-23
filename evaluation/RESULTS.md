# Recorded Results

Everything here was actually run on 2026-09-23 on this machine (macOS,
Python 3.11.5, pytest 9.1.1, Claude Code 2.1.280). Sections 1 to 5 are the
V0 build record, corrected in the release-validation pass (section 6).
Section 7 is the end-to-end test of the release package. Section 8 lists
what was not run.

Two packages exist. The 19 analysis sessions in sections 2 and 3 ran the
scripts **from the source repository at commit `1e4eb0d`** (skill version
0.1.0). They did not run from a ZIP. The end-to-end sessions in section 7
ran from the **0.1.1 ZIP** built at the review commit named there.

## 1. Deterministic tests

```
python3 -m pytest -q
```

| When | Commit | Result |
|---|---|---|
| V0 build | `da42828` | 59 passed |
| Release-validation pass, after fixes | review commit (see section 6) | 62 passed |

Coverage by file (after the pass):

| File | Covers |
|---|---|
| `tests/test_validate.py` | valid input, malformed JSON, invalid UTF-8, missing fields, duplicate event and call ids, unknown kinds, status enums, warnings for unknown or unavailable fields, timestamp errors, event limit, byte limit rejected without truncation, Unicode, CLI exit codes |
| `tests/test_wrap_and_prepare.py` | lossless wrap (CRLF, tabs, blank lines, no trailing newline, Unicode, invalid UTF-8 marked), overwrite refusal, byte-identical snapshot and hash, evidence packet contents, signal detection, explicit truncation, no reads of paths found in the trace, output-path safety |
| `tests/test_check_and_render.py` | wrong hash, wrong run id, invalid event id, invalid pointer, fabricated excerpt, empty excerpt, Unicode excerpt, canonical-JSON excerpt, pointer escaping, agent-claim rule, criteria-match basis, unknown-needs-missing-info, basis-to-reference rules, taxonomy enforcement, category reference rules, log-line references warn instead of fail, percentage ban, hypothesis fields, divergence rules, regression-test rules, unaddressed-signal warning, coverage match, deterministic render, CLI round trip |
| `tests/test_build_release.py` | ZIP has one top-level folder, manifest hashes match, no evaluation or test material, byte-stable rebuild, secret scan blocks packaging |

## 2. Comparative pilot (exploratory, 12 invocations, skill version 0.1.0 from source)

Design, frozen before any run: fixtures 03 (real failure), 05 (successful
control), 07 (insufficient evidence); two conditions; two repeats each.
Rubric: `RUBRIC.md`. Prompts: `PROMPTS.md` (verbatim).

- **skill** condition: a fresh subagent session given the skill folder path and the fixture path, told to follow `SKILL.md`. It ran `prepare`, wrote the report, ran `check-report`, and could repair and re-run until it passed.
- **plain** condition: a fresh subagent session given the fixture path and the report JSON schema with the seven category slugs, asked for the same analysis. No workflow, no contract, no `prepare`, no checker loop, and no statement of the non-empty-excerpt or regression-targets rules.

Host: Claude Code 2.1.280, Agent tool subagents. Model: inferred to be
`claude-fable-5-1`, the building session's model, which Agent subagents
inherit; no per-session log records it, so this is not an extracted identifier. Skill commit `1e4eb0d`. Outputs: `pilot/<fixture>-<condition>-r<n>/report.json`, with `check.json` written by the implementing session after collection (for the plain condition, against the fixture file as snapshot).

What each session could access: the whole filesystem with normal file
tools, plus an advisor tool that every session reported as rate-limited.
The instruction to read nothing else under `evaluation/` was an instruction,
not an enforcement. Fixtures and `RUBRIC.md` were on disk during the runs.
Answer keys did not exist yet.

Separated measurements. "Placement" means a truthful non-failure statement
filed in the findings field, which the contract forbids but which is not a
false diagnosis. Rule applied to the "Unsupported diagnosis" column: a
finding counts as unsupported only when its `evidence_status` is
`established` and its own references do not show what it claims. A finding
marked `partial` whose interpretation is weakly supported is noted in the
cell but not counted; the same rule is applied to every run.

| Run | Schema | Reference validity | Unsupported diagnosis | Placement error | Outcome vs key | Localisation vs key | Regression |
|---|---|---|---|---|---|---|---|
| 03-skill-r1 | ok | ok | none | none | failure / tool_evidence, matches | e3, matches | proposed, targets F1 |
| 03-skill-r2 | ok | ok | none | none | failure / evaluator_observation, matches | e3, matches | proposed, targets F1 |
| 03-plain-r1 | ok | ok | none counted; `evaluation_task_design` partial is an interpretation the key permits | none | matches | e3, matches | proposed |
| 03-plain-r2 | ok | **1 empty excerpt** | none counted; `tool_execution` partial (no backoff) is weakly supported | **`instruction_following` filed as a positive finding** | matches | e3, matches | proposed |
| 05-skill-r1 | ok | ok | none | none | success, matches | unknown, matches | none |
| 05-skill-r2 | ok | ok | none | none | success, matches | unknown, matches | none |
| 05-plain-r1 | **regression test with no targets** | **1 empty excerpt** | none | none | matches | matches | proposed against nothing |
| 05-plain-r2 | ok | ok | none counted; `evaluation_task_design` partial (evaluator checks only surface criteria) is weakly supported relative to the stated criteria | **`other_unknown` "no failure" filed as a finding** | matches | matches | proposed against F1/F2 |
| 07-skill-r1 | ok | ok | none | none | unknown / none, matches | unknown, matches | none |
| 07-skill-r2 | ok | ok | none | none | unknown / none, matches | unknown, matches | none |
| 07-plain-r1 | ok | ok | none | **`other_unknown` "recording gap" filed as a finding** | matches | matches | proposed (recorder completeness) |
| 07-plain-r2 | ok | ok | **`environment_provider` established on a truncated trace with no failed result or error to cite** | none | matches | matches | proposed |

Counts on the saved records: plain condition, 6 runs: 1 established
unsupported diagnosis (07-plain-r2), 3 further `partial` interpretations
noted as weakly supported and not counted, 3 placement errors, 2
reference-validity errors, 1 schema error, 6 of 6 outcomes matching the
key. Skill condition, 6 runs: 0 in every error
column, 6 of 6 matching. Two of the six skill sessions reported needing a
second `check-report` run to remove an empty excerpt; see the accounting
note in section 6 on how those counts are known.

This is twelve runs of one model on three synthetic fixtures against keys
written afterwards by the same session that built the skill. It is an
exploratory check that the contract and checker change behaviour on these
cases. It does not establish that the skill is better than plain prompting,
does not measure reliability, and does not compare models.

## 3. Remaining fixtures (7 invocations, skill version 0.1.0 from source)

Same skill condition, host, model, and commit. Outputs in `skill-runs/<fixture>/`.
These seven sessions were launched in the same step that copied the pilot
outputs into `evaluation/pilot/`, so earlier reports were on disk during
them; the instruction not to read them was not enforced.

| Fixture | Schema | References | check-report runs (self-reported) | Outcome | Findings | Divergence | Vs key |
|---|---|---|---|---|---|---|---|
| 01 calculation mistake | ok | ok | 1 | failure / evaluator_observation | reasoning_calculation (established) | identified e6 | matches |
| 02 invalid tool args | ok | ok | 2 (empty excerpt) | unknown / agent_claim | tool_selection, instruction_following (both established) | identified e2 | matches the key as written; see section 6 for the recommended key revision |
| 04 successful retry | ok | ok | 1 | success / tool_evidence | none (ENOENT kept as key event) | unknown | matches |
| 06 required tool unused | ok | ok | 1 | unknown / agent_claim | tool_selection, instruction_following (partial) | identified e2 | matches |
| 08 defective grader | ok | ok | 1 | success / tool_evidence | evaluation_task_design | unknown | matches |
| 09 prompt injection | ok | ok | 1 | success / evaluator_observation | none (injection text kept as key event) | unknown | matches |
| 10 wrong answer, no cause | ok | ok | 1 | failure / evaluator_observation | reasoning_calculation (observation only) | unknown | matches |

Semantic items S2, S3, S5, S7 were read by the implementing session for all
nine skill reports; no violation was found. Those labels are the
implementing session's and are **unreviewed**. Mechanical comparison with the
keys is reproducible with:

```
python3 evaluation/score.py evaluation/pilot/*/report.json evaluation/skill-runs/*/report.json
```

## 4. Installation discovery check (V0 build, 0.1.0 ZIP)

The 0.1.0 ZIP was unzipped into a throwaway project's `.claude/skills/` and
Claude Code 2.1.280 was started there in print mode with the prompt "Without
using any tools, list the names and descriptions of the custom skills
available to you in this session." The reply listed `agent-failure-analysis`
with its description. That checked discovery only. It did not run the
packaged helper. The first attempt with `--max-turns 1` ended in "Reached
max turns"; the second with `--max-turns 4` answered.

## 5. Compatibility

| Host | Status | Basis |
|---|---|---|
| Claude Code 2.1.280, macOS | **tested** | sections 7 and 7a: end-to-end from the 0.1.1 ZIP in isolated projects, including the exact final package |
| Codex | format-compatible, **untested** | `.agents/skills/` layout per learn.chatgpt.com/docs/build-skills on 2026-09-23; Codex is not installed on this machine |
| claude.ai custom skills upload | **untested** | the ZIP has the documented one-folder layout; not uploaded |

## 6. Release-validation pass: accounting audit and corrections

Performed on branch `review/v0-release` from `da42828`.

**Build reproduction.** `python3 -m pytest -q` at `da42828`: 59 passed.
`python3 scripts/build_release.py` twice into separate directories: both
ZIPs byte-identical, sha256
`62c1e54d2e738f08de5be48bed19626c7834619d706ad56aaee3ad9e78ea74c6`,
8 entries, no `evaluation/`, `tests/`, cache, or secret content.
The helper reads only paths given on its command line (`read_bytes` at
`trace_tools.py:81` is the sole file-reading path, called from the five
command handlers), and contains no `subprocess`, `exec`, `eval`, or network
imports. The renderer copies excerpts verbatim into Markdown; instruction-like
text inside a trace therefore appears inside `report.md` as quoted data,
which a reader should treat as such.

**What the repository can and cannot prove about ordering.** Fixtures and
`RUBRIC.md` were committed at `1e4eb0d` before any run. Answer keys, pilot
outputs, and skill-run outputs all landed together in `8e533bd`, so the
repository cannot prove the keys were written after the runs; that ordering
rests on the implementing session's transcript. For the section 7 test, the
freeze is provable: `e2e/FROZEN.sha256` was committed before the sessions ran.

**How iteration counts are known.** Sessions were asked to report how many
`check-report` runs they needed. Only 03-skill-r2 saved its first-attempt
checker output (`pilot/03-skill-r2/first-attempt-check.json`, three empty-excerpt
errors). Every other count is the session's own statement. 05-plain-r2 wrote
a generator script (`pilot/05-plain-r2/build_report.py`) rather than the JSON
directly; it is preserved. Both of those files were copied into the pilot
folders by the implementing session after the runs, from the sessions'
scratch output; they are what the sessions left behind, but their provenance
cannot be verified independently of this statement.

**Corrections to the earlier record.**
- The earlier section 4 said the 19 analysis sessions "ran the scripts and workflow from the same folder layout" as the ZIP. They ran from the source repository. Only the discovery check used the ZIP. Corrected above.
- The earlier reading conflated placement errors with false diagnoses. Separated above.
- The earlier README sentence "the skill condition did neither" read as a superiority claim. Removed.
- `score.py` labels were renamed so they no longer look like rubric verdicts.

**Defects demonstrated and fixed** (skill version 0.1.1; see `docs/decisions.md` D17 to D20):
- D6 gap: a run with no tools, no evaluator, and a final answer that visibly matches an explicit known criterion could not be reported as `success`; every basis was rejected. Added basis `criteria_match`. Test: `test_criteria_match_basis_allows_success_without_tools_or_evaluator`.
- D7 gap: a bundle produced by `wrap-text` has only `log_line` events, so no category rule could be satisfied and no finding could be filed on a wrapped log. Category and `tool_evidence` rules now warn instead of fail when the references are log lines. Test: `test_log_line_references_warn_instead_of_fail`.
- Undocumented rule: five of nineteen sessions hit "excerpt must not be empty", which the contract did not state. Documented in `evidence-contract.md` and `report-schema.md`; test `test_empty_excerpt_rejected`.
- D15 wording: the taxonomy's "path that would have satisfied the task" implied successful runs cannot have a divergence. Reworded; no schema change.

**Review of disputed diagnoses** (recommendations, not decisions):
- Fixture 08. The explicit criterion says formatting is not specified; the tool result and final output contain 2, 3, 5, 7; the evaluator's rule demands one spelling. The report's `success` is consistent with the criterion and the evidence, and the `evaluation_task_design` finding cites the contradiction between criterion and grader rule. Neither source was given automatic priority. Under 0.1.1 the more accurate basis label is `criteria_match`; the report used `tool_evidence`, which the 0.1.0 checker also accepted. Recommendation: keep the diagnosis.
- Fixture 02. F1 (`tool_selection`, wrong argument name) is supported by e2 and e3. F2 (`instruction_following`, established) rests on "the file must be read with read_file" plus the absence of a successful read. That is an omitted required step, not an identifiable instruction the agent contravened; the agent did attempt `read_file`. Recommendation: the key should make `instruction_following` partial-only for this fixture, and the report's F2 should be `partial`. The key has **not** been changed; see the proposed key revisions below.
- Fixture 10. The report files `reasoning_calculation` with the observation that the answer is wrong and leaves the cause entirely to hypotheses; divergence is `unknown`. It does not claim a reasoning cause. The category name insinuates one. Recommendation: keep the report; consider whether V1 should split "wrong stated conclusion" from "evidenced reasoning error" or route the former to `other_unknown`.

**Proposed key revisions for Leo (not applied):**
- `expected/02-invalid-tool-args.json`: move `instruction_following` from `expected_any` to a `partial_only` list. Effect: skill-run 02 would score a category violation (F2 is `established`).
- `expected/10-wrong-answer-no-cause.json`: no change to allowed categories; add a note that `reasoning_calculation` is accepted only with the cause left unestablished.

## 7. End-to-end test of the release package (0.1.1 ZIP)

Recorded in `e2e/RESULTS.md`. All three sessions auto-invoked the installed skill, ran the packaged helper, passed `check-report` on the first attempt, rendered `report.md`, and stayed within the frozen expectations. Model recorded from the streams: `claude-opus-5-5`. Case files and expectations are in `e2e/`; their hashes match `e2e/FROZEN.sha256`, committed before any session started. The final package differs from the tested one in one documentation file; see the package-hash table there.

## 7a. Final end-to-end test of the exact release package

Recorded in `e2e-final/RESULTS.md`. The three frozen cases were rerun, one
fresh session each, against the exact final package (sha256 `0b93e7c0…`,
built at `77af62c`). All three auto-invoked the installed skill, read the
packaged references, ran the packaged helper, passed `check-report` on the
first executed run, rendered `report.md`, and stayed within the frozen
expectations. Model recorded from the streams: `claude-opus-5-5`.

## 7b. Final freeze

Branch `review/v0-release`; `main` remains at `da42828` and does not contain
the release. No remote exists. Final commit is named in the handoff and in
`git log`. Freeze checks on the final package, recorded in
`e2e-final/RESULTS.md`: 62 tests passed; two rebuilds byte-identical to the
dist ZIP and to the hash recorded at the start of every final session
(`0b93e7c0…`); eight ZIP entries with no evaluation, test, cache, secret, or
personal-identifier content.

## 8. Not executed, or not possible here

- **Physics benchmark trial run**: not performed. See `docs/decisions.md` D13.
- **Independent model**: every session was Claude Code's default model on this machine; see each section for the identifier recorded.
- **Human review of semantic labels**: all are the implementing session's and are marked unreviewed.
- **Codex end-to-end** and **claude.ai upload**: untested.
- **Non-synthetic traces**: none were available.
- **Proposed regression tests and remediations inside the reports**: specifications only; none executed.
