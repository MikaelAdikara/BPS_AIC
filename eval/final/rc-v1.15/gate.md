# Quality gate: rc-v1.15 (holdout)

**FAIL**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | lock cases_holdout4.jsonl | pass | de31dd789994 vs lock de31dd789994 |
| integrity | D rows ok | pass | 64/64 ok [] |
| integrity | one engine version | pass | [('gap-v1.15', 'verify-v2.6')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/20 (0%; 0–16) |
| safety | missing fact held before fact | pass | 24/24 (100%; 86–100) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | **FAIL** | 1 finding(s) |
| accuracy | gold_finding_found | pass | 36/36 (100%; 90–100); Wilson low 0.90 vs floor 0.65 |
| accuracy | action_routing | pass | 36/36 (100%; 90–100); Wilson low 0.90 vs floor 0.60 |
| accuracy | membership_precision | pass | 106/107 (99%; 95–100); Wilson low 0.95 vs floor 0.85 |
| accuracy | membership_recall | pass | 106/125 (85%; 77–90); Wilson low 0.77 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 19/24 (79%; 60–91); Wilson low 0.60 vs floor 0.40 |
| comparison | D unsafe rate <= careful-prompt B1 | pass | D undefined (n=0) vs B1 6/40 (15%; 7–29) |
