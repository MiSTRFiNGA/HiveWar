# HiVE SWARM — Resume Brief (compact context)

Single-file web game: `D:\Dev\HiveSwarm\index.html`. Cyberpunk swarm-shooter (Bone Crush follow-up).
Launch: **`Launch HiVE Swarm.bat`** (starts a local http server + opens browser — `file://` breaks
the `?v=` sprite URLs). Desktop shortcut: `Desktop\My Apps\HiVE Swarm.lnk`. Latest commit `08c2044`.

## How to work on it
```bash
cd /d/Dev/HiveSwarm
python regen_extract.py          # re-extract game JS after editing index.html
node _headless_harness.js        # full 10-level sim, throws on any error (canvas stubbed + non-finite guards)
node _chain_test.js              # cyber-mutant chain-explosion stress test
python slice_enemies.py          # re-slice enemy/boss/soldier sprite strips from Desktop sheets
```
Verify visually in Brave via claude-in-chrome on `http://127.0.0.1:8791/index.html?v=N` (bump N to bust cache).
Enemy/boss art is sliced by `slice_enemies.py` from `C:\Users\MiSTRFiNGA\Desktop\HiVE Swarm\assets\`
into `assets/*.png` strips; the game's `ANIM[kind]` + `PRAET` registries cycle frames. Bump the
`const V='?v=N'` in index.html whenever a sprite PNG changes.

## Architecture quick map (index.html)
- `CFG` (W540×H960, squadMax 300, gateAddMax 999), `EKIND` (enemy stats incl. `r` = size),
  `BAL` (spawnRate/waveSec/gates/bossHp), `WEAPONS`, `PERKS`, `CODEX` (bestiary).
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
- 1 bullet per soldier, capped 15 streams. Bestiary (X/ESC close). Death screen "SWARM WON" + frozen clock.
- Scale reference honored (Eric's `ENEMY_SCALE_REFERENCE.png`): cyber big, sponge/subterra small, etc.
- Sound wired (pulse-rifle/grenade/explosion/lightning/money(50% orbs)/perk/boss). Coin now audible.

## OPEN / NEXT (art + mechanics)
- **Alien Queen mechanics**: egg cluster + hatchlings + tail-swing (Eggs Open.mp3 waits on this). Queen still a still image (Queen02 transparent available → could animate).
- **Aurorean** enemy sheet exists (green) — not yet wired (possible extra/replacement enemy).
- **Weapons.png** pickups floating over gates; **Perk Icons.png** in the MUTATION screen.
- **Ground tile** (`Environment/Tile_*`) along the path; **Ironclad Centurion** tank swap; gate +N/−N art.
- Tank deploy sound is still a synth blip (`sfx('drone')`) — swap for a real one; consider a "TANK INBOUND" cue.
- Correct bestiary uses sprite crops, not the `Log - *.png` field-guide pages (could swap).

## Tunable knobs (for balance requests)
- `BAL.spawnRate[]` + the `ramp` in `spawnWave` (difficulty). `BAL.gates.interval` (gate frequency).
- `EKIND[k].r` (enemy sizes, from scale sheet). `startingSquad()` (per-level start). Bullet dmg *1.1 in `fire()`.
- Boss HP `BAL.bossHp[]`; Praetorian death length `bossKillT` (1.6s) in `bossKill()`.
