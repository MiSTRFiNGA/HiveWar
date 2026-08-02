"""Run continuous browser telemetry-bot games and report survival/economy telemetry.

Usage: python qa/telemetry.py [--runs 15] [--cap-sec 900]
The bot is intentionally reported as automation, not as a 70%-skill human proxy.
It uses `?telemetry=1`, not the finite `?test=1` fixture.
"""
import argparse
import json
import statistics

from playwright.sync_api import sync_playwright


def one_run(browser, base_url, index, cap_sec, speed):
    page = browser.new_page(viewport={"width": 540, "height": 960})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    seed = 10_000 + index * 7_919
    page.goto(base_url + f"?telemetry=1&telemetrySpeed={speed}&telemetrySeed={seed}", wait_until="load", timeout=20_000)
    elapsed = 0.0
    first_shop_credits = None
    try:
        while elapsed < cap_sec:
            page.wait_for_timeout(200)
            state = page.evaluate("window.__dbg()")
            if not state.get("testBot"):
                raise RuntimeError("test bot was disabled; rejecting contaminated run")
            if not state.get("telemetryBot"):
                raise RuntimeError("finite test fixture loaded; rejecting invalid telemetry run")
            elapsed = float(state.get("simTime", 0))
            if first_shop_credits is None:
                first_shop_credits = state.get("firstShopCredits")
            if state.get("state") in ("dead", "win"):
                return {"run": index, "seed": seed, "sim_sec": round(elapsed, 1), "state": state["state"],
                        "level": state.get("level"), "credits": state.get("credits"),
                        "first_shop_credits": first_shop_credits, "death_cause": state.get("lastDeathCause"), "kills": state.get("kills"),
                        "errors": errors}
        return {"run": index, "seed": seed, "sim_sec": cap_sec, "state": "TIMEOUT", "level": state.get("level"),
                "credits": state.get("credits"), "first_shop_credits": first_shop_credits,
                "death_cause": state.get("lastDeathCause"), "kills": state.get("kills"), "errors": errors}
    finally:
        page.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=15)
    parser.add_argument("--start-run", type=int, default=1, help="first deterministic scenario index")
    parser.add_argument("--cap-sec", type=int, default=900)
    parser.add_argument("--speed", type=int, default=20, help="telemetry simulation multiplier (1-60)")
    parser.add_argument("--url", default="http://127.0.0.1:8791/index.html")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        rows = [one_run(browser, args.url, args.start_run + i, args.cap_sec, args.speed) for i in range(args.runs)]
        browser.close()
    seconds = sorted(row["sim_sec"] for row in rows)
    print(json.dumps(rows, indent=2))
    print("n={} min={:.1f} p50={:.1f} max={:.1f}".format(
        len(seconds), seconds[0], statistics.median(seconds), seconds[-1]))
    first_shops = sorted(row["first_shop_credits"] for row in rows if row["first_shop_credits"] is not None)
    if first_shops:
        print("first-shop n={} min={} p50={} max={}".format(
            len(first_shops), first_shops[0], statistics.median(first_shops), first_shops[-1]))
    else:
        print("first-shop n=0")
    print("Continuous telemetry bot only: compare its simulated band to the 198–413 s human target; do not equate them.")


if __name__ == "__main__":
    main()
