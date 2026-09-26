# Playable core alpha candidate

Start from the repository root:

```powershell
python -B -m alpha.server
```

Open <http://127.0.0.1:8765>. Python 3.12 is sufficient; playing needs no packages, build tools, external assets, or account. Stop the server with Ctrl+C. This is a local alpha candidate, not a public deployment.

Each successful GitHub Actions run publishes a 14-day source package named `BloodTap-alpha-<commit>`. To build the same deterministic package locally:

```powershell
python -B -m tools.package_alpha
```

Extract the ZIP, keep its folder structure intact, and run `Start-BloodTap.cmd`. `PACKAGE-MANIFEST.txt` records the SHA-256 of every packaged source file. Python is intentionally not bundled.

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
- Every preserved v0.19-v0.28 milestone assertion passes. Exchange, Garden, Oath, and Calendar fidelity remains limited to those assertions: v0.24 covers only two mutation rows, v0.27 asserts Oaths 6-11, and v0.28 covers only core Calendar lifecycle plus selected Communion hooks. Missing original rules prevent an exact-parity claim.
- Ownership is limited to 1,000 per producer. Finite floating-point economy values and scientific notation support large late-game numbers, with ordinary floating-point rounding; arbitrary-precision economy support is not claimed.
- No public deployment, telemetry, audio, or multiplayer. The server binds only to 127.0.0.1 and rejects cross-origin mutations.
- Fresh-run pacing is measured in [the core balance report](balance/README.md). The capped starter-prestige curve puts seeds 1–20 at 69m15s–89m50s with an 82m15s median under uninterrupted four-tap/s automated play and perfect Omen collection. A real fresh-player session is still required because human play will be slower and less consistent.

## Verification

```powershell
python -B -m simulator.verify
python -B -m unittest discover -s alpha -p "test_*.py"
python -B -m alpha.balance
```

The first command tests the restored core, every preserved v0.19-v0.28 assertion, and added boundary coverage. Its output calls out the limits of that evidence. `--all` also discovers any historical milestone script added outside the declared set.

Optional browser verification uses installed Google Chrome and Playwright:

```powershell
python -m pip install -r requirements-dev.txt
python -B -m alpha.browser_check
```

This exercises actual desktop/mobile flows, keyboard tapping, purchases/upgrades, reload, export/import, Omen collection, Reawakening, and reset cancellation/confirmation. It writes screenshots under ignored `test-artifacts/` and uses a temporary save, leaving player progress alone.
