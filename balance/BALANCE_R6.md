# HiVE SWARM — Balance R6 (post-overhaul regression + CG trial knobs)

**Version:** 6.0 · **Author:** Grok · **Date:** 2026-07-15  
**Inputs:** R4/R5 sign-off models · live `index.html` (still largely flat-scroll as of this pass) · LOOK_TARGET near-band z>0.35  
**Codex R5 look:** ACTIVE (not yet DONE with screenshot) — regression covers **current live** + **intended perspective**  
**No `index.html` edits.**

---

## 1. Perspective / geometry status

| Build | Geometry | Combat spawn |
|-------|----------|--------------|
| **Live now** | Flat scroll; enemies spawn `y=-30`, move with `vy` | Full on-screen path ~5–6s to contact |
| **Intended (Codex R5)** | Road `(u,z)`; **sim only z>0.35**; far layer fake | Spawn at near edge; τ_near ≈ **2.8–3.6s** (R5 used 3.2s) |

**Implication:** Moving to near-only sim **shortens** time-on-target vs full-scroll flat path → less overlapping EHP if spawn rate unchanged → **slightly easier**, not harder. Pool pressure stays well under 900 (R5).

---

## 2. Perspective-sim regression (70% skill, R3/R4 combat model)

Re-ran same logic as R4 sign-off with R5 spawn rates `[8…44]` and power columns.

### 2.1 Live flat geometry (current index)

| L | kill% wave | boss TTK / budget | vs R4 | Flags |
|---|------------|-------------------|-------|-------|
| 1–7 | 100% | ≪ 1.0× budget | same / better | no death |
| 8–9 | 100% | under | same | ok |
| 10 Queen | waves clear | **~10s / 35s** | same | **PASS** |

**Death before L8 at 70%:** none.  
**Boss >1.5× budget:** none.

### 2.2 Near-band geometry (Codex-intended)

Assumptions: `spawnNear = BAL.spawnRate` at z=0.35; τ_near=3.2s; far not simulated.

| Metric | R4 flat | Near-band R6 | Delta |
|--------|---------|--------------|-------|
| Peak N_near L10 | ~rate×5.5s path ≈ 240* | rate×3.2 ≈ **141** | **−40% live pressure** |
| Wave kill% 70% | 100% | **100%** (more margin) | easier |
| Boss TTK | as R4 | **unchanged** (boss not band-gated the same way) | same |
| Death before L8 | no | **no** | same |

\*Order-of-magnitude under full path; still ≪900.

### 2.3 Verdict

| Check | Result |
|-------|--------|
| 70% campaign no death before L8 | **PASS** (live + near-band) |
| Boss TTK ≤ 1.5× budget | **PASS** |
| Near spawn rate correction needed? | **No** — keep R5 table |
| Soft pool brake live>850 | Keep from R5 |

**Optional if perspective feels empty:** +10% far visual density only (`intent*22 → intent*26`); do **not** raise `spawnNear`.

---

## 3. CrazyGames portal metrics prediction

### Session construction

| Segment | Est. duration |
|---------|----------------|
| Level combat | waveSec + boss ≈ 90–130s mid |
| Shop / ad | **12–25s** (first sessions longer) |
| Death→retry | 3–8s |

### 50% skill (trial-typical first session)

From R4 50% model: campaign **survives all 10** in pure math (gates still strong). Real first-timers miss more gates / die earlier.

| Scenario | Levels seen | Median session (est.) |
|----------|-------------|------------------------|
| Die L3 (messy gates) | 1–3 | **4–7 min** |
| Die L5 | 1–5 | **9–14 min** |
| Die L8 | 1–8 | **16–24 min** |
| Full clear first try | 1–10 | **22–32 min** |

**P(die before L3) soft target for trial:** ~25–35% of cold starts.  
**Risk of <3 min median:** only if L1 is confusing / soft-locked — currently L1 is **trivial** (R4) → **low risk of sub-3min from difficulty**; risk is **bounce from UX** (controls, mute, orientation), not HP sponges.

### First-session content depth

| Beats before first death (recommended) | Why |
|----------------------------------------|-----|
| Gates + first growth | 0–30s |
| First perk | ~30–50s |
| L1 boss | ~1.5–2 min |
| L2–3 environments | novelty |
| **Ideal first death: L4–L5 boss or mid L5** | Engagement peak: learned gates, not yet bored; retry is cheap |

**Recommendation:**  
- **Do not** buff L1–2 difficulty for trial (keeps >3 min).  
- Optional: first-run tip + slightly juicier L1 boss FX so clear feels earned.  
- If analytics show median **>20 min** and low D1 return, nudge **D hard** (below), not raw tables.

### Loading

Single-file `index.html` + tiny assets → load risk low. Flag only if sprite atlas balloons post-art pass (>5–8 MB uncompressed).

---

## 4. Global difficulty scalar **D**

One knob applied in sim (Claude/Codex hot-tweak):

```js
// Apply after BAL lookups
e.hp     *= D;           // all enemy + boss + queen phase HP
// spawn:
spawnAcc += BAL.spawnRate[li] * endlessSpawn * D_spawn * dt;
// where:
D_spawn = 1 + 0.5 * (D - 1);   // spawn reacts half as hard as HP
// credits unchanged (don't punish grinding with D)
```

Equivalent compact form:

```
HP  × D
spawn rate × (0.5 + 0.5*D)
```

### Presets

| Preset | **D** | Feel | When |
|--------|-------|------|------|
| **easy** | **0.85** | Faster clears, more dopamine | Median session low / high bounce on death |
| **default** | **1.00** | R4/R5 sign-off | Ship / trial start |
| **hard** | **1.18** | Later deaths L6–8 | Median session too long; veterans only |

**Do not** re-derive per-level tables for trial — only touch **D**.

Validation sketch @70% skill:

| D | Queen TTK (rel) | Death-before-L8 risk |
|---|-----------------|----------------------|
| 0.85 | ~0.85× | lower |
| 1.00 | baseline ~10s | none (sign-off) |
| 1.18 | ~1.18× still ≪35s | still low at 70%; 50% skill dies earlier |

---

## 5. Delta vs R4 (summary)

| Item | R4 | R6 |
|------|----|----|
| Campaign 70% | PASS | **PASS** (unchanged / easier under near-band) |
| Queen | PASS | **PASS** |
| Spawn rates | R5 table | **Keep** |
| New | — | **D** presets · CG session estimates · ideal first death L4–5 |

---

## 6. Merge checklist

1. Keep spawnNear = R5 rates.  
2. Implement far visual only (Codex).  
3. Add `CFG.difficulty D` + presets easy/default/hard.  
4. Streak/Endless from R5 if not already in.  
5. Re-bot after perspective lands; if τ_near measured ≠3.2s ±20%, ping Grok R6.1.

---

## 7. Files

- `balance/BALANCE_R6.md`
- `balance/balance.json` v6.0

*End R6.*
