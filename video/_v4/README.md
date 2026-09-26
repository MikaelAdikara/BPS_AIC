# Deciqo — architecture flight (HyperFrames, v4)

150 s · 1920×1080 · 30 fps · **silent** · made to play behind a live presenter (icons and short tags, no sentences).

One continuous Three.js world driven by HyperFrames time (`hf-seek`); DOM chapter tags and the lock-up on a GSAP timeline.

| File | Role |
|---|---|
| `index.html` | root composition: canvas, chapter tags, route pill, lock-up; icon/logo/footage preload |
| `assets/v4/film.js` | the world, beat table `T`, camera table `CAM`, Qo table `QO`, `render(t)` |
| `assets/v4/icons.js` | lucide icons drawn as vectors on canvases, logo tiles, billboard pill tags |
| `assets/v4/qo.js`, `props.js`, `engine.js`, `kit.js` | mascot rig, prop builders, renderer + bloom + seek wiring, eases |
| `assets/logos/`, `assets/icons/` | official brand marks (media-use) and lucide-static icons |

- To retime a beat, edit `T` and the matching rows in `CAM`/`QO` in `film.js`, and the chapter times in `index.html`.
- Credit numbers in chapter 05 are illustrative, computed with the engine's own formula; measured cost is in `docs/worklog/engine.md`.
- v1–v3 are archived in `_v1/`, `_v2/`, `_v3/`.

```bash
npx hyperframes preview --background
npx hyperframes check
npx hyperframes render -o output/deciqo-architecture-v4.mp4 --quality high
```
