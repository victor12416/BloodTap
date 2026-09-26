# BloodTap engineering changelog

## v0.21
- Added per-producer current-run highest-owned tracking.
- Chalice Exchange storage now uses highest ownership, producer level, office flat bonuses, and the final office x1.5 multiplier.
- Reawakening resets run-local highest ownership and Exchange office state.
- Added targeted Exchange capacity tests.

## v0.20
- Blood Moon research milestones now raise the target wrath stage without instantly jumping the live stage.
- Added geometric waiting-time implementation for the 0.001-per-frame stage transition.
- Pledge expiry resumes at stage 1 when wrath research exists.
- Permanent suppression pins the live wrath stage to zero.
- Added targeted stage-transition tests.

## v0.19
- Ritual 4 free producer grants now advance normal producer price scaling.
- Natural Omens break the Ascetic Oath, unslot it, consume remaining swaps, and restart recharge.
- Forced/spell-created Omens do not trigger that Ascetic break.
- Prestige-effectiveness run purchases now require permanent root U363 rather than merely a nonzero prestige level.
- Added targeted fidelity tests.

No broad progression simulations were run for v0.19-v0.21.
