#!/usr/bin/env python3
"""Static smoke checks for the GitHub Pages alpha.

These catch deployment-shape failures before Pages publishes them. Browser-level
interaction remains a separate manual/browser check, but a broken asset path,
missing core control, or accidental Python-server dependency must fail CI.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)

def main() -> None:
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    script = (DOCS / "play.js").read_text(encoding="utf-8")
    style = (DOCS / "play.css").read_text(encoding="utf-8")
    economy_path = DOCS / "economy_data.json"

    for name in ("index.html", "play.js", "play.css", "economy_data.json"):
        require((DOCS / name).is_file(), f"Pages asset missing: docs/{name}")

    for asset in re.findall(r'(?:src|href)="([^"]+)"', index):
        if asset.startswith(("data:", "http:", "https:", "#")):
            continue
        clean = asset.split("?", 1)[0]
        # "./" is the wordmark/home navigation target, not an asset file.
        if clean in (".", "./", ""):
            continue
        target = (DOCS / clean).resolve()
        require(target.is_file(), f"index.html references missing Pages asset: {asset}")

    for element_id in ("vessel", "bank", "eps", "producers", "upgrades",
                       "settings", "reawaken", "export-save", "import-file"):
        require(f'id="{element_id}"' in index, f"missing required UI element #{element_id}")

    require("fetch('./economy_data.json'" in script,
            "web alpha must load economy data from inside docs/")
    require("../simulator/" not in script and "/api/" not in script,
            "Pages client must not depend on files outside docs/ or the Python API")
    require("$('vessel').onclick" in script and "earn(v)" in script,
            "manual Gather Echoes handler is missing")
    require("localStorage.setItem" in script and "localStorage.getItem" in script,
            "browser save/load path is missing")
    require("requestAnimationFrame(tick)" in script,
            "main browser game loop is missing")
    require("#vessel" in style, "Gather Echoes control has no Pages styling")

    data = json.loads(economy_path.read_text(encoding="utf-8"))
    require(len(data.get("producers", [])) == 20, "Pages economy must contain 20 producers")
    require(data["producers"][0]["base_cost"] == 15, "unexpected first producer cost")
    require(data["producers"][0]["base_eps"] == 0.1, "unexpected first producer EPS")

    print("GitHub Pages smoke checks passed.")

if __name__ == "__main__":
    main()
