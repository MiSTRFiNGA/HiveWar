"""HW.11 — capture HW.8 / HW.9 full-frame shots into Desktop Tests pack."""
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(r"C:\Users\MiSTRFiNGA\Desktop\Tests\hivewar_playtest_pack")
out.mkdir(parents=True, exist_ok=True)
url = "http://127.0.0.1:8791/index.html"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 540, "height": 960})
    page.goto(url, wait_until="load", timeout=30000)
    page.keyboard.press("Enter")
    page.wait_for_timeout(500)
    # Drive ~11 s so early gift is on-screen but not yet collected
    page.evaluate(
        """() => {
      if (typeof startRun === 'function') startRun('campaign');
      for (let i = 0; i < 110; i++) {
        if (typeof update === 'function') update(0.1);
      }
      if (typeof draw === 'function') draw();
    }"""
    )
    page.wait_for_timeout(150)
    page.screenshot(path=str(out / "HW8_early_squad_gift.png"), full_page=True)

    page.keyboard.press("F2")
    page.wait_for_timeout(400)
    # FORGE tabs are often custom buttons with text WAVES + BOSS
    clicked = page.evaluate(
        """() => {
      const nodes = [...document.querySelectorAll('#forge * , #forgeHead * , button, .tab, [role=tab]')];
      const waves = nodes.find(t => /WAVES/i.test((t.textContent||'').trim()) && (t.tagName==='BUTTON' || t.onclick || t.getAttribute('data-tab')!=null || t.className));
      if (waves) { waves.click(); return (waves.textContent||'').trim().slice(0,40); }
      // fallback: walk forge tab bar by index (ENTITIES=0 ... WAVES=3)
      const bar = document.querySelectorAll('#forgeHead button, #forge .tabs button, #forge [class*=tab]');
      if (bar && bar[3]) { bar[3].click(); return 'idx3'; }
      return null;
    }"""
    )
    print("forge tab:", clicked)
    page.wait_for_timeout(250)
    page.screenshot(path=str(out / "HW9_forge_waves_help.png"), full_page=True)
    browser.close()

print("wrote", sorted(p.name for p in out.glob("*.png")))
