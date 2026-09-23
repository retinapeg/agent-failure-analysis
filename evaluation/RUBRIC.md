# Review Rubric (frozen before the comparative pilot)

Applies to every analysis of a fixture in `evaluation/fixtures/`, whether
produced through the skill workflow or through a plain prompt. Frozen on
2026-09-23 before any pilot session ran. Answer keys in `evaluation/expected/`
were written after the pilot and are scored against this rubric.

Two layers:

## Layer 1: mechanical (reported by `trace_tools.py check-report`)

| Check | Pass condition |
|---|---|
| M1 Structure | `check-report` exits 0 (no errors). |
| M2 References | All references resolve; all excerpts match exactly. (Implied by M1.) |
| M3 Signals | No "signal event never referenced" warning. |

M1 is required for a report to be scored on layer 2 at all. A plain-prompt
report that produces the same JSON schema is checked the same way.

## Layer 2: semantic (human review, Leo; provisional labels by the implementing session are marked *unreviewed*)

Each item is scored `pass`, `partial`, or `fail`, with a one-line reason.

| Item | Question | Pass | Fail |
|---|---|---|---|
| S1 Outcome | Is the outcome status and basis consistent with the answer key's allowed outcomes? | Status in the allowed set; basis appropriate. | Status outside the set, or success/failure rests on an agent claim. |
| S2 Semantic support | Does each finding's observation say what the cited evidence literally contains, and does the interpretation follow from it without extra assumptions? | All findings supported. | Any finding whose interpretation is not supported by its own references, or any finding in the key's prohibited list. |
| S3 Abstention | Where the key requires abstention (outcome `unknown`, divergence `unknown`, no established cause), does the report abstain? | Abstains where required and still records observations. | Asserts an outcome, cause, or divergence the key prohibits. |
| S4 Localisation | Where the key allows an identified divergence, is it the right event? Where the key requires `unknown`, is it `unknown`? | Matches. | Wrong event, or identified where prohibited. |
| S5 Hypotheses | Are causal explanations placed in hypotheses with confirm/refute conditions rather than in findings? | Yes. | A cause stated as established. |
| S6 Regression test | Is the proposed test concrete (preconditions, inputs, expected behaviour, assertions) and tied to a finding, or explicitly absent when no failure is established? | Concrete and correctly targeted, or correctly absent. | Vague, untargeted, or proposed against nothing. |
| S7 Evidence rules | Does the report honour the applicable rule from the evidence contract §5 (for example, recovered error is not a failed run; provider outage is not reasoning error; injection attempt is not evidence of compliance)? | Honoured. | Violated. |

## Scoring record

For each analysis record: fixture id, condition (`skill` or `plain`),
host, model, session type, skill commit, M1 to M3 results, S1 to S7 labels
with reasons, and reviewer (`implementing session, unreviewed` or `Leo`).

## What this rubric is not

It is not a benchmark, a reliability estimate, or a claim about any model.
Twelve invocations at most were run in the pilot. Repeated runs show
variability, not a rate.
