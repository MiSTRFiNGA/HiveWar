"""Bestiary tab smoke test — must load WITHOUT ?telemetry (FORGE is disabled for bots)."""
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_page(viewport={"width": 1200, "height": 900})
    errs = []; p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("http://127.0.0.1:8791/index.html", wait_until="load", timeout=20000)
    p.wait_for_timeout(1500)
    p.click("#forgeBtn"); p.wait_for_timeout(600)
    tabs = p.evaluate("Array.from(document.querySelectorAll('#forgeTabs button')).map(b=>b.textContent)")
    print("tabs:", tabs)
    p.evaluate("document.querySelectorAll('#forgeTabs button')[9].click()"); p.wait_for_timeout(700)
    print("pages:", p.evaluate("document.querySelectorAll('#forgeBody [data-pick]').length"))
    print("upload/delete/add present:", p.evaluate(
        "[!!document.querySelector('#cxPick'),!!document.querySelector('#cxDel'),!!document.querySelector('#cxAdd')]"))
    # add a page, rename it, confirm it persists into EDIT
    p.evaluate("document.querySelector('#cxAdd').click()"); p.wait_for_timeout(400)
    p.fill("#cxTitle", "Test Entry"); p.wait_for_timeout(200)
    print("after add:", p.evaluate("EDIT.codexPages.length"), p.evaluate("EDIT.codexPages.at(-1).title"))
    p.screenshot(path=r"C:\Users\MiSTRFiNGA\Desktop\Tests\hivewar_hw20\forge_bestiary.png")
    p.evaluate("document.querySelector('#cxDel')")  # delete uses confirm(); accept it
    p.on("dialog", lambda d: d.accept())
    p.evaluate("document.querySelector('#cxDel').click()"); p.wait_for_timeout(400)
    print("after delete:", p.evaluate("EDIT.codexPages.length"))
    print("errors:", errs)
    b.close()
