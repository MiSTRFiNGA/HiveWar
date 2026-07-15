# HiVE SWARM — Balance R2 (sim validation)

**Version:** 2.0 · **Author:** Grok · **Date:** 2026-07-15  
**Against:** `index.html` commit with `BAL` + `WEAPONS` (R1 integrated)  
**Method:** Closed-form DPS matching live `fire()` + gate-growth monte-ish model  
**Artifacts:** `balance/BALANCE_R2.md`, `balance/balance.json` (v2.0), `balance/r2_validate.py`, `balance/r2_raw.json`  
**Do not edit `index.html`** — Claude merges.

---

## 1. Real sim DPS model (verified)

From `fire()` in `index.html`:

```
cols   = min(squad, 14)
rof    = weapon.rof * (1 + 0.15 * OverclockStacks)
bullet = (weapon.dmg + meta.baseDamage * 0.5) * (1 + 0.06 * log2(1 + squad))
DPS    = cols * weapon.n * bullet * rof
```

| Tier | name | n | dmg | rof | DPS @ squad≥14, meta0 | ratio vs T1 |
|------|------|---|-----|-----|------------------------|-------------|
| 1 | Blaster | 1 | 1.00 | 8 | **138.3** | 1.00 |
| 2 | Twin Plasma | 2 | 0.62 | 10 | **214.3** | 1.55 |
| 3 | Scatter Rail | 4 | 0.38 | 12 | **315.2** | 2.28 |
| 4 | Heavy Plasma | 3 | 0.82 | 11 | **467.6** | 3.38 |
| 5 | Orbital Link | 5 | 0.89 | 9 | **692.1** | 5.01 |

**Note:** Claude’s handoff cited 112/174/258/381/560 — that is the **pre-log2** product `14×n×dmg×rof`. Live game multiplies by `1+0.06·log2(1+squad)` (~×1.234 at squad=14), so use **138…692** for TTK.

**Critical structural fact:** after **14 squad**, adding soldiers barely raises DPS (log2 only). Power fantasy is visual count + rare weapon/meta/perk spikes. R1 tables assumed more continuous scaling than the sim delivers.

---

## 2. Assumed “decent play” squad model

- Start run: squad `8 + 2·meta.squad`, weapon `min(4, meta.weapon)`.
- Per level: `gates ≈ waveSec / interval(L)`; take **~70%** as positive (add / mult / weapon 55/30/15).
- Squad **carries within a run** (matches continuous play, not per-level reset).
- Boss TTK uses **end-of-wave** DPS; wave pressure uses **~mid-level** DPS.

Script: `python balance/r2_validate.py` → `balance/r2_raw.json`.

---

## 3. Findings (fresh run, no meta)

| L | mid kill rate vs spawn EHP/s | boss TTK / budget | Flags |
|---|------------------------------|-------------------|-------|
| 1–6 | ≥100% | well under budget | **ok** |
| 7 | ~94% | under | ok |
| 8 | ~80% | under | mild pressure |
| 9 | ~70% | under | borderline |
| 10 waves | ~58% | — | **WAVE_LEAK risk** (mid) |
| 10 Queen 86k | — | **~32s / 35s** | **ok** if T5 + huge squad at arrival |

**Boss fights (L1–9):** no level exceeds `bossSecBudget × 1.5`. R1 boss HP is **generous for the player** once columns fill.

**Queen 86k:** reachable in ~32s with end-L10 DPS ~2650 (T5, capped columns). With Overclock 3 (~×1.4 rof) ≈ **23s**. **No forced Queen HP cut** if players typically hold T4–T5 by L10; optional softer Queen below if first-win data shows fails.

**Wave leak:** L9–L10 spawn EHP/s outruns mid-level column-capped DPS. Elites (divers/burrowers) in live `spawnWave` add extra pressure not fully in mix tables.

**Squad overflow:** mult compounding produces absurd true counts (millions+) by mid campaign — fine for HUD “xN” fantasy, useless for DPS, can stress UI/debug. Recommend softer mults (below).

**Light meta (dmg5, +6 start squad, start W2):** all kill% ≥100%, bosses trivial, Queen ~8.5s — meta is strong (OK for retention, watch shop sink R3).

---

## 4. Corrected tables (R2)

### 4.1 Spawn rate (fix late WAVE_LEAK)

| L | R1 | **R2** |
|---|----|--------|
| 1–7 | 8…32 | unchanged |
| 8 | 38 | **34** |
| 9 | 45 | **39** |
| 10 | 52 | **44** |

```
spawnRate: [8,11,14,18,22,27,32,34,39,44]
```

### 4.2 Unit HP (slight tank nerf — eldritch was sponge relative to capped DPS)

| Unit | R1 | **R2** |
|------|----|--------|
| Biomorph | `8+2.2L` | **`8+2.0L`** |
| Eldritch | `45+12L` | **`38+9.5L`** |
| Cyber | `22+5L` | **`20+4.5L`** |

Elite (live code, not R1 json): keep `30+7L` diver / `45+10L` burrower — monitor; if still spongy, R2.1 → `26+6L` / `40+9L`.

### 4.3 Boss HP (keep early challenge, shave late fat)

Bosses already clear fast at end-wave DPS; **no increase**. Optional −10% L7–9 only if players report boredom:

```
bossHp R2: [2200,3400,5000,7200,10000,13500,16000,21000,28000,0]
```

(L7–9 −11–12%; L1–6 unchanged.)

### 4.4 Queen (optional soft path)

**Default keep** `28000 / 36000 / 22000` (86k) — validated vs 35s with T5.

**If first-win Queen fails >40% in telemetry**, use:

```
queen R2-soft: p1=24000, p2=30000, p3=18000  # total 72k → ~27s at 2650 DPS
eggInt: 2.0 (was 1.8), eggHp: 100 (was 120)
```

### 4.5 Gate mult soft-cap (anti-overflow)

True count explosion is cosmetic-only but pollutes balance intuition.

| L | multCap R1 | **multCap R2** |
|---|------------|----------------|
| 1–5 | 2.0–2.8 | unchanged |
| 6 | 3.0 | **2.8** |
| 7 | 3.2 | **2.9** |
| 8 | 3.5 | **3.0** |
| 9 | 3.8 | **3.1** |
| 10 | 4.0 | **3.2** |

`plusCap` unchanged (still feeds the every-~20s dopamine when under column cap).

### 4.6 Recommended formula tweak for Claude (optional, not required for R2 merge)

To make post-14 squad matter without breaking mobile:

```js
// in bullet dmg:
const overflow = Math.max(0, G.squad - 14);
bullet *= (1 + 0.06 * Math.log2(1 + G.squad) + 0.0004 * Math.sqrt(overflow));
```

If adopted, **revert spawnRate R2 cuts by half** (use midpoint of R1/R2).

### 4.7 Economy

No R2 change. Shop ×1.6 still OK. R3 = long-meta sink (25-level baseDamage) + Endless scaling.

---

## 5. Session pacing re-check

| Level | waveSec | boss budget | wave+boss est. |
|-------|---------|-------------|----------------|
| 1 | 70 | 18 | ~90s |
| 5 | 86 | 24 | ~110s |
| 9 | 102 | 30 | ~132s |
| 10 | 55 + Queen ≤35 | | **≤90s** special |

Still inside **90–150s** design band. Growth pulse via gate interval still ~20s.

---

## 6. Merge checklist for Claude

1. Replace `BAL.spawnRate` with R2 array.  
2. Replace `BAL.hp` lambdas with R2 formulas.  
3. Optionally apply `bossHp` L7–9 trims.  
4. Apply `multCap` soft list.  
5. Queen: keep unless QA fails.  
6. Do **not** require index formula change for R2 accept.  
7. Re-run `?test=1` bot on L8–10 + Queen for empirical leak rate.

---

## 7. Summary flags

| Issue | Severity | Action |
|-------|----------|--------|
| Column cap → late WAVE_LEAK | **High** | spawnRate + eldritch HP R2 |
| Boss too easy at end-wave | Low | optional bossHp trim L7–9 |
| Queen 86k | OK | keep; soft alt documented |
| Mult overflow counts | Med | multCap soft |
| Meta strong | Low | OK; R3 economy |

---

*End R2. Awaiting Claude merge + R3 economy long-game.*
