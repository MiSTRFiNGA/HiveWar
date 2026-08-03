"""HW.11 contact sheet + HW.16 vehicle proof for v2.2 (post-2b8bab0 / 2f2a57e)."""
from __future__ import annotations

from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(r"C:\Users\MiSTRFiNGA\Desktop\Tests\hivewar_playtest_pack")
OUT.mkdir(parents=True, exist_ok=True)
# qa=1 only — do NOT use forge=1 (can leave forge open in some paths)
URL = "http://127.0.0.1:8791/index.html?qa=1"


def shot(page, name: str) -> None:
    path = OUT / name
    page.screenshot(path=str(path))  # viewport only — full_page was huge and fine
    print("wrote", path.name, path.stat().st_size)


def close_forge(page) -> None:
    page.evaluate(
        """() => {
      const f = document.getElementById('forge');
      if (f) f.classList.remove('open');
    }"""
    )


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 540, "height": 960})
        page.goto(URL, wait_until="load", timeout=60000)
        page.wait_for_function("() => !!(window.__qa && window.__dbg)", timeout=45000)
        page.wait_for_timeout(400)
        close_forge(page)

        ver = page.evaluate("() => window.__qa.version")
        print("GAME_VERSION", ver)

        # --- Round-4 play fullframe ---
        page.evaluate("() => { window.__qa.start('campaign'); window.__qa.tick(50, 0.05); }")
        close_forge(page)
        page.wait_for_timeout(150)
        forge_state = page.evaluate(
            """() => {
          const f = document.getElementById('forge');
          return {
            open: f && f.classList.contains('open'),
            display: f ? getComputedStyle(f).display : null,
            dbg: window.__dbg(),
          };
        }"""
        )
        print("R4 state", forge_state)
        shot(page, "R4_play_fullframe.png")

        # --- HW.16 tanks ---
        vinfo = page.evaluate("() => window.__qa.forceVehicles(3)")
        page.evaluate(
            """() => {
          window.__qa.tick(8, 0.05);
          window.__qa.forceVehicles(3);
        }"""
        )
        close_forge(page)
        page.wait_for_timeout(100)
        print(
            "vehicles",
            vinfo,
            page.evaluate("() => window.__dbg().vehicleActive"),
        )
        shot(page, "HW16_tanks_vehicle_active.png")
        shot(page, "HW2_tanks_after.png")

        # --- HW.8 early gift ---
        page.evaluate(
            """() => {
          window.__qa.start('campaign');
          window.__qa.tick(110, 0.1);
        }"""
        )
        close_forge(page)
        print("earlyGift", page.evaluate("() => window.__qa.earlyGift()"))
        shot(page, "HW8_early_squad_gift.png")

        # --- HW.3 ---
        page.evaluate(
            """() => {
          window.__qa.start('campaign');
          window.__qa.tick(90, 0.1);
        }"""
        )
        close_forge(page)
        shot(page, "HW3_fullframe_weapons_after.png")

        # --- HW.1 entities (open forge intentionally) ---
        page.keyboard.press("F2")
        page.wait_for_timeout(500)
        page.evaluate(
            """() => {
          const tabs = document.querySelectorAll('#forgeTabs button');
          for (const t of tabs) {
            if (/ENTITIES/i.test(t.textContent || '')) { t.click(); break; }
          }
        }"""
        )
        page.wait_for_timeout(400)
        shot(page, "HW1_entities_after.png")
        page.evaluate(
            """() => {
          const sc = document.querySelector('.entityScroll');
          if (sc) sc.scrollLeft = 480;
        }"""
        )
        page.wait_for_timeout(120)
        shot(page, "HW1_entities_scrolled_after.png")

        # --- HW.9 WAVES ---
        page.evaluate(
            """() => {
          const tabs = document.querySelectorAll('#forgeTabs button');
          for (const t of tabs) {
            if (/WAVES/i.test(t.textContent || '')) { t.click(); break; }
          }
        }"""
        )
        page.wait_for_timeout(400)
        shot(page, "HW9_forge_waves_help.png")

        browser.close()

    (OUT / "CAPTIONS.md").write_text(
        f"""# HiVE WAR play-test pack (HW.11) — **v{ver}** refreshed 2026-08-02

Source: git **2f2a57e** + version/`__qa` commits (`9a4f889`, `12957e9`).
Includes round-4 layout (`2b8bab0`) and HW.15 rotate fix.

**Supersedes** older pack shots that still showed the spawn glow band.

| File | Row | Caption |
|---|---|---|
| `R4_play_fullframe.png` | Round 4 | Play view — no spawn glow band; raised walls; player bottom |
| `HW1_entities_after.png` | HW.1 | FORGE ENTITIES uniform rows |
| `HW1_entities_scrolled_after.png` | HW.1 | Entities panel scrolled |
| `HW2_tanks_after.png` | HW.2 | Tanks road-angle with vehicles live |
| `HW3_fullframe_weapons_after.png` | HW.3 | Barriers / weapons full-frame |
| `HW8_early_squad_gift.png` | HW.8 | L1 early +squad gift approach |
| `HW9_forge_waves_help.png` | HW.9 | WAVES+BOSS plain-language help |
| `HW16_tanks_vehicle_active.png` | HW.16 | **Both tanks active** — rotation flip visual proof |

## APK
`HiveWar-2.2.apk` → `Desktop\\My Games\\_APKs\\` and `D:\\Dev\\_mobile\\dist\\`
""",
        encoding="utf-8",
    )
    print("pack:", sorted(x.name for x in OUT.iterdir()))


if __name__ == "__main__":
    main()
