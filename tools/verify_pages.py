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

    # Player-facing lore vocabulary must stay coherent. Internal save keys and
    # DOM ids intentionally retain legacy names for backwards compatibility.
    require("Whisperer" not in index and "Whisperer" not in script,
            "stale player-facing Whisperer terminology returned")
    require("The First Vigil" not in index and "Loading the vigil" not in index,
            "stale vigil terminology returned to the visible Pages UI")
    require("lifetime prestige" not in script and "new fragments" not in script,
            "raw prestige terminology leaked back into player-facing text")
    require("Sleeping vigil" not in index and "Sleeping vigil" not in script,
            "obsolete Sleeping vigil name returned")
    require("Blood Echoes" in index and "Return to the Dream" in index,
            "core Hunt/Dream vocabulary is missing from the visible UI")
    require("const REVEAL_AT=" in script and "visibleName(i)" in script and "visibleLore(i)" in script,
            "Insight-gated lore revelation is missing")
    require('id="marks-open"' in index and 'id="marks-list"' in index,
            "Marks of the Hunt record UI is missing")
    require('class="game-dock"' in index and 'id="upgrades-open"' in index
            and 'id="knowledge"' in index and 'id="upgrade-badge"' in index,
            "fixed game command dock or Hunter's Knowledge panel is missing")
    require('id="hunt-open"' in index and 'id="dream-open"' in index
            and 'id="dream"' in index and 'id="dream-badge"' in index,
            "dedicated Hunt/Dream navigation is missing")
    require("$('dream-open').onclick=()=>$('dream').showModal()" in script
            and "$('hunt-open').onclick" in script,
            "Hunt/Dream system screen wiring is missing")
    require("$('upgrades-open').onclick" in script and "$('upgrade-badge').textContent=ups.length" in script,
            "knowledge dock interaction or upgrade badge wiring is missing")
    require("function markRecord(id)" in script and "function renderMarks()" in script,
            "achievement-to-Mark presentation layer is missing")
    require('id="phase-name"' in index and 'id="phase-detail"' in index
            and "const HUNT_PHASES=" in script and "function huntPhase()" in script,
            "narrative Hunt chapter progression is missing")
    require("['Messengers','Huntsmen','Blood Ministers','Hunter Workshops','Church Hunters','Tomb Prospectors'" in script,
            "early Hunt/Church producer order drifted from the narrative progression")
    require("Perception of truths beyond the Hunt" not in index,
            "opening UI explains the cosmic layer too directly")

    data = json.loads(economy_path.read_text(encoding="utf-8"))
    require(len(data.get("producers", [])) == 20, "Pages economy must contain 20 producers")
    require(data["producers"][0]["base_cost"] == 15, "unexpected first producer cost")
    require(data["producers"][0]["base_eps"] == 0.1, "unexpected first producer EPS")

    print("GitHub Pages smoke checks passed.")

if __name__ == "__main__":
    main()
