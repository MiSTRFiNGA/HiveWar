"""HiVE SWARM R4 full-run sign-off under R3-merged model."""
import math
import json
from pathlib import Path

"""Default-loadout analytic proxy for the live HiVE WAR balance tables.

Keep this file manually synchronised with index.html: it intentionally does not
parse JavaScript so it stays reproducible. It models default Forge values and
no purchases/perks/combat losses; its outputs are not live-harness measurements.
"""

WEAPONS = [
    {"dmg": 2.00, "rof": 4.5},
    {"dmg": 0.62, "rof": 10},
    {"dmg": 0.38, "rof": 12},
    {"dmg": 0.82, "rof": 11},
    {"dmg": 16.0, "rof": 1.6},
]
spawn = [1.0, 1.5, 2.5, 4.0, 6.0, 8.5, 12.0, 16.5, 22.0, 28.0]
wave_sec = [75, 78, 82, 86, 90, 94, 98, 102, 106, 60]
# Default EDIT.kinds mirror. The live wave picker uses weights/minLvl, not BAL.mixEld/mixCyb.
KINDS = [
    {"hp_base": 8, "hp_lvl": 2.0, "weight": 60, "min_level": 1},
    {"hp_base": 38, "hp_lvl": 9.5, "weight": 20, "min_level": 1},
    {"hp_base": 20, "hp_lvl": 4.5, "weight": 12, "min_level": 2},
    {"hp_base": 30, "hp_lvl": 7.0, "weight": 4.5, "min_level": 4},
    {"hp_base": 45, "hp_lvl": 10.0, "weight": 2.5, "min_level": 6},
    {"hp_base": 40, "hp_lvl": 14.0, "weight": 1, "min_level": 3},
]
plus_cap = [8, 14, 22, 32, 45, 60, 80, 105, 135, 170]
plus_spawn = [[2,6],[3,9],[4,12],[6,16],[8,22],[10,28],[13,34],[16,42],[20,52],[24,64]]
mult_opts = [
    [1.2, 1.5], [1.3, 1.6], [1.4, 1.7], [1.5, 1.8], [1.5, 2.0],
    [1.6, 2.0], [1.7, 2.2], [1.8, 2.3], [2.0, 2.5], [2.0, 2.6],
]
mult_cap = [2.0, 2.2, 2.4, 2.6, 2.8, 2.8, 2.9, 3.0, 3.1, 3.2]
minus_spawn = [[-4,-1],[-6,-2],[-10,-4],[-16,-7],[-24,-10],[-34,-14],[-46,-18],[-58,-24],[-70,-30],[-85,-40]]
boss_hp = [3600,5600,8800,12800,18000,25000,30000,40000,52000,0]
queen_hp = 86000  # p1 28000 + p2 36000 + p3 22000


def interval(L):
    return max(12.0, 18.0 - 0.4 * (L - 1))  # EDIT.gateInterval defaults


def cols(squad):
    """Live fire ladder: 1 through 10, 2 at 20, 3 at 30+, never more."""
    return 3 if squad >= 30 else 2 if squad >= 20 else 1


def dps(squad, tier, meta_dmg=0, oc=0):
    w = WEAPONS[min(4, max(0, tier))]
    c = cols(squad)
    rof = w["rof"] * (1 + 0.10 * oc)
    # The live code divides the full squad volley across the capped visible-bolt ladder.
    # Bolts add coverage, while every soldier continues to contribute damage.
    bullet = w["dmg"] * 1.1 * (1 + 0.08 * meta_dmg)
    return max(1, squad) * bullet * rof


class Rng:
    """Small deterministic PRNG: repeatable scenario samples without JS parsing."""
    def __init__(self, seed): self.state = seed & 0xffffffff
    def rand(self):
        self.state = (1664525 * self.state + 1013904223) & 0xffffffff
        return self.state / 2**32
    def uniform(self, lo, hi): return lo + (hi - lo) * self.rand()


def gate(rng, L, weapon, allow_locked):
    """Mirror spawnGatePair's campaign branch; campaign multipliers are points."""
    li, roll = L - 1, rng.rand()
    if roll < .42:  # .34 add plus the pre-unlock former multiplier slot
        kind, val = "add", round(rng.uniform(*plus_spawn[li]))
    elif roll < .52:
        kind, val = "wpn", 0
    else:
        kind, val = "add", round(rng.uniform(*minus_spawn[li]))
    locked = allow_locked and rng.rand() < .22
    if locked:
        kind = "add"
        val = -round(rng.uniform(minus_spawn[li][1] * -2.2, minus_spawn[li][1] * -1.4))
    weapon2 = None
    if kind == "wpn" and rng.rand() < .38:
        primary = min(4, weapon + 1)
        weapon2 = int(rng.rand() * 5)
        if weapon2 == primary: weapon2 = (weapon2 + 1) % 5
    return {"kind": kind, "val": val, "locked": locked, "weapon2": weapon2}


def score_gate(g, squad, weapon):
    """Value a crossing by immediate squad or next-weapon DPS; locked red is avoided."""
    if g["locked"] or (g["kind"] == "add" and g["val"] < 0):
        return -10000 + g["val"]
    if g["kind"] == "add": return g["val"]
    candidates = [min(4, weapon + 1)]
    if g["weapon2"] is not None: candidates.append(g["weapon2"])
    return max(dps(max(squad, 1), candidate) for candidate in candidates) - dps(max(squad, 1), weapon)


def apply_gate(g, squad, weapon):
    if g["kind"] == "add":
        squad = max(1 if g["val"] < 0 else 0, squad + min(170, g["val"]))
    else:
        candidates = [min(4, weapon + 1)]
        if g["weapon2"] is not None: candidates.append(g["weapon2"])
        weapon = max(candidates, key=lambda candidate: dps(max(squad, 1), candidate))
    return min(300, squad), weapon


def sim_gates(L, squad, weapon, skill, rng):
    """Sample actual single/pair gates; skill is the chance to take the best safe option.

    Gate shooting is intentionally not credited here: it depends on steering and wall
    exposure, so granting caps in a closed-form survival check would overstate it.
    """
    li = L - 1
    # Gates begin at time zero and need ~6 s to reach the squad; gates too near wave end
    # do not affect the boss. The live countdown carries between levels; this conservative
    # closed-form approximation counts only gates safely inside a wave.
    gates = max(1, int((wave_sec[li] - 6) / interval(L)))
    peak = squad
    for _ in range(gates):
        left = gate(rng, L, weapon, True)
        choices = [left] if rng.rand() < .40 else [left, gate(rng, L, weapon, not left["locked"])]
        best = max(choices, key=lambda g: score_gate(g, squad, weapon))
        if score_gate(best, squad, weapon) <= 0:
            continue  # a good player dodges a single bad wall / pair of bad walls
        picked = best if rng.rand() < skill else choices[int(rng.rand() * len(choices))]
        squad, weapon = apply_gate(picked, squad, weapon)
        peak = max(peak, squad)
    return squad, weapon, peak, gates


def wave_ehp_s(L):
    li = L - 1
    live_kinds = [k for k in KINDS if L >= k["min_level"]]
    total_weight = sum(k["weight"] for k in live_kinds)
    avg_hp = sum(k["weight"] * (k["hp_base"] + k["hp_lvl"] * L) for k in live_kinds) / total_weight
    # spawnWave uses min(1, .10 + levelT / 38). Integrate that exact ramp across the wave.
    t_full = 0.9 * 38
    ramp_area = ((0.10 + 1.0) / 2) * min(wave_sec[li], t_full) + max(0, wave_sec[li] - t_full)
    avg_ramp = ramp_area / wave_sec[li]
    return spawn[li] * avg_ramp * avg_hp


def run_campaign(pass_rate, meta_dmg=0, start_sq_bonus=0, start_wpn=0, seed=1):
    weapon = start_wpn
    rng = Rng(seed)
    rows = []
    died_before = None
    survival_seconds = 0.0
    for L in range(1, 11):
        # Live levelStart resets this every level; only weapon/meta persist across the campaign.
        squad = 1 + start_sq_bonus
        start = squad
        end_s, weapon, peak, gates = sim_gates(L, squad, weapon, pass_rate, rng)
        mid = max(1, int(0.6 * start + 0.4 * end_s))
        Dmid = dps(mid, weapon, meta_dmg)
        Dend = dps(end_s, weapon, meta_dmg)
        ehp = wave_ehp_s(L)
        kill = min(1.0, Dmid / ehp) if ehp else 1.0
        # bio TTK stretch check early
        bio = KINDS[0]["hp_base"] + KINDS[0]["hp_lvl"] * L
        ttk_bio = bio / max(Dmid, 1e-6)
        bhp = boss_hp[L - 1] if L < 10 else queen_hp
        bttk = bhp / max(Dend, 1e-6)
        bud = 35 if L == 10 else 18 + 1.5 * (L - 1)
        flags = []
        if kill < 0.55:
            flags.append("WAVE_LEAK")
        if bttk > bud * 1.5:
            flags.append("BOSS_SLOW")
        if L <= 3 and ttk_bio > 15:
            flags.append("BORING_TTK")
        if L <= 3 and ttk_bio < 0.05 and kill > 0.99:
            flags.append("TRIVIAL_EARLY")
        if kill < 0.40 and L < 8:
            if died_before is None:
                died_before = L
                flags.append("DEATH")
        rows.append(
            dict(
                L=L,
                start=start,
                end=end_s,
                peak=peak,
                weapon=weapon,
                dps_mid=round(Dmid, 1),
                dps_end=round(Dend, 1),
                kill_pct=round(kill * 100, 1),
                bio_ttk=round(ttk_bio, 3),
                boss_ttk=round(bttk, 1),
                boss_bud=round(bud, 1),
                flags=flags,
            )
        )
        if died_before == L:
            survival_seconds += wave_sec[L - 1]
            break
        survival_seconds += wave_sec[L - 1] + min(bttk, bud * 1.5)
    return rows, died_before, survival_seconds


def shop_total(base, growth, n):
    return sum(math.floor(base * (growth ** i)) for i in range(n))


def percentile(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, round((len(values) - 1) * p))]


def sample_campaigns(skill, meta_dmg=0, samples=400):
    runs = [run_campaign(skill, meta_dmg=meta_dmg, seed=1000 + n * 7919) for n in range(samples)]
    seconds = [run[2] for run in runs]
    deaths = sum(run[1] is not None for run in runs)
    median = percentile(seconds, .50)
    representative = min(runs, key=lambda run: abs(run[2] - median))
    return representative, {
        "samples": samples,
        "survival_p10_s": round(percentile(seconds, .10), 1),
        "survival_p50_s": round(median, 1),
        "survival_p90_s": round(percentile(seconds, .90), 1),
        "proxy_wave_deaths_before_L8": deaths,
    }


def main():
    print("cols check:", [(s, cols(s)) for s in [1, 8, 14, 50, 100, 200, 500, 2000]])
    print("T5 dps@14/100/400:", dps(14, 4), dps(100, 4), dps(400, 4))
    print("DEFAULT-LOADOUT PROXY ONLY: default EDIT values, no shop tiers/perks/combat losses; not a live-harness measurement")
    print("campaign mechanics: seeded gate samples; squad resets each level; campaign multipliers disabled")

    scenarios = {
        "50% safe-gate decisions": sample_campaigns(0.50),
        "70% safe-gate decisions": sample_campaigns(0.70),
        "70% safe-gate decisions + meta dmg2": sample_campaigns(0.70, meta_dmg=2),
        "90% safe-gate decisions": sample_campaigns(0.90),
    }
    out = {}
    for name, ((rows, died, _), summary) in scenarios.items():
        print(f"\n=== {name} sample died_before_L8={died} ===")
        print("survival band p10/p50/p90: "
              f"{summary['survival_p10_s']}/{summary['survival_p50_s']}/{summary['survival_p90_s']} s; "
              f"proxy L1-L7 wave deaths {summary['proxy_wave_deaths_before_L8']}/{summary['samples']}")
        for r in rows:
            fl = ",".join(r["flags"]) or "ok"
            print(
                f"L{r['L']:2d} kill={r['kill_pct']:5.1f}% bioTTK={r['bio_ttk']:6.3f} "
                f"boss={r['boss_ttk']:5.1f}/{r['boss_bud']:4.1f} W{r['weapon']} "
                f"sq {r['start']}->{r['end']} {fl}"
            )
        out[name] = {"representative_died_before_L8": died, "summary": summary, "rows": rows}

    # economy soft-cap with R3 shop
    bd = shop_total(45, 1.5, 15)
    print(f"\nbaseDamage 15x1.5 base45 total={bd} runs@12k={bd/12000:.1f}")
    # ads: double credits one level ~ +level clear value ~200-400; headstart
    print("ad double one level est +300-500 credits (~3-4% of softcap run)")
    print("headstart 28 units early is large vs one-soldier start; later DPS still scales with squad")

    Path(__file__).with_name("r4_raw.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote r4_raw.json")


if __name__ == "__main__":
    main()
