# HiVE SWARM — Look Target (Eric's primary reference video)

Source: YouTube short `lXHBP2JYmoA` — frames extracted in `art_src/ref/frame_01..14.jpg`.
**This is the look Eric wants.** We keep OUR cyberpunk neon palette + alien enemies,
but adopt this STRUCTURE. Study frames 02, 06, 10, 13 especially.

## What the reference does (per frame evidence)

1. **Perspective road, not flat top-down** (all frames): a highway/bridge strip
   narrowing to a vanishing point near the top of the screen. Side rails/edges;
   wasteland visible beyond both edges. Camera is high-angle behind the squad.
2. **The horde is a WALL** (frames 01–10): thousands of tiny packed bodies filling
   the road's full width from the horizon, flowing downward. They're mowed down at
   a "kill line" mid-screen — a churning strip of gore/sparks where bullets meet
   the mass. Far enemies are tiny (5–8px), near ones bigger (perspective scale).
3. **Small hero squad** (frames 02, 06, 10): only 1–5 LARGE soldier units
   (~40–50px) with bright glowing rings under each, firing continuous bright
   tracer streams (long streaks, not small dots) up the road.
4. **Big center kill counter** (frames 06, 10, 13): huge popup number (321→892)
   mid-screen tallying the kill streak; smaller "+N unit" icon popups above.
5. **Giant boss looms at the horizon** (frames 13–14): a screen-filling colossus
   standing at the vanishing point BEHIND the horde, visible long before the fight.
6. **Ally vehicle rows** (frame 13): 6–8 friendly tanks in formation rows on the
   road firing with the squad — the vehicle-drop power fantasy.

## Mapping to HiVE SWARM (cyberpunk skin, same structure)

| Reference | Ours |
|---|---|
| desert highway/bridge | neon-lit cyberpunk elevated highway, magenta/cyan rails, city glow beyond edges |
| human zombie horde | biomorph swarm (neon green accents), same wall density |
| red gore kill line | neon-green acid kill line (green splatter strip + sparks) |
| blue soldiers + green rings | our soldiers + cyan glow rings |
| tan tanks | hover-tanks, orange plasma |
| gray colossus | Hive Guardian / Alien Queen silhouette at vanishing point |

## Implementation notes (Canvas2D, keep pooling)

- Perspective transform: road-space `(u, z)` → screen: `x = W/2 + u·roadHalfWidth(z)`,
  `y = horizonY + (H - horizonY)·z^1.6` (z 0=horizon → 1=bottom), `scale = lerp(0.18, 1, z)`.
  Road half-width shrinks toward horizon: `roadHalfWidth(z) = lerp(40, 250, z)`.
- Horde: keep the enemy pool as the "near band" (z > 0.35, real collision).
  Add a cheap **far-horde layer**: grid of dots drawn in rows near the horizon whose
  density = incoming spawn pressure (no per-entity sim — pure rendering illusion).
- Kill line: where bullets expire into the horde band, draw persistent green splat
  decals + spark bursts; keep a rolling kill-streak counter popup (big font, center).
- Squad: render as 3–7 large soldier sprites max (formation slots); the true squad
  count shows as the multiplier + fatter tracers, NOT more dots.
- Tracers: bullets render as 20–40px bright streaks with additive glow.
- Boss: draw at the vanishing point at 3–5x scale, dimmed/hazed, from level start;
  slides down into combat range for the fight.
