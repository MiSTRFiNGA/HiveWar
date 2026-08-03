"""Visual capture for HW.20/21 — rail gun arc, rocket launcher, shatter particles, boss burn."""
from playwright.sync_api import sync_playwright
OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hivewar_hw20"
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_page(viewport={"width": 540, "height": 960})
    errs = []; p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("http://127.0.0.1:8791/index.html?telemetry=1&telemetrySpeed=1&telemetrySeed=4242",
           wait_until="load", timeout=20000)
    p.wait_for_timeout(4000)
    for idx, name in ((6, "railgun"), (7, "rocket"), (5, "flamethrower")):
        p.evaluate(f"(()=>{{G.weapon={idx};G.squad=40;}})()")
        p.wait_for_timeout(2500)
        p.screenshot(path=f"{OUT}/weapon_{name}.png")
        print(name, "bullets on screen:", p.evaluate("(()=>{let n=0;bullets.each(()=>n++);return n})()"))
    print("errors:", errs)
    b.close()
