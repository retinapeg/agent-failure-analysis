# Final End-to-End Test of the Release Package (V0.1.1)

Run on 2026-09-23 as the final release check. Same three frozen cases and
the same frozen expectations as `evaluation/e2e/` (hashes in
`evaluation/e2e/FROZEN.sha256`, committed at `8fe396c`, verified again
before and after this run; expectations were not altered). Prompts verbatim
in `evaluation/e2e/PROMPTS.md`.

## Package under test

`dist/agent-failure-analysis-0.1.1.zip`, sha256
`0b93e7c01de2ebdbfb2a96001fb2b01b8e5100d7f902d6ff392552b51d8c4a9a`, built at
commit `77af62c`. The hash was recorded at the start of each session
(`runs/case-*.zip-hash-at-start.txt`) and the manifest of the installed copy
in each project (`outputs/case-*/installed-MANIFEST.txt`) equals the
manifest inside the dist ZIP. This package differs from `b06149…` only in
`references/evidence-contract.md` (the D17 sentence).

## How each session ran

- A fresh throwaway project directory outside this repository per case, containing only `.claude/skills/agent-failure-analysis/` (unzipped from the ZIP above) and `input/`.
- Host: Claude Code 2.1.280, print mode, `--output-format stream-json --verbose`, `--max-turns 60`, permission mode `default`. Read, Write, Edit, Glob, Grep, Skill, and Bash for `python3`, `mkdir`, `ls`, `cat` were pre-approved with `--allowedTools`; that flag does not restrict, and the init event lists all 31 built-in tools.
- Model: the init event reports `claude-opus-5-5[1m]`; every assistant event reports `claude-opus-5-5`. Session ids: A `c765232c-1464-4fa7-a5f0-06100c286f57`, B `e9163f33-aa65-4087-a8bb-3125f3ade6c7`, C `1ced2109-222b-4b54-bbbb-c84c45a40230`.
- One session per case, first attempt. Full streams in `runs/`. Each `runs/case-*.stderr` holds only the CLI notice "Warning: no stdin data received in 3s, proceeding without it", which is harmless.
- Isolation: no tool input in any stream references this repository, the expectations file, the freeze file, the inputs folder, or another throwaway project. The sessions did share this machine's user-level Claude Code state (four unrelated personal skills, user settings, and the host's bash-safety filter).

## Criteria, per case, from the streams

| # | Criterion | Case A | Case B | Case C |
|---|---|---|---|---|
| 1 | Fresh isolated project | yes | yes | yes |
| 2 | Exact final ZIP installed | yes, `0b93e7…` | yes, `0b93e7…` | yes, `0b93e7…` |
| 3 | Nothing resolved to the source repository | verified | verified | verified |
| 4 | One fresh first-attempt session | yes, 7 turns, 81 s | yes, 7 turns, 33 s | yes, 9 turns, 77 s |
| 5 | Host and model recorded | 2.1.280 / `claude-opus-5-5` | same | same |
| 6 | Installed skill triggered | Skill tool, `agent-failure-analysis`, turn 1 | same | same |
| 7 | Packaged references used | `cat $S/references/*.md` (all four), content in the tool result | same | same |
| 8 | Packaged helper executed | `prepare`, `check-report`, `render` from `.claude/skills/…/scripts/trace_tools.py` | same | `wrap-text`, `prepare`, `check-report`, `render` |
| 9 | `report.json` passes the checker | first executed run: ok, 0 errors, 0 warnings | same | same |
| 10 | `report.md` rendered by the helper | yes | yes | yes |
| 11 | Matches frozen expectation | yes (below) | yes | yes |
| 12 | Corrections recorded | one, below | one, below | one, below |

Independent re-check by the implementing session using the **installed**
helper copy in each project (not the repository copy): all three reports
`ok` with zero errors and zero warnings; `render` succeeds.

## Within-session corrections (all visible in the streams; none replaced a first attempt)

Every session's first attempt to write `report.json` was a shell heredoc
(`cat > work/report.json <<'EOF' …`), which the host's bash-safety filter
refused with "Contains brace with quote character (expansion obfuscation)".
Each session then wrote `report.json` once with the Write tool and ran the
checker, which passed. Cases B and C reworded some prose between the blocked
heredoc and the Write; the substance is the same and both versions are in the
streams. No `report.json` was edited after a check. Case C
also ran `wrap-text -h` once alongside its real `wrap-text` call.

Case C wrapped the log with `--task` only, so `success_criteria` stayed
`unknown` in the bundle and the criterion given in the prompt appears only
in the report's coverage note and statement. The session did not pass
`--synthetic`, so the wrapped bundle records `synthetic: false` for a log
that is in fact synthetic; the prompt had not said so. Both are consequences
of `wrap-text` having no criteria or policy flags (D22, deferred).

## Outcomes against the frozen expectations

| Case | Outcome / basis | Findings | Divergence | Regression | Vs frozen expectation |
|---|---|---|---|---|---|
| A evidenced failure | failure / evaluator_observation | `instruction_following` (established); `reasoning_calculation` (partial: the final message omits the .log deletion) | identified e2 | proposed, targets F1, F2 | matches: outcome, expected category present, no prohibited category, divergence e2, test proposed. The second finding is not in the expectation's prohibited list; its interpretation is marked partial. No prohibited claim: the pre-run existence of app.log is attributed to the evaluator, and "why" is left to hypotheses. |
| B success, optional tools unused | success / criteria_match | none | unknown ("no departure observed") | none | matches on every field; the statement says the success is the analyst's criteria match, not an evaluator verdict. |
| C insufficient evidence (plain log) | unknown / none | none | identified L6 | none | matches: `unknown` with basis `none`, no finding, divergence at L6 is in the allowed set, no regression. Retry result named as the deciding missing item. No prohibited claim. |

## Comparison with the earlier run (`evaluation/e2e/`, package `194a8d…`)

Same outcomes, bases, and divergence statuses in all three cases. Differences:
case A now carries a second, partial finding about the misleading completion
message; case C now files no finding where the earlier run filed a partial
`tool_execution` finding, and this time did not add the criterion to the
bundle. Both variants sit inside the frozen expectations. Two runs of one
model per case show variation, not a rate.

## Adversarial verification of this record

After the three sessions, five further agents of the implementing session's
model checked this record (they are not independent of that model). Three
refuters, one per case, were told to prove the case fails any of the twelve
criteria or the frozen expectation; each returned `pass` on all twelve with
in-stream evidence and no prohibited claim found. One auditor confirmed from
git objects that the only packaged change since `c36f168` is the criteria_match
row of `evidence-contract.md`, that no original evaluation artefact was
modified, that two rebuilds are byte-identical to the dist ZIP, that the ZIP
holds eight entries with no evaluation, test, cache, secret, or personal
identifier content, and that the suite passes. A completeness critic then
listed record-level corrections, all of which are applied in this file, the
README, `docs/decisions.md`, and `evaluation/e2e/RESULTS.md`. It also
confirmed from the host transcripts that all three sessions received the
`PROMPTS.md` text verbatim.

## Freeze record for this package

Run by the implementing session after the sessions and again after the
verification:

```
python3 -m pytest -q            -> 62 passed
python3 scripts/build_release.py (twice, separate directories)
cmp r1 r2; cmp r1 dist          -> byte-identical
shasum -a 256 dist/agent-failure-analysis-0.1.1.zip
  -> 0b93e7c01de2ebdbfb2a96001fb2b01b8e5100d7f902d6ff392552b51d8c4a9a
unzip -l                        -> 8 entries, all under agent-failure-analysis/
grep of extracted files for evaluation/, __pycache__, private keys, AKIA, sk-, the user name -> none
```

The hash equals the one recorded at the start of each session, so the final
package is the tested package.

## Result

All three cases pass the release criteria against the exact final package.
V0.1.1 is recorded as **release-ready for Leo's review**. The expectations
and every semantic label are model-written and provisional; three cases are
not a reliability estimate.
