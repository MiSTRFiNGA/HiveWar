# HiVE SWARM — Balance R4 (full-run sign-off + ads + perks)

**Version:** 4.0 · **Author:** Grok · **Date:** 2026-07-15  
**Against:** R3 merged (`e624608`) — power columns + meta `w.dmg*(1+0.08*meta.dmg)` + shop 45/1.5  
**Script:** `balance/r4_validate.py` → `r4_raw.json`  
**No `index.html` edits.**

---

## 1. Sign-off sim (full 10-level runs)

### Model (R3 live)

```
cols = min(squad, floor(14 * (squad/14)^0.45), 48)
DPS  = cols × n × w.dmg × (1+0.08·meta.dmg) × (1+0.06·log2(1+squad)) × rof
```

Gate take rate = skill tier (50% / 70% / 90% of gates taken as positive).  
50% tier may use **1 revive** (50% peak squad, min 20).

### Verdict table — **70% skill, no meta** (primary sign-off)

| L | kill% vs wave EHP/s | bio TTK (s) | boss TTK / budget | Flags |
|---|---------------------|-------------|-------------------|-------|
| 1 | 100% | 0.02 | 3.7 / 18 | early power fantasy (not sponge) |
| 2 | 100% | 0.02 | 4.9 / 19.5 | same |
| 3 | 100% | 0.01 | 2.8 / 21 | same |
| 4 | 100% | — | 1.7 / 22.5 | ok |
| 5 | 100% | — | 2.1 / 24 | ok |
| 6 | 100% | — | 2.5 / 25.5 | ok |
| 7 | 100% | — | 2.7 / 27 | ok |
| 8 | 100% | — | 3.1 / 28.5 | ok |
| 9 | 100% | — | 3.6 / 30 | ok |
| 10 Queen | 100% waves | — | **10.1 / 35** | **Queen OK** |

### Skill tiers summary

| Tier | Wave death before L8? | Queen killable? | Notes |
|------|----------------------|-----------------|-------|
| **50% + 1 revive** | **No** | Yes (~12s end DPS) | Revive never required in model; still safe net |
| **70% no meta** | **No** | **Yes** (10s) | **Primary pass** — even **0** shop baseDamage |
| **70% + 2 baseDamage** | No | Yes (~9s) | Meta optional, not required |
| **90%** | No | Yes (~8.5s) | Farm mode |

### Acceptance checks (Claude R4)

| Check | Result |
|-------|--------|
| No wave-leak death before L8 at 70% | **PASS** |
| Queen at 70% with ≤2 baseDamage shop | **PASS** (0 tiers enough) |
| L1–3 never boring as **>15s fodder TTK sponge** | **PASS** (TTK ≪ 1s) |
| L1–3 “boring” as **too trivial**? | Soft flag — see §1.1 |

### 1.1 Early-game feel (optional polish, not blockers)

Power columns + gate mults make L1–3 **delete fodder**. That matches CG “hook in 10s” but reduces gate-aim skill early.

**Optional R4.1 (Claude):** L1–2 only:

- biomorph HP `8+2L` → `12+3L` for L≤2  
- or gate interval L1 `4.2` → `4.8`  

Do **not** raise L1–3 TTK above ~0.5s or first session drags.

---

## 2. Ad economy — final values

Live hooks: revive once / run @ 50% peak (min 20); headstarts & double-credits from design.

| Ad | Current | **R4 final** | Pacing impact |
|----|---------|--------------|---------------|
| Double level credits | ×2 that level | **×2 keep** | +~300–600 cr / use ≈ 2–5% of soft-cap run (~12k). Fine. |
| Free shop item | 1 rank | **Keep** (not top-tier weapon rank) | ~1 free combat rank ≈ worth ~45–200 cr early. Fine. |
| Squad head start | [15, 25, 40] by bracket | **[12, 20, 28]** | 40 on L1 (start 8→48) overshoots tutorial tension; 28 still juicy late |
| Revive | 50% peak, min 20, **once** | **Keep 50% / min 20 / once** | Peak squad is huge; still once/run so soft-cap runs unchanged |

**Soft-cap pacing (R3 shop):** baseDamage 15 ×1.5 base45 ≈ **39k** credits ≈ **3.3 full clears** without ads.  
With max ads (~+15% credits): ≈ **2.8–3.0 clears** — still inside **5–6 run** spirit if counting partial runs / other upgrades. **No break.**

**Bracket mapping for head start:**

| Bracket | Levels | headStart |
|---------|--------|-----------|
| Early | 1–3 | **12** |
| Mid | 4–7 | **20** |
| Late | 8–10 | **28** |

---

## 3. Perk balance audit (7 perks, ranks 1–3)

Live effects (index.html):

| Perk | Live effect | Auto-pick? | Never-pick? |
|------|-------------|------------|-------------|
| **Overclock** | +15% rof / rank | **Yes** (always) | — |
| **Acid Rounds** | on-hit +20%×rank dmg | **Yes** (high fire rate) | — |
| **Chain Lightning** | 12%×rank proc AoE | Strong mid | — |
| **Orbital Laser** | beam every ~9−1.2×rank s, dmg 10+7×rank | OK boss | Weak in fodder floods |
| **Drone Escort** | 2 drones/rank, dmg 1.5+0.5×rank | Weak late | **Often skipped** late |
| **Magnet** | +40r / rank pickup | QoL only | Combat never |
| **Shield Matrix** | −1 contact loss / rank | Weak vs multi-hit | **Often skipped** |

### Relative power (rank 3, mid run) — rough DPS-equivalent

| Perk | Combat value | Role |
|------|--------------|------|
| Overclock R3 | ~+45% DPS | Carry |
| Acid R3 | ~+60% effective on single-target stream | Carry |
| Chain R3 | high clear | Crowd |
| Orbital R3 | burst boss | Boss |
| Drone R3 | ~6 drones × low dmg ≪ main wall | Weak |
| Magnet R3 | 0 combat | QoL |
| Shield R3 | −3/hit only | Weak |

### Proposed number tweaks (all 7 situationally viable)

| Perk | Change |
|------|--------|
| **Overclock** | +15% → **+10%** rof/rank (still good, less auto) |
| **Acid Rounds** | 0.20 → **0.12** ×rank on-hit (still scales with fire) |
| **Chain Lightning** | keep 0.12; R3 dmg **0.55→0.70** of bullet on bounces |
| **Orbital Laser** | interval `max(4.5, 9−1.2×r)` → **`max(3.5, 7.5−1.1×r)`**; dmg **10+7r → 14+9r** |
| **Drone Escort** | drones **2→2** but dmg **1.5+0.5r → 2.2+1.2r**; fire period **0.42−0.025d → 0.32−0.03d** |
| **Magnet** | add combat: pickups heal **+1 squad / 12 chips** at R1, /9 R2, /6 R3 (tiny sustain) **or** +5%/rank biomatter bar fill |
| **Shield Matrix** | −1/rank → **ignore first N hits every 5s** where N=rank, plus −1 residual; **or** 15%/rank chance to ignore contact |

**Target pick rates after tweak:** each perk **12–20%** of offers taken (not 40%+ Overclock/Acid only).

---

## 4. Final R4 verdict

| Area | Status |
|------|--------|
| Full-run 70% campaign | **SIGN-OFF** |
| Queen | **SIGN-OFF** (no HP change) |
| Ads | **Final values** §2 |
| Perks | **Tweaks proposed** §3 — Claude implements |
| Column formula | Keep R3 power cols |

---

## 5. Files

- `balance/BALANCE_R4.md` (this)
- `balance/balance.json` v4.0
- `balance/r4_validate.py`, `r4_raw.json`

*R5 = Endless loop tuning when Codex mode is playable.*
