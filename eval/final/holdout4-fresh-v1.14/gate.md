# Quality gate: holdout4-fresh-v1.14 (holdout)

**PASS**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | lock cases_holdout4.jsonl | pass | de31dd789994 vs lock de31dd789994 |
| integrity | D rows ok | pass | 16/16 ok [] |
| integrity | one engine version | pass | [('gap-v1.14', 'verify-v2.6')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/5 (0%; 0–43) |
| safety | missing fact held before fact | pass | 6/6 (100%; 61–100) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | pass | 0 finding(s) |
| accuracy | gold_finding_found | pass | 9/9 (100%; 70–100); Wilson low 0.70 vs floor 0.65 |
| accuracy | action_routing | pass | 9/9 (100%; 70–100); Wilson low 0.70 vs floor 0.60 |
| accuracy | membership_precision | pass | 28/28 (100%; 88–100); Wilson low 0.88 vs floor 0.85 |
| accuracy | membership_recall | pass | 28/31 (90%; 75–97); Wilson low 0.75 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 5/6 (83%; 44–97); Wilson low 0.44 vs floor 0.40 |
| comparison | D unsafe rate <= careful-prompt B1 | pass | D undefined (n=0) vs B1 4/10 (40%; 17–69) |
