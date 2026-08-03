# HiVE WAR — Resume Brief (compact context)

**Current build: `v0.2.5beta`** (was `2.5`; renumbered 2026-08-03 to a pre-1.0 beta scheme at
Eric's request). `GAME_VERSION` in `index.html`, `sw.js` `CACHE_VERSION = 'v14'` — bump together.
Signed APK: `Desktop\My Games\_APKs\HiveWar-0.2.5beta.apk` (25.5 MB).
Rebuild: `powershell -File D:\Dev\_mobile/build_apk.ps1 -Game HiveWar -Version 0.2.5beta`

## HW.20 / HW.21 — 2026-08-03 combat pass
- **Two new weapons** (ladder is now 8): **Rail Gun** (slot 6, `minLvl 3`) — single piercing slug
  wrapped in a live electric bolt; **Rocket Launcher** (slot 7, `minLvl 4`) — contact-detonating
  warheads that reuse the tank-shell blast path. `WEAPON_LAST = 7`.
  ⚠️ A rocket sets `b.grenade` (detonation) **and** `b.rocketArt` — the renderer's grenade branch
  is for TANK shells only, so without `rocketArt` a rocket draws as a fireball.
- **Flamethrower now hurts bosses.** Its damage budget lives in the burn DoT and burn was only ever
  applied to pooled enemies, so the gun did nothing to a boss. Bosses now ignite and tick.
- **AoE reaches the boss** — every splash weapon used to miss it because `aoe()` only walked the
  enemy pool.
- **Power-stacking fix.** Squad size multiplied damage LINEARLY on top of meta damage, soldier tier,
  weapon tier, perks and `dmgMul` — five multiplicative stacks. Now:
  - `squadPower(n)` soft curve (`EDIT.player.squadDmgSoft` 24, `squadDmgExp` 0.72) — 400 troops
    contribute ~95 instead of 400. Set the exponent to 1 to restore the old behaviour.
  - `EDIT.bossDefense` — `perHitCapPct` (1.5% of max HP per projectile), **`maxPctPerSec` (8%)**
    leaky-bucket DPS ceiling, `dr`, `burnMul`. The DPS ceiling is the real anti-melt lever: it puts
    a **12.5 s floor** on any boss fight no matter what is stacked. Verified: 500 hits of 1e9 damage
    removed only 12% of the boss's health.
  - All of it is FORGE-editable, so balance is tunable without a code change.
- **Death shatter** — enemies burst into particles tinted from their own sprite (`shatter()`),
  after the FORGE `Die` strip finishes if one is authored, otherwise immediately. Sampling uses
  `getImageData`, which throws on a tainted canvas over `file://` — hence the palette fallback.
- **BEASTIARY tab** (FORGE tab index 9). Add/edit/delete field-guide pages across
  enemy/boss/weapon/vehicle/item/player/lore, one uploaded image each. Page TEXT lives in
  `EDIT.codexPages` (so it travels in a `.hivepack`); IMAGES live in IndexedDB under `codex:`
  alongside the sprite library, and ride along in the pack as `pack.codex`.
  ⚠️ `saveCodexMedia` must stay INSIDE the FORGE closure — `queueMedia`/`mediaPut`/`dataBlob`
  are scoped there.

## Save slots + unlocking beastiary (2026-08-03, later)

**3 save slots.** Keys `hiveswarm_v1_s1..3`, active slot in `hiveswarm_slot`, and the old flat
`hiveswarm_v1` is migrated into slot 1 once (`migrateLegacySave`) and then left alone so an older
build still finds its progress. `slotInfo/useSlot/eraseSlot`; **SAVE SLOTS** button on the title
screen, ERASE per row behind a confirm. `meta.maxLevel` tracks the campaign high-water mark per
slot — that is what the picker shows, and it matters more once the campaign grows past 10 levels.

**The in-game beastiary now reads the FORGE pages.** It used to render the hardcoded `CODEX` array
(6 enemies, unlocked on kill). It now renders `EDIT.codexPages` — all 18 authored pages including
weapons, bosses, tank and player, with uploaded page art when there is any.

- Each page has a **`link`** = its unlock key: `enemy:0-5`, `weapon:0-7`, `boss:guardian`,
  `boss:queen`, `vehicle:tank`, or empty for always-visible. Editable on the FORGE BEASTIARY tab.
- `codexSee(link, count)` reports a sighting. Enemies unlock on **spawn** (you SAW it), not on kill;
  kills only increment the "n terminated" counter. Weapons unlock when equipped, bosses on spawn,
  the tank on its first drop.
- Unlocks live in `meta.codexSeen`, i.e. **per save slot** — a fresh install or an erased slot
  starts the beastiary empty, which is the point of it.
- FORGE has **RE-LOCK ALL**, which clears this slot's sightings without touching progress, so the
  unlock flow can be re-tested.
- First sighting fires a `NEW BEASTIARY ENTRY` toast (`drawCodexToast`, drawn after `draw()` so
  gameplay never covers it).

### QA scripts added
```bash
python -m http.server 8791          # serve first — the FORGE is disabled under ?telemetry=1
python qa/_forge_beastiary_check.py  # beastiary CRUD + image upload + reload persistence
python qa/_shot_hw20.py             # weapon screenshots -> Desktop\Tests\hivewar_hw20
python qa/_slots_codex_check.py     # 3 slots are independent + beastiary unlock/erase/persistence
```
⚠️ Ports 8791/8792 may already be held by a stale server from another game (8792 was serving
`D:\Dev\ZombieWaves` on 2026-08-03) — `curl` the port before trusting a test result.

Single-file web game: `D:\Dev\HiveWar\index.html`. Cyberpunk swarm-shooter (Bone Crush follow-up).
Launch: **`Launch HiVE War.bat`** (starts a local http server + opens browser — `file://` breaks
the `?v=` sprite URLs). Desktop shortcut: `Desktop\My Apps\HiVE Swarm.lnk` (not yet renamed —
lives outside this repo). Latest commit `08c2044`.

## How to work on it
```bash
cd /d/Dev/HiveWar
python regen_extract.py          # re-extract game JS after editing index.html
python qa/telemetry.py           # 15 real Playwright test-bot survival/economy runs
node _headless_harness.js        # full 10-level sim, throws on any error (canvas stubbed + non-finite guards)
node _chain_test.js              # cyber-mutant chain-explosion stress test
# per-level env screenshot: headless Brave, URL ?test=1&lvl=N (debug level-jump param), 540x960
python slice_enemies.py          # re-slice enemy/boss/soldier sprite strips from Desktop sheets
```
Verify visually in Brave via claude-in-chrome on `http://127.0.0.1:8791/index.html?v=N` (bump N to bust cache).
Enemy/boss art is sliced by `slice_enemies.py` from `C:\Users\MiSTRFiNGA\Desktop\HiVE Swarm\assets\`
into `assets/*.png` strips; the game's `ANIM[kind]` + `PRAET` registries cycle frames. Bump the
`const V='?v=N'` in index.html whenever a sprite PNG changes.

## Architecture quick map (index.html)
- `CFG` (W540×H960, squadMax 300, gateAddMax 999), `EKIND` (enemy stats incl. `r` = size),
  `BAL` (spawnRate/waveSec/gates/bossHp), `WEAPONS`, `PERKS`, `CODEX` (beastiary).
- Pools: bullets(1800), enemies, splats(1400 particles), pickups, dmgnums.
- Enemy kinds: 0 Xenoid, 1 Eldritch Sponge, 2 Cyber-Mutant, 3 Xenoptera(winged), 4 Subterra(burrower), 5 Psychoid.
- Bosses: Praetorian (mini, per level) ANIMATED (idle/attack/death via `PRAET`); Alien Queen (L10, still still-image).
- Audio: `AUDIO` closure. Real SFX in `assets/SFX/` mapped in `SAMPLES`. Force-unmuted on load;
  unlocked on first gesture (`AUDIO.resume()` play+pause). `AUDIO.sample(name)` / `sfx()`.

## DONE (verified in-browser)
- Freezes fixed: L2 chain-explosion recursion; L7 empty-perk soft-lock; NaN gate-gradient crash.
- Enemies **lane-relative** (`e.lane` -1..1 × road perspective width) — never cross the pink/blue walls.
- Animated sprites for kinds 0,1,2,3,4,5 + animated soldier squad + animated Praetorian.
- Explosions = fireball + colored ember particles + shockwave (boom()). Gates = upright 3D walls.
- Difficulty: low early spawn + within-level ramp; +10% dmg; harsher contact; each level starts
  with a scaled squad ~5-20 (Start-Squad shop +8). Gate value grows as fast as you shoot it.
- 1 bullet per soldier, capped 15 streams. Beastiary (X/ESC close). Death screen "HIVE WON" + frozen clock.
- Scale reference honored (Eric's `ENEMY_SCALE_REFERENCE.png`): cyber big, sponge/subterra small, etc.
- Sound wired (pulse-rifle/grenade/explosion/lightning/money(50% orbs)/perk/boss). Coin now audible.

## ▶ 2026-07-19: PER-LEVEL ENVIRONMENT ART — BAKED (all 10 levels)
Eric delivered breakdown sheets `Desktop\HiVE Swarm\assets\Environment\Level N.png`
(each = mockup + bg horizon + 4-wide path tile + side wall panel). `slice_env.py`
crops the three panels per level → **`assets/env/L1..L10_{bg,path,side}.png`** (all 30 baked,
caption/border trimmed, bg≤1080 tiles≤512). Shared tilesets copied to `assets/env/shared/`
(Tile_cyber01, Tile_Hive01, Wall_City01 city skyline strip, Wall_Hive01). `Level 4b.png` is an
alternate L4 strip — unused. Level names now real (EDIT.env): Security Outpost / City Ruins /
Commercial District / Central Spire / Overrun Factory / Reactor Nursery / Hive Gate /
Chitin Fields / Brood Caverns / Queen's Chamber. `?v=9`. Re-crop = edit boxes in slice_env.py.

## Env pipeline reference (wired earlier)
- **Env pipeline (done)**: FORGE (F2) → WORLD tab → per-level clickable slots **＋ path / ＋ bg / ＋ side**
  (upload → localStorage override, live instantly, ✕ clears; auto-downscale tiles 512 / bg 1080).
  Fallback = files `assets/env/L<n>_{path,bg,side}.png` (see assets/env/README.txt). FORGE upload wins.
- **Path = TRUE perspective tiling**: always 4 tiles across the road, rows foreshortened, scrolls toward
  player. Density knob = `S=13` in `drawPerspectiveRoad` (not yet in FORGE — expose if Eric wants).
- **bg**: wide strips (aspect >1.8) anchor on the horizon; full 540×960 covers canvas. **side**: pattern-fills
  off-road areas, scrolls.
- Eric HAS art ready for L1 (City Streets: neon road tile + purple skyline) and L10 (Inside the Hive:
  green alien tile + biomech strip) — he uploads via WORLD slots, or hands me files to bake into assets/env/.
- Level names in WORLD tab (announced at level start). L2-L9 still "Sector N" placeholders.
- When a set is final: bake into assets/env/ + commit, so it ships (localStorage is per-browser).

## NEW (2026-07-18 session, pass 3)
- Swarm AI: two-phase flow — spawns blanket the road full-width, NO player-homing above
  `FUNNEL_Y = CFG.H-330`, hard converge + latch-attack below (bites every .85s until killed).
  Harder than before (harness dies L1) — tune via FORGE armor/HP/spawn if needed.
- Far-horde indicator band halved + raised (z .02-.19, kill line z=.20).
- HUD in-run buttons top-right: ⟳ RESTART, ⏸/▶ PAUSE (freeze+dim+banner, tap resumes), ⚙ mute.
  Mute = HARD stop (pauses+rewinds all playing samples + tank loop instantly).
- WORLD tab (FORGE): barrier interval per level (EDIT.gateInterval), rolling hazards
  (EDIT.rollers: interval/%armored/hp+lvl/speed/size/dmg/minLvl2; breakable=hp+credits,
  armored=dodge-only; temp procedural art; real sprites via SPRITES→ITEMS→Roller slots),
  per-level env (EDIT.env names + upload slots).
- FORGE core (earlier passes): auto-pause on open, resizable/draggable, transport ⏸⏩⏭,
  UNITS/PLAYER/WEAPONS/WAVES+BOSS/WORLD/SPRITES/DATA. Sprite frame paint editor +
  creatable slots (XANIM Walk override + Die one-shot; XSPRITE rollers). `?forge=1&ftab=N`.
- Boss: descends to EDIT.bossY≈560 (close combat), HP bar floats above boss head.
- Praet death frame idx2 = ONE connected sprite (looks like 2; CC-verified) — repaint/DEL in FORGE if wanted.
- Repo: private GitHub **MiSTRFiNGA/HiveWar** (renamed 2026-07-30, was HiveSwarm); mirror = `D:\Drive\AI\My apps\HiveSwarm`
  (robocopy /MIR /XD .git __pycache__ after each pass). ZeldaForge shipped separately (D:\Dev\ZeldaForge).

## NEW (2026-07-18 session, pass 2)
- Boss HP bar floats above the boss's head (follows B.x/B.y, clamped on-screen) — no longer hidden under the top HUD.
- FORGE header debug transport: ⏸ pause, ⏩ ×4 fast-forward, ⏭ level skip (boss→bossKill, play→nextLevel, perk→dismiss). `window.FORGE_DBG` read by main loop.
- SPRITES tab: vertical categorized grid (ENEMIES/BOSSES/PLAYER/ITEMS, alpha-sorted) — every unit shows Walk/Attack/Die/Idle slots w/ thumbnails; empty slots greyed placeholders (game ignores until art lands). Deep-link `?forge=1&ftab=4`.
- Alien Queen "missing assets" = she only HAS queen_hero.png (Idle 1f); Attack/Die slots await art.
- Praet death "doubled" frame = frame idx2 is ONE connected sprite (CC-verified, 17k px blob) — a hunched collapse pose that reads as two figures. Not splittable by cutting; repaint/DEL it in FORGE if unwanted.

## NEW (2026-07-18 session)
- **HiVE FORGE game editor** (F2 / ⚒ button / `?forge=1`): floating branded window. Tabs: UNITS
  (per-enemy hpBase+hpLvl w/ L1-L10 preview, spd/size/credits, spawn WEIGHT w/ live %, minLvl),
  PLAYER (rofMul/dmgMul/armor%), WEAPONS (rof/dmg/n/spread), WAVES+BOSS (spawnRate[10], bossHp[10],
  bossY, queen), SPRITES (per-frame paint editor, +dup/−del frames, save-live via localStorage
  dataURL override, DOWNLOAD strip to bake into assets/), DATA (export/import JSON, resets).
  Game reads `EDIT.*` (localStorage `hiveswarm_forge_v1`, sprites `hiveswarm_forge_sprites_v1`).
  Self-disables headless (try/catch on document.head). SOP: every future game embeds a FORGE.
- Fresh-run reset: startRun() zeroes shop meta (dmg/squad/weapon/perkSlot/vehicleDrop/credits) — no tank leak.
- Boss descends to EDIT.bossY≈560 (close-quarters); minions/eggs spawn ABOVE the boss now.
- Deploy cues: announce() banner — "TANK INBOUND", "<PERK> ONLINE". Drone shots purple + orbit-synced.
- Tank = Ironclad sprite (slice_items.py) + looping tank-track.mp3 @0.45. Perk icons in MUTATION,
  weapon icons on WPN gates. HUD 2x w/ glow (squad cyan/level purple/money green). Orbs: money=green, mutation=blue.
- Cyber-Mutant legs fixed + Praetorian green blades kept (alpha-key slicing, sprites ?v=8).

## OPEN / NEXT (art + mechanics)
- **Alien Queen mechanics**: egg cluster + hatchlings + tail-swing (Eggs Open.mp3 waits on this). Queen still a still image (Queen02 transparent available → could animate).
- **Aurorean** enemy sheet exists (green) — not yet wired (possible extra/replacement enemy).
- **Weapons.png** pickups floating over gates; **Perk Icons.png** in the MUTATION screen.
- **Ground tile** (`Environment/Tile_*`) along the path; **Ironclad Centurion** tank swap; gate +N/−N art.
- Tank deploy sound is still a synth blip (`sfx('drone')`) — swap for a real one; consider a "TANK INBOUND" cue.
- Correct beastiary uses sprite crops, not the `Log - *.png` field-guide pages (could swap).

## Tunable knobs (for balance requests)
- `BAL.spawnRate[]` + the `ramp` in `spawnWave` (difficulty). `BAL.gates.interval` (gate frequency).
- `EKIND[k].r` (enemy sizes, from scale sheet). `startingSquad()` (per-level start). Bullet dmg *1.1 in `fire()`.
- Boss HP `BAL.bossHp[]`; Praetorian death length `bossKillT` (1.6s) in `bossKill()`.

## 2026-07-30 (Claude): rename to HiVE WAR + soldier/weapon tier + rating prompt
- Product renamed HiVE SWARM → HiVE WAR everywhere player-facing/docs (repo + Pages already
  moved). Death banner "SWARM WON" → "HIVE WON". `hiveswarm_v1`-family localStorage keys and
  `build.py`'s `hiveswarm-poki.zip`/`__HIVESWARM_PLATFORM__` token deliberately untouched
  (save-breaking / qa-test-breaking respectively).
- New persistent (survives `startRun()`'s per-run meta reset) `G.meta.soldierTier` /
  `G.meta.weaponTier`, tier 1-5, +12%/tier, multiplied into `fire()`'s `b.dmg`. Tier 1 = 1.0x
  so baseline balance (incl. Queen ~823s TTK) is unchanged until bought in the shop
  (`SOLDIER_TIER_MAX`/`WEAPON_TIER_MAX` in the WEAPONS block). Soldier tier renders as a
  ring-colour/scale/chevron-insignia change in `drawSquad()` — see `SOLDIER_TIER_COLORS`.
- New rating-prompt module (search `RATING_PORTAL_URL`): queues on level-clear/boss-kill/new
  endless best, never on launch or death, one-tap dismiss, decline persists forever
  (`G.meta.ratingAsked`/`ratingDeclined`).
- **Found, not fixed:** `_progress_test.js`/`_headless_harness.js` intermittently (~1/3 runs)
  throw a `createRadialGradient non-finite` from a pre-existing NaN-lane enemy spawn bug —
  confirmed present on the pre-rename baseline too (`git stash` + identical repro at step
  807/1305). `startingSquad()` uses unseeded `Math.random()` so runs aren't fully
  deterministic; worth a dedicated fix pass before the next CG submission.
