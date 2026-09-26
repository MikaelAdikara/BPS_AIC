---
workflow: general-video
flow: automation
storyboard: no
message: "Deciqo's whole architecture, flown through: sources in, OpenAI credit reserved and settled, code decides, the seller decides."
destination: pitch-screen (played while a presenter talks)
aspect: 1920x1080
language: en
audience: hackathon judges and technical viewers
length: 150s
angle: the architecture as one walkable 3D diagram (Docker host, containers, external islands) guided by the mascot Qo; show, don't tell
---

## Intent

v4 (26 Sep 2026, replaces v3). User asked for the overall architecture — including how credit flows into OpenAI and the
technical detail — with less on-screen text and many more icons. A presenter narrates live, so the video only shows.
Silent. English labels only as short icon tags.

## Assets

- ../apps/api/app/deciqo/engine/llm.py (reserve worst case → call → settle from usage, ledger per call, 401 → rule mode).
- ../apps/api/app/deciqo/engine/{discovery,membership,triage}.py (max 8 findings, 150 reviews in batches of 50, ≤45 candidates).
- ../docs/worklog/engine.md, platform.md (measured $0.135 / 10 Lazada products; Apify ledger; Telegram outbox).
- assets/footage/R1, R4, R5, R6, R7 — real UI captures on the seller's 3D laptop.
- assets/logos/* — official brand marks resolved via media-use; assets/icons/* — lucide-static.

## Notes

- Silent: no <audio>.
- Credit amounts on screen ($0.029 reserve, $0.007 settle, $4.971/$4.993 remaining) are illustrative values computed
  from the code's formula (chars/2 input tokens, max_output_tokens × $2.00/M); measured cost lives in the worklog.
- v1–v3 are archived in _v1/, _v2/, _v3/.
