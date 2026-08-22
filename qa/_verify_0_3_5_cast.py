"""v0.3.5 Swarm-cast import checks (no browser)."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SW = (ROOT / "sw.js").read_text(encoding="utf-8")
SWARM = ROOT / "assets" / "swarm"
SFX = ROOT / "assets" / "SFX"

STEMS = [
    "biomorph", "cyber_mutant", "psychoid", "shambler", "runner", "crawler",
    "brute", "armored_dead", "necro_node", "mutant_enforcer", "zombie_colossus",
    "slime", "node_spawn", "rotter",
]
WEAPON_SFX = ["pulse_fire.mp3", "flame_loop.mp3", "beam_fire.mp3", "nova_fire.mp3"]
ENEMY_SFX = ["shambler_attack.mp3", "shambler_die.mp3", "slime_attack.mp3", "colossus_die.mp3"]


class CastImportTests(unittest.TestCase):
    def test_version_pair(self):
        self.assertIn("const GAME_VERSION = '0.3.9'", HTML)
        self.assertIn("CACHE_VERSION = 'v30'", SW)

    def test_pickkind_uses_full_roster(self):
        self.assertIn("function kindCount()", HTML)
        fn = re.search(r"function pickKind\(lvl\) \{.*?\n\}", HTML, re.S).group(0)
        self.assertIn("kindCount()", fn)
        self.assertNotIn("k < 6", fn)

    def test_seventeen_kinds(self):
        kinds = re.findall(r"\{ name:'([^']+)'", HTML.split("kinds: [")[1].split("],")[0])
        self.assertGreaterEqual(len(kinds), 17)
        for name in ("Shambler", "Hive Slime", "Node Spawn", "Rotter", "Zombie Colossus"):
            self.assertIn(name, kinds)

    def test_minlvl_spreads(self):
        block = HTML.split("kinds: [")[1].split("],")[0]
        self.assertIn("minLvl:8", block)   # colossus
        self.assertIn("minLvl:7", block)   # enforcer / rotter
        self.assertIn("name:'Shambler'", block)

    def test_directional_sheets_on_disk(self):
        missing = []
        for stem in STEMS:
            for d in ("s", "se", "sw"):
                p = SWARM / f"{stem}_walk_{d}.png"
                if not p.is_file():
                    missing.append(p.name)
        self.assertEqual(missing, [])

    def test_sfx_on_disk(self):
        for name in WEAPON_SFX + ENEMY_SFX:
            self.assertTrue((SFX / name).is_file(), name)

    def test_anim_and_audio_wired(self):
        self.assertIn("load3('shambler'", HTML)
        self.assertIn("function animFace(", HTML)
        self.assertIn("sfx:'gun'", HTML)
        self.assertIn("name:'Heat Seeker'", HTML)
        self.assertIn("sfx:'pulse'", HTML)
        self.assertIn("sfxAttack:'shamblerAtk'", HTML)

    def test_fourteen_weapon_icons(self):
        from PIL import Image
        im = Image.open(ROOT / "assets" / "weapon_icons.png")
        self.assertEqual(im.size, (1792, 128))
        self.assertIn("WEAPON_LAST = 13", HTML)
        self.assertIn("wrapImg(IMGS.weaponIcons, 14)", HTML)


if __name__ == "__main__":
    unittest.main()
