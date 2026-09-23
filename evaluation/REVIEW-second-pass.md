> Historical note added 2026-09-23 after the final release check: statements below that the 0.1.1 package in `dist/` (`b06149…`) is final or has no end-to-end run are superseded. The final package is `0b93e7c0…`, built at `77af62c`, and was run end to end on the three frozen cases; see `evaluation/e2e-final/RESULTS.md`. The rest of this file is unchanged.

# Release-validation review, second pass (2026-09-23)

Written by a second Claude Code session (`claude-fable-5-1`, Claude Code
2.1.280) that ran the release-validation brief at the same time as the
session that produced commits `8fe396c`, `89f80da` and `e07cf02` on
`review/v0-release`. That other session is the one that built V0; this one
is not. Neither session saw the other's end-to-end expectations before its
own runs. This document records what this pass verified independently,
where it disagrees, and what it found that the first pass did not. Nothing
here is approved by anyone; every recommendation is proposed.

Conventions: `da42828` is the V0 release candidate as committed on `main`
(skill 0.1.0). `e07cf02` is the head of `review/v0-release` at the time of
writing (skill 0.1.1). Line references name the commit they were read at.

## 1. What this pass reproduced

| Claim | Result | Evidence |
|---|---|---|
| Tests at `da42828` | 59 passed (pytest 9.1.1, Python 3.11.5); per file 23/10/24/2 | run in a `git archive da42828` copy (an earlier run in the working tree also passed 59, but its timing relative to the concurrent edits is not recorded) |
| Tests at `e07cf02` | 62 passed; per file 23/10/27/2 (`pytest --collect-only`) | working tree, clean |
| 0.1.0 ZIP byte-identical rebuild | yes, sha256 `62c1e54d2e738f08de5be48bed19626c7834619d706ad56aaee3ad9e78ea74c6`, 23,949 bytes, 8 entries | built twice from the tree and once from the archive; all equal to the `dist/` file present at the start |
| 0.1.1 tested ZIP (first pass, `8fe396c`) | reproduced, `194a8ddd7188d5901e21d1af44f99231f4e0b37c4239524c69f15e0cc0eb95ab`; its MANIFEST equals `evaluation/e2e/MANIFEST-of-tested-package.txt` | built from `git archive 8fe396c` |
| 0.1.1 final ZIP (`e07cf02`) | `b06149d07e200fb1c9f4c1be60250696a188d4cd8c35e261db6a894263aeecfb`, 24,981 bytes; differs from the tested ZIP only in `references/report-schema.md` line 11 | rebuilt to scratch, `cmp` equal to `dist/`; per-file `cmp` of both ZIPs |
| ZIP contents | one top-level folder; SKILL.md, four references, `trace_tools.py`, INSTALL.md, MANIFEST.txt; every manifest hash verifies; no `evaluation/`, `tests/`, `__pycache__`, `.pyc`, answer keys, fixtures, absolute paths or secret-pattern hits | `unzip -l`, `shasum -c`, grep |
| Caches | `__pycache__/` and `.pytest_cache/` exist on disk but are untracked and ignored; never enter the ZIP | `git ls-files`, `git status --ignored` |
| 19 saved check records | all 19 `check.json` files reproduce byte-for-byte when `check-report` is re-run against the fixture as snapshot with a fresh `evidence.json` | scripted re-run |
| 13 saved `report.md` | all reproduce byte-for-byte from `render` | scripted re-run |
| `examples/` | the four bundles equal fixtures 01, 08, 07, 03; the four reports equal `skill-runs/01`, `skill-runs/08`, `pilot/07-skill-r1`, `pilot/03-skill-r1`; every `snapshot.sha256` matches | `cmp`, `shasum` |
| Original artifacts across the first pass | no file under `evaluation/pilot`, `skill-runs`, `expected`, `fixtures`, `PROMPTS.md`, `RUBRIC.md` or `examples/` was modified or deleted between `da42828` and `e07cf02`; two files were added (see 4.3) | `git diff --diff-filter=MD` |
| Skill drift during V0 evaluation | `skills/`, `evaluation/fixtures`, `RUBRIC.md` are identical between `1e4eb0d` (the commit the 19 sessions used) and `da42828` | `git diff --stat` |

## 2. Accounting audit of the V0 evaluation (independent of the first pass)

Separated measurements over the 19 saved reports, computed from the saved
`check.json` files and the reports themselves:

- **Reference validity** (every event id and pointer resolves, every excerpt
  is an exact substring): 19 of 19. No `does not resolve` or `not found`
  error appears in any record. The two "empty excerpt" errors are a format
  rule, not a wrong citation; they are counted under schema below, which
  differs from the first pass's table in `RESULTS.md` §2, where they sit
  under "Reference validity". Either placement is defensible; the rule
  should be stated once. This pass's reading: an empty excerpt cites a real
  location and proves nothing, so it is a schema-format violation.
- **Schema/format compliance**: 16 of 19. Failures: `03-plain-r2` (empty
  excerpt), `05-plain-r1` (empty excerpt, regression test without targets),
  `07-plain-r2` (category evidence rule). All three are plain-condition
  reports. The category rule is a structural safeguard (D7), so
  `07-plain-r2` is also the one case where the guard caught an unsupported
  diagnosis.
- **Outcome vs key**: 19 of 19. **Localisation vs key**: 19 of 19.
  **Regression test present as the key expects**: 15 of 19; the four
  `partial` results are plain-condition tests proposed where no failure was
  established (05-plain-r1, 05-plain-r2, 07-plain-r1, 07-plain-r2).
- **Key-prohibited categories**: 4 plain reports. Read individually:
  `03-plain-r2` F3 (`instruction_following`, "positive finding"),
  `05-plain-r2` F1 (`other_unknown`, "No failure is present"),
  `07-plain-r1` F1 (`other_unknown`, "evidence gap, not demonstrated agent
  error") are truthful statements filed in the findings field: placement
  errors, not false diagnoses. `07-plain-r2` F1 asserts as `established`
  that "the recording/harness failed to capture the remainder of the run
  (or the run was terminated)" with nothing but the truncation to cite: an
  unsupported diagnosis. This matches the first pass's split (1 unsupported,
  3 placement).
- **Semantic support and regression-test usefulness** for the nine skill
  reports: this pass read `skill-runs/02`, `08` and `10` in full; the
  outcome, key events and divergence of `04`; the findings and divergence
  of `06`; and, for the six pilot skill reports, every finding with its
  references, every divergence statement, the hypothesis statements and
  the regression-test status. No unsupported established claim was found:
  both 03 `environment_provider` findings cite the `ok:false` results and
  the `error` event; 05 and 07 file no finding. The proposed tests in 02,
  08 and 10 are concrete (preconditions, inputs, assertions) and targeted;
  the tests in 04, 06, 03 and the pilot reports were not read for
  usefulness. These are this session's labels, unreviewed.

What the repository cannot show, stated the same way as the first pass and
confirmed here: the skill-condition iteration counts are self-reported
except `03-skill-r2`; the "keys written after the runs" ordering is
consistent with the commit history (`1e4eb0d` 14:23:35, `8e533bd`
14:38:55) but is not provable from it; the read restriction in
`PROMPTS.md` was an instruction, not an enforcement.

## 3. Semantic decisions (this pass's reading)

- **D6 / fixture 08.** Resolved against the explicit criterion
  ("formatting not specified") and the evidence (e3 output and
  `final_output` both contain 2, 3, 5, 7): the answer meets the criterion;
  the grader rule contradicts the criterion as supplied. `success` with an
  `evaluation_task_design` finding is the supported reading. The first
  pass's `criteria_match` basis (D17) is the right *shape* for this, but it
  is a contract change (new enum value, new checker rule, SKILL.md text)
  made without approval; see §6. One further point on the key: allowing
  `failure / evaluator_observation` "only with `evaluation_task_design`"
  is self-contradictory. A report that establishes the grader is defective
  cannot rest the outcome on that grader. Recommend removing that allowance
  in a key addendum.
- **Fixture 02.** Agrees with the first pass: F1 (`tool_selection`) is
  established by e2/e3; F2 (`instruction_following`, established) rests on
  a required step not completing, not on an instruction contravened; the
  identifiable act is e4 (reporting a value the task frame says could only
  come from the file). `partial` is the supportable label; key should say
  `partial_only`. Not changed.
- **Fixture 10.** Agrees: the report withholds cause, leaves divergence
  unknown, and puts causes in hypotheses. The taxonomy row
  `reasoning_calculation` literally covers "stated conclusion is wrong in a
  way the evidence shows", so the report complies; the slug implies a cause
  it does not claim. Taxonomy wording is Leo's decision.
- **D7.** The first pass fixed the `log_line` case (D18). Two further
  structural rejections of sufficient evidence remain in 0.1.1; see 4.1.
- **D15 / fixture 04.** The `skill-runs/04` report says divergence
  `unknown` "records that there is no divergence to identify". The first
  pass reworded the taxonomy (D19) and left the `none_observed` value
  proposed. Agrees with leaving the schema alone. Note that
  `expected/04-successful-retry.json` forces `unknown`; under D19's wording
  `identified` at e2/e3 with the recovery stated would also be legitimate,
  so that key should allow both. Not changed.

## 4. Findings of this pass

### 4.1 Reproduced defects in the checker (present in 0.1.0 and 0.1.1, not fixed)

1. **Root-pointer references into `/events/N/...` are valid under the
   contract but never satisfy a category rule.** `evidence-contract.md` §2
   says a pointer without `event_id` resolves from the bundle root, so
   `{"pointer": "/events/2/content/error", "excerpt": "boom"}` is a valid
   reference. `_resolve_reference` classifies it by first path token
   (`trace_tools.py:555-556` at `e07cf02`), giving kind `events`, which no
   `CATEGORY_RULES` entry lists; the `environment_provider` extra check
   (`:749-754`) keys on `event_id` only. Reproduction (both versions): a
   `tool_execution` finding whose only reference is that pointer to a
   failed result is rejected with "needs a reference to a tool_result or
   error event"; the same reference with `event_id: e3` passes. No recorded
   session used the root form, so no run was affected. Minimal fix: when
   `eid is None` and the pointer matches `^/events/(\d+)(/|$)`, set `kind`
   to that event's `kind` and let the `environment_provider` check inspect
   the same event. Not applied in this pass to avoid a third package
   without an end-to-end run; recommended for the next version with a test.
2. **The percentage ban rejects quoted evidence.** `PERCENT` (`:68`) and
   `_no_percent` (`:606`) reject any `\d+%` in `outcome.statement`, finding
   interpretations and hypothesis statements. Quoting the task's own "8%
   sales tax" in an interpretation is rejected ("numeric percentage is not
   allowed ('8%')"). The `skill-runs/01` session wrote "8 percent" in a
   key-event summary and kept "8%" only in the unchecked observation field,
   which is the model working around the rule. Recommend narrowing the rule
   (for example, allow a percentage that appears verbatim in the snapshot,
   or restrict the check to confidence-like phrasing) or documenting it in
   `evidence-contract.md` §6. Design choice; not changed.

### 4.2 Usability gaps seen in this pass's end-to-end runs (0.1.0; unchanged in 0.1.1)

- `render` refuses to overwrite `report.md` without `--force`
  (`write_new`, `:157-159`). SKILL.md step 7 (`SKILL.md:81`) does not say
  so; a session that re-renders after a post-check edit gets exit 2. Seen
  in case B of `evaluation/e2e-v0/`. One-line documentation fix.
- SKILL.md's "Work in a fresh output directory" (`SKILL.md:26`) led two of
  three sessions to run `mkdir -p work`, which the Claude Code host blocked
  even inside the project. `prepare` creates the directory itself; SKILL.md
  could say so. Host behaviour, documented for the next author.

### 4.3 Observations on the first pass's commits (`8fe396c`..`e07cf02`)

Verified true: the freeze commit (`8fe396c`, 15:18:14 +0100) precedes the
first e2e session (stream start 15:18:39 +0100); `FROZEN.sha256` verifies;
all three streams show `Skill` invoked with `agent-failure-analysis`, the
packaged helper run, and first-attempt `check-report` ok; references were
read via `Read` in case B and via `cat` in A and C; no repository or
expectations path appears in any stream; the three output reports re-check
clean under 0.1.1 and re-render identically.

Points to correct or note:

- `evaluation/e2e/RESULTS.md:12` says tools were "limited with
  `--allowedTools`". The init events list the full built-in tool set
  (`Task`, `WebFetch`, `WebSearch`, `SendMessage`, … 31 tools) as
  *available*; `--allowedTools` pre-approved a subset. Unlisted tools would
  have prompted and been denied in print mode, which is a permission limit,
  not an availability limit. Wording only.
- The committed raw streams (`evaluation/e2e/runs/*.stream.jsonl`) contain
  `session_id`, per-message `uuid`s, the host's scratch-workspace paths and
  the user's home-directory path in the memory-path field. Not secrets, but
  more than the record needs; a derived tool-call log would carry the same
  evidence. Hygiene, non-blocking.
- `evaluation/pilot/05-plain-r2/build_report.py` was added inside an
  original pilot output folder. It hard-codes an absolute repository path
  and a long absolute scratch path from the building session. The original
  `report.json` there is unchanged (verified), so this is not a
  preservation violation, but the folder is no longer "as collected", and
  the script's provenance (recovered from the building session's transcript)
  is not stated in the file. Recommend a one-line header or a move to
  `evaluation/pilot/README`-style notes.
- `evaluation/pilot/03-skill-r2/first-attempt-check.json` is likewise a
  post-hoc addition whose source is the building session's transcript;
  this pass cannot verify it.
- The first pass's e2e sessions ran `claude-opus-5-5`; the V0 sessions'
  model is "inferred", and this pass's e2e sessions ran `claude-fable-5-1`
  (recorded). The three sets are therefore not one model, and
  `README.md:118`'s summary should not be read as covering one model.

### 4.4 Packaging notes (non-blocking)

- The ZIP contains no `LICENSE`; `build_release.py` packages only
  `skills/agent-failure-analysis/` (`build_release.py:43-53`). The README
  says MIT. Add `LICENSE` to the ZIP or state that the licence travels
  separately.
- `INSTALL.md` says to check discovery with `/skills`; this pass did not
  verify that an interactive `/skills` command exists in 2.1.280 (the init
  event lists no such slash command). Unverified, not shown wrong.
- Byte-stable rebuild is shown on one machine, one Python (3.11.5) and one
  zlib; identical bytes on other platforms are not established.

## 5. End-to-end coverage by package

| Package | Commit | sha256 | End-to-end runs |
|---|---|---|---|
| 0.1.0 | `da42828` | `62c1e54d…74c6` | 3 sessions, `claude-fable-5-1`, `evaluation/e2e-v0/` (this pass) |
| 0.1.1 tested | `8fe396c` | `194a8ddd…95ab` | 3 sessions, `claude-opus-5-5`, `evaluation/e2e/` (first pass) |
| 0.1.1 final | `e07cf02` | `b06149d0…ecfb` | **none**; differs from `194a8ddd…` in one example line of `report-schema.md` |

## 6. Decisions that need Leo (not made here)

1. Whether to accept the 0.1.1 contract changes made in the first pass
   without prior approval: `criteria_match` basis (D17), `log_line` rules
   downgraded to warnings (D18), taxonomy wording (D19), version bump
   (D20), schema example change (D21). They are tested and documented, but
   they are architecture, and 0.1.0 remains the last package whose exact
   bytes have an end-to-end run.
2. Whether a `none_observed` divergence value is added (D15/D19).
3. Whether `reasoning_calculation` keeps covering "wrong stated conclusion
   with no evidenced reasoning step" (fixture 10).
4. The two key revisions (02 `partial_only`; 08 remove the
   `failure/evaluator_observation` allowance; 04 allow `identified` with
   recovery) and this pass's own key disagreement on e2e case A
   (`instruction_following` established vs the key's partial-only).
5. Whether to fix 4.1 (root-pointer kinds; percentage rule) before release,
   which would produce a third package and require a further end-to-end run.

## 7. Release blockers versus limitations, as this pass sees them

Blocking until decided: item 6.1 (the shipped package's contract is not
the reviewed one), and the fact that the final 0.1.1 bytes have no
end-to-end run (§5).

Non-blocking: 4.1, 4.2, 4.3 wording and hygiene points, 4.4; one model per
evaluation set; all semantic labels unreviewed; Codex and claude.ai
untested; no non-synthetic trace analysed.
