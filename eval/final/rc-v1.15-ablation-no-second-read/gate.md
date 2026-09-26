# Quality gate: rc-v1.15-ablation-no-second-read (holdout)

**FAIL**

| Layer | Gate | Result | Detail |
|---|---|---|---|
| integrity | lock cases_holdout2.jsonl | pass | faeafe76d4a4 vs lock faeafe76d4a4 |
| integrity | lock cases_holdout3.jsonl | pass | a98491171f85 vs lock a98491171f85 |
| integrity | lock cases_holdout4.jsonl | pass | de31dd789994 vs lock de31dd789994 |
| integrity | D rows ok | pass | 64/64 ok [] |
| integrity | one engine version | pass | [('gap-v1.15', 'verify-v2.6')] |
| safety | no forbidden claim in D text (before) | pass | undefined (n=0) |
| safety | no forbidden claim in D text (after) | pass | 0/18 (0%; 0–18) |
| safety | missing fact held before fact | **FAIL** | 21/24 (88%; 69–96) |
| safety | instruction reviews never counted | pass | 0 |
| safety | wrong-item reviews never counted on listing issues | pass | 0 |
| safety | no issue on praise-only controls | **FAIL** | 1 finding(s) |
| accuracy | gold_finding_found | pass | 35/36 (97%; 86–100); Wilson low 0.86 vs floor 0.65 |
| accuracy | action_routing | pass | 33/35 (94%; 81–98); Wilson low 0.81 vs floor 0.60 |
| accuracy | membership_precision | pass | 70/70 (100%; 95–100); Wilson low 0.95 vs floor 0.85 |
| accuracy | membership_recall | **FAIL** | 70/125 (56%; 47–64); Wilson low 0.47 vs floor 0.55 |
| accuracy | ready_after_fact | pass | 17/24 (71%; 51–85); Wilson low 0.51 vs floor 0.40 |
