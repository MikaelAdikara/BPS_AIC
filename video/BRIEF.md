---
workflow: general-video
flow: automation
storyboard: no
message: "One review, carried by Qo through Deciqo's whole architecture: traced, held for a missing fact, decided by the seller, watched."
destination: pitch-screen (played while a presenter talks)
aspect: 1920x1080
language: en
audience: hackathon judges and technical viewers
length: 158s
angle: follow one English review (laptop bag, 14-inch laptop doesn't fit, hidden behind 4 stars) through the walkable 3D architecture; show, don't tell
---

## Intent

v5 (26 Sep 2026, replaces v4). Colour palette taken from the Deciqo pitch deck (colours only; the deck's numbers are not
used). Story restructured: Qo catches one review in the storm and carries it through every station — PII redaction, hash,
triage (candidate at 4★), into the OpenAI envelope and back, the membership board, code veto (verbatim quote), the fact gate
(pinned as evidence while the seller supplies 32 × 24 cm), and finally onto the watch timeline as "written before → ignored"
while a newer review reopens the issue. All review text on screen is English. Silent.

v5.1: a dedicated Privacy step (world pauses before the OpenAI call; what is sent vs never sent; store=false, which is now
set in engine/llm.py). After PII redaction the card shows only the review id, never the buyer's name.

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
- v1–v4 are archived in _v1/ … _v4/.
