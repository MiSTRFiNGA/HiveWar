# HiVE SWARM — Balance R5 (horde density + streaks + Endless)

**Version:** 5.0 · **Author:** Grok · **Date:** 2026-07-15  
**Context:** Perspective road + far-horde fake layer (z≤0.35 render-only); near band z>0.35 simulated (Codex look pass / LOOK_TARGET).  
**Live pools:** enemies 1600 · bullets 900 · target live near ≤**900** (headroom for boss adds).  
**No `index.html` edits.**

---

## 1. Horde density model (near sim + far fake)

### Geometry assumptions (from LOOK_TARGET)

| Param | Value | Notes |
|-------|-------|-------|
| z range | 0 horizon → 1 squad | perspective road |
| Near band | **z > 0.35** | real HP/collision |
| Far layer | **z ≤ 0.35** | sprites only, no pool |
| Near depth fraction (linear z) | 0.65 | |
| Typical near dwell | **2.8–3.6 s** | depends on `vy + scroll`; use **τ_near = 3.2 s** for design |
| Far transit (visual only) | **1.4–2.0 s** | cosmetic pack |

### Steady-state near count

```
N_near ≈ spawnNear(L) × τ_near
```

Target: **N_near ≤ 750 peak wave** at L10 (≤900 hard, leave ~150–250 for boss minions/eggs).

| L | BAL spawnRate (intent) | **spawnNear/s (R5)** | Est. N_near @ τ=3.2 | Headroom to 900 |
|---|------------------------|----------------------|---------------------|-----------------|
| 1 | 8 | **8** | 26 | ok |
| 2 | 11 | **11** | 35 | ok |
| 3 | 14 | **14** | 45 | ok |
| 4 | 18 | **18** | 58 | ok |
| 5 | 22 | **22** | 70 | ok |
| 6 | 27 | **27** | 86 | ok |
| 7 | 32 | **32** | 102 | ok |
| 8 | 34 | **34** | 109 | ok |
| 9 | 39 | **39** | 125 | ok |
| 10 | 44 | **44** | 141 | ok |

**Verdict:** Current BAL `spawnRate` already satisfies the **900 live cap** with huge margin under τ≈3.2s.  
**Do not cut rates** for pool safety — density must come from the **far fake wall**.

If Codex’s near dwell is longer (slow scroll), clamp:

```js
// soft cap near spawns if pool pressure high
if (enemies.live > 850) spawnAcc *= 0.35;
```

### Far-layer density (visual wall)

Far entities are **not** in `enemies` pool. Density should *look* like full-road BAL pressure from the horizon.

```js
// particles or instanced dots in far band; update each frame
// L = level, t = levelT or G.t, k = endless loop
const intent = BAL.spawnRate[L-1] * (G.mode==='endless' ? Math.pow(1.09, G.loop) : 1);
// visual "bodies" packed on road u∈[-1,1], z∈[0.02, 0.35]
const farCount = Math.min(
  1400,  // GPU/CPU cheap sprites budget
  Math.floor(
    180 + intent * 22               // base wall thickness vs spawn intent
    + L * 35                        // deeper campaign = thicker wall
    + 40 * Math.sin(t * 0.7)        // breathing churn
  )
);
// Optional: recycle far sprites in a ring buffer; scale = lerp(0.12, 0.38, z)
```

| Term | Role |
|------|------|
| `180 + intent×22` | Wall thickness tracks balance spawn intent |
| `L×35` | Late campaign denser horizon |
| `sin` | Kill-line churn illusion |
| Cap 1400 | Stay cheap on mobile |

**Kill line (mid-screen):** when far sprites cross z=0.35, either (a) promote 1:1 into near spawn budget already counted by `spawnNear`, or (b) despawn far and rely solely on `spawnNear` — prefer **(b)** so pressure stays = BAL tables (no double spawn).

### Effective pressure contract

| Layer | Contributes to DPS/TTK? | Count source |
|-------|-------------------------|--------------|
| Far | No | `farCount(L,t,k)` |
| Near | Yes | `spawnNear = BAL.spawnRate` (R4 table) |
| Boss adds | Yes | existing egg/minion rates; keep near total ≤900 |

---

## 2. Kill-streak counter

Matches LOOK_TARGET big center numbers without wrecking R3/R4 economy (~12k/clear soft-cap).

| Param | Value |
|-------|-------|
| **Streak window** | **1.15 s** without a kill → reset |
| Combo grace on boss phase shift | +0.4 s once |

### Display thresholds (show big popup when crossing)

| Streak | Label | Popup scale |
|--------|-------|-------------|
| 10 | HOT | 1.0 |
| 25 | RAMPAGE | 1.15 |
| 50 | GENOCIDE | 1.3 |
| 100 | SWARM BREAKER | 1.5 |
| 250 | HIVE CRISIS | 1.7 |
| 500 | EXTINCTION | 2.0 |

### Credit bonus (small)

| Streak tier reached | One-shot bonus credits | Per-kill while in tier |
|---------------------|------------------------|------------------------|
| 10 | +3 | +0 |
| 25 | +6 | +0 |
| 50 | +12 | +0 |
| 100 | +25 | +0 |
| 250 | +50 | +0 |
| 500 | +80 | +0 |

**Also:** optional tiny per-kill `floor(streak/100)` credits (0–5) — **off by default** (can inflate endless).

**Economy check:** aggressive player might hit 100-streak ~3–6× per level → ~100–200 bonus credits/run ≪ 12k (**~1–2%**). Safe.

### Implementation notes

```js
// on kill:
if (now - G.lastKillT < 1.15) G.streak++; else G.streak = 1;
G.lastKillT = now;
// if G.streak hits a threshold not yet awarded this streak life → add bonus once
```

---

## 3. Endless Hive validation (live exponents)

### Live (Codex landed)

```
spawn × 1.09^k
HP    × 1.12^k
boss  32000 × 1.15^k
credits × 1.10^k
gates frozen at L10
```

Threat growth per loop (wave EHP/s):

```
threat(k) ∝ 1.09^k × 1.12^k = 1.2208^k
```

### Player DPS ceiling (R3/R4 model, T5, high squad)

| Squad | cols (power) | DPS ≈ |
|-------|--------------|-------|
| 14 | 14 | 690 |
| 100 | 33 | ~1850 |
| 400+ | 48 | ~2900 |

L10 base wave EHP/s ≈ **3200** (R4 tables).

| Loop k | threat× | EHP/s | kill% @2900 DPS | Feel |
|--------|---------|-------|-----------------|------|
| 0 | 1.00 | 3200 | 91% | strong |
| 1 | 1.22 | 3900 | 74% | ok |
| 2 | 1.49 | 4770 | 61% | sweat |
| 3 | 1.82 | 5820 | 50% | leaky |
| 4 | 2.22 | 7100 | 41% | **death likely** |
| 5 | 2.71 | 8670 | 33% | dead |
| 6 | 3.31 | 10600 | 27% | dead |

**Verdict vs target death loops 4–8:** current curve kills **mid skill ~ loops 3–5** — slightly **early**. Boss 1.15^k is fine; **wave threat is the spike**.

### R5 recommended Endless exponents

| Param | Live | **R5** | Why |
|-------|------|--------|-----|
| spawn | 1.09^k | **1.07^k** | slower density climb |
| HP | 1.12^k | **1.10^k** | softer sponges |
| combined wave | 1.221^k | **~1.177^k** | |
| boss | 1.15^k | **1.13^k** | match wave |
| credits | 1.10^k | **1.12^k** | slightly better reward for lasting |

Recomputed kill% @2900 DPS, base 3200:

| k | threat× R5 | kill% | |
|---|------------|-------|---|
| 0 | 1.00 | 91% | |
| 2 | 1.39 | 65% | |
| 4 | 1.92 | 47% | sweat |
| 6 | 2.66 | 34% | **death zone** |
| 8 | 3.68 | 25% | dead |

→ Mid skill death **~loops 5–7**, high skill **7–9** with meta/perks — fits **4–8** target band.

### Score formula (keep R3)

```
score = floor(kills*10 + bosses*500 + maxSquad*2 + loop*2000
            + creditsEarned*0.25 + (weaponTier+1)*100)
```

No change required; loop weight already leaderboard-friendly.

---

## 4. Merge checklist (Claude / Codex)

1. Keep `BAL.spawnRate` as R4 (near-band rates §1 table).  
2. Add far-layer `farCount` renderer; **do not** double-count into sim.  
3. Soft pool brake if `enemies.live > 850`.  
4. Kill-streak §2.  
5. Endless exponents → R5 table §3.  
6. Bot: campaign L10 + endless until death; log loop index.

---

## 5. Files

| File | Role |
|------|------|
| `balance/BALANCE_R5.md` | This doc |
| `balance/balance.json` | v5.0 |

*End R5.*
