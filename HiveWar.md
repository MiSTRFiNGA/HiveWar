---
type: game-documentation
title: HiVE WAR
description: Canonical source of truth for HiVE WAR — status, spawn mix, developer rules, and APK/Pages.
status: playable-in-development
version: 0.3.8
updated: 2026-08-22
tags: [game, hivemind, webgame, documentation]
---

# ⚔️ HiVE WAR — source of truth

**This file is the only live document for HiVE WAR.**
`HIVEWAR_STATUS_ROADMAP.md`, `RESUME.md`, boards, and empire memory are pointers or history.
If they disagree with this file, this file wins. Update this file in place when the game, APK, Pages, or open work changes.

| | |
|---|---|
| **Version** | `0.3.8` · `sw.js` `CACHE_VERSION = v29` |
| **Master path** | `D:\Dev\HiveWar` — edit here only |
| **Game file** | `index.html` — one file: engine, FORGE, HUD, run loop |
| **Launcher** | `Launch HiVE War.bat` (never `file://`) |
| **GitHub** | https://github.com/MiSTRFiNGA/HiveWar (public, Pages on `master`) |
| **Pages** | https://mistrfinga.github.io/HiveWar/ |
| **APK (one only)** | `C:\Users\MiSTRFiNGA\Desktop\My Games\_APKs\HiveWar-0.3.8.apk`. Older War APKs are in `_APKs\Archive`. |
| **Genre** | Lane / corridor shooter (refs: Real War, Z Route). |
| **Not** | HiVE SWARM (`D:\Dev\HiveSwarm`) is the 360° survivors-like. Borrow a *behaviour* from it; do not edit that repo from this lane. |

**Owner last human verdict (2026-08-05):** "getting fun."

**Do not** rebuild CrazyGames / Poki (`python build.py`) until the owner asks.

---

## 1. How to run and verify

```bat
Launch HiVE War.bat
```

```powershell
cd D:\Dev\HiveWar
python regen_extract.py
node _headless_harness.js          # crash detector — SIM ENDED clean is not a play bot
python qa/_verify_0_3_5_cast.py    # roster / sheet / SFX wiring
python -m unittest discover -s qa -v
```

Bump `GAME_VERSION` **and** `sw.js CACHE_VERSION` together.

---

## 2. Roster (0.3.5)

`pickKind()` walks **every** `EDIT.kinds` row gated by `minLvl`. Through 0.3.4 it hard-looped `k < 6`, so kinds 6–13 (Swarm names, old 4-frame strips) **never spawned**.

| kind | Name | minLvl | Walk |
|---:|---|---:|---|
| 0 | Xenoid | 1 | Swarm biomorph SW/S/SE |
| 1 | Eldritch Sponge | 2 | War `eldritch_ooze` (unique) |
| 2 | Cyber-Mutant | 2 | Swarm cyber_mutant SW/S/SE |
| 3 | Xenoptera | 4 | War `xenoptera_fly` |
| 4 | Subterra | 6 | War `subterra_scan` |
| 5 | Psychoid | 3 | Swarm psychoid SW/S/SE |
| 6 | Shambler | 1 | Swarm shambler SW/S/SE |
| 7 | Runner | 2 | Swarm runner SW/S/SE |
| 8 | Crawler | 3 | Swarm crawler SW/S/SE |
| 9 | Brute | 5 | Swarm brute SW/S/SE |
| 10 | Armored Dead | 4 | Swarm armored_dead SW/S/SE |
| 11 | Necro Node | 6 | Swarm necro_node SW/S/SE (spd 22 so it actually walks the corridor) |
| 12 | Mutant Enforcer | 7 | Swarm mutant_enforcer SW/S/SE |
| 13 | Zombie Colossus | 8 | Swarm zombie_colossus SW/S/SE |
| 14 | Hive Slime | 3 | Swarm slime SW/S/SE (3-frame) |
| 15 | Node Spawn | 5 | Swarm node_spawn SW/S/SE |
| 16 | Rotter | 7 | Swarm rotter SW/S/SE |

Facing: `e.lane < -0.16` → SW, `> 0.16` → SE, else S. Sheets live in `assets/swarm/{stem}_walk_{s,se,sw}.png`.

War guns keep rifle/MG/lightning/grenade. Swarm ports (Pulse Carbine, Heat Seeker, Breach Laser, Storm Arc, Nova Shell, Toxin Injector) use Swarm `pulse/seeker/beam/chain/nova/poison` samples. Flamethrower uses `flame_loop`. FORGE v5 refreshes saved weapon sfx.

`assets/weapon_icons.png` is a **14-cell** 128px strip (1792×128, magenta keyed). Cells 0–4 are the original pixel guns; 5–13 are the missing ladder art (Flamethrower through Toxin). HUD `wpnIcon` sizes itself from `WEAPONS.length` (`1400%` strip, position `i * 100 / 13`). FORGE wrap is 14 frames. Gate draw already sliced by `width/height`.

Queen stays out of the fodder roster. Praetorian stays the level guardian (`PRAET` idle/attack/death).

---

## 3. Developer / AI rules

- **One agent on `index.html` at a time.**
- Never `git checkout -- index.html`.
- `art_src/` is **build-time** for this game (Gemini source). Do not ship it in the APK. Runtime art is `assets/` (including `assets/swarm/`).
- One versioned APK on the desktop shelf. Archive the rest.
- `SIM ENDED clean` proves the sim did not throw. It is not a playtest.

| Agent | Lane |
|---|---|
| Grok | Art / SFX / APK / publish / this doc |
| Codex | Do not open unless assigned |
| Claude | Design review + verification |
| Eric | Play, store uploads, portal submit |

---

## 4. Change record

### 2026-08-22 — Grok · v0.3.8 · 14 gun icons + leftover sprite frames

- Generated + keyed nine missing weapon icons and appended them to `assets/weapon_icons.png` (cells 5–13: Flame, Rail, Rocket, Pulse, Seeker, Breach, Storm, Nova, Toxin). HUD/FORGE now treat the strip as 14 cells.
- Runner `walk_s` frame 0 had a headless torso — replaced with a full-body opposite-contact pose.
- Colossus `walk_s` frame 1 was cropped at the waist — replaced with a full-body mid-step. SE/SW frame 3 were half-bodies — replaced.
- Recopied Swarm `runner` / `zombie_colossus` SW/S/SE walks into `assets/swarm/`.
- Honest leftovers: War colossus **S** is the tank giant; **SE/SW** are still the skull-and-saw body (same name, two silhouettes on the lane edges). New icons 5–13 are painted vs pixel 0–4. Necro Node frame 0 is a smaller pulse, not a crop.

### 2026-08-22 — Grok · v0.3.7 · Swarm weapon port

Added Pulse Carbine, Heat Seeker (homing), Breach Laser (pierce), Storm Arc (chain jumps), Nova Shell (blast), Toxin Injector (DoT) to the corridor ladder with Swarm SFX. Flamethrower uses flame_loop. Twin Plasma `rof:10` is **10 volleys per second** (2 pellets each), not a “10 rounds” card. No Giant Rounds.

### 2026-08-22 — Grok · v0.3.6 · crop blanks, revert gun SFX

- Draw crops each walk sheet to the opaque union so 256px cell padding (and leftover scrap on cyber_mutant) does not render as empty glass. Packed Swarm `walk/idle/attack` sources, recopied SW/S/SE into `assets/swarm/`.
- Weapon fire samples reverted to the pre-0.3.5 War pool (`gun` / `mg` / `lightning01|02` / `grenade`). `FORGE_ENTITY_VERSION = 4` clears saved pulse/nova/beam names. Enemy attack/die SFX stay Swarm.

### 2026-08-21 — Grok · v0.3.5 · Swarm cast + SFX on the corridor

Owner: add Swarm characters to War, SW/S/SE only, give War enemies their anims, bring weapon/enemy sounds, APK on the desktop shelf.

- Copied 42 walk sheets (`14 stems × s/se/sw`) into `assets/swarm/`.
- Copied Swarm weapon + enemy attack/die mp3s into `assets/SFX/`.
- `pickKind` / `pctShare` use `kindCount()` (all 17 kinds), not `k < 6`.
- New kinds 14–16: Hive Slime, Node Spawn, Rotter. Entity ids in `entityDefaults()`.
- `animFace` + `animSheet` pick SW/S/SE; Xenoid/Cyber/Psychoid use Swarm walks; Eldritch/Xenoptera/Subterra keep War loops.
- `FORGE_ENTITY_VERSION = 3` clears stale per-kind/weapon sfx on migrate.
- Tests: `python qa/_verify_0_3_5_cast.py` 7/7. `node scripts/check_index_syntax.mjs` OK. `node _headless_harness.js` → `SIM ENDED clean` (L1 death with 1-soldier opener is the crash detector, not a campaign clear).
- APK `HiveWar-0.3.5.apk` 33.65 MB. Unzip-read `GAME_VERSION = 0.3.5`. 42 swarm walks inside the package. 0.3.4 moved to `_APKs\Archive`.
- Git **`8d8f779`** `feat: Swarm cast SW/S/SE walks, SFX, and spawn mix (v0.3.5)` pushed `origin/master`.

### Older

See git `bbbfcf0` (0.3.0 full Swarm strips that never spawned) through `8462322` (0.3.4 forge tooltips) and `HIVEWAR_STATUS_ROADMAP.md` for 2026-07 history.
