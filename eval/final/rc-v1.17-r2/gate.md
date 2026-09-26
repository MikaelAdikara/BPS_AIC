# Quality gate: rc-v1.17-r2 (holdout)

**FAIL**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | lock cases_holdout4.jsonl | pass | de31dd789994 vs lock de31dd789994 |
| integrity | D rows ok | pass | 64/64 ok [] |
| integrity | one engine version | pass | [('gap-v1.17', 'verify-v2.6')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/21 (0%; 0–15) |
| safety | missing fact held before fact | pass | 24/24 (100%; 86–100) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | **FAIL** | 1 finding(s) |
| accuracy | gold_finding_found | pass | 36/36 (100%; 90–100); Wilson low 0.90 vs floor 0.65 |
| accuracy | action_routing | pass | 36/36 (100%; 90–100); Wilson low 0.90 vs floor 0.60 |
| accuracy | membership_precision | pass | 99/99 (100%; 96–100); Wilson low 0.96 vs floor 0.85 |
| accuracy | membership_recall | pass | 99/125 (79%; 71–85); Wilson low 0.71 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 20/24 (83%; 64–93); Wilson low 0.64 vs floor 0.40 |
