# E2E protocol (frozen before any session ran)

Package under test: agent-failure-analysis-0.1.0.zip built from commit da42828
(sha256 62c1e54d2e738f08de5be48bed19626c7834619d706ad56aaee3ad9e78ea74c6),
unzipped into `<project>/.claude/skills/`. Each throwaway project contains only
`.claude/skills/agent-failure-analysis/` and `input/bundle.json`. No expectations,
no repository files, no CLAUDE.md.

Prompt (identical for all three sessions; does not name the skill):

    Analyse the recorded agent run in input/bundle.json (an afa-bundle/1 file; the task, success criteria and tool policy are inside it). Write your outputs to the work/ directory of this project. Finish by giving the paths of report.json and report.md and a short summary of the outcome and findings.

Command (cwd = the throwaway project):

    claude -p "$PROMPT" --model claude-fable-5-1 --tools Read,Write,Edit,Bash,Glob,Skill \
      --allowedTools "Bash(python3 *)" Read Write Edit Glob Skill \
      --output-format stream-json --verbose --no-session-persistence --strict-mcp-config \
      --max-turns 80 --system-prompt-snapshot on > out.jsonl 2> err.txt

Deliberate choices: Bash is allowed only for `python3 *` (the helper needs it; the
prefix is broader than the one script, so the interpreter could in principle read any
path). File tools are not confined to the project (no --restricted / --setting-sources,
to avoid hiding the project skill on a first attempt that cannot be repeated); isolation
is therefore by prompt and by transcript inspection, not enforcement. User settings
apply (they turn the four user-level skills off). One session per case; first attempts
recorded; no reruns.
