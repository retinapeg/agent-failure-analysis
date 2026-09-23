# End-to-end prompts (verbatim)

Used unchanged for the `evaluation/e2e/` run (package built at `8fe396c`) and
the `evaluation/e2e-final/` run (final package). Sent as the single `-p`
argument to `claude` from inside each throwaway project. The skill is not
named, so auto-invocation is exercised.

Cases A and B:

```
I have a recorded agent run in input/bundle.json. Please analyse what happened, whether the run failed, which failures the evidence actually supports, what remains a hypothesis, and what regression test would catch a recurrence. Put every output file under work/ in this project. Work only inside this project directory.
```

Case C:

```
I have a plain text log of an agent run in input/run.log. The task the agent was given was: Deploy the docs site to staging. The success criterion is: https://staging.example/docs serves the new build. Please analyse what happened, whether the run failed, which failures the evidence actually supports, what remains a hypothesis, and what would be needed to decide. Put every output file under work/ in this project. Work only inside this project directory.
```

Flags: `--output-format stream-json --verbose --max-turns 60 --allowedTools "Read" "Write" "Edit" "Glob" "Grep" "Skill" "Bash(python3:*)" "Bash(python3 *)" "Bash(mkdir:*)" "Bash(mkdir *)" "Bash(ls:*)" "Bash(ls *)" "Bash(cat:*)" "Bash(cat *)"`, wrapped in `perl -e 'alarm 1500; exec @ARGV'`.
