# 🐝 HiVE SWARM — Game Design Document

**Version:** 1.0 (2026-07-15) · **Owner:** Eric Johnson · **Lead dev:** Claude (HiVEMiND)
**Lane:** CrazyGames / Poki web-portal release (same lane as Skull Drift, Bone Crush)
**Repo:** `D:\Dev\HiveSwarm` · **Dev server:** `python -m http.server 8380`

---

## 1. Pitch

Aliens and eldritch horrors have invaded a neon cyberpunk world. You command an
ever-growing swarm of soldiers auto-firing through **thousands** of enemies,
steering through math gates that grow your army and upgrade your guns, fighting
a screen-filling boss at the end of every level — until you reach the **Alien
Queen's egg chamber** and kill her mid-lay to save the city.

Genre: "count-gate auto-shooter swarm runner" (Swarmageddon-style).
The entire appeal is **visual satisfaction**: exponential growth, floods of
enemies, neon acid gore, screen shake, big damage numbers.

## 2. Core Loop

```
steer swarm → shoot gates to buff them → pass gate (army/weapons grow)
→ mow down swarm waves → collect biomatter/chips → in-run perk pick
→ LEVEL BOSS → level clear → shop (spend credits / rewarded ad boost)
→ next level (harder, new enemy mix) → ... → QUEEN fight → WIN → NG+/endless
```

### 2.1 Controls
- **Portrait-ish playfield** (letterboxed on desktop), vertical auto-scroll.
- Drag (touch) or mouse-drag / A-D / arrows to steer **horizontally only**.
- Squad auto-fires forward constantly. No fire button.

### 2.2 Gates (signature mechanic)
- Paired/tripled floating gates spanning lanes: `+N` soldiers, `xN` multiplier,
  `-N` penalty, and **weapon gates** (upgrade tier: Blaster → Twin Plasma →
  Scatter Rail → Heavy Plasma → Orbital-linked).
- **Shootable:** gate values change while shot (`+10 → +50`, `-30 → -5 → +5`,
  weapon gate tier climbs). Choosing which gate to feed bullets IS the skill.
- Some gates subtract or halve — dodge or convert them.
- TODO(video pass): exact escalation curves, gate HP-per-tick feel, and gate
  visual language extracted from reference Shorts (see §12).

### 2.3 Squad
- Visible individual soldiers in formation (blob packing around leader point).
- Cap visible units (~150–200 sprites) then represent overflow as
  **count multiplier + denser formation + bigger muzzle flash wall**; HUD shows
  true count ("x1,247").
- Losing units: enemy contact kills units first; player dies at 0.
- Heavy vehicle drops (meta unlock): periodic tank/mech rolls alongside for a
  duration — big sprite, big gun (the "tanks in the reference video" moment).

### 2.4 In-run progression
- Enemies drop **biomatter** (green globs) and **data chips** (cyan).
- Fill the bar → quick 3-choice perk card pause (game freezes, one tap):
  - Chain Lightning · Orbital Laser · Drone Escort · Acid Rounds (DoT) ·
    Cryo Rounds (slow) · Ricochet · Magnet (pickup radius) · Overclock
    (fire rate) · Shield Matrix (unit-loss protection).
- Perks are temporary (run-scoped); stack up to 3 levels each.

## 3. Levels & Bosses

- **10 levels** to the Queen (tunable). Each = ~90–150s of waves + 1 boss.
- Environment rotation: neon highway → ruined mega-city → biomech hive
  (parallax backdrop swap + tint; same play space).
- **Enemy roster:**
  | Tier | Enemy | Behavior |
  |---|---|---|
  | Fodder | **Biomorphs** — sleek, eyeless, chitinous, bladed | fast, weak, flood in waves/lanes; neon-green acid splatter on death |
  | Tank | **Eldritch Horrors** — asymmetrical flesh, tentacles, glowing eyes | slow HP sponges, soak fire, block lanes |
  | Hazard | **Cyber-Mutants** — half-machine, sparking implants | medium speed, **explode in AoE on death** (spacing puzzle) |
  | Elite | Winged biomorph divers, burrowers (emerge under swarm) | pattern spice from level 4+ |
- **Bosses (end of each level):** screen-filling, multi-phase, weak-point based.
  Rotation examples: Biomorph Praetorian (blade rushes), Flesh Cathedral
  (tentacle sweeps + eye cores), Mutant Colossus (spawns exploders).
- **Level 10 — THE ALIEN QUEEN:** egg chamber arena. Phases:
  1. Egg-laying — destroy eggs before they hatch hatchling floods.
  2. Enrage — tail/claw sweep patterns, acid spit lanes.
  3. Exposed abdomen weak-point burn → kill → cinematic gib + WIN.
- Post-win: credits + unlock **Endless Hive** mode (infinite scaling waves,
  leaderboard-friendly) for retention.

## 4. Meta-progression & Economy

- **Credits** earned per run (kills, level clears, boss bonus).
- Permanent shop (between runs and between levels):
  - Base damage ↑ · Starting squad size ↑ · Starting weapon tier ↑ ·
    Biomatter value ↑ · Vehicle drop unlock/upgrade · Perk slot +1.
- Cost curve: exponential (x1.6/level) — classic idle-adjacent sink.
- **Save:** `localStorage` (versioned JSON blob, same pattern as Bone Crush),
  CrazyGames data-policy compliant. Optional later: PSDK user cloud save.

## 5. Ads & Monetization (CrazyGames/Poki SDK)

- **Rewarded (player-initiated only):**
  - Between levels: double level credits · free shop item · +squad head start.
  - On death: revive once per run with 50% squad.
- **Interstitial:** at level-clear screen via `sdk.gameplayStop()` →
  ad → `sdk.gameplayStart()`. Never mid-combat.
- Mute audio during ads; pause loop. Reuse Skull Drift PSDK adapter + `build.py`
  packaging (CG = Eric uploads extracted `index.html`; Poki = zip works).

## 6. Gore & Content Rating

- Default **neon-green acid blood** on all enemies (alien = portal-safe).
- `settings.bloodColor: 'green' | 'red'` in code; **red hidden from shipped UI**
  (offline/personal builds only). Xenomorph-type biomorphs are ALWAYS green
  even in red mode.
- No humans harmed on screen; soldiers "teleport out" (blue flash) not gibbed.

## 7. Visual Direction

- Cyberpunk neon palette: deep purple/ink backgrounds, magenta/cyan city glow,
  toxic-green enemy accents, orange plasma fire.
- Heavy juice budget: screen shake (boss hits/kills), hit-stop on boss phase
  kills, damage number popups (pooled), chromatic flash on gate pass,
  parallax dust/embers layers.
- Art path: vector/canvas placeholder first (Bone Crush pattern), then
  sprite passes — local ComfyUI (:8188) for concept/texture source where it
  helps, hand-tuned atlas for the tiny units (128px pieces don't fit here;
  units are ~24–32px sprites).

## 8. Tech Architecture

- **Renderer:** PixiJS v8 (WebGL2, single sprite atlas, `ParticleContainer`
  for fodder swarms and bullets).
- **Structure:** small modules bundled to ONE `index.html` by `build.py`
  (esbuild or hand-rolled concat, matching Skull Drift lane). No frameworks.
- **Pooling (strict, non-negotiable):** enemies, bullets, splatters, damage
  numbers, pickups — preallocated arrays, freelist indices, zero GC churn
  in the hot loop.
- **Collision:** spatial hash grid (cell ≈ max enemy radius); bullets vs
  enemies via grid query; swarm units vs enemies via leader-blob capsule.
- **Perf targets:** 60fps with 1,500 live enemies + 800 bullets + 300
  particles on mid mobile; degrade gracefully (particle LOD, splat decals
  merge to canvas texture).
- **Test bot:** `?test=1` auto-plays (steers to best gate, survives),
  hands off on first real input; `window.__dbg()` state dump —
  same conventions as Bone Crush.
- **Determinism hook:** seeded RNG per level for replayable balance tests.

## 9. Audio

- Punchy layered weapon sounds (tier = fatter sound), squelch/acid pops,
  bass boss roars, synthwave loop per environment. Web Audio, pooled
  sources, ducking during perk pick and ads.

## 10. Team & Delegation

| Who | Role |
|---|---|
| Claude | Architecture, core sim/renderer, review gate, CG compliance |
| Codex | Feature implementation passes in `D:\Dev\HiveSwarm` (after GPU run) |
| Grok 4.5 | Wave/gate/economy balance math, difficulty curves |
| GPT 5.6 | Store copy, descriptions, name/SEO, marketing assets brief |
| Local ComfyUI | Concept art / texture source material |

## 11. Milestones

1. **M0 — Greybox core** — steer + gates (shootable) + fodder swarm + pooling
   + 60fps proof at 1.5k enemies.
2. **M1 — Juice pass** — weapons tiers, gore, shake, damage numbers, perks.
3. **M2 — Levels & bosses** — 10-level flow, 3 boss archetypes, shop, saves.
4. **M3 — Queen + win** — final fight, credits, Endless Hive.
5. **M4 — Portal pass** — PSDK adapter, ads, `build.py`, size budget, QA bot
   runs, CG submission package (reuse Skull Drift `store/` pattern).

## 12. Open items

- [ ] Extract exact gate math/feel + target look from reference Shorts:
      `D7yU_NRUtnU`, `bwLzo4ZbUkE`, `BxvmrsoDTRI`, **`lXHBP2JYmoA` (primary
      look target)** — via browser watch or local `yt-watch --visual` once
      Codex frees the GPU.
- [ ] Confirm level count (10) and run length vs CG session-length metrics.
- [ ] Name check: "HiVE SWARM" availability on CG/Poki (no conflicts found yet).
