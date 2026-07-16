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

## 2026-07-16 (pt 2) — shake fix, perspective gates, art-export decision

### Done + verified (Brave screenshots)
- **Screen shake normalized:** removed per-kill accumulation (dense swarm pinned it on);
  shake now only for big beats and ONLY during play/boss — upgrade/level-clear screens stay still.
- **Perspective gates:** gates now render + collide as trapezoids that follow the road
  corridor (narrow far → wide near) via `gateRect(lane,y)`. No longer flat falling boxes.

### Background color decision (for clean asset export)
Sampled the new enemy sprites — bodies span purple (Xenoid, Cyber Mutant), olive-green
(Subterra) and red-brown (Psychoid). So NO single chroma color is clean for all:
- magenta clashes with the 2 purple enemies; neon green clashes with Subterra.
- **BEST: export true-transparent PNGs from the PSD** (the checkerboard is Photoshop's
  transparency display — "Export As → PNG" keeps real alpha; the current files were
  flattened so the checker got baked in, alpha=255).
- **If a solid matte is unavoidable: NEON GREEN #00FF00** — clashes least with this roster
  (only Subterra is greenish, and it's olive, distinguishable from pure neon), easiest to key.

### Queued (needs the clean transparent exports)
- Replace ALL non-boss enemies with the new animated sprites (Xenoid, Subterra, Cyber
  Mutant, Psychoid) — build a sprite-sheet frame-cycler once grid dims are known.
- Perk/MUTATION screen: it is ALREADY free (picking a perk never spends credits — confirmed
  in code). Remaining: wire the perk icons from the sheet + prettify the layout.
- Weapon-tier icons, gate art (+N/×N panels), pickups, barrier weapon variety.

## 2026-07-16 (pt 3) — gameplay batch (all verified in Brave)
- **3D wall gates:** gates now stand UP as upright energy walls (base on road, rising
  vertically, taller as they near; scan bars, steel-bar locks, top cap). Per Eric's pen sketch.
- **Escape guaranteed:** a gate pair can never be both impassable (locked-negative).
- **Pickups:** ~25% smaller, tractor-beam pull toward the character (Magnet extends reach).
- **Tanks:** exactly one per side; shells detonate ON IMPACT with a big explosion (ring+AOE+shake).
- **Death screen:** clock freezes at death (was still ticking); "SWARM LOST" → "SWARM WON".
- **Army:** squadMax 100→300; Start Squad shop +8/level (max 20) so meta upgrades build a real army.
- **In-run perks are free** (confirmed — collecting the dots → MUTATION pick costs no credits).

### Background decision for enemy cutouts
- GREEN (#00FF00) background is GOOD — Claude will key it with **edge flood-fill**, which
  removes only the green touching the border and PRESERVES the creatures' interior green/cyan
  glow accents. Requirement: leave a small margin so the creature doesn't touch the image edge.
- Transparent PNG is still the gold standard (no key needed).

### NEXT (the animated-sprite pass — needs frame specs)
Replace all non-boss enemies with the animated sheets (Cyber Mutant / Xenoid / Subterra /
Psychoid). Claude will build a sprite-atlas frame-cycler. NEED per sheet: the frame grid —
e.g. Cyber Mutant sheet has labelled rows of different lengths (idle 4, walk ~10, attack, death).
Tell Claude the columns×rows (or which row = the looping walk/idle to use in-game) and it wires them.

## 2026-07-16 (pt 4) — animated enemy sprites LIVE
- Built `slice_enemies.py`: green-screen keyer (border-flood for Subterra's green head,
  full-key for flesh creatures) + largest-blob (drops baked labels) + halo erosion + edge
  green-despill → 128px horizontal strip atlases.
- In-game `ANIM[kind]` + `drawEnemyAnim()`; enemy **kinds 0/2/4/5 now animate**:
  Xenoid walk, Cyber-Mutant idle, Subterra scan, Psychoid swim. Bestiary uses frame 0. Verified in Brave.
- **Still static/vector:** kind 1 Eldritch sponge + kind 3 Winged diver (no sheets provided yet).
- Next: Eldritch + Winged sheets; optional death/attack anims from the same sheets; minor
  green tint at the far horizon (tiny distant sprites) — cosmetic.

## 2026-07-16 (pt 5) — CRITICAL campaign fix + more sprites
- **FIXED: Campaign froze instantly** — gateRect did pow(negative,1/1.6)=NaN for gates
  spawned above the horizon (y=-60) → createLinearGradient(NaN) crashed the render loop on
  the first gate. Clamped base to >=0. Hardened the headless harness to throw on non-finite
  gradient args so this class is caught offline in future.
- **Xenoptera** (winged, kind 3): animated flight loop; renamed 'Winged Diver' → Xenoptera.
- **Animated squad**: rear-view trooper fire loop (soldier_fire) replaces the vector trooper.
- **Bosses**: Praetorian mini-boss + Alien Queen hero sprites wired into drawBoss (verified
  Praetorian renders in Brave; Queen shows at L10).
- **Still needs a sheet:** kind 1 sponge — a `Log - Aurorean.png` exists (likely its new name)
  but no `Aurorean.png` sprite sheet yet. Send it (green bg) and Claude wires it like the rest.
