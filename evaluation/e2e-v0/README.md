# Second end-to-end test: the 0.1.0 package as committed at `da42828`

Run on 2026-09-23 by the second release-validation session (this pass ran
concurrently with the one recorded in `evaluation/e2e/`; the two used
different cases, different models and different packages, and neither saw
the other's expectations). Everything here is model-authored and
provisional until Leo reviews it. Three cases are not a reliability estimate.

## Package under test

`agent-failure-analysis-0.1.0.zip` built from a `git archive` of commit
`da42828` (the V0 release candidate as committed on `main`), sha256
`62c1e54d2e738f08de5be48bed19626c7834619d706ad56aaee3ad9e78ea74c6`. The
same hash was obtained three times (twice from the working tree before the
concurrent pass changed it, once from the archive), and matches the
`dist/` file that existed at the start of the pass. It is **not** the
0.1.1 package that `dist/` now holds; see "Coverage" below.

## Freeze

`cases/`, `expected/` and `protocol.md` were written and committed to a
scratch git repository (commit `8203061`, 2026-09-23 15:22:37 +0100,
outside this repository) before the first session started (15:22:55
+0100). `FROZEN.sha256` lists their hashes; `shasum -a 256 -c
FROZEN.sha256` from this directory must pass. The files were copied here
after the runs. The throwaway projects contained only the installed skill
and `input/bundle.json`.

## Sessions

Host Claude Code 2.1.280, print mode, model `claude-fable-5-1` (recorded
in the init event, every assistant event and the result usage), permission
mode `default`, no MCP servers, tools `Bash, Edit, Glob, Read, Skill,
Write`. The four user-level skills were not listed (user settings turn
them off). The `advisor` tool was **not** in the tool list; the name
appears only in the session's slash-command list. Exact command and
prompt: `protocol.md`. Per-session facts: `runs/*/session.txt`. Tool
calls, helper results and the final message, with paths relativised and
session identifiers removed: `runs/*/tool-calls.txt`. Raw streams stay
outside the repository.

| Evidence from the transcript | A | B | C |
|---|---|---|---|
| Skill listed at init | yes | yes | yes |
| `Skill` tool invoked with `agent-failure-analysis` | call 01 | call 01 | call 01 |
| Packaged references read | 4 via `Read` (calls 03–06) | 3 via `cat` (call 03; `bundle-schema.md` not read) | 4 via `Read` (03–06) |
| Packaged helper run from `.claude/skills/…/trace_tools.py` | prepare, check-report, render | prepare, check-report+render, check-report+render, render | prepare, check-report, render |
| `check-report` first attempt | ok, 0 errors, 0 warnings | ok, 0/0 | ok, 0/0 |
| `report.json` writes / within-session edits | 1 / none | 1 / one `Edit` after the check passed (added two `ts` references to a key event; re-checked ok) | 1 / none |
| `report.md` rendered by the packaged helper | yes | yes (second render needed `--force`) | yes |
| Repository, `expected/`, `frozen/` paths in the transcript | none | none | none |
| Turns / wall time | 14 / 192 s | 12 / 130 s | 15 / 157 s |

Within-session events that were not reruns:

- B and C: the session's `mkdir -p work` was blocked by the host
  ("may only create directories in the allowed working directories"),
  although `work/` is inside the project. Both sessions continued; the
  helper's `prepare` creates the directory itself. Host behaviour, not a
  skill defect, but SKILL.md's "Work in a fresh output directory" invites
  the blocked command.
- B: after editing `report.json` post-pass, the chained
  `check-report && render` failed with exit 2 because `render` refuses to
  overwrite `report.md` without `--force`. The session re-ran with
  `--force`. SKILL.md does not mention `--force` for the re-render.
- The `Bash(python3 *)` allowlist did not stop `ls` and `cat`: the host
  auto-approved those read-only commands. Isolation was therefore by
  prompt and transcript inspection, as `protocol.md` says.

## Outcomes against the frozen expectations

`check.json` in each run folder is an independent re-check with the
0.1.0 helper from the `da42828` archive; all three are `ok` with no
warnings. `report.md` in each folder equals a fresh deterministic render.

| Case | Outcome / basis | Findings | Divergence | Regression test | Vs frozen key |
|---|---|---|---|---|---|
| A evidenced failure (wrong key edited, claim contradicted by read-back) | failure / tool_evidence | `instruction_following` (established), `reasoning_calculation` (established) | identified **e4** | proposed, targets F1, F2 | outcome, divergence, regression: match. Categories: key listed `instruction_following` as partial-only; the report filed it as established, citing criterion 2 ("other keys unchanged") and the e4 content. That is an identifiable instruction violated, so the key was stricter than the evidence; recorded here, key left as frozen. No prohibited claim. |
| B success, optional tool unused | success / evaluator_observation | none | unknown ("no divergence to identify") | none | match on every item. The no-tool signal is dismissed in the coverage note with the policy cited. |
| C vague task, no criteria, no evaluator | unknown / agent_claim | none | unknown | none | match on every item. Four missing-information entries; three hypotheses, one of which (the removal lost wanted information) is the counter-reading. |

## Coverage

These runs cover the committed 0.1.0 package only. The 0.1.1 package
now in `dist/` (sha256
`b06149d07e200fb1c9f4c1be60250696a188d4cd8c35e261db6a894263aeecfb`) has
no end-to-end run of its own from either pass; the concurrent pass tested
the intermediate 0.1.1 build `194a8ddd…` (see `evaluation/e2e/RESULTS.md`).
