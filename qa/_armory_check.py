from playwright.sync_api import sync_playwright
OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hivewar_armory"
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_page(viewport={"width": 540, "height": 960})
    errs = []; p.on("pageerror", lambda e: errs.append(str(e))); p.on("dialog", lambda d: d.accept())
    p.goto("http://127.0.0.1:8791/index.html", wait_until="load", timeout=20000); p.wait_for_timeout(1500)
    # fake a cleared level and open the debrief
    p.evaluate("""(()=>{ startRun('campaign'); G.lvlKills=[14,5,3,0,2,1]; G.lvlBio=23; G.lvlOrbs=17; G.lvlCredits=85;
      G.credits=1800; G.level=2; startDebrief(); })()""")
    p.wait_for_timeout(900); p.screenshot(path=f"{OUT}/01_debrief_counting.png")
    p.wait_for_timeout(4200); p.screenshot(path=f"{OUT}/02_debrief_fireworks.png")
    print("debrief done:", p.evaluate("G.debriefDone"), "fireworks:", p.evaluate("G.fireworks.length"))
    p.evaluate("G.state='shop'"); p.wait_for_timeout(500)
    p.screenshot(path=f"{OUT}/03_armory.png")
    print("start weapon:", p.evaluate("G.meta.startWeapon"), "owned:", p.evaluate("Object.keys(G.meta.weaponsOwned||{})"))
    print("buy railgun:", p.evaluate("buyStartWeapon(6)"), "-> startWeapon", p.evaluate("G.meta.startWeapon"),
          "credits", p.evaluate("G.credits"))
    p.wait_for_timeout(300); p.screenshot(path=f"{OUT}/04_armory_railgun.png")
    # FORGE: add enemy / add boss
    p.evaluate("G.state='title'"); p.click("#forgeBtn"); p.wait_for_timeout(600)
    before_k = p.evaluate("EDIT.kinds.length"); before_b = p.evaluate("EDIT.entities.filter(e=>e.class==='boss').length")
    p.evaluate("document.querySelector('#entAddEnemy').click()"); p.wait_for_timeout(500)
    p.evaluate("document.querySelector('#entAddBoss').click()"); p.wait_for_timeout(500)
    print("kinds", before_k, "->", p.evaluate("EDIT.kinds.length"),
          "| bosses", before_b, "->", p.evaluate("EDIT.entities.filter(e=>e.class==='boss').length"))
    print("boss roster selectors:", p.evaluate("document.querySelectorAll('[data-boss-level]').length"))
    print("beastiary pages:", p.evaluate("EDIT.codexPages.length"))
    p.screenshot(path=f"{OUT}/05_forge_entities.png")
    print("errors:", errs)
    b.close()
