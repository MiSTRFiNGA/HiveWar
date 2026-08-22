"""Line up every War enemy + every HUD gun and screenshot the live canvas."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"D:\Dev\HiveWar\qa\evidence\live_gfx")
OUT.mkdir(parents=True, exist_ok=True)
BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

PLACE_KINDS = """() => {
  if (typeof startRun === 'function' && G.state === 'title') startRun('campaign');
  G.state = 'play';
  G.paused = true;
  G.squad = 8;
  G.level = 8;
  G.graceT = 999;
  spawnAcc = 0;
  EDIT.spawnRate = EDIT.spawnRate.map(() => 0);
  enemies.each(e => enemies.release(e));
  const n = kindCount();
  const names = [];
  for (let k = 0; k < n; k++) {
    const e = enemies.alloc();
    if (!e) break;
    const K = enemyRow(k);
    e.kind = k;
    e.lane = ((k % 6) - 2.5) / 3.2;
    e.y = 280 + Math.floor(k / 6) * 170;
    e.x = CFG.W / 2 + ((k % 6) - 2.5) * 78;
    e.vx = 0; e.vy = 0;
    e.maxhp = e.hp = 9999;
    e.r = (K && K.r ? K.r : 16);
    e.t = 0.35;
    e.acidT = e.poisonT = e.burnT = 0;
    names.push((K && K.name) || ('k'+k));
  }
  draw();
  return {n, names, version: GAME_VERSION, wpn: WEAPONS.map(w => w.name)};
}"""

SET_WEAPON = """(i) => { G.weapon = i; G.state = 'play'; draw(); return WEAPONS[i] && WEAPONS[i].name; }"""


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=BRAVE)
        page = browser.new_page(viewport={"width": 540, "height": 960})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://127.0.0.1:8791/index.html?qa=1", wait_until="load", timeout=30000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(OUT / "00_title.png"))
        info = page.evaluate(PLACE_KINDS)
        print("placed", info)
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "01_all_kinds.png"))
        # runner + colossus close-up: kinds 7 and 13
        page.evaluate(
            """() => {
              enemies.each(e => enemies.release(e));
              const specs = [
                {k:7, x:120, y:520, lane:-0.5},
                {k:7, x:270, y:520, lane:0},
                {k:7, x:420, y:520, lane:0.5},
                {k:13, x:120, y:720, lane:-0.5},
                {k:13, x:270, y:720, lane:0},
                {k:13, x:420, y:720, lane:0.5},
              ];
              for (const s of specs) {
                const e = enemies.alloc(); if (!e) continue;
                const K = enemyRow(s.k);
                e.kind = s.k; e.lane = s.lane; e.x = s.x; e.y = s.y;
                e.vx = 0; e.vy = 0; e.hp = e.maxhp = 9999;
                e.r = K.r; e.t = 0.2;
              }
              draw();
            }"""
        )
        page.wait_for_timeout(250)
        page.screenshot(path=str(OUT / "02_runner_colossus.png"))
        for i in range(14):
            name = page.evaluate(SET_WEAPON, i)
            page.wait_for_timeout(80)
            safe = "".join(c if c.isalnum() else "_" for c in (name or str(i)))
            page.screenshot(path=str(OUT / f"wpn_{i:02d}_{safe}.png"))
            print("weapon", i, name)
        print("errors", errs)
        browser.close()


if __name__ == "__main__":
    main()
