# Agent Run Analysis

**Run:** `syn-01-calculation-mistake`  
**Source snapshot:** `snapshot.json` sha256 `6d33846517939fe88f9ff42410dbd99edc3b7721471209f189b4432a82a88fa4`  
**Skill version:** `0.1.0` (report `afa-report/1`)

> Reference validity confirms that cited locations and excerpts exist in the snapshot. It does not confirm that any interpretation follows from them.

## Task, criteria, and evidence coverage

- Task: `/task/description`
- Success criteria: **known**
- Tool policy: **optional**
- Events reviewed: 6 of 6. All six events were read in full from snapshot.json (no field was truncated in evidence.json). prepare emitted no validation warnings and no signals (signal_event_ids is empty: no failed tool results, error events, unpaired or orphan calls, repeated identical calls, completion keywords, or instruction-like text), so there is nothing to dismiss. The bundle is declared synthetic in provenance; no real agent produced these events.

## Outcome

**FAILURE** (basis: `evaluator_observation`)

The evaluator observation o1 records a fail verdict, stating the expected value was 40.50 and the produced value was 40.30. Evaluator observations can be wrong, but here the final output is directly comparable to the known success criterion: the criterion requires a final answer equal to 40.50 and the final output reads 'Total: 40.30'. The trace's own tool results (subtotal 37.5, tax 3.0) are consistent with 40.50 rather than 40.30. The run did not satisfy the task.

References: `/evaluator/observations/0/verdict` "fail"; `/evaluator/observations/0/text` "Expected 40.50, got 40.30."; `/success_criteria/criteria/0` "Final answer equals 40.50"; `/final_output/text` "Total: 40.30"; `ev:e3 /content/output` "37.5"; `ev:e5 /content/output` "3.0"

## Key observable events

- `e1`: User message states the task: 3 items at 12.50 each plus 8 percent sales tax, total to two decimal places. It matches /task/description. References: `ev:e1 /content/text` "Compute the total cost of 3 items priced at 12.50 each plus 8% sales tax. Report the total to two decimal places."; `/task/description` "Compute the total cost of 3 items priced at 12.50 each plus 8% sales tax."
- `e2`: Agent calls the calculator tool (call c1) with expression '3 * 12.50' to compute the subtotal. Tool use is permitted under the optional tool policy. References: `ev:e2 /content/args/expression` "3 * 12.50"; `/tool_policy/status` "optional"
- `e3`: Calculator result for c1 returns ok with output '37.5', the correct subtotal. References: `ev:e3 /content/output` "37.5"
- `e4`: Agent calls the calculator tool (call c2) with expression '37.50 * 0.08' to compute the tax on the subtotal. References: `ev:e4 /content/args/expression` "37.50 * 0.08"
- `e5`: Calculator result for c2 returns ok with output '3.0', the correct tax amount for the submitted expression. References: `ev:e5 /content/output` "3.0"
- `e6`: Agent's final message states the subtotal as 37.50, the tax as 2.80, and the total as 40.30. The tax figure contradicts the tool output in e5. The final_output text 'Total: 40.30' matches this message. References: `ev:e6 /content/text` "Subtotal is 37.50. Tax at 8% is 2.80. Total: 37.50 + 2.80 = 40.30."; `/final_output/text` "Total: 40.30"

## Findings

### F1: `reasoning_calculation` (evidence: established)

- **Observation:** In e4 the agent submitted the expression '37.50 * 0.08' to the calculator and in e5 the tool returned ok: true with output '3.0'. In e6 the agent's message states 'Tax at 8% is 2.80.' and then 'Total: 37.50 + 2.80 = 40.30.' The final_output text is 'Total: 40.30'. The task description specifies an 8% sales tax on 3 items priced at 12.50 each, and the success criterion is 'Final answer equals 40.50'.
- **Interpretation:** The tax figure the agent stated (2.80) is wrong and is contradicted by the agent's own tool result (3.0) for the exact expression the agent chose. The subsequent addition, 37.50 plus 2.80 giving 40.30, is arithmetically correct given the wrong tax, so the error is confined to the stated tax amount; because the wrong tax propagates into the total, the final answer misses the criterion of 40.50. This is a visible calculation error in the agent's stated conclusion. It is not a tool selection or tool execution problem: both calculator calls were appropriate and both returned correct, usable results. Why the agent stated 2.80 rather than 3.0 is not shown by the trace and is treated as a hypothesis, not a finding.
- **References:** `ev:e6 /content/text` "Tax at 8% is 2.80."; `ev:e6 /content/text` "Total: 37.50 + 2.80 = 40.30."; `ev:e5 /content/output` "3.0"; `ev:e5 /content/ok` "true"; `ev:e4 /content/args/expression` "37.50 * 0.08"; `/final_output/text` "Total: 40.30"; `/task/description` "plus 8% sales tax"; `/success_criteria/criteria/0` "Final answer equals 40.50"

## Earliest evidenced divergence

**Identified** at `e6`: Events e2 through e5 are on a path that would satisfy the task: the subtotal expression and result (37.5) and the tax expression and result (3.0) are correct. The first event that departs from that path is e6, where the agent states the tax as 2.80 instead of the 3.0 returned in e5, and carries that figure into the total 40.30.

References: `ev:e6 /content/text` "Tax at 8% is 2.80."; `ev:e5 /content/output` "3.0"; `ev:e3 /content/output` "37.5"

## Causal hypotheses (not established root causes)

### H1

- **Hypothesis:** The tool result 3.0 from e5 was present in the agent's context but the agent did not use it, instead stating its own tax figure of 2.80 in the final message.
- **Would confirm:** A record of the model input for the turn that produced e6 showing the e5 result (3.0) present in context, together with the same behaviour recurring across repeated runs of the identical prompt in which the tool result is confirmed delivered.
- **Would refute:** A record of the model input for the turn that produced e6 showing that the e5 result was absent, malformed, or attached to the wrong call id.
- **References:** `ev:e5 /content/output` "3.0"; `ev:e6 /content/text` "Tax at 8% is 2.80."

### H2

- **Hypothesis:** The tool result from e5 was recorded in the trace but was not delivered to the model (for example a harness or transport fault between tool execution and the next model turn), so the agent produced a tax figure without the tool output.
- **Would confirm:** Harness or transport logs showing the c2 result was not appended to the model's context, or a model input record for the e6 turn that lacks the e5 output.
- **Would refute:** A model input record for the e6 turn that contains the e5 output '3.0' under call id c2.
- **References:** `ev:e4 /content/call_id` "c2"; `ev:e5 /content/call_id` "c2"; `ev:e6 /content/text` "Tax at 8% is 2.80."

## Missing information

- The model-side input record (context window contents) for the turn that produced e6, including whether the e5 tool result was included and in what form. Discriminates: H1 (result present but not used) from H2 (result not delivered).
- Harness or transport logs for the delivery of tool result c2 to the model. Discriminates: H1 from H2.
- Repeated runs of the same prompt with confirmed tool-result delivery, to see whether the wrong tax figure recurs. Discriminates: Whether H1 describes a reproducible behaviour or a one-off, which the single synthetic run cannot show.

## Proposed remediation

Proposed, not verified: require that every numeric figure in the final answer be taken from a tool result when the calculator has been invoked for that quantity, and add a final calculator call for the total (for example '37.5 + 3.0') so the reported total is a tool output rather than a hand-stated sum. Additionally, a consistency check that compares each number in the final message against the most recent tool outputs and flags any mismatch before the answer is emitted would have caught the 2.80 versus 3.0 discrepancy in e6.

## Proposed regression test (specification, not executed)

Targets: `F1`

**Preconditions**

- The agent under test has access to a calculator tool that returns correct results for arithmetic expressions.
- Tool-result delivery to the model is logged so that the test can confirm each result reached the model's context.

**Inputs**

- Prompt: 'Compute the total cost of 3 items priced at 12.50 each plus 8% sales tax. Report the total to two decimal places.'
- Variants with other item counts, prices, and tax rates whose correct totals are known (for example 2 items at 19.99 with 5 percent tax).

**Expected observable behavior**

- Every intermediate figure stated in the agent's final message (subtotal, tax, total) equals the corresponding calculator output when the agent called the calculator for that quantity.
- The final reported total equals the known correct total, formatted to two decimal places (40.50 for the primary prompt).

**Suggested assertions**

- assert final_answer == '40.50' for the primary prompt
- assert every numeric value in the final message that corresponds to a calculator call equals that call's output (e.g. stated tax == output of '37.50 * 0.08' == 3.0)
- assert no assistant message contains a tax or total figure that differs from the most recent calculator output for the same quantity
- assert all calculator calls returned ok: true (to distinguish an agent error from a tool error)

---

Source sha256 `6d33846517939fe88f9ff42410dbd99edc3b7721471209f189b4432a82a88fa4` · skill `0.1.0`
