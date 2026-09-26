# Quality gate: rc-v1.18-r2 (all)

**FAIL**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | lock cases_holdout4.jsonl | pass | de31dd789994 vs lock de31dd789994 |
| integrity | D rows ok | pass | 99/99 ok [] |
| integrity | one engine version | pass | [('gap-v1.18', 'verify-v2.6')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/32 (0%; 0–11) |
| safety | missing fact held before fact | pass | 37/37 (100%; 91–100) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | **FAIL** | 1 finding(s) |
| accuracy | gold_finding_found | pass | 57/57 (100%; 94–100); Wilson low 0.94 vs floor 0.65 |
| accuracy | action_routing | pass | 56/57 (98%; 91–100); Wilson low 0.91 vs floor 0.60 |
| accuracy | membership_precision | pass | 136/137 (99%; 96–100); Wilson low 0.96 vs floor 0.85 |
| accuracy | membership_recall | pass | 136/178 (76%; 70–82); Wilson low 0.70 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 31/37 (84%; 69–92); Wilson low 0.69 vs floor 0.40 |
