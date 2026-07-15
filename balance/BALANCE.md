# HiVE SWARM — Balance Bible (Round 1)

**Version:** 1.0 · **Author:** Grok · **Date:** 2026-07-15  
**Source design:** `DESIGN.md` v1.0  
**Machine-readable:** `balance.json` (same folder)  
**Status:** Round 1 deliverable for Claude review / sim validation

---

## Design goals (locked for R1)

| Goal | Target | How tables enforce it |
|------|--------|------------------------|
| Feel **exponential growth** | Major power spike every **~20s** | Gate cadence + value curves; squad multiplier doubles roughly every 18–22s when feeding good gates |
| **Near-death recoverable** | 0→viable in one good gate pass | `-N` gates start convertible; mid-run `+N` / `xN` can restore 30–80% of peak squad if shot hard |
| Level length | **90–150s** combat + boss | Wave budget + boss phase HP tuned for mid-skill clear in that window |
| Portal session norms (CrazyGames) | Short dopamine loops, optional continue | 10 levels ≈ **18–28 min** first clear; Endless separate |
| Shop sink | Idle-adjacent, never soft-lock | `cost = floor(base * 1.6^level)` validated below |

**Player power model (abstract):**

```
squadPower ≈ squadCount * weaponDps(tier) * perkMult * vehicleUptime
threat(level,t) ≈ enemiesAlive * mixThreat * density(t)
win when squadPower tracks above threat by ~15–40% after each growth tick
```

---

## 1. Gates

### 1.1 Spawn cadence

| Param | Value | Notes |
|-------|-------|-------|
| Gate pair interval L1 | **4.2s** | First gates feel generous |
| Gate pair interval L10 | **3.0s** | +pressure |
| Interval formula | `max(3.0, 4.2 - 0.12*(L-1))` | Linear tighten |
| Gates per pair | 2 lanes 70% / 3 lanes 30% from L4+ | Triple starts L4 |
| Vertical approach time | **2.4–3.1s** | Time from spawn to pass plane |
| Shootable window | Full approach + **0.35s** after plane | Late conversions |
| Min distance between pairs | **2.0s** equivalent travel | Avoid stacked choices |

**Growth pulse:** with interval ~4s and good-gate selection, player hits a meaningful spike every **~4–5 gates ≈ 18–22s** (matches “every ~20s”).

### 1.2 Gate value ranges by level

Values are **at spawn** (before shooting). Shooting escalates within HP budget (§1.3).

#### Soldier `+N` gates (add units)

| L | Spawn min | Spawn max | Soft cap after shoot | Notes |
|---|-----------|-----------|----------------------|-------|
| 1 | +3 | +12 | +28 | Teach shooting upgrades |
| 2 | +5 | +16 | +40 | |
| 3 | +8 | +22 | +55 | |
| 4 | +10 | +28 | +70 | Triples appear |
| 5 | +12 | +35 | +90 | |
| 6 | +15 | +42 | +110 | |
| 7 | +18 | +50 | +135 | |
| 8 | +22 | +58 | +160 | |
| 9 | +26 | +68 | +190 | |
| 10 | +30 | +80 | +220 | Pre-Queen buffer |

#### Multiplier `xN` gates (multiply current squad, floored)

| L | Spawn options (discrete) | Max after shoot | Notes |
|---|--------------------------|-----------------|-------|
| 1 | x1.2, x1.5 | x2.0 | Rare early |
| 2 | x1.3, x1.6 | x2.2 | |
| 3 | x1.4, x1.7 | x2.4 | |
| 4 | x1.5, x1.8 | x2.6 | |
| 5 | x1.5, x2.0 | x2.8 | |
| 6 | x1.6, x2.0 | x3.0 | |
| 7 | x1.7, x2.2 | x3.2 | |
| 8 | x1.8, x2.3 | x3.5 | |
| 9 | x2.0, x2.5 | x3.8 | |
| 10 | x2.0, x2.6 | x4.0 | Never above x4.0 raw (stack via multiple passes) |

Apply: `squad = min(SQUAD_SOFT_CAP, floor(squad * mult))`  
**SQUAD_SOFT_CAP (true count):** 50_000 (HUD); **visible sprites:** 180.

#### Penalty `-N` / halve gates

| L | Spawn `-N` range | After shoot floor | Halve gate chance | Convertible to `+`? |
|---|------------------|-------------------|-------------------|---------------------|
| 1 | −2 … −8 | −0 or +3 | 5% | Yes — 100% if fully shot |
| 2 | −4 … −12 | −1 … +5 | 8% | Yes |
| 3 | −6 … −16 | −2 … +6 | 10% | Yes |
| 4 | −8 … −20 | −3 … +8 | 12% | Yes |
| 5 | −10 … −28 | −5 … +10 | 14% | Yes |
| 6 | −12 … −35 | −6 … +12 | 15% | Yes |
| 7 | −15 … −42 | −8 … +14 | 16% | Yes |
| 8 | −18 … −50 | −10 … +16 | 18% | Yes |
| 9 | −22 … −60 | −12 … +18 | 18% | Yes |
| 10 | −25 … −70 | −15 … +20 | 20% | Yes — still recoverable |

**Halve gate:** on pass, `squad = max(1, floor(squad * 0.5))`. Shoot converts: each full HP step raises multiplier by +0.05 toward 1.0, then into +add mode (see ticks).

#### Weapon tier gates

| L | Spawn tier weight | Max tier after shoot |
|---|-------------------|----------------------|
| 1 | T1 80% / T2 20% | T2 |
| 2 | T1 60 / T2 35 / T3 5 | T3 |
| 3 | T2 50 / T3 40 / T4 10 | T4 |
| 4–5 | T2 30 / T3 40 / T4 25 / T5 5 | T5 |
| 6–7 | T3 35 / T4 40 / T5 25 | T5 |
| 8–10 | T3 20 / T4 40 / T5 40 | T5 |

Tiers: 1 Blaster · 2 Twin Plasma · 3 Scatter Rail · 4 Heavy Plasma · 5 Orbital-linked.

**Relative DPS** (vs T1 = 1.0): `1.0 / 1.55 / 2.3 / 3.4 / 5.0`  
Fire rate ticks/s: `8 / 10 / 12 / 11 / 9` (T4–T5 heavier projectiles).

### 1.3 Shoot-to-upgrade tick curves (gate HP)

Gates have **value steps**. Each **step** requires HP damage.

| Gate type | HP per step L1 | HP per step L10 | Formula |
|-----------|----------------|-----------------|---------|
| `+N` | 6 | 14 | `round(6 + 0.9*(L-1))` |
| `xN` | 10 | 22 | `round(10 + 1.3*(L-1))` |
| `-N` → improve | 5 | 12 | `round(5 + 0.8*(L-1))` |
| Weapon tier | 18 | 36 | `round(18 + 2.0*(L-1))` |

**Step sizes when upgraded by shooting:**

| Type | Per step change |
|------|-----------------|
| `+N` | +1 (L1–3), +2 (L4–7), +3 (L8–10) |
| `xN` | +0.1 mult (display one decimal) |
| `-N` | +2 toward zero, then becomes `+N` at 0 |
| Weapon | +1 tier (max 5) |

**Squad DPS reference (for feel):**

| Squad size | T1 DPS to gate | Time to +1 step on `+N` L1 (HP6) |
|------------|----------------|-----------------------------------|
| 10 | ~10 | ~0.6s |
| 50 | ~50 | ~0.12s |
| 200 | ~200 | instant multi-step |

Design intent: small armies must **commit** to a gate; big armies convert almost instantly (skill = early aiming).

### 1.4 Lane layout weights

| Pattern | Weight L1–3 | L4–10 |
|---------|-------------|-------|
| Left good / right bad | 40% | 30% |
| Left bad / right good | 40% | 30% |
| Both mild positive | 15% | 15% |
| Triple (good / bait / bad) | 0% | 20% |
| Double xN + penalty | 5% | 5% |

---

## 2. Waves & bosses

### 2.1 Level duration budget (seconds)

| Phase | Seconds | Notes |
|-------|---------|-------|
| Intro / empty steer | 2–3 | |
| Wave combat | **70–110** | Scales with L |
| Boss | **18–35** | Queen separate |
| **Total combat** | **90–150** | Design target |

**Wave duration by level:** `waveSec = 70 + 4*(L-1)` (L1=70 … L10=106)  
**Boss budget:** `bossSec = 18 + 1.5*(L-1)` (L1=18 … L10=31.5)  
**Sum:** L1 ≈ 88–95s · L5 ≈ 115s · L10 ≈ 140s → inside 90–150s.

### 2.2 Enemy spawn rates (enemies/sec during wave)

Base spawn rate (all types combined before elite extras):

| L | enemies/sec | Peak simultaneous soft cap | Notes |
|---|-------------|----------------------------|-------|
| 1 | 8 | 120 | Teach |
| 2 | 11 | 180 | |
| 3 | 14 | 250 | |
| 4 | 18 | 350 | Elites start |
| 5 | 22 | 450 | |
| 6 | 27 | 550 | |
| 7 | 32 | 700 | |
| 8 | 38 | 900 | |
| 9 | 45 | 1100 | |
| 10 | 52 | 1400 | Pre-Queen; still under 1.5k perf target with pooling |

Formula: `spawnRate = 8 + 4.9*(L-1)` rounded.

**Micro-waves:** every **8s**, 1.4× rate burst for 1.5s (growth-feel punctuation).

### 2.3 Mix % by level (biomorph / eldritch / cyber-mutant)

| L | Biomorph % | Eldritch % | Cyber-mutant % | Elite extras |
|---|------------|------------|----------------|--------------|
| 1 | 90 | 10 | 0 | none |
| 2 | 85 | 12 | 3 | none |
| 3 | 78 | 15 | 7 | rare |
| 4 | 70 | 18 | 12 | divers 3% of biomorphs |
| 5 | 62 | 22 | 16 | divers 5% |
| 6 | 55 | 25 | 20 | burrowers 4% |
| 7 | 50 | 28 | 22 | divers 6% + burrowers 5% |
| 8 | 45 | 30 | 25 | both 7% |
| 9 | 42 | 32 | 26 | both 8% |
| 10 | 40 | 33 | 27 | both 10% |

### 2.4 Unit stats (baseline)

| Unit | HP | Speed | Contact dmg (units lost) | Death effect |
|------|-----|-------|--------------------------|--------------|
| Biomorph | 8 + 2.2*L | 1.15 | 1 | green splat |
| Eldritch | 45 + 12*L | 0.55 | 2 | big splat |
| Cyber-mutant | 22 + 5*L | 0.85 | 1 | AoE r=48, dmg 3 units |
| Elite diver | 18 + 4*L | 1.6 | 2 | dive once |
| Burrower | 28 + 6*L | 0.7 emerge | 3 | spawn under swarm |

**Player bullet damage T1:** 4 + 0.3*L (global slight scale so late gates remain relevant).

### 2.5 Boss HP curves (levels 1–9)

Boss HP is **effective HP** (sum of weak-point phases).

| L | Boss HP | Phases | Weak points | Adds |
|---|---------|--------|-------------|------|
| 1 | 2_200 | 2 | 1 then 1 | none |
| 2 | 3_400 | 2 | 1+1 | light fodder |
| 3 | 5_000 | 2 | 2 cores | |
| 4 | 7_200 | 3 | 2+1 | |
| 5 | 10_000 | 3 | rotating | cyber adds |
| 6 | 13_500 | 3 | | |
| 7 | 18_000 | 3 | | |
| 8 | 24_000 | 3 | | heavy adds |
| 9 | 32_000 | 3 | | |

Formula fit: `bossHP ≈ 1600 * 1.38^L` (rounded to table).

**Boss contact:** loses 3–8 units/s if stacked on boss body (encourage kiting with steer).

### 2.6 Level 10 — Alien Queen

| Phase | Name | HP | Duration budget | Mechanics |
|-------|------|-----|-----------------|-----------|
| 1 | Egg-laying | **28_000** | ~25–35s | Eggs spawn every **1.8s**; egg HP **120**; hatch → 6 biomorphs if not killed in 4s |
| 2 | Enrage | **36_000** | ~30–40s | Tail sweep every 5s (lane clear), acid spit 3 lanes every 7s |
| 3 | Exposed abdomen | **22_000** | ~20–30s | Single large weak point ×1.5 dmg taken; no eggs |

**Total Queen HP:** 86_000 effective.  
**Egg rate:** 1.8s → ~0.55 eggs/s; with mid squad T4+, player clears eggs with ~30–40% fire diverted.

**Queen clear target:** skilled **70–100s** fight; total L10 including waves still ≤150s if waves trimmed to **55s** on L10 only (`waveSec_L10 = 55` special case).

---

## 3. Economy

### 3.1 Credit earn (per run)

| Source | Credits | Notes |
|--------|---------|-------|
| Biomorph kill | 1 | |
| Eldritch kill | 4 | |
| Cyber-mutant kill | 3 | |
| Elite kill | 6 | |
| Boss clear L | `40 + 25*L` | |
| Level clear bonus | `80 + 40*L` | |
| Queen clear | **2_500** | |
| Death consolation | 15% of run credits | |

**Expected credits per full clear (L1–10, mid skill):** ~**9_500–12_000** first win.  
**Partial run (die L4):** ~1_200–2_000.

### 3.2 Shop cost curve (x1.6 baseline — validated)

Permanent upgrades use:

```
cost(level) = floor(baseCost * (1.6 ** (purchases)))
```

| Upgrade | baseCost | Max purchases | Effect per buy | L0→L5 total cost |
|---------|----------|---------------|----------------|------------------|
| Base damage | 50 | 25 | +8% dmg | 50+80+128+205+328 = **791** |
| Starting squad | 80 | 15 | +2 start units | 80 … **≈1_265** to rank 5 |
| Start weapon tier | 200 | 4 | +1 tier (cap T5) | 200+320+512+819 = **1_851** |
| Biomatter value | 60 | 20 | +10% bar fill | |
| Vehicle drop | 300 | 5 | unlock then +dur/dmg | |
| Perk slot | 500 | 2 | max 5 perk kinds active | 500+800 = **1_300** |

**Validation vs earn rate:**  
After first clear (~10k credits), player can buy **~8–12** meaningful ranks without ads — sinks remain relevant into clear #5–8. Not soft-locked: free revive path is ad, not paywall.

**If too poor:** reduce baseCosts 15% in R2.  
**If too rich:** raise boss/level clear by −20% or shop bases +15%.

### 3.3 In-run perk stack values (max 3 ranks each)

| Perk | Rank 1 | Rank 2 | Rank 3 |
|------|--------|--------|--------|
| Chain Lightning | 1 bounce, 30% dmg | 2 bounce, 40% | 3 bounce, 50% |
| Orbital Laser | every 12s, 80 AoE | 10s, 110 | 8s, 150 |
| Drone Escort | 1 drone 40% dps | 2 drones | 3 drones |
| Acid Rounds | +15% DoT/3s | +25% | +40% |
| Cryo Rounds | slow 15% | 25% | 35% |
| Ricochet | 1 bounce | 2 | 3 |
| Magnet | +40% radius | +80% | +130% |
| Overclock | +12% fire rate | +24% | +40% |
| Shield Matrix | ignore 1 hit / 8s | /6s | /4s |

Perk pick cadence: bar fills from **~18 biomatter + 1 chip ≈ 20 points**; need **100 / 90 / 85** points for pick 1/2/3 (slight accel). First pick ~**25–35s** into level.

### 3.4 Rewarded-ad boosts (non-breaking)

| Offer | Effect | Cap / fairness |
|-------|--------|----------------|
| Double level credits | ×2 for that level only | Once per level |
| Free shop item | One random owned-path upgrade rank | Once per intermission; not highest tier |
| +Squad head start | +15 / +25 / +40 start units by world tier | Once per run start after L1 |
| Revive | 50% of peak squad this run, min 20 | **Once per run** |

These must not exceed **~25%** of long-term progression speed vs no-ads players (portal guideline). Numbers above ≈ +15–22% estimated — OK for R1.

---

## 4. Session pacing vs CrazyGames norms

| Metric | CrazyGames-friendly target | HiVE SWARM R1 |
|--------|----------------------------|---------------|
| Time to first dopamine | <30s | Gates + first growth ~20s |
| Level length | 1–3 min | **90–150s** ✓ |
| Full campaign | 15–40 min | **~20–28 min** mid skill |
| Death → retry | <3s UI | Keep |
| Optional ads | Player-initiated | Rewarded only + interstitial between levels |

**Confirm 90–150s:** wave+boss tables sum into that band (§2.1). L10 Queen is the only special-case wave trim.

**Adjust if playtests show:**
- Levels too short → +10% waveSec  
- Too long → −10% boss HP and −1.0 enemies/sec  
- Growth not felt → shorten gate interval by 0.3s and +1 step size on `+N`

---

## 5. Starting state & death

| Param | Value |
|-------|-------|
| Start squad L1 (no meta) | **8** |
| Start weapon | T1 |
| Start credits | 0 |
| Death at | squad ≤ 0 |
| Near-death recovery | Next `+N`/`xN` fully shot should restore ≥ **max(20, 0.35 * peakSquadThisLevel)** |

---

## 6. Constants cheat-sheet (for `index.html` / sim)

```
GATE_INTERVAL(L)     = max(3.0, 4.2 - 0.12*(L-1))
PLUS_HP_STEP(L)      = round(6 + 0.9*(L-1))
MULT_HP_STEP(L)      = round(10 + 1.3*(L-1))
MINUS_HP_STEP(L)     = round(5 + 0.8*(L-1))
WEAPON_HP_STEP(L)    = round(18 + 2.0*(L-1))
SPAWN_RATE(L)        = round(8 + 4.9*(L-1))
WAVE_SEC(L)          = L==10 ? 55 : (70 + 4*(L-1))
BOSS_HP(L)           = table or round(1600 * 1.38**L)
SHOP_COST(base, n)   = floor(base * 1.6**n)
VISIBLE_SQUAD_CAP    = 180
TRUE_SQUAD_SOFT_CAP  = 50000
GROWTH_PULSE_TARGET  = 20  // seconds
LEVEL_SEC_MIN/MAX    = 90 / 150
```

---

## 7. Round 1 open risks (for Claude / R2)

1. Exact gate HP feel depends on real bullet DPS in sim — retune ±20% after first playable greybox.  
2. Queen egg rate vs fire diversion needs bot stress (`?test=1`).  
3. x1.6 shop may feel steep if first-clear credits land <8k — watch telemetry.  
4. Video-reference extraction (DESIGN §12) may shift gate visual cadence; math above is independent of art.

---

## 8. Files

| File | Role |
|------|------|
| `balance/BALANCE.md` | This document |
| `balance/balance.json` | Machine-readable tables for tools/bots |

---

*End of Round 1 balance pass. Claude: assign Round 2 difficulty tuning against real sim when ready.*
