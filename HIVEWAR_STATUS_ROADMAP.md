# HiVE WAR — Status & Roadmap

Single-file web game at `D:\Dev\HiveWar\index.html`. Portal builds via `build.py`
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
cd /d/Dev/HiveWar
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

## 2026-07-16 (pt 6) — production pass 1 (new 1.md batch)
DONE + verified in Brave (commit cdd297c):
- Exciting EXPLOSIONS: colored fireball + ember/spark particles + fiery shockwave (was ring+circle).
- Soldier GRAY BOX removed; one shot per soldier; shot streak half length.
- Enemy pathfinding clamped inside road walls (perspective). Xenoid +10%.
- Gates RARE (12-18s); locked = 1 at a time, always big red, devastating; gate value uncapped (grows as shot).
- More player damage; money orbs halved; kill-streak window tightened; Praetorian HP doubled.
- Shop overhauled (modest); HUD 'LEVEL N' + gem/money split; Bestiary ✕ / ESC close.
- Enemy scale-reference image generated → Desktop\HiVE Swarm\ENEMY_SCALE_REFERENCE.png.

STILL TODO (art-heavy / mechanics — next loop):
- Eldritch Sponge sprite (kind 1 still old art — shows MISSING on scale ref); Aurorean.
- Cyber-Mutant animation timing tweak; full attack+death anims for Praetorian & Psychoid.
- Alien Queen mechanics: egg cluster + hatchlings + tail-swing attack.
- Weapons.png pickups floating over the last sprite; Perk Icons into MUTATION screen.
- Ground tile (Environment/Tile_*) tiled along the path; Tank swap (Items/Ironclad Centurion).
- Correct bestiary LOG images (Enemies/Log - *.png) instead of sprite crops.
- Transparent 02 assets: USE THEM (best for bounding boxes — no keying). Re-slice bosses from 02.

## 2026-07-19 — Claude (Fable 5): per-level environment art baked (L1–L10)
- Eric delivered 10 per-level breakdown sheets (`Desktop\HiVE Swarm\assets\Environment\Level N.png`),
  each containing a background horizon, a 4-wide path tile segment, and a side wall panel,
  plus shared tilesets (Tile_cyber01, Tile_Hive01, Wall_City01, Wall_Hive01).
- New `slice_env.py`: hand-tuned crop boxes per sheet → `assets/env/L{n}_{bg,path,side}.png`
  (30 files; captions/borders/watermark frames trimmed; bg capped 1080, tiles 512).
  Shared tilesets copied to `assets/env/shared/`. `Level 4b.png` = alternate L4 strip, unused.
- Level names wired into `EDIT.env` (announced at level start + FORGE WORLD tab):
  Security Outpost, City Ruins, Commercial District, Central Spire, Overrun Factory,
  Reactor Nursery, Hive Gate, Chitin Fields, Brood Caverns, Queen's Chamber.
- Cache bump `?v=9`. Headless 10-level harness runs clean (dies L1 = known difficulty, no errors).
- The game's env loader (`loadEnv`) picks the baked files up automatically; FORGE WORLD
  uploads still override via localStorage.

## 2026-07-30 — HiVE WAR rename + soldier/weapon tier system + rating prompt (Claude)

### Product rename: HiVE SWARM → HiVE WAR
"HiVE SWARM" now names a different, future title, so every player-facing string and doc in
this repo became **HiVE WAR** (title/meta tags, in-canvas title screen, HUD, manifest, service
worker comment, privacy policy, store kit text, `Launch HiVE War.bat`, this file). The death
banner (previously "SWARM WON") is now **"HIVE WON"** — parallel with the win banner "HIVE
PURGED". "Swarm" stays wherever it's gameplay vocabulary (enemy swarm, `swarmT`-style
variables, "swarm density", genre descriptor) — only the brand was touched, not the mechanics
noun. **Intentionally NOT renamed:** the `hiveswarm_v1` / `hiveswarm_forge_v1` /
`hiveswarm_forge_sprites_v1` localStorage keys (renaming wipes every existing player's save —
see the comment above `load()`), `build.py`'s `hiveswarm-poki.zip` output name and the
`__HIVESWARM_PLATFORM__` token in `psdk_adapter.js` (qa/test_packaging.py asserts these exact
strings), and the `com.empiregames.hiveswarm` package/bundle id (a persistent store identifier,
not live yet, out of scope for this pass — mobile/ wasn't touched either).

### Soldier tier × weapon tier power curve
Per `D:\Dev\_ref\UPGRADES_AND_MONETIZATION.md` §2: power used to be squad COUNT + a flat
weapon index. Added a QUALITY axis: `DPS ≈ squadCount × soldierTierMultiplier ×
weaponTierMultiplier` (both computed in `fire()`). Two new **persistent** (not reset between
runs, unlike the five existing per-run shop upgrades) SHOP entries — Soldier Tier and Weapon
Tier, max 5 each, +12%/tier — start at tier 1 = multiplier 1.0 exactly, so the CG-KPI-tuned
baseline (`spawnRate`, L1 minus-gates, `startingSquad` floor 10, `EKIND[0].hp=1`) and the
Queen's ~823s kill time are unchanged until a player actually buys a tier. Soldier tier is
visually legible: ring colour climbs cyan→blue→violet→orange→gold, a subtle scale bump, and
rank-chevron insignia above the head. Surfaced in the HUD (★tier, weapon `Tn` suffix) and the
shop screen (rows now use a dynamic height so the extra 2 rows fit above DEPLOY without
overlapping it).

### Rating prompt (Task 3)
CrazyGames scored retention badly; we had no rating nudge. Added a non-blocking banner that
queues at genuine high points only — level clear (which always follows a boss kill in this
game's structure) or a new endless-mode best score reached live — **never** on launch, **never**
after a loss (no hook in `die()`). Shown on the shop screen's dead-zone gap (above the first
shop row) and the win screen's empty mid-section. Any tap dismisses it; only an explicit ✕
persists `ratingDeclined` forever. `RATING_PORTAL_URL` is empty (no fake URL) until the game is
live on a portal; `nativeReviewRequest()` is a documented no-op hook for a future Capacitor
Play In-App Review plugin.

### Found during verification (pre-existing, NOT caused by this pass)
`_progress_test.js` / `_headless_harness.js` intermittently throw `createRadialGradient
non-finite` around L1 (roughly 1-in-3 runs). Bisected with a scratch harness: an enemy spawns
with `lane`/`x` = NaN (root cause not yet isolated — `G.clusterLane`/`G.clusterT` lazy-init
path looks suspect) and, if that enemy later triggers a splat, a NaN-coordinate
`createRadialGradient` call throws in the stubbed canvas. **Confirmed identical on the
pre-rename `1d5eb5d` baseline** (same exact error string, same step 1305, same enemy state at
step 807) via `git stash` — this repo's `startingSquad()` uses unseeded `Math.random()`, so the
overall sim isn't fully deterministic across process runs, and this pre-existing bug's chance
of actually manifesting as a thrown error varies by run. Left unfixed here (out of scope for
this pass); worth a dedicated investigation before the next CG submission push.
