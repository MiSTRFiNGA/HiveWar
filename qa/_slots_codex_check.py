"""Save slots + per-slot bestiary unlock smoke test.

Run a local server first:  python -m http.server 8791
Loads the plain URL (the FORGE and the real title screen are disabled for ?telemetry bots).
"""
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hivewar_slots"
URL = "http://127.0.0.1:8791/index.html"

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_page(viewport={"width": 540, "height": 960})
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.on("dialog", lambda d: d.accept())
    p.goto(URL, wait_until="load", timeout=20000)
    p.wait_for_timeout(1500)

    # a brand-new install starts with an empty bestiary
    print("fresh unlocked:", p.evaluate("__dbg().codexUnlocked"), "of", p.evaluate("__dbg().codexTotal"))
    print("slot:", p.evaluate("__dbg().slot"))
    p.screenshot(path=f"{OUT}/01_title.png")

    # bestiary screen while empty
    p.evaluate("G.state='codex'"); p.wait_for_timeout(400)
    p.screenshot(path=f"{OUT}/02_bestiary_empty.png")

    # meet things: two enemy kinds, a weapon, the guardian
    p.evaluate("""(()=>{ codexSee('enemy:0',0); codexSee('enemy:2',0);
                         codexSee('weapon:6',0); codexSee('boss:guardian',0); })()""")
    p.wait_for_timeout(300)
    print("after sightings:", p.evaluate("__dbg().codexUnlocked"))
    p.evaluate("G.codexPage=0"); p.wait_for_timeout(400)
    p.screenshot(path=f"{OUT}/03_bestiary_page.png")

    # slots screen
    p.evaluate("G.state='slots'"); p.wait_for_timeout(400)
    p.screenshot(path=f"{OUT}/04_slots.png")

    # switch to slot 2: must be a clean save with an empty bestiary
    p.evaluate("useSlot(2)"); p.wait_for_timeout(300)
    print("slot 2 unlocked:", p.evaluate("__dbg().codexUnlocked"), "slot:", p.evaluate("__dbg().slot"))

    # back to slot 1: sightings must still be there
    p.evaluate("useSlot(1)"); p.wait_for_timeout(300)
    print("slot 1 unlocked again:", p.evaluate("__dbg().codexUnlocked"))

    # erase slot 1
    p.evaluate("eraseSlot(1)"); p.wait_for_timeout(300)
    print("slot 1 after erase:", p.evaluate("__dbg().codexUnlocked"),
          "maxLevel:", p.evaluate("G.meta.maxLevel"))

    # survives reload
    p.reload(wait_until="load"); p.wait_for_timeout(1500)
    print("after reload:", p.evaluate("__dbg().codexUnlocked"), "slot:", p.evaluate("__dbg().slot"))
    print("errors:", errs)
    b.close()
