"""Run actual browser test-bot games and report survival/economy telemetry.

Usage: python qa/telemetry.py [--runs 15] [--cap-sec 900]
The bot is intentionally reported as automation, not as a 70%-skill human proxy.
"""
import argparse
import json
import statistics

from playwright.sync_api import sync_playwright


def one_run(browser, base_url, index, cap_sec):
    page = browser.new_page(viewport={"width": 540, "height": 960})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base_url + "?test=1", wait_until="load", timeout=20_000)
    elapsed = 0
    first_shop_credits = None
    try:
        while elapsed < cap_sec:
            page.wait_for_timeout(1000)
            elapsed += 1
            state = page.evaluate("window.__dbg()")
            if not state.get("testBot"):
                raise RuntimeError("test bot was disabled; rejecting contaminated run")
            if first_shop_credits is None and state.get("state") == "shop":
                first_shop_credits = state.get("credits")
            if state.get("state") in ("dead", "win"):
                return {"run": index, "sec": elapsed, "state": state["state"],
                        "level": state.get("level"), "credits": state.get("credits"),
                        "first_shop_credits": first_shop_credits, "kills": state.get("kills"),
                        "errors": errors}
        return {"run": index, "sec": cap_sec, "state": "TIMEOUT", "level": state.get("level"),
                "credits": state.get("credits"), "first_shop_credits": first_shop_credits,
                "kills": state.get("kills"), "errors": errors}
    finally:
        page.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=15)
    parser.add_argument("--cap-sec", type=int, default=900)
    parser.add_argument("--url", default="http://127.0.0.1:8791/index.html")
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        rows = [one_run(browser, args.url, i + 1, args.cap_sec) for i in range(args.runs)]
        browser.close()
    seconds = sorted(row["sec"] for row in rows)
    print(json.dumps(rows, indent=2))
    print("n={} min={:.1f} p50={:.1f} max={:.1f}".format(
        len(seconds), seconds[0], statistics.median(seconds), seconds[-1]))
    print("Bot measurement only: compare its band to the 198–413 s human target; do not equate them.")


if __name__ == "__main__":
    main()
