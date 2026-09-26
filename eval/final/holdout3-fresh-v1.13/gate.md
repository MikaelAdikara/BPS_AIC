# Quality gate: holdout3-fresh-v1.13 (holdout)

**FAIL**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | D rows ok | pass | 12/12 ok [] |
| integrity | one engine version | pass | [('gap-v1.13', 'verify-v2.5')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/4 (0%; 0–49) |
| safety | missing fact held before fact | pass | 4/4 (100%; 51–100) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | pass | 0 finding(s) |
| accuracy | gold_finding_found | **FAIL** | 7/7 (100%; 65–100); Wilson low 0.65 vs floor 0.65 |
| accuracy | action_routing | pass | 7/7 (100%; 65–100); Wilson low 0.65 vs floor 0.60 |
| accuracy | membership_precision | **FAIL** | 21/22 (95%; 78–99); Wilson low 0.78 vs floor 0.85 |
| accuracy | membership_recall | pass | 21/24 (88%; 69–96); Wilson low 0.69 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 4/4 (100%; 51–100); Wilson low 0.51 vs floor 0.40 |
| comparison | D unsafe rate <= careful-prompt B1 | pass | D undefined (n=0) vs B1 1/8 (12%; 2–47) |
