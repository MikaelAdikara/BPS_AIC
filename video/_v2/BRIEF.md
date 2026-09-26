---
workflow: general-video
flow: automation
storyboard: no
message: "With OpenAI switched on, the model proposes and code still decides what reaches the seller."
destination: pitch-screen
aspect: 1920x1080
language: en
audience: hackathon judges and technical viewers
length: 92s
angle: infrastructure showreel of the AI-on pipeline, rule mode as the fail-safe branch (replaces v1)
---

## Intent

v2 of the showreel. User (26 Sep 2026): v1 only showed the no-AI path; show the infrastructure when
the OpenAI key is on. No music — completely silent. Do not follow the HyperFrames house style or the
Deciqo design-system zip; be creative, "all out, flex your motion graphics skill". Replace the old
video. English on screen, ~90 s, verified technical numbers from the repo allowed.

## Assets

- ../apps/api/app/deciqo/engine/* (gap-v1.9 / verify-v2.2) — source of truth for the flow.
- ../docs/worklog/engine.md — measured cost/latency ($0.135 for 10 Lazada products, 40–67 s per product).
- assets/footage/*.png — real UI captures (optional proof).

## Notes

- Silent: no <audio> at all.
- Only claims backed by code/worklog. Illustrative values are labelled as such.
- v1 sources archived in _v1/.
