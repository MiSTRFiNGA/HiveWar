"""Browser-level regression coverage for the shipped HiVE FORGE.

Run with: python -m unittest qa.test_forge
Requires Playwright's Chromium (`playwright install chromium` once on a new machine).
"""
import contextlib
import http.server
import json
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
TABS = ['ENTITIES', 'PLAYER', 'WEAPONS', 'WAVES + BOSS', 'BALANCE', 'WORLD', 'SPRITES', 'AUDIO', 'DATA']


@contextlib.contextmanager
def serve_root():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT), **kwargs)
        def log_message(self, _format, *args):
            pass
    handler = Handler
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


class ForgeBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = serve_root()
        cls.base = cls.server.__enter__()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.__exit__(None, None, None)

    def setUp(self):
        self.errors = []
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        self.page = self.context.new_page()
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.context.close()

    def open_tab(self, tab):
        self.page.goto(f'{self.base}/index.html?forge=1&ftab={tab}', wait_until='domcontentloaded')
        self.page.wait_for_timeout(450)
        self.assertFalse(self.errors, self.errors)

    def test_every_tab_opens_and_has_controls(self):
        for tab, name in enumerate(TABS):
            with self.subTest(tab=name):
                self.open_tab(tab)
                self.assertEqual(self.page.locator(f'#forgeTab{tab}').inner_text(), name)
                self.assertGreater(self.page.locator('#forgeBody input, #forgeBody button, #forgeBody select').count(), 0)

    def test_telemetry_mode_advances_across_real_animation_frames(self):
        self.page.goto(f'{self.base}/index.html?telemetry=1', wait_until='domcontentloaded')
        self.page.wait_for_function("window.__dbg().state === 'play'")
        before = self.page.evaluate('window.__dbg().levelT')
        self.page.wait_for_timeout(900)
        after = self.page.evaluate('window.__dbg().levelT')
        self.assertTrue(self.page.evaluate('window.__dbg().telemetryBot'))
        self.assertGreater(after, before + .2, 'telemetry mode must use continuous rAF, not the fixed test fixture')
        self.assertFalse(self.errors, self.errors)

    def test_live_value_persists_and_pack_round_trips(self):
        self.open_tab(4)
        credit = self.page.locator('input[data-p="balance.startCredits"]')
        credit.fill('37')
        credit.dispatch_event('input')
        self.page.locator('#forge .x').click()
        self.page.locator('#game').click(position={'x': 300, 'y': 300})
        self.assertEqual(self.page.evaluate('window.__dbg().credits'), 37)
        self.open_tab(8)
        with self.page.expect_download() as download_info:
            self.page.locator('#pkSave').click()
        exported = json.loads(Path(download_info.value.path()).read_text(encoding='utf-8'))
        self.assertEqual(exported['values']['balance']['startCredits'], 37)
        exported['values']['balance']['startCredits'] = 81
        self.page.set_input_files('#pkLoad', {
            'name': 'forge-roundtrip.hivepack', 'mimeType': 'application/json',
            'buffer': json.dumps(exported).encode(),
        })
        self.page.wait_for_timeout(350)
        values = json.loads(self.page.evaluate("localStorage.getItem('hiveswarm_forge_v1')"))
        self.assertEqual(values['balance']['startCredits'], 81)
        self.page.reload(wait_until='domcontentloaded')
        self.page.wait_for_timeout(250)
        self.page.locator('#forge .x').click()
        self.page.locator('#game').click(position={'x': 300, 'y': 300})
        self.assertEqual(self.page.evaluate('window.__dbg().credits'), 81)
        self.assertFalse(self.errors, self.errors)

    def test_sprite_save_revert_and_indexeddb_reload(self):
        self.open_tab(6)
        self.page.locator('[data-sp]').first.click()
        self.page.wait_for_timeout(250)
        self.assertTrue(self.page.locator('#spSave').is_visible())
        self.page.locator('#spSave').click()
        self.page.wait_for_timeout(300)
        records = self.page.evaluate("""async () => new Promise((resolve, reject) => {
          const req=indexedDB.open('hiveswarm_forge_media_v2');
          req.onerror=()=>reject(req.error); req.onsuccess=()=>{const tx=req.result.transaction('media');
          const all=tx.objectStore('media').getAll(); all.onsuccess=()=>resolve(all.result.map(x=>x.id));}; })""")
        self.assertTrue(any(record.startswith('sprite:') for record in records))
        sprite_id = next(record for record in records if record.startswith('sprite:'))
        self.page.reload(wait_until='domcontentloaded')
        self.page.wait_for_timeout(500)
        reloaded = self.page.evaluate("""async () => new Promise((resolve, reject) => {
          const req=indexedDB.open('hiveswarm_forge_media_v2'); req.onerror=()=>reject(req.error);
          req.onsuccess=()=>{const get=req.result.transaction('media').objectStore('media').getAll();
          get.onsuccess=()=>resolve(get.result.map(x=>x.id));}; })""")
        self.assertIn(sprite_id, reloaded)
        self.assertFalse(self.errors, self.errors)
        self.page.on('dialog', lambda dialog: dialog.accept())
        self.page.locator('#forgeTab6').click()
        self.page.locator('[data-sp]').first.click()
        self.page.locator('#spRev').click()
        self.page.wait_for_function("""async id => new Promise((resolve, reject) => {
          const req=indexedDB.open('hiveswarm_forge_media_v2'); req.onerror=()=>reject(req.error);
          req.onsuccess=()=>{const get=req.result.transaction('media').objectStore('media').getAll();
          get.onsuccess=()=>resolve(!get.result.some(x=>x.id===id));}; })""", arg=sprite_id)

    def test_sprite_rotate_gif_import_and_tiling(self):
        self.open_tab(6)
        self.page.locator('[data-sp]').first.click()
        self.page.wait_for_timeout(250)
        def saved_signature():
            return self.page.evaluate("""async () => new Promise((resolve, reject) => {
              const req=indexedDB.open('hiveswarm_forge_media_v2'); req.onerror=()=>reject(req.error);
              req.onsuccess=()=>{const all=req.result.transaction('media').objectStore('media').getAll();
              all.onsuccess=async()=>{const row=all.result.find(x=>x.id.startsWith('sprite:'));
              const b=new Uint8Array(await row.blob.arrayBuffer()); let h=2166136261;
              for(const v of b) h=Math.imul(h^v,16777619); resolve([row.id,b.length,h>>>0]);};}; })""")
        self.page.locator('#spSave').click(); self.page.wait_for_timeout(150)
        original = saved_signature()
        self.page.locator('#spRot').fill('15')
        self.page.locator('#spRotGo').click()
        self.page.locator('#spSave').click(); self.page.wait_for_timeout(150)
        rotated = saved_signature()
        self.assertEqual(rotated[0], original[0])
        self.assertNotEqual(rotated[2], original[2])
        self.page.reload(wait_until='domcontentloaded'); self.page.wait_for_timeout(300)
        self.assertEqual(saved_signature(), rotated)
        self.page.locator('#forgeTab6').click(); self.page.locator('[data-sp]').first.click()
        self.page.locator('#spImp').click()
        # A tiny two-frame GIF: ImageDecoder must preserve both frames, not flatten it.
        gif = 'R0lGODlhAQABAPAAAP///wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAIfkEAAAAAAAsAAAAAAEAAQAAAgJEADs='
        import base64
        self.page.set_input_files('#spFile', {
            'name': 'two-frames.gif', 'mimeType': 'image/gif', 'buffer': base64.b64decode(gif),
        })
        self.page.wait_for_timeout(400)
        self.assertGreaterEqual(self.page.locator('#spFrames canvas').count(), 2)
        self.page.locator('#spSave').click()
        self.page.wait_for_timeout(150)
        def saved_dimensions():
            return self.page.evaluate("""async () => new Promise((resolve, reject) => {
              const req=indexedDB.open('hiveswarm_forge_media_v2'); req.onerror=()=>reject(req.error);
              req.onsuccess=()=>{const all=req.result.transaction('media').objectStore('media').getAll();
              all.onsuccess=async()=>{const row=all.result.find(x=>x.id.startsWith('sprite:'));
              const bitmap=await createImageBitmap(row.blob); resolve([bitmap.width,bitmap.height]);};}; })""")
        before = saved_dimensions()
        self.page.locator('#spTileX').fill('2')
        self.page.locator('#spTileY').fill('2')
        self.page.locator('#spTileGo').click()
        self.page.locator('#spSave').click()
        self.page.wait_for_timeout(150)
        after = saved_dimensions()
        self.assertEqual(after, [before[0] * 2, before[1] * 2])
        self.assertFalse(self.errors, self.errors)

    def test_entity_scale_changes_live_canvas_draw(self):
        def run_with_scale(scale):
            self.open_tab(0)
            field = self.page.locator('input[data-p="entities.0.scale"]')
            field.fill(str(scale)); field.dispatch_event('input')
            self.page.locator('#forge .x').click()
            self.page.locator('#game').click(position={'x': 300, 'y': 300})
            self.page.wait_for_function('window.__dbg().playerDrawSize > 0')
            return self.page.evaluate('window.__dbg().playerDrawSize')
        small = run_with_scale(.5)
        self.context.close()
        self.errors = []
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900})
        self.page = self.context.new_page()
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        large = run_with_scale(2)
        self.assertAlmostEqual(large / small, 4, places=3,
                               msg='player entity scale must reach the live drawImage destination size')
        self.assertFalse(self.errors, self.errors)

    def test_visual_level_editor_persists_authored_marks_and_scrubs(self):
        self.open_tab(5)
        self.assertTrue(self.page.locator('#lvTrack').is_visible())
        for kind in ('gates', 'hazards', 'spawns'):
            self.page.locator(f'[data-lv-add="{kind}"]').click()
        self.page.locator('#lvScrub').fill('12.5')
        self.assertIn('12.5s', self.page.locator('#lvPreviewText').inner_text())
        track = self.page.locator('#lvTrack').bounding_box()
        gate = self.page.locator('[data-lv-kind="gates"]').last.bounding_box()
        self.page.mouse.move(gate['x'] + 8, gate['y'] + 8)
        self.page.mouse.down()
        self.page.mouse.move(track['x'] + track['width'] * .25, gate['y'] + 8, steps=5)
        self.page.mouse.up()
        self.page.wait_for_timeout(120)
        # The boss and end marker are independently draggable and use the same persisted layout.
        boss = self.page.locator('[data-lv-kind="boss"]').bounding_box()
        self.page.mouse.move(boss['x'] + 8, boss['y'] + 8)
        self.page.mouse.down(); self.page.mouse.move(track['x'] + 3, boss['y'] + 8, steps=4); self.page.mouse.up()
        end = self.page.locator('[data-lv-kind="end"]').bounding_box()
        self.page.mouse.move(end['x'] + 3, end['y'] + 30)
        self.page.mouse.down(); self.page.mouse.move(track['x'] + track['width'] * .55, end['y'] + 30, steps=4); self.page.mouse.up()
        values = json.loads(self.page.evaluate("localStorage.getItem('hiveswarm_forge_v1')"))
        layout = values['levelLayout'][0]
        self.assertTrue(layout['gates'] and layout['hazards'] and layout['spawns'])
        self.assertTrue(all('t' in mark for key in ('gates', 'hazards', 'spawns') for mark in layout[key]))
        self.assertNotEqual(layout['duration'], 75)
        self.assertGreaterEqual(layout['gates'][-1]['t'], 0)
        # Put every authored event at t=0 and prove a real campaign run consumes the layout.
        layout['duration'] = 90; layout['bossAt'] = 0
        for key in ('gates', 'hazards', 'spawns'):
            for mark in layout[key]: mark['t'] = 0
        self.page.evaluate("v => localStorage.setItem('hiveswarm_forge_v1', JSON.stringify(v))", values)
        self.page.reload(wait_until='domcontentloaded'); self.page.wait_for_timeout(250)
        self.page.locator('#forge .x').click()
        self.page.locator('#game').click(position={'x': 300, 'y': 300})
        self.page.wait_for_function("window.__dbg().state === 'boss'")
        self.assertGreater(self.page.evaluate('window.__dbg().gates'), 0)
        self.assertFalse(self.errors, self.errors)


if __name__ == '__main__':
    unittest.main()
