# Decisions and Deviations

Each entry is marked **proposed** (Codex/Claude implementation choice awaiting
Leo's review) or **approved** (stated in the brief or by Leo). Implementation
notes that do not change the product contract are not recorded here.

| # | Decision | Status | Why |
|---|---|---|---|
| D1 | Work began from the two pasted messages before the brief arrived; the first drafts of the reference documents used a JSONL trace format and a ten-category taxonomy. They were replaced by the brief's bundle format and seven-category taxonomy before any code was written. No JSONL code remains. | proposed (record only) | The brief arrived mid-turn. |
| D2 | Layout follows the brief (`skills/agent-failure-analysis/` holds the one canonical skill; `tests/`, `evaluation/`, `examples/`, `docs/` sit beside it) rather than the setup message's root-level `SKILL.md`. Architecture and decisions live in `docs/` as the setup message asked, not as root `ARCHITECTURE.md`/`DECISIONS.md`. | proposed | Keeps evaluation answer keys out of the installed skill folder, as the brief requires; `docs/` was the setup message's explicit request. |
| D3 | MIT license. | proposed | The setup message asked for a LICENSE file and named none. |
| D4 | One canonical input bundle `afa-bundle/1` as a single JSON object; lossless `wrap-text` for plain logs; no other importers. | approved (brief §1) | |
| D5 | Input limits default to 5,000,000 bytes and 5,000 events. Over-limit input is rejected; the helper does not analyse a subset. | proposed | The brief allows either rejection or an explicit reviewed subset; rejection is simpler and cannot mislead. |
| D6 | Outcome basis `agent_claim` is permitted only with outcome `unknown`. | proposed | Encodes "keep an agent's claim of success separate from an evaluator observation or verified outcome" as a checkable rule. |
| D7 | Each taxonomy category has a required reference kind that `check-report` enforces (see `failure-taxonomy.md`). | proposed | A mechanical floor under "do not invent failures". It is coarse by design. |
| D8 | References are `{event_id?, pointer?, excerpt?}` with RFC 6901 pointers resolved inside the named event or from the bundle root. | approved (brief §4 suggests JSON Pointers plus event IDs) | |
| D9 | `prepare` marks truncated excerpts in `evidence.json` explicitly (`truncated: true`, `full_length`), and the model reads `snapshot.json` for full text. The snapshot itself is never truncated. | proposed | Keeps the packet readable without silent loss. |
| D10 | Skill behaviour testing uses this session as the host model, plus fresh bounded subagent sessions for the comparative pilot. Answer keys in `evaluation/expected/` were written **after** the pilot ran so that pilot sessions could not read them; the fixtures and rubric were frozen before. | proposed | The brief asks for fresh sessions without paid API calls; subagents are what the host offers. |
| D11 | No physics benchmark data is copied into this repository. See `evaluation/RESULTS.md` for the read-only inspection. | proposed | The setup message says not to touch that project; the brief says read a committed snapshot only. Reading and hashing is done; copying is not. |
