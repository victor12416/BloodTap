# BloodTap

BloodTap is an original gothic-horror incremental/clicker game project inspired by the progression depth of classic web incrementals. It uses original project names, presentation, code, and assets.

## Current status

**Pre-alpha / simulator phase — executable baseline restored, v0.19-v0.21 tested behavior restored**

The simulator, economy data, Garden catalog, and core tests have been restored from the user-provided executable archive. The core suite and v0.19-v0.21 milestone tests now pass. Historical v0.22-v0.28 tests remain pending integration; the archive did not contain their merged implementation. See [engineering status](docs/STATUS.md) and [recovery notes](docs/RECOVERY.md).

Run the verified subset from the repository root with Python 3.12 (no external dependencies):

```powershell
python -B -m simulator.verify
```

Use `import simulator` in study scripts. Do not enable Python's `-O` flag: the historical test scripts use assertions. Running all historical tests currently fails on the pending milestones.

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

First resolve missing office bonuses and reapply v0.22-v0.28 against explicit rules and tests. Then continue Garden passive effects and harvest/death rewards, natural Omen candidate/wrath parity, Calendar collections and carryover, Great One/aura and parasite integration, and accounting/seeded verification. See `docs/STATUS.md` for the ordered queue.

## Development rules

1. GitHub `main` is the permanent source of truth for verified milestones.
2. Reference economy changes must be explicit and documented.
3. Broad progression simulations are run only when they answer a meaningful balance question or prevent future architecture problems.
4. Small deterministic/unit tests are preferred during implementation.
5. A first prestige level is not treated as the project's target "meaningful Reawakening"; useful ascension bundles are measured separately.
6. No Cookie Clicker artwork, names, descriptions, or playable implementation are copied into BloodTap.

## Launch path

See `docs/ROADMAP.md` for the staged path from the current simulator to a playable alpha and launch candidate.
