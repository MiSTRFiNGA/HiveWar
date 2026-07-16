# HiVE SWARM — Status & Roadmap

Single-file web game at `D:\Dev\HiveSwarm\index.html`. Portal builds via `build.py`
(CrazyGames + Poki). Reference look: [LOOK_REFERENCE_LASTZ.md](LOOK_REFERENCE_LASTZ.md).

## Current phase — DONE 2026-07-15 (Claude / Fable 5)

### Level-2 freeze — FIXED (root-caused, not patched blind)
- **Bug:** the game hard-froze on level 2. Reproduced deterministically with a headless
  Node harness (`_headless_harness.js`) that runs the real game logic with stubbed canvas.
- **Root cause:** infinite recursion → stack overflow. A dying cyber-mutant (enemy
  kind 2) calls `aoe()`, which damages nearby enemies, which can kill another clustered
  cyber-mutant → `aoe()` again → recurse. A dense cluster chain-explodes until the call
  stack blows, the exception breaks the `requestAnimationFrame` chain, and the game
  freezes. **Level-specific because cyber-mutants have `mixCyb=0` on level 1 and first
  spawn on level 2** (`mixCyb[1]=3`).
- **Fix:** chain explosions now drain through a flat work-queue (`queueBlast`) with an
  8000-iteration guard — clusters detonate iteratively, never recursively. Verified: a
  300-cyber-mutant cluster fully chain-detonates with zero survivors and no overflow;
  a full 10-level godmode sim runs clean.

### Caps corrected (per Eric)
- **Soldiers cap at 100** (`CFG.squadMax = 100`). Enforced leak-free — clamped at every
  gain site (gates, pickups) plus a top-of-frame backstop. Verified squad never exceeds 100.
- **Gates cap at +15** (`CFG.gateAddMax = 15`) — a single gate never grants more than
  +15 units (add gates clamped at spawn, upgrade, and pass; mul-gate gain also capped
  at +15). Slows early snowballing; Eric flagged current difficulty as "too easy."

### Enemy motion — organic xeno crawl (replaces "Frogger" slide)
- Old motion: enemies funnelled to the player's column and slid left/right in a uniform
  lane oscillation — read like traffic.
- New: per-enemy body **wiggle + slow meander + forward lurch-and-settle** (crawl surges),
  with only a gentle pull down the corridor. Winged divers keep a wide diving swoop.

## How to test locally
```bash
cd /d/Dev/HiveSwarm
python -m http.server 8777           # then open http://127.0.0.1:8777/index.html
# headless regression (no browser needed):
python regen_extract.py              # re-extract game JS after editing index.html
node _headless_harness.js            # full 10-level sim, reports any throw
node _chain_test.js                  # cyber-mutant chain-explosion stress test
```

## Roadmap — next steps

### Eric's lane (art + audio)
- Sound effects (fire, gate, kill-streak, boss, explosion, victory).
- New art assets. **Note:** enemies already render photoreal PNGs (`assets/*.png`) with a
  vector fallback — replacing the PNGs upgrades the look with no code change. Drop-in slots:
  `biomorph_a/b`, `eldritch`, `cyber_a/b`, `winged`, `burrower`, `praetorian`, `soldier_front`,
  `tank_front`, `parallax_city`, `tile_highway`.
- **Labeled asset sheets:** Eric mentioned earlier labeled asset images to implement —
  those are not in Claude's current session context. Re-share them and Claude will wire
  each labeled asset to its slot.

### Claude's lane (swarm feel + gameplay, using the video reference)
1. **Swarm density** — make dozens of enemies in a tight space read as a real swarm:
   tighter cluster packing, overlap/jostle, staggered depth scaling, so a knot of xenos
   pouring down the corridor feels overwhelming (per the reference frames).
2. **Difficulty pass** — Eric found it too easy; with the +15 gate / 100 soldier caps,
   retune `spawnRate`, `waveSec`, enemy HP, and contact losses after his playtest.
3. **Reference-accurate UI juice** — big white impact numbers on breakable obstacles,
   clearer blue(+)/red(−) gate panels, escalating full-width tracer wall, kill-feed banner,
   victory celebration beat (all catalogued in LOOK_REFERENCE_LASTZ.md).
4. **Boss variety** per level (currently rush/sweep alternating; queen at L10).

### Awaiting Eric
- Playtest with the new caps → report difficulty → Claude retunes balance.
- Re-share the labeled asset sheets for implementation.

## 2026-07-16 — Claude (Fable 5): freeze fix + challenge/juice pass + Psychoid + Bestiary

### Fixed
- **L7 "MUTATION READY" freeze** — soft-lock: `offerPerks()` entered the perk screen with
  an empty pool once all 3 perk slots were maxed. Now skips the screen + banks +60 credits.
  Reproduced/verified headless (`_perk_test.js`).

### Challenge + juice (verified in Brave)
- Swarm density ~2.5×; harsher contact + shorter grace → you can actually be overwhelmed.
- Gates: spaced ~6–9s; ~40% single-gate choices; ~30% **LOCKED** (unshootable, steel-bar,
  must steer around); bigger locked negatives; exact negative subtraction.
- Orbital perk = central **NUKE** (beam + shock ring + big AoE), not a thin line.
  Chain Lightning draws forked arcs; Acid Rounds = green corrosion tint + DoT.
- Tank now **lobs heavy grenades** (fat shells, big AoE), not soldier bullets.
- **Cephalo-Psychoid** (enemy kind 5): coordination node, buffs nearby swarm (+45%),
  purple aura; priority kill. **Bestiary** log book: unlock pages on first kill, per-enemy
  tactical tip, title-screen button.

### Still open (next session)
- **ART EXPORT NEEDED (Eric):** Psychoid + all `ASSETS 01/02` sheet items must be exported
  as **clean transparent PNGs (no checkerboard)** — the sheets have the gray checker baked in
  (alpha=255), so slicing leaves grid specks. Per-enemy top-down frames, gate art (+5/+10/
  +25/×2/×3, −5/−10), weapon-tier icons, pickups, tanks, queen.
- **Barrier weapon variety** (flamethrower / laser / machine-gun / rail-gun gates) — not built.
- **Full sprite-sheet animation** (Psychoid 8-frame wiggle; soldier run/fire; biomorph walk).
- **Weapon-tier + perk icons** from the sheet wired into UI.
- **Sounds** (Eric's lane).
- Minor: hide top HUD bar while on the Bestiary screen.
