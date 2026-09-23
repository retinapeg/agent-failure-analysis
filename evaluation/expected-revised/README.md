# Revised answer keys

Keys in this folder supersede the same-named files in `evaluation/expected/`
for scoring, per Leo's release decisions of 2026-09-23. The originals are
kept unchanged as the historical record. Score with:

```
python3 evaluation/score.py --keys evaluation/expected-revised evaluation/skill-runs/02/report.json evaluation/skill-runs/10/report.json
```

Both keys were written after the recorded runs by the implementing session.
They are development labels, not independent ground truth. The condition
fields (no asserted cause for fixture 10; a cited violated instruction for
fixture 02) need a reader; `score.py` checks only category, status, and
divergence.
