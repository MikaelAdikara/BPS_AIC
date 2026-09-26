# Quality gate: dev-regression-v1.13 (development)

**PASS**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | D rows ok | pass | 35/35 ok [] |
| integrity | one engine version | pass | [('gap-v1.13', 'verify-v2.5')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/12 (0%; 0–24) |
| safety | missing fact held before fact | pass | 13/13 (100%; 77–100) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | pass | 0 finding(s) |
| accuracy | gold_finding_found | pass | 21/21 (100%; 85–100); Wilson low 0.85 vs floor 0.65 |
| accuracy | action_routing | pass | 21/21 (100%; 85–100); Wilson low 0.85 vs floor 0.60 |
| accuracy | membership_precision | pass | 47/47 (100%; 92–100); Wilson low 0.92 vs floor 0.85 |
| accuracy | membership_recall | pass | 47/53 (89%; 77–95); Wilson low 0.77 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 12/13 (92%; 67–99); Wilson low 0.67 vs floor 0.40 |
