# Canonical Input Bundle (`afa-bundle/1`)

The skill analyses one JSON file: the **bundle**. It holds the explicit task,
whatever success criteria and tool policy are known, the ordered events of the
run, the final output if available, evaluator observations if available, and
provenance. Any of these may be declared unknown or unavailable. Declaring a
thing unknown is always allowed; guessing it is never allowed.

This is the only analysed format. `trace_tools.py wrap-text` produces a bundle
from a plain text log losslessly (one `log_line` event per line, original text
preserved). Native vendor formats are unsupported; the validator says so
rather than attempting a partial import.

## Top-level object

| Field | Type | Required | Notes |
|---|---|---|---|
| `schema_version` | string | yes | Must be `"afa-bundle/1"`. |
| `run_id` | string | yes | Identifier for the run. |
| `task` | object | yes | `description` (string, required), `constraints` (array of string, optional). |
| `success_criteria` | object | yes | `status`: `known` or `unknown`. If `known`, `criteria`: non-empty array of string. |
| `tool_policy` | object | yes | `status`: `required`, `optional`, `prohibited`, or `unknown`. Optional `tools` (array of string) naming the tools the policy concerns, and `note`. |
| `events` | array | yes | Ordered events, see below. May be empty. |
| `final_output` | object | yes | `status`: `available` or `unavailable`. If available, `text` (string). This is what the agent produced, not a judgement of it. |
| `evaluator` | object | yes | `status`: `available` or `unavailable`. If available, `observations`: array of `{id, text, verdict?}` with `verdict` one of `pass`, `fail`, `unknown`. Observations are evidence about the evaluator's view; they can be wrong. |
| `provenance` | object | yes | `source` (string, required), `synthetic` (boolean, required), optional `collected_at`, `notes`, `original_sha256`. |

Unknown top-level fields are a validation warning. Unknown event kinds are an error.

## Events

Each event: `id` (string, unique in the bundle), `kind` (string), `content`
(object), optional `ts` (ISO 8601 string or epoch number).

| `kind` | Required `content` fields | Optional |
|---|---|---|
| `user_message` | `text` (string) | |
| `assistant_message` | `text` (string) | |
| `tool_call` | `call_id` (string, unique among tool calls), `tool` (string), `args` (object) | |
| `tool_result` | `call_id` (must match an earlier `tool_call`), `ok` (boolean), `output` (string) | `error` (string) |
| `error` | `message` (string) | `call_id`, `fatal` (boolean) |
| `log_line` | `line_number` (integer), `text` (string) | |

## Validation

`trace_tools.py validate bundle.json` reports **errors** (exit 1, the skill
must not analyse) and **warnings** (exit 0, analysed and surfaced as missing
information):

- Errors: not a JSON object, wrong schema version, missing required fields,
  wrong types, duplicate event ids, duplicate `call_id`, unknown event kind,
  `tool_result` without a matching earlier `tool_call`, unknown status
  values, file over the size or event limits.
- Warnings: unknown top-level fields, events without `ts`, timestamps that go
  backwards, `tool_call` with no result, `success_criteria` unknown,
  `tool_policy` unknown, `final_output` unavailable, `evaluator` unavailable,
  empty `events`.

## Limits

Defaults: 5,000,000 bytes and 5,000 events, adjustable with `--max-bytes` and
`--max-events`. Over-limit input is rejected with a clear message. The helper
never analyses a silent subset.

## Snapshot and hash

`trace_tools.py prepare` copies the bundle byte-for-byte to
`<out>/snapshot.json`, writes its SHA-256 to `<out>/snapshot.sha256`, and
writes `<out>/evidence.json`. Reports carry the snapshot hash, and the report
checker recomputes it.

## Minimal example

```json
{
  "schema_version": "afa-bundle/1",
  "run_id": "demo-001",
  "task": {"description": "Print hello"},
  "success_criteria": {"status": "known", "criteria": ["stdout contains 'hello'"]},
  "tool_policy": {"status": "optional"},
  "events": [
    {"id": "e1", "kind": "tool_call", "ts": "2026-01-01T00:00:01Z",
     "content": {"call_id": "c1", "tool": "bash", "args": {"cmd": "echo hello"}}},
    {"id": "e2", "kind": "tool_result", "ts": "2026-01-01T00:00:02Z",
     "content": {"call_id": "c1", "ok": true, "output": "hello\n"}},
    {"id": "e3", "kind": "assistant_message", "ts": "2026-01-01T00:00:03Z",
     "content": {"text": "Done: printed hello."}}
  ],
  "final_output": {"status": "available", "text": "Done: printed hello."},
  "evaluator": {"status": "unavailable"},
  "provenance": {"source": "hand-written example", "synthetic": true}
}
```
