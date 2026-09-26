# BloodTap

BloodTap is an original gothic-horror incremental/clicker game project inspired by the progression depth of classic web incrementals. It uses original project names, presentation, code, and assets.

## Current status

**Pre-alpha / simulator phase — v0.18**

The economy and progression reference is pinned and versioned. The current engineering focus is making the mathematical simulator correct and fast enough to validate progression without relying on unnecessary full-run simulations.

### Verified in v0.18

- 20-producer base economy and 1.15 price growth
- Standard producer upgrade tiers
- Messenger/click progression
- Achievement → Insight fixed-point resolution
- Prestige/Reawakening core
- Offline-production framework
- Event-driven timing
- Conservative cheap affordability frontier for scheduling
- Targeted v0.17 and v0.18 correctness tests

### Still under active fidelity work

Omens, Hunter Ritual edge cases, Caryll Oath break behavior, Blood Moon stage transitions, Chalice Exchange fidelity, Blood Garden mutation/neighbor systems, calendar effects, and later ascension systems.

## Development rules

1. GitHub `main` is the permanent source of truth for verified milestones.
2. Reference economy changes must be explicit and documented.
3. Broad progression simulations are run only when they answer a meaningful balance question or prevent future architecture problems.
4. Small deterministic/unit tests are preferred during implementation.
5. A first prestige level is not treated as the project's target "meaningful Reawakening"; useful ascension bundles are measured separately.
6. No Cookie Clicker artwork, names, descriptions, or playable implementation are copied into BloodTap.

## Launch path

See `docs/ROADMAP.md` for the staged path from the current simulator to a playable alpha and launch candidate.
