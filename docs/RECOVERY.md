# Simulator recovery

## Recovered executable and v0.19 restoration

The user supplied `BloodTap_VSCode_Current_Executable.zip` on 2026-09-26. It contains the same `simulator.py` previously supplied separately, plus `economy_data.json`, `garden_data.json`, `test_core.py`, and a README explicitly stating that v0.19-v0.28 were not merged into this source.

Restored files and original SHA-256 hashes are recorded in [the archive manifest](archive/manifest.json); the original [archive README](archive/README.txt) is preserved as provenance. Its contents describe the archive, not additional user instructions. The bundled Python 3.13 bytecode was not imported or restored.

The source was installed as `simulator/__init__.py`, with the data beside it, so existing `import simulator` calls and module-based test commands work from the repository root. No dependencies outside Python's standard library are needed. The core script passed on Python 3.12 before changes.

Reapplied v0.19 changes:

- Ritual 4 grants advance the owned count without adding to the free-price offset.
- Prestige-effectiveness purchases require permanent root U363; the recovered core test was updated to match this documented correction.
- Natural Omen resolution removes Ascetic, consumes swaps, and restarts recharge; forced Omens preserve the Oath.
- Data files are read explicitly as UTF-8. Their contents and balance values are unchanged.

Validation: recovered core script, existing v0.19 script, and six integration/boundary tests pass. v0.20-v0.28 remain unmerged and fail their historical scripts. This restores a working foundation, not a fully verified v0.28 simulator.

## Baseline audit: 2026-09-26

Repository: `victor12416/BloodTap`, commit `2a9321eb3b929568ba1a42c80b2ed083f24a1bb9`.

- GitHub advertises only `main`, with no tags; local HEAD matches it.
- The tracked tree contains four documentation files and ten milestone test scripts.
- No simulator implementation or pinned economy/rules specification appears in the available Git history. `git fsck --full --no-reflogs --unreachable` reported no recoverable unreachable objects.
- Targeted filename searches in the workspace, common user project/download folders, and nearby project directories found no source copy. This was not an exhaustive scan of every file or backup.
- All ten v0.19-v0.28 scripts were executed individually as Python modules with assertions enabled. Each failed on its first `State(...)` call with `NameError: name 'State' is not defined`.

Historical reproduction command from the repository root:

```powershell
python -B -m simulator.tests.test_v28_calendar_core
```

Before restoration, `simulator` was importable only as an empty namespace package, without `State` or the functions used by the tests. A successful import alone did not establish a working baseline.

## Remaining recovery material

The complete frozen economy/rules specification and earlier v0.17/v0.18 tests remain unavailable. The recovered data tables are useful, but do not contain the complete mutation matrix or exact Exchange tick specification. Any further source or specification recovery should be compared with this baseline before replacing files.

The existing scripts preserve useful examples and expected values, but do not specify the complete economy, event scheduler, mutation matrix, or reward formulas. Reconstructing a replacement from those examples would be new implementation work with unresolved rules, not recovery of a verified v0.28 simulator.

Next, reapply the v0.20-v0.28 milestones and rerun their tests alongside the core suite. Garden passive-effect families and harvest/death reward integration remain queued after that restoration; no v0.29 milestone has been claimed.
