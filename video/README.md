# Deciqo — one review's journey (HyperFrames, v5.2)

158 s · 1920×1080 · 30 fps · **silent** · v5.2 adds 13 presenter cues (`CUES` in `index.html`: key point + detail, placed in each scene's empty space).

One continuous Three.js world driven by HyperFrames time (`hf-seek`); DOM passport, chapter cards, phase stepper and lock-up
on a GSAP timeline. Palette from the pitch deck (navy night, royal blue, Hold orange).

| File | Role |
|---|---|
| `index.html` | root composition: canvas, review passport + stamps, chapter cards, phase stepper, mode pill, lock-up |
| `assets/v5/film.js` | the world, beat table `T`, camera table `CAM`, Qo table `QO`, hero-review path, `render(t)` |
| `assets/v5/props.js` | prop builders incl. deck-style `reviewCard` / `cardFaceTex` |
| `assets/v5/icons.js`, `qo.js`, `engine.js`, `kit.js` | icons/logos, mascot rig, renderer + bloom + seek wiring, eases + `PAL` |
| `assets/logos/`, `assets/icons/` | official brand marks (media-use) and lucide-static icons |

- The hero review's path lives in the "hero review" block of `render()`; its hold windows (`HELD`) drive Qo's hands.
- Privacy stop: at film time 57.6 the world freezes for 8 s (`PRIV_AT`, `PRIV_D` in `film.js` and `index.html`) while the envelope is
  scanned; `index.html` wraps every later world time in `W()`.
- Passport stamp times in `index.html` (`STAMPS`) match those hero beats; retime both together with `T`.
- Presenter script with timestamps: `SCRIPT.md`.
- Credit numbers in chapter 05 are illustrative, computed with the engine's own formula; measured cost is in `docs/worklog/engine.md`.
- v1–v4 are archived in `_v1/` … `_v4/` (v4's modules are also still in `assets/v4/`).

```bash
npx hyperframes preview --background
npx hyperframes check
npx hyperframes render -o output/deciqo-review-journey-v5.2.mp4 --quality high --gpu
```
