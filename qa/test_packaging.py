import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import build


class PackagingTests(unittest.TestCase):
    def test_adapter_is_injected_before_core_script(self):
        html = "<html><script>'use strict';</script></html>"
        result = build.inject_adapter(html)
        self.assertLess(result.index("psdk_adapter.js"), result.index("'use strict'"))

    def test_platform_token_is_replaced(self):
        self.assertIn('const platform = "crazygames"', build.adapter_for("crazygames"))
        self.assertIn('const platform = "poki"', build.adapter_for("poki"))

    def test_build_outputs_extracted_cg_and_poki_zip(self):
        with tempfile.TemporaryDirectory() as td:
            dist = Path(td) / "dist"
            with patch.object(build, "DIST", dist):
                outputs = build.build()
            self.assertTrue((dist / "crazygames" / "index.html").is_file())
            self.assertTrue((dist / "crazygames" / "psdk_adapter.js").is_file())
            archive = dist / "poki" / "hiveswarm-poki.zip"
            self.assertIn(archive, outputs)
            with zipfile.ZipFile(archive) as bundle:
                self.assertEqual(set(bundle.namelist()), {"index.html", "psdk_adapter.js"})


if __name__ == "__main__":
    unittest.main()
