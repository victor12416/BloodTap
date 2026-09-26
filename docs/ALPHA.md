# Playable core preview

Start from the repository root:

```powershell
python -B -m alpha.server
```

Open <http://127.0.0.1:8765>. Python 3.12 is sufficient; playing needs no packages, build tools, external assets, or account. Stop the server with Ctrl+C. This is a local preview, not a public deployment.

## Implemented

- Twenty producer types using the recovered economy, with original client display names.
- Manual taps, passive production, purchases in batches of 1/10/100, producer and global upgrades.
- Achievements and Insight, visible collectible Omens and timed buffs.
- Reawakening and implemented permanent offline memories. The first useful bundle costs two fragments: First memory and Sleeping vigil.
- Versioned JSON saves, import/export, typed reset/Reawakening confirmations, atomic writes and previous-save backup.
- Responsive desktop/mobile layout, keyboard controls, reduced motion, and local settings.

## Save behavior

Only one server may use a save folder at a time; a second is rejected before loading or writing progress.

`alpha-data/save.json` is saved every ten seconds while connected and after purchases. `alpha-data/save.bak` holds the previous saved version. Export before importing or resetting. To recover manually, stop the server, preserve both files, and copy a valid backup over `save.json`.

Malformed saves and unknown schema versions are rejected, not silently reset. Schema 1 is the first supported format; older standalone simulator snapshots do not have a defined migration. Future versions must add explicit migrations before changing this format.

The local server is authoritative. A connected tab earns full production. A gap over ten seconds without a state/action request is treated as closed time; offline earnings require Sleeping vigil. Restarting the server also applies unlocked offline earnings. Closed time does not collect Omens. This applies to suspended mobile/background tabs as well.

## Current limits

- Preview scope is the playable core. Garden, Ritual, Oath, Exchange, Blood Moon, Calendar, and later ascension interfaces are not exposed. Their incomplete simulator behavior does not run behind the preview.
- v0.22-v0.28 fidelity restoration is pending. Missing original rules prevent an exact-parity claim. v0.21 office bonuses are implemented only for recovered stages 0, 3, and 5.
- Ownership is limited to 1,000 per producer. Finite floating-point economy values and scientific notation support large late-game numbers, with ordinary floating-point rounding; arbitrary-precision economy support is not claimed.
- No public deployment, telemetry, audio, or multiplayer. The server binds only to 127.0.0.1 and rejects cross-origin mutations.
- Fresh-run pacing is measured in [the core balance report](balance/README.md). The first useful two-fragment bundle takes about 20.3–20.9 hours of uninterrupted four-tap/s automated play across three seeds. That is too long for a reasonable first-session alpha target. A target window and explicit balance change are required before declaring alpha ready.

## Verification

```powershell
python -B -m simulator.verify
python -B -m unittest discover -s alpha -p "test_*.py"
python -B -m alpha.balance
```

The first command explicitly tests the restored core and v0.19-v0.21 subset. Add `--all` to audit historical pending milestone scripts (currently fails).

Optional browser verification uses installed Google Chrome and Playwright:

```powershell
python -m pip install -r requirements-dev.txt
python -B -m alpha.browser_check
```

This exercises actual desktop/mobile flows, keyboard tapping, purchases/upgrades, reload, export/import, Omen collection, Reawakening, and reset cancellation/confirmation. It writes screenshots under ignored `test-artifacts/` and uses a temporary save, leaving player progress alone.
