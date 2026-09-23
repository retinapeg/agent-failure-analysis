# End-to-End Test of the Release Package

Run on 2026-09-23 during the release-validation pass. Three new synthetic
cases, expectations frozen by hash in `FROZEN.sha256` at commit `8fe396c`
before any session ran, and kept outside the repository until all three
sessions had finished. The hashes verified after copying (`shasum -a 256 -c FROZEN.sha256`: all OK).

## What was installed and how the sessions ran

- Package under test: `agent-failure-analysis-0.1.1.zip` built at commit `8fe396c`, sha256 `194a8ddd7188d5901e21d1af44f99231f4e0b37c4239524c69f15e0cc0eb95ab`. Its manifest is saved as `MANIFEST-of-tested-package.txt`.
- Three throwaway project directories outside this repository, each with the ZIP unzipped into `<project>/.claude/skills/` and the case input copied into `<project>/input/`. Nothing else in the project.
- Host: Claude Code 2.1.280, print mode, `--output-format stream-json --verbose`, `--max-turns 60`, Read, Write, Edit, Glob, Grep, Skill, and Bash for `python3`, `mkdir`, `ls`, `cat` pre-approved with `--allowedTools`. That flag pre-approves; it does not restrict: the init event lists all 31 built-in tools as available. Permission mode `default`. No skip-permissions flag.
- Model, recorded from every assistant event in the streams: `claude-opus-5-5` (the CLI's default on this machine). This differs from the V0 subagent sessions, which inherited the building session's model.
- Prompts were natural requests that did not name the skill, so auto-invocation was tested. Case C's prompt gave the task and success criterion in words, since a plain log carries neither.
- Full event streams: `runs/case-*.stream.jsonl`. Outputs as the sessions left them: `outputs/case-*/`. Stderr was empty for all three.

Isolation actually achieved: the sessions could not see this repository
and none of them referenced its path. The frozen expectations and inputs
sat on the same filesystem one directory above each project, readable in
principle; a grep of every tool input in the three streams for the
expectations file, the inputs folder, the freeze file, and the other two
projects found no access. They did share this machine's user-level Claude Code state:
four unrelated personal skills in `~/.claude/skills/`, user settings, and
the harness's own bash-safety filter, which blocked two of case C's shell
commands. That is the isolation available without a second machine.

## Verification from the streams

| Check | Case A | Case B | Case C |
|---|---|---|---|
| Skill listed at session init | yes | yes | yes |
| Skill auto-invoked (Skill tool, `agent-failure-analysis`) | yes, turn 1 | yes, turn 1 | yes, turn 1 |
| Packaged references read | not as separate reads (SKILL.md content is injected by the Skill tool) | yes: all four | not as separate reads |
| Packaged helper executed from `.claude/skills/…/scripts/trace_tools.py` | prepare, check-report, render (5 calls) | prepare, check-report, render (5 calls) | wrap-text, prepare, check-report (7 calls) |
| Source repository path anywhere in the session | no | no | no |
| `check-report` first attempt | ok, 0 errors, 0 warnings | ok, 0 errors, 0 warnings | ok, 0 errors, 1 warning (log_line rule not applicable, reviewer must check) |
| `report.md` rendered by the packaged helper | yes | yes | yes |
| Independent re-check by the implementing session (repo copy of 0.1.1) | ok, 0/0 | ok, 0/0 | ok, 0 errors, same 1 warning |
| Turns / wall time | 15 / 151 s | 18 / 104 s | 20 / 221 s |

Within-session corrections, all visible in the streams and none a rerun:

- All three sessions first wrote `"skill_version": "0.1.0"`, copied from the example in `report-schema.md`, then edited it to `0.1.1` after seeing the helper's version. Fixed after this test by replacing the hard-coded example value (see the note on package hashes below).
- Case B also rephrased one observation from "answers directly without calling a tool" to "the trace records no tool call".
- Case C's first `wrap-text` call omitted `--run-id` and printed usage; the second succeeded. Two later shell commands were blocked by the Claude Code bash-safety filter ("expansion obfuscation"), so the session wrote a short Python file in its own temp directory to add the success criterion (given in the prompt) to the wrapped bundle. It kept the events byte-identical, recorded the addition in `provenance.notes`, and kept the untouched wrap-text output as `bundle.wrapped.json`. This is a usability gap: `wrap-text` accepts `--task` but not criteria or tool policy. Not changed in this pass; proposed for V1.

## Outcomes against the frozen expectations

| Case | Input | Outcome / basis | Findings | Divergence | Regression | Vs frozen expectations | Semantic read (unreviewed) |
|---|---|---|---|---|---|---|---|
| A evidenced failure | bundle, evaluator fail | failure / evaluator_observation | `instruction_following` (established) | identified e2 | proposed, targets F1 | matches on all five items | The command text alone establishes the constraint breach; the report keeps "e2 is what deleted app.log" as a hypothesis because the trace has no pre-run listing. No prohibited claim. |
| B success, optional tools unused | bundle, no evaluator, no tools | success / criteria_match | none | unknown ("no divergence observed") | none | matches; exercises the new `criteria_match` basis | States that success is the analyst's criteria match, not an independent grade. Dismisses the no-tool signal with the policy cited. No prohibited claim. |
| C insufficient evidence | plain log, wrapped by the session | unknown / none | `tool_execution` (partial) | identified L6 | proposed, targets F1 | matches; the partial finding is within the frozen partial-only allowance; exercises the log-line warning path | Says plainly the log cannot decide the outcome, lists the retry result as the missing item, and offers five hypotheses. No prohibited claim. |

Three cases, one model, one run each. This shows the package installs,
triggers, runs its helper, validates, and renders in a fresh project, and
that on these three cases the reports stayed inside the frozen expectations.
It is not a reliability estimate. The expectations are the implementing
session's, written before the runs but not reviewed by anyone else.

## Package hashes

| Package | Commit | sha256 | Covered by |
|---|---|---|---|
| 0.1.1 as tested here (not kept on disk; `dist/` is ignored. The build is byte-stable, so checking out `8fe396c` and running `python3 scripts/build_release.py` reproduces this hash) | `8fe396c` | `194a8ddd7188d5901e21d1af44f99231f4e0b37c4239524c69f15e0cc0eb95ab` | the three sessions above |
| 0.1.1 final (after the `report-schema.md` example fix) | review commit | `b06149d07e200fb1c9f4c1be60250696a188d4cd8c35e261db6a894263aeecfb` | **no end-to-end run**; differs from the tested package only in `references/report-schema.md` (one example value), per the manifest diff recorded in the commit message |
