"""HiVE SWARM R4 full-run sign-off under R3-merged model."""
import math
import json
from pathlib import Path

WEAPONS = [
    {"n": 1, "dmg": 1.00, "rof": 8},
    {"n": 2, "dmg": 0.62, "rof": 10},
    {"n": 4, "dmg": 0.38, "rof": 12},
    {"n": 3, "dmg": 0.82, "rof": 11},
    {"n": 5, "dmg": 0.89, "rof": 9},
]
spawn = [8, 11, 14, 18, 22, 27, 32, 34, 39, 44]
wave_sec = [70, 74, 78, 82, 86, 90, 94, 98, 102, 55]
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
mult_cap = [2.0, 2.2, 2.4, 2.6, 2.8, 2.8, 2.9, 3.0, 3.1, 3.2]
boss_hp = [2200, 3400, 5000, 7200, 10000, 13500, 16000, 21000, 28000, 0]
queen_hp = 86000


def interval(L):
    return max(3.0, 4.2 - 0.12 * (L - 1))


def hp(L):
    return 8 + 2.0 * L, 38 + 9.5 * L, 20 + 4.5 * L


def cols(squad):
    # R3 pick, clamped ≤ squad (early game)
    c = max(1, math.floor(14 * (max(squad, 1) / 14) ** 0.45))
    c = min(48, c)
    return min(c, max(1, squad))


def dps(squad, tier, meta_dmg=0, oc=0):
    w = WEAPONS[min(4, max(0, tier))]
    c = cols(squad)
    rof = w["rof"] * (1 + 0.15 * oc)
    bullet = w["dmg"] * (1 + 0.08 * meta_dmg) * (1 + 0.06 * math.log2(1 + max(0, squad)))
    return c * w["n"] * bullet * rof


def sim_gates(L, squad, weapon, pass_rate):
    li = L - 1
    gates = max(1, int(wave_sec[li] / interval(L)))
    take = max(1, int(gates * pass_rate))
    peak = squad
    for g in range(take):
        r = (g * 7 + L * 3) % 100
        if r < 55:
            lo, hi = plus_spawn[li]
            mid = (lo + hi) / 2
            val = mid + 0.45 * (plus_cap[li] - mid)
            squad = max(0, squad + int(val))
        elif r < 85:
            mids = mult_opts[li]
            m = (mids[0] + mids[1]) / 2 + 0.35 * (mult_cap[li] - (mids[0] + mids[1]) / 2)
            squad = max(0, int(round(squad * m)))
        else:
            weapon = min(4, weapon + 1)
        peak = max(peak, squad)
    return squad, weapon, peak, gates


def wave_ehp_s(L):
    bio, eld, cyb = hp(L)
    li = L - 1
    bp = 100 - mix_eld[li] - mix_cyb[li]
    return spawn[li] * (bp / 100 * bio + mix_eld[li] / 100 * eld + mix_cyb[li] / 100 * cyb)


def run_campaign(pass_rate, meta_dmg=0, start_sq_bonus=0, start_wpn=0, death_at_50=False):
    squad = 8 + start_sq_bonus
    weapon = start_wpn
    death_used = False
    rows = []
    died_before = None
    for L in range(1, 11):
        start = squad
        end_s, weapon, peak, gates = sim_gates(L, squad, weapon, pass_rate)
        mid = max(1, int(0.6 * start + 0.4 * end_s))
        Dmid = dps(mid, weapon, meta_dmg)
        Dend = dps(end_s, weapon, meta_dmg)
        ehp = wave_ehp_s(L)
        kill = min(1.0, Dmid / ehp) if ehp else 1.0
        # bio TTK stretch check early
        bio = hp(L)[0]
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
        # death model: if kill < 0.45 mid and not yet revived at 50% tier
        if death_at_50 and not death_used and kill < 0.45 and L <= 7:
            death_used = True
            died_before = L
            end_s = max(20, int(peak * 0.5))  # revive
            flags.append("REVIVED")
        if kill < 0.40 and L < 8 and not (death_at_50 and death_used):
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
        squad = end_s
    return rows, died_before


def shop_total(base, growth, n):
    return sum(math.floor(base * (growth ** i)) for i in range(n))


def main():
    print("cols check:", [(s, cols(s)) for s in [1, 8, 14, 50, 100, 200, 500, 2000]])
    print("T5 dps@14/100/400:", dps(14, 4), dps(100, 4), dps(400, 4))

    scenarios = {
        "50% gates +1 death": run_campaign(0.50, meta_dmg=0, death_at_50=True),
        "70% gates no meta": run_campaign(0.70, meta_dmg=0),
        "70% gates meta dmg2": run_campaign(0.70, meta_dmg=2),
        "90% gates no meta": run_campaign(0.90, meta_dmg=0),
    }
    out = {}
    for name, (rows, died) in scenarios.items():
        print(f"\n=== {name} died_before_L8={died} ===")
        for r in rows:
            fl = ",".join(r["flags"]) or "ok"
            print(
                f"L{r['L']:2d} kill={r['kill_pct']:5.1f}% bioTTK={r['bio_ttk']:6.3f} "
                f"boss={r['boss_ttk']:5.1f}/{r['boss_bud']:4.1f} W{r['weapon']} "
                f"sq {r['start']}->{r['end']} {fl}"
            )
        out[name] = {"died_before_L8": died, "rows": rows}

    # economy soft-cap with R3 shop
    bd = shop_total(45, 1.5, 15)
    print(f"\nbaseDamage 15x1.5 base45 total={bd} runs@12k={bd/12000:.1f}")
    # ads: double credits one level ~ +level clear value ~200-400; headstart
    print("ad double one level est +300-500 credits (~3-4% of softcap run)")
    print("headstart 40 units early is large vs start 8; late negligible for DPS if cols power")

    Path(__file__).with_name("r4_raw.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote r4_raw.json")


if __name__ == "__main__":
    main()
