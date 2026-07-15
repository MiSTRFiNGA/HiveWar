"""HiVE SWARM R2 balance validation vs real sim DPS model (index.html)."""
import math
import json
from pathlib import Path

WEAPONS = [
    {"name": "Blaster", "rof": 8, "dmg": 1.00, "n": 1},
    {"name": "Twin Plasma", "rof": 10, "dmg": 0.62, "n": 2},
    {"name": "Scatter Rail", "rof": 12, "dmg": 0.38, "n": 4},
    {"name": "Heavy Plasma", "rof": 11, "dmg": 0.82, "n": 3},
    {"name": "Orbital Link", "rof": 9, "dmg": 0.89, "n": 5},
]
spawn_rate = [8, 11, 14, 18, 22, 27, 32, 38, 45, 52]
wave_sec = [70, 74, 78, 82, 86, 90, 94, 98, 102, 55]
boss_hp = [2200, 3400, 5000, 7200, 10000, 13500, 18000, 24000, 32000, 0]
mix_eld = [10, 12, 15, 18, 22, 25, 28, 30, 32, 33]
mix_cyb = [0, 3, 7, 12, 16, 20, 22, 25, 26, 27]
plus_cap = [28, 40, 55, 70, 90, 110, 135, 160, 190, 220]
plus_spawn = [
    [3, 12], [5, 16], [8, 22], [10, 28], [12, 35],
    [15, 42], [18, 50], [22, 58], [26, 68], [30, 80],
]
mult_opts = [
    [1.2, 1.5], [1.3, 1.6], [1.4, 1.7], [1.5, 1.8], [1.5, 2.0],
    [1.6, 2.0], [1.7, 2.2], [1.8, 2.3], [2.0, 2.5], [2.0, 2.6],
]
mult_cap = [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.5, 3.8, 4.0]


def interval(L):
    return max(3.0, 4.2 - 0.12 * (L - 1))


def hp_bio(L):
    return 8 + 2.2 * L


def hp_eld(L):
    return 45 + 12 * L


def hp_cyb(L):
    return 22 + 5 * L


def boss_budget(L):
    return 35.0 if L == 10 else 18 + 1.5 * (L - 1)


def dps(squad, tier, meta_dmg=0, overclock=0):
    w = WEAPONS[min(4, max(0, tier))]
    cols = min(max(0, squad), 14)
    rof = w["rof"] * (1 + 0.15 * overclock)
    bullet = (w["dmg"] + meta_dmg * 0.5) * (1 + 0.06 * math.log2(1 + max(0, squad)))
    return cols * w["n"] * bullet * rof


def sim_level_squad(L, start_squad, start_weapon):
    """Decent play: take ~70% of gates as positive (add/mult/wpn)."""
    li = L - 1
    T = wave_sec[li]
    gates = max(1, int(T / interval(L)))
    squad = start_squad
    weapon = start_weapon
    peak = squad
    for g in range(gates):
        if (g * 3 + L) % 10 >= 7:  # skip ~30%
            continue
        r = (g * 7 + L * 3) % 100
        if r < 55:
            lo, hi = plus_spawn[li]
            mid = (lo + hi) / 2
            val = mid + 0.45 * (plus_cap[li] - mid)
            squad = max(0, squad + int(val))
        elif r < 85:
            mids = mult_opts[li]
            m = (mids[0] + mids[1]) / 2
            m = m + 0.35 * (mult_cap[li] - m)
            squad = max(0, int(round(squad * m)))
        else:
            weapon = min(4, weapon + 1)
        peak = max(peak, squad)
    return squad, weapon, peak, gates


def analyze(meta_dmg=0, start_bonus_squad=0, start_weapon=0, label="no meta"):
    squad = 8 + start_bonus_squad
    weapon = start_weapon
    rows = []
    print(f"\n=== {label} ===")
    print(
        f"{'L':>2} {'start':>6} {'end':>7} {'W':>2} {'DPSmid':>7} {'DPSend':>7} "
        f"{'kill%':>6} {'bossTTK':>8} {'bud':>5} flags"
    )
    for L in range(1, 11):
        li = L - 1
        end_s, weapon, peak, gates = sim_level_squad(L, squad, weapon)
        mid_s = max(1, int(0.65 * squad + 0.35 * end_s))
        D_mid = dps(mid_s, weapon, meta_dmg=meta_dmg)
        D_end = dps(end_s, weapon, meta_dmg=meta_dmg)
        bio, eld, cyb = hp_bio(L), hp_eld(L), hp_cyb(L)
        bio_p = 100 - mix_eld[li] - mix_cyb[li]
        ehp_s = spawn_rate[li] * (
            bio_p / 100 * bio + mix_eld[li] / 100 * eld + mix_cyb[li] / 100 * cyb
        )
        kill_frac = min(1.0, D_mid / ehp_s) if ehp_s else 1.0
        bhp = boss_hp[li] if L < 10 else 86000
        boss_ttk = bhp / max(D_end, 1e-6)
        bud = boss_budget(L)
        flags = []
        if kill_frac < 0.55:
            flags.append("WAVE_LEAK")
        if boss_ttk > bud * 1.5:
            flags.append("BOSS_SLOW")
        if boss_ttk > bud * 2.5:
            flags.append("BOSS_BROKEN")
        if (eld / max(D_mid, 1e-6)) > 2.5 and L >= 3:
            flags.append("TANK_SPONGE")
        row = dict(
            L=L,
            start=squad,
            end=end_s,
            peak=peak,
            weapon=weapon,
            dps_mid=D_mid,
            dps_end=D_end,
            kill_frac=kill_frac,
            boss_ttk=boss_ttk,
            bud=bud,
            ehp_s=ehp_s,
            bio=bio,
            eld=eld,
            cyb=cyb,
            flags=flags,
            gates=gates,
        )
        rows.append(row)
        fl = ",".join(flags) if flags else "ok"
        print(
            f"{L:2d} {squad:6d} {end_s:7d} {weapon:2d} {D_mid:7.0f} {D_end:7.0f} "
            f"{kill_frac*100:5.0f}% {boss_ttk:8.1f} {bud:5.1f} {fl}"
        )
        squad = end_s
    return rows


def main():
    print("Tier DPS @ squad>=14, meta0 (expect ~112/174/258/381/560):")
    for i in range(5):
        print(f"  T{i+1}: {dps(14, i):.1f}  ratio={dps(14,i)/dps(14,0):.2f}")

    r0 = analyze(0, 0, 0, "fresh run no meta")
    r1 = analyze(5, 6, 1, "light meta dmg5 squad+6 wpn+1")

    L10 = r0[-1]
    print(
        f"\nQueen vs no-meta end DPS {L10['dps_end']:.0f}: "
        f"TTK={86000/max(L10['dps_end'],1):.1f}s needDPS_35s={86000/35:.0f}"
    )
    print(
        f"With OC3 (*1.4 rof): {L10['dps_end']*1.4:.0f} "
        f"TTK={86000/(L10['dps_end']*1.4):.1f}s"
    )
    print(
        f"OC3+Acid~*1.25: {L10['dps_end']*1.4*1.25:.0f} "
        f"TTK={86000/(L10['dps_end']*1.4*1.25):.1f}s"
    )

    out = {
        "fresh": r0,
        "light_meta": r1,
        "tier_dps_14": [dps(14, i) for i in range(5)],
    }
    # serialize without huge floats issues
    def clean(rows):
        return [
            {
                k: (round(v, 3) if isinstance(v, float) else v)
                for k, v in row.items()
            }
            for row in rows
        ]

    Path(__file__).with_name("r2_raw.json").write_text(
        json.dumps(
            {
                "tier_dps_14": out["tier_dps_14"],
                "fresh": clean(r0),
                "light_meta": clean(r1),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("\nWrote balance/r2_raw.json")


if __name__ == "__main__":
    main()
