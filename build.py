"""Build HiVE SWARM portal artifacts without modifying Claude's source index."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SOURCE_HTML = ROOT / "index.html"
ADAPTER = ROOT / "psdk_adapter.js"
SCRIPT_TAG = '<script src="psdk_adapter.js"></script>\n'


def inject_adapter(html: str) -> str:
    """Load PSDK before the game's first script; source index stays untouched."""
    if SCRIPT_TAG.strip() in html:
        return html
    marker = "<script>"
    if marker not in html:
        raise ValueError("index.html has no script insertion point")
    return html.replace(marker, SCRIPT_TAG + marker, 1)


def inline_assets(html: str) -> str:
    """Replace assets/*.png references with base64 data URIs (single-file portal builds)."""
    import base64
    import re

    def repl(match: re.Match) -> str:
        path = ROOT / "assets" / match.group(1)
        if not path.is_file():
            return match.group(0)
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{b64}"

    html = re.sub(r"assets/([A-Za-z0-9_\-]+\.png)", repl, html)

    def repl_snd(match: re.Match) -> str:
        path = ROOT / "sounds" / match.group(1)
        if not path.is_file():
            return match.group(0)
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:audio/mpeg;base64,{b64}"

    return re.sub(r"sounds/([A-Za-z0-9_\-]+\.mp3)", repl_snd, html)


def adapter_for(platform: str) -> str:
    source = ADAPTER.read_text(encoding="utf-8")
    token = "__HIVESWARM_PLATFORM__"
    if source.count(token) != 1:
        raise ValueError("psdk_adapter.js must contain exactly one platform token")
    return source.replace(token, platform)


def write_platform(platform: str, html: str) -> Path:
    target = DIST / platform
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(html, encoding="utf-8")
    (target / "psdk_adapter.js").write_text(adapter_for(platform), encoding="utf-8")
    return target


def build() -> list[Path]:
    if not SOURCE_HTML.is_file() or not ADAPTER.is_file():
        raise FileNotFoundError("index.html and psdk_adapter.js are required")
    shutil.rmtree(DIST, ignore_errors=True)
    html = inline_assets(inject_adapter(SOURCE_HTML.read_text(encoding="utf-8")))
    crazygames = write_platform("crazygames", html)
    poki = write_platform("poki", html)
    archive = poki / "hiveswarm-poki.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(poki / "index.html", "index.html")
        bundle.write(poki / "psdk_adapter.js", "psdk_adapter.js")
    outputs = [crazygames / "index.html", crazygames / "psdk_adapter.js", archive]
    for output in outputs:
        try:
            label = output.relative_to(ROOT)
        except ValueError:
            label = output
        print(f"{label} ({output.stat().st_size} bytes)")
    return outputs


if __name__ == "__main__":
    build()
