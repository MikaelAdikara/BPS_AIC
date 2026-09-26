# Deciqo — AI-on infrastructure showreel (HyperFrames, v2)

92 s · 1920×1080 · 30 fps · **silent** · output: `output/deciqo-showreel.mp4`
Flow source of truth: `apps/api/app/deciqo/engine/` (gap-v1.9 / verify-v2.2) and `docs/worklog/engine.md`.

| Time | Scene | File |
|---|---|---|
| 0–7 s | Ignition: `.env` with the OpenAI key, switch RULES → AI | `compositions/a1-ignition.html` |
| 7–13.4 s | "The model proposes. Code decides." | `compositions/a2-title.html` |
| 13.4–27.4 s | Isometric CSS-3D map: your server + the OpenAI zone floating above, packet journey | `compositions/a3-map.html` |
| 27.4–36 s | Triage (selection, not counting) + budget reservation / ledger | `compositions/a4-budget.html` |
| 36–47.5 s | Call 1 · Discovery: request, prompt-injection guard, strict-JSON response | `compositions/a5-discovery.html` |
| 47.5–55 s | Call 2 · Membership: 150 reviews in balanced batches | `compositions/a6-membership.html` |
| 55–65.5 s | Code veto (verbatim, relevance, routing) + metrics / Wilson bound | `compositions/a7-veto.html` |
| 65.5–74.5 s | Fact gate + the seller's fact | `compositions/a8-gate.html` |
| 74.5–83.5 s | Fail-safes (no key, key rejected, budget) → labelled rule mode; watch / reopen | `compositions/a9-failsafe.html` |
| 83.5–92 s | Measured cost + close | `compositions/a10-close.html` |

- `index.html` is generated: `node scripts/build-index.mjs` (scene order and durations live there).
- Text effects (`assets/v2.js`) are callback-free (clip-path steps / pre-rendered frames), so scrubbing is seek-safe.
- Values marked "illustrative" (the $0.025 reservation / $0.007 settle) are examples; measured numbers come from the worklog.
- v1 (rule-mode showreel with music) is archived in `_v1/`.

```bash
npx hyperframes preview --background
npx hyperframes check
npx hyperframes render -o output/deciqo-showreel.mp4 --quality delivery
```
