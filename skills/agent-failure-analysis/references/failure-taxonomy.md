# Failure Taxonomy (V0)

A closed list. A finding's `category` must be one of these slugs. The
taxonomy classifies *findings*; it does not decide the run *outcome*. A run
can carry a `tool_execution` finding and still have outcome `success`.

The **required references** column is enforced by `check-report`: a finding
in that category whose references do not include the listed kind fails the
check. This is the mechanical floor under "do not invent failures"; the
semantic judgement remains the model's and the reviewer's.

| Slug | Covers | Required references |
|---|---|---|
| `instruction_following` | The agent did something the task, constraints, user, or tool policy forbade, or omitted something they required. | At least one of `/task`, `/tool_policy`, or a `user_message` event, plus at least one `assistant_message` or `tool_call` event, or the `/final_output` pointer, showing the act or omission. |
| `tool_selection` | The agent chose a wrong tool, called a tool with arguments that do not fit the situation, or did not use a tool it needed. | At least one `tool_call` event, or the `/tool_policy` pointer when the finding is about a missing call. |
| `tool_execution` | A tool ran and returned an error or an unusable result, and that affected the run. | At least one `tool_result` or `error` event. |
| `reasoning_calculation` | The agent's visible reasoning, arithmetic, or stated conclusion is wrong in a way the evidence shows. | At least one `assistant_message` event, `tool_result` event, or the `/final_output` pointer, containing the wrong statement, plus the evidence that shows it wrong. |
| `environment_provider` | The environment, provider, network, or sandbox failed independently of the agent's choices. | At least one `tool_result` with `ok: false` or an `error` event. |
| `evaluation_task_design` | The task, success criteria, or evaluator is defective, ambiguous, or contradicts the supplied evidence. | At least one of `/task`, `/success_criteria`, or `/evaluator`. |
| `other_unknown` | Something observably went wrong that fits no category, or the category cannot be determined. | Any reference. Interpretation should say why no category fits. |

## Not failures

- A tool error that the agent retried or worked around, when the outcome was
  unaffected. Record it as a key event.
- Tool use absent when policy is `optional` or `unknown`.
- A `failure` evaluator verdict on its own. It is evidence of the evaluator's view.
- Slowness, verbosity, or style.

## Earliest evidenced divergence

Separately from categories, a report may name the earliest event at which the
run observably departs from a path that would have satisfied the task. It is
`identified` only when a specific event can be cited and the observation
alone shows the departure. Otherwise it is `unknown`. A wrong final answer
with no intermediate evidence leaves it `unknown`.
