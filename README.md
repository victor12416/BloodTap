# BloodTap

BloodTap is an original gothic-horror incremental/clicker game project inspired by the progression depth of classic web incrementals. It uses original project names, presentation, code, and assets.

## Play locally

Run `python -B -m alpha.server` from this folder, then open <http://127.0.0.1:8765>. On Windows, you can also double-click `Start-BloodTap.cmd`. See [the playable-core guide](docs/ALPHA.md) for saves, tests, and current limits.

## Current status

**Local playable-core alpha candidate — executable baseline restored and every preserved v0.19-v0.28 assertion passes**

The simulator, economy data, Garden catalog, and core tests were restored from the user-provided executable archive. The archive did not contain the merged v0.19-v0.28 implementation, so the surviving milestone assertions were reconstructed in small tested increments. The recovered core, every preserved v0.19-v0.28 assertion, 47 simulator boundary tests, 20 playable-core tests, and the desktop/mobile browser flow pass. Successful CI runs also publish a deterministic source ZIP. This proves the documented test-supported subset; rules absent from the recovered source and tests remain unavailable. See [engineering status](docs/STATUS.md), [playable-core guide](docs/ALPHA.md), and [recovery notes](docs/RECOVERY.md).

Run the verified subset from the repository root with Python 3.12 (no external dependencies):

```powershell
python -B -m simulator.verify
```

Use `import simulator` in study scripts. Do not enable Python's `-O` flag: the historical milestone scripts use assertions.

### Recovered core

- 20-producer base economy and 1.15 price growth
- Standard producer upgrade tiers
- Messenger/click progression
- Achievement and Insight progression
- Prestige/Reawakening core
- Offline-production framework
- Adaptive purchase policy and affordability scheduling helpers

The archive's core suite identifies its original baseline as v0.15. Earlier v0.17/v0.18 test suites and the full pinned fidelity specification were not recovered; those milestones are not newly certified.

### Remaining fidelity work

The original specification is still needed for unasserted Exchange office/tick behavior, most Garden mutation and passive-effect rules, earlier Oath hooks, Calendar collections and carryover, natural Omen candidate/wrath parity, and Great One/aura integration. These advanced systems stay outside the playable alpha candidate. The first useful two-fragment bundle now has a capped onboarding curve and reaches an 82m15s median across the 20-seed automated sample. A real fresh-player session is the remaining core-alpha validation step. See [engineering status](docs/STATUS.md) for the evidence and queue.

## Development rules

1. GitHub `main` is the permanent source of truth for verified milestones.
2. Reference economy changes must be explicit and documented.
3. Broad progression simulations are run only when they answer a meaningful balance question or prevent future architecture problems.
4. Small deterministic/unit tests are preferred during implementation.
5. A first prestige level is not treated as the project's target "meaningful Reawakening"; useful ascension bundles are measured separately.
6. No Cookie Clicker artwork, names, descriptions, or playable implementation are copied into BloodTap.

## Launch path

See `docs/ROADMAP.md` for the staged path from the current simulator to a playable alpha and launch candidate.
