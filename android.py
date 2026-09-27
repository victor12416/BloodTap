"""BloodTap Android/Pydroid launcher.

Open this file in Pydroid 3 and press Run. Keep Pydroid open, then open
http://127.0.0.1:8765 in the phone's browser.

This wrapper deliberately reuses alpha.server so Android testing runs the
same authoritative local server and save system as the desktop alpha.
"""

from __future__ import annotations

import sys
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    # Pydroid may populate argv with editor/launcher arguments. alpha.server
    # owns its CLI, so give it a clean argv when launched from this wrapper.
    sys.argv = [str(Path(__file__).name)]

    from alpha.server import main as run_server

    url = "http://127.0.0.1:8765"
    print("BloodTap Android alpha")
    print("Keep Pydroid running while you play.")
    print(f"Open this address in Chrome: {url}")
    print("Your save is stored in this BloodTap folder under alpha-data.")
    print()

    # Opening the browser is best-effort; some Android/Pydroid versions do not
    # hand this request to Chrome, so the printed URL is always the fallback.
    try:
        webbrowser.open(url)
    except Exception:
        pass

    run_server()


if __name__ == "__main__":
    main()
