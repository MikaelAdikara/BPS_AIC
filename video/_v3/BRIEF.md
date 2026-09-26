---
workflow: general-video
flow: automation
storyboard: no
message: "Two routes, one gate: with or without OpenAI, code decides what reaches the seller."
destination: pitch-screen
aspect: 1920x1080
language: en
audience: hackathon judges and technical viewers
length: 95s
angle: one continuous 3D world guided by the mascot Qo; AI route and rule route shown side by side (replaces v2)
---

## Intent

v3 (26 Sep 2026). User asked for richer, more creative 3D motion graphics ("showcase Claude's motion
graphics skill, all out"), a roaming mascot, and both routes: with the OpenAI API key and without it.
No music, no voice-over. English on screen, 95 s. Mascot: Qo (rounded Deciqo diamond with a glass face).

## Assets

- ../apps/api/app/deciqo/engine/* (gap-v1.9 / verify-v2.2) — source of truth for both routes.
- ../docs/worklog/engine.md — measured cost/latency ($0.135 for 10 Lazada products, 40–67 s per product).
- assets/footage/R4, R6, R7 — real UI captures shown on the 3D laptop.

## Notes

- Silent: no <audio> at all.
- Only claims backed by code/worklog. The $0.025 reservation is labelled "illustrative".
- v1 and v2 sources are archived in _v1/ and _v2/.
