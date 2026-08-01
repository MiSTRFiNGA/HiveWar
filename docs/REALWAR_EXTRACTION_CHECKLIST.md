# Real War APK — remaining extraction checklist

**Date:** 2026-08-01 · **Author:** Grok · **Task:** MASTER_TODO 1.3  
**Sources:** `D:\Dev\_ref\apks\Real War.apk` (167 MB), extracted tree `D:\Dev\_ref\apks\rw\`,  
`D:\Dev\_ref\REFERENCE_ANALYSIS.md`, IL2CPP `global-metadata.dat` symbol names, HiVE WAR `index.html` / DESIGN.md / HIVEWAR_STATUS_ROADMAP.md  

> **Scope boundary (unchanged):** architecture / design learning only. **No art, audio, or code**  
> from Real War is copied into HiVE WAR. This is a gap list for *mechanics and systems* still missing  
> relative to the reference product and Eric's DESIGN.md.

---

## Already ported (do not re-do)

| Area | HiVE WAR status |
|---|---|
| Corridor auto-shooter core loop | ✅ |
| Gates (+/− / mul / weapon) | ✅ (paired free-x, not lane-bucketed) |
| Squad formation + count growth | ✅ |
| Cone / fan volley fire | ✅ (restored in `710e4bc`) |
| Soldier tier × weapon tier DPS | ✅ (2026-07-30) |
| In-run perks (Orbital, Drone, Chain, Acid, …) | ✅ partial roster |
| Tank / vehicle drop meta | ✅ |
| Level boss + Queen shell | ✅ (Queen still image-only) |
| Between-level shop + credits | ✅ |
| Bestiary / codex | ✅ |
| Rating prompt at high points | ✅ |
| CrazyGames / Poki PSDK hooks | ✅ packaging path |
| FORGE live-tune editor | ✅ (beyond reference) |

---

## Still un-ported — checklist (implement later, not now)

### A. Architecture patterns worth adopting

| # | Item | Evidence (Real War symbol / note) | Priority | Notes for implementer |
|---|---|---|---|---|
| A1 | **Lane-bucketed obstacles** | `LeftLaneObstacles` / `RightLaneObstacles` / `ExtraLaneObstacles` | Med | Gates/hazards as free `x` force `pairId` exclusivity hacks. Lane membership makes “took left → forfeit right” trivial. Deferred to Forge F1 entity table or a dedicated obstacle pass. |
| A2 | **Unified Obstacle pipeline** | `GateObstacle`, `TireOrBarrelObstacle`, `BossObstacle` share one spawn/collide/despawn | Med | HiVE WAR splits gates / rollers / bosses. One pipeline = fewer special cases for two-weapon barriers (task 2.6). |
| A3 | **Crowd as one volley entity** | `CrowdConeShooter` / `CrowdConeShooterV2` / `OnCrowdConeShooterFiredVolley` | Low | Already approximated with formation fire; only matters if bullet pool becomes a mobile bottleneck. |
| A4 | **Amortised formation rebuild** | `RebuildCrowdForCountAllBulletsRoutine`, `SnapFormationNow`, `freezeFormation` | Low | Visual crowd rebuild is currently per-frame math; coroutine-style amortisation only if we raise squad cap hard. |

### B. Gameplay systems still missing vs DESIGN.md / roadmap

| # | Item | Status in HiVE WAR | Priority |
|---|---|---|---|
| B1 | **Alien Queen: egg cluster + hatchlings** | Still image; `Eggs Open.mp3` waits on it | **High** |
| B2 | **Alien Queen: tail / claw sweep attacks** | Unimplemented | **High** |
| B3 | **Queen phase 3: exposed abdomen weak-point burn** | Partial phase shell only | High |
| B4 | **Winged divers / burrowers (elite patterns L4+)** | Roster gaps | Med |
| B5 | **Two-weapon choice barriers** | Task 2.6 still open (Codex) | High |
| B6 | **Breakable number obstacles (barrels / tire stacks)** | Real War has `TireOrBarrelObstacle` / `DamageUpgradeTireTower` — HiVE only has gates | Med |
| B7 | **Roadside recruit pickups with outline glow** | Last-Z / Real War recruit absorb; HiVE uses gates only | Low |
| B8 | **Victory celebration / dance + kill-feed banner** | DESIGN § look-reference; not in game | Low |
| B9 | **Boss multi-phase weak-points (non-Queen)** | Bosses are HP sponges + basic attacks | Med |
| B10 | **Endless Hive leaderboard-friendly scoring polish** | Endless exists; ranking/export incomplete | Low |

### C. Economy / monetisation / retention (from Real War stack)

| # | Item | Real War | HiVE WAR | Priority |
|---|---|---|---|---|
| C1 | **In-app rating (done-ish)** | RateBox | ✅ rating banner | Done |
| C2 | **Rewarded: double credits / free shop / revive** | Full ad mediation | Partial PSDK path — verify all three still fire | Med |
| C3 | **Ad mediation depth** | Mintegral + Unity Ads + OM SDK | Portal SDK only (correct for CG/Poki) | N/A for web |
| C4 | **Telemetry (GameAnalytics-class)** | `ga.sqlite3` | Portal analytics only | Low |
| C5 | **Observable / reactive upgrade UI bindings** | `*ObservedValue` symbols | Manual redraw | Low |

### D. Content / art pipeline still open (not APK theft — our own assets)

| # | Item | Source of truth |
|---|---|---|
| D1 | Eldritch Sponge sprite (kind 1) | HIVEWAR_STATUS_ROADMAP |
| D2 | Full attack+death anims: Praetorian, Psychoid | roadmap |
| D3 | Ground tile tiling along path (Forge F3 tiling) | FORGE_TEMPLATE_V3 |
| D4 | Distinct L/R wall art per level | handoff §5 |
| D5 | Bestiary LOG images vs sprite crops | roadmap |
| D6 | Perk icons into MUTATION screen completeness | roadmap |

### E. Explicitly out of scope

- Decompiling / shipping Real War code or assets  
- Switching HiVE WAR from Canvas2D to Unity perspective camera  
- Copying Real War monetisation SDKs onto CrazyGames builds  

---

## Suggested next implementation order (when Eric prioritises)

1. **B1–B3** Queen fight (biggest “game unfinished” feel)  
2. **B5** Two-weapon barriers (player choice moment)  
3. **A1–A2** Lane/obstacle unify (unblocks cleaner gate + hazard work)  
4. **B6** Tire/barrel breakables if we want Last-Z density  
5. Art D-items as Eric delivers sheets  

---

## VERIFIED

- APK present: `D:\Dev\_ref\apks\Real War.apk` (166,936,804 bytes)  
- Extract tree: `D:\Dev\_ref\apks\rw\assets\bin\Data\Managed\Metadata\global-metadata.dat`  
- Prior write-up: `D:\Dev\_ref\REFERENCE_ANALYSIS.md`  
- **No implementation performed for 1.3** — checklist only, as ordered.
