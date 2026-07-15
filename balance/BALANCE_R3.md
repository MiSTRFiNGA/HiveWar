# HiVE SWARM — Balance R3 (economy + column-cap fix)

**Version:** 3.0 · **Author:** Grok · **Date:** 2026-07-15  
**Input:** R2 merged (`dec200e`) + live `fire()` model  
**Deliverables:** this file + `balance.json` v3.0  
**Constraint:** no `index.html` edits — Claude merges  

---

## 1. Column-cap bottleneck — option eval

Live model (R2):

```
cols = min(squad, 14)
DPS  = cols × n × (dmg + 0.5·meta) × (1 + 0.06·log2(1+squad)) × rof
```

After squad **14**, only the weak log2 term grows. L10 wave EHP/s ≈ **3200** (R2 spawn/HP); T5@14cols ≈ **692** DPS → structural late leak.

### Options modeled

| Opt | Idea | T5 DPS @50 / @200 / @1000 | L10 kill vs ~3200 EHP/s | Notes |
|-----|------|---------------------------|-------------------------|--------|
| **(a)** | `cols = min(14 + floor(squad/50), 22)` | 805 / 1052 / 1408 | still **fail** at 1000 | Simple; not enough alone |
| **(b)** | Raise log2 coeff → ramp 0.06→0.14 | 797 / 1137 / 1343 | fail | Soft feel; still short |
| **(c)** | Overflow volley every N sec | 755 / 847 / 1070 | fail unless volley huge | Juicy VFX; tuning fragile |
| **PICK** | **Power-column scale (a-strong)** below | 752→ / **~1800+** / **~2900+** | **pass** late | Clean, one formula |

### Recommended formula (pick)

**Winner: option (a) generalized — power-scaled columns** (readable, one line, no extra systems):

```js
// Replace: const cols = Math.min(G.squad, 14);
const cols = Math.min(
  48,
  Math.max(1, Math.floor(14 * Math.pow(Math.max(G.squad, 1) / 14, 0.45)))
);
// squad 14 → 14 cols
// squad 56 → ~24
// squad 200 → ~40
// squad 400+ → cap 48
```

Keep existing bullet log2 term as-is.

**Why not pure (b)/(c):** neither reaches L10 wave EHP without absurd coefficients; (c) needs new systems and pool pressure.  
**Why not raw (a) with max 22:** math shows max 22 cols never clears ~3.2k EHP/s at T5.

### Side effects of PICK

| Effect | Handling |
|--------|----------|
| More bullets at huge squads | Already pooled; LOD if FPS dips (particle half) |
| Visual “wall of fire” | Desired fantasy |
| Mult overflow less critical | Still soft-cap mults from R2 |

### Revised late tables (only if Claude adopts PICK)

With PICK, **R2 spawnRate L8–10 can stay** (34/39/44) — kill rate recovers.  
If Claude keeps hard 14-cap, **must** further cut L9–10 spawn ~20% (not preferred).

Optional companion (only if PICK still short in bot):

```js
// mild overflow (optional R3.1)
const overflow = Math.max(0, G.squad - 14);
b.dmg *= 1 + 0.04 * Math.log2(1 + overflow / 14);
```

---

## 2. Economy long game (25-level baseDamage sink)

### Live cost model

```
cost(n) = floor(baseCost * 1.6^n)   // n = purchases already owned
```

| Upgrade | base | max | Total credits to max |
|---------|------|-----|----------------------|
| baseDamage | 50 | 25 | **~10.56M** |
| startSquad | 80 | 15 | ~1.27M |
| startWeapon | 200 | 4 | ~1.85k |
| biomatterValue | 60 | 20 | ~3.0M |
| vehicleDrop | 300 | 5 | ~2.5k |
| perkSlot | 500 | 2 | 1.3k |
| **All** | | | **~11.9M** |

**Earn:** ~**11–13k** credits per full L1–10 clear (mid skill, R2).

| Metric | At ×1.6 / max25 baseDamage |
|--------|----------------------------|
| Runs to max **only** baseDamage | **~960 runs** |
| Wall-clock @ 25 min/run | **~400 hours** |
| First 10 ranks | ~9.1k (≈1 clear) — good early curve |
| Ranks 20–24 alone | ~9.6M — **dead sink** |

**Verdict:** Early curve good; **late ranks are fictional** (never reached). Not a balance problem for first-week players, but **shop UX lies** if UI shows rank 25.

### Recommended economy (R3)

| Param | R1/R2 | **R3** |
|-------|-------|--------|
| baseDamage max | 25 | **15** |
| baseDamage baseCost | 50 | **45** |
| shop growth (all) | 1.6 | **1.50** for permanent combat stats; keep **1.6** only for perkSlot/vehicle |
| startSquad max | 15 | **12** |
| biomatterValue max | 20 | **12** |

**Approx totals after R3:** baseDamage 15 ×1.5 from 45 ≈ **~50–70k** → **~5–6 full clears** to soft-cap main DPS meta — healthy for CG retention without infinite grind.

**Damage effect alignment:** Design text says +8%/rank; sim uses `+0.5 flat` on bullet.  
Recommend Claude unify to:

```js
// percent model (cleaner long-game)
b.dmg = w.dmg * (1 + 0.08 * G.meta.dmg) * (1 + 0.06 * Math.log2(1 + G.squad));
// cap meta.dmg at 15 → +120% weapon base
```

Until then, flat +0.5 remains strong early / weak late (OK with column PICK).

**Time-to-soft-cap estimate (R3):** ~**2–3 hours** play for main combat metas; prestige cosmetics later.

---

## 3. Endless Hive / NG+

### Mode entry
After first Queen kill → unlock **Endless Hive** (DESIGN §3). Separate high-score run from campaign.

### Wave scaling (per loop index `k = 0,1,2,…`)

```
spawnRate_k = spawnRate[L10] * (1.09 ** k)      // +9%/loop
hpMult_k    = 1.12 ** k                          // +12% HP all units
bossHp_k    = 32000 * (1.15 ** k)                // mini-boss every 3 loops optional
creditMult  = 1.10 ** k                          // rewards track threat
```

| Loop k | spawn× | HP× | credit× | Feel |
|--------|--------|-----|---------|------|
| 0 | 1.00 | 1.00 | 1.00 | Queen+ post |
| 3 | 1.30 | 1.40 | 1.33 | spicy |
| 6 | 1.68 | 1.97 | 1.77 | sweat |
| 10 | 2.37 | 3.11 | 2.59 | leaderboard |

**Gate values:** freeze at L10 tables; do **not** inflate `+N` (prevents infinite mult break).  
**Weapon:** stays at run’s tier; meta applies.

### Soft fail / length
- No hard end; death → score screen.  
- Target death for mid skill: loops **4–8** (~8–15 min endless session).

### Leaderboard score

```
score = floor(
    kills * 10
  + bosses * 500
  + maxSquad * 2
  + loop * 2000
  + creditsEarned * 0.25
  + (weaponTier+1) * 100
)
```

Deterministic, no time bonus (avoids stalling). Display `loop` and `score`.

### NG+ campaign (optional lighter)
New Game+: start with **+1 weapon tier** (cap T5) and **+10% enemy HP** permanent for that profile flag; credits carry. Not required for M3.

---

## 4. Merge checklist (Claude)

1. **Columns:** adopt PICK formula (§1).  
2. **Economy:** max ranks + growth R3 (§2); optional percent dmg.  
3. **Endless:** new state `endless` using loop scalers + score (§3).  
4. Re-bot `?test=1` L8–10 + 3 endless loops.  
5. No balance file renames required.

---

## 5. Files

| Path | Role |
|------|------|
| `balance/BALANCE_R3.md` | This doc |
| `balance/balance.json` | v3.0 machine tables |
| `balance/BALANCE_R2.md` | Prior sim validation |
| `balance/BALANCE.md` | R1 bible |

---

*End R3. Monitor continues for R4 if Claude posts.*
