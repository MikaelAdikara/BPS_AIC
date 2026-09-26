# Deciqo — "Qo's route" showreel (HyperFrames, v3)

95 s · 1920×1080 · 30 fps · **silent** · output: `output/deciqo-showreel.mp4`
Flow source of truth: `apps/api/app/deciqo/engine/` (gap-v1.9 / verify-v2.2) and `docs/worklog/engine.md`.

One continuous Three.js world driven by HyperFrames time (`hf-seek`), with the DOM type on a GSAP timeline.

| File | Role |
|---|---|
| `index.html` | root composition: canvas, HUD, chapter tags, statements, rewind overlay |
| `assets/v3/film.js` | the world, beat table `T`, camera and Qo scripts, `render(t)` |
| `assets/v3/qo.js` | Qo rig (pose is a pure function of the values passed in) |
| `assets/v3/props.js` | prop builders (labels, cards, arches, gears, laptop, tubes) |
| `assets/v3/engine.js` | renderer, bloom, lights, seek wiring |
| `assets/v3/kit.js` | eases, keyframes, seeded random, canvas textures |

- To retime a beat, edit `T` in `film.js` and the matching times in `index.html`.
- The rewind (47–49 s) maps film time back onto world time, so the AI route literally plays backwards.
- Values marked "illustrative" ($0.025 reservation) are examples; measured numbers come from the worklog.
- v1 and v2 are archived in `_v1/` and `_v2/`.

```bash
npx hyperframes preview --background
npx hyperframes check
npx hyperframes render -o output/deciqo-showreel.mp4 --quality high
```
