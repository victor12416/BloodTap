# BloodTap engineering changelog

## Save durability hardening
- Added an OS-owned save-folder lock to prevent concurrent servers from overwriting the same progress; locks release after process exit.
- Added corruption-preservation and offline-reward checkpoint tests. Invalid action payloads return errors without crashing the request.
- Fifteen alpha tests and the desktop/mobile browser flow pass.

## Local browser preview
- Added the responsive gothic core client and a loopback-only Python server with same-origin action checks.
- Exposed live production, shop, upgrades, Omens, permanent memories, import/export, typed confirmations, and reduced-motion settings.
- Desktop and 390px mobile flows passed in installed Chrome with no JavaScript exceptions. Twelve alpha unit/integration tests pass.
- Added the launch guide and Windows launcher. Preview remains short of alpha readiness pending balance and restoration decisions.

## Playable-core action model
- Added validated player actions using the existing simulator: taps, bulk producer purchases, upgrades, collectible Omens, Reawakening, and implemented permanent offline memories.
- Added original display names for the client; recovered balance tables remain unchanged.
- Passive income splits at buff expiry; disconnected intervals over ten seconds use offline rules.
- Five gameplay tests cover purchase/reload, buff accounting, one-time Omen collection, import/reset safeguards, and the two-fragment root-plus-offline bundle.

## Playable-core save foundation
- Added schema-v1 JSON save validation, atomic replacement, previous-save backup, and unlocked offline earnings. Unknown versions and malformed values are rejected without replacing a good save.
- Fixed impractical large-number prestige correction loops using bounded integer bisection over the stored decimal value.
- Added five persistence/numeric tests and CI coverage; restored simulator checks still pass.
- Alpha persistence supports the core economy only; advanced systems remain gated. Ownership is capped at 1,000 per producer in this initial save schema.

## v0.21 supported behavior reapplied
- Track highest producer ownership on purchases and Ritual grants; clear it and Exchange office state on Reawakening.
- Restore capacity for office stages covered by surviving tests; unknown office bonuses fail explicitly.
- Reject invalid producer/count/discount purchases without mutating state.
- Added four ownership tests, an explicit restored-subset test runner, and CI.

## v0.20 reapplied
- Restored .001-per-frame stochastic stage transitions with persisted geometric waits.
- Research raises only the target; pledge expiry resumes at stage 1; suppression and Reawakening clear pending transitions.
- Core, v0.19-v0.20 scripts, and eleven integration/boundary tests pass.

## 2026-09-26 executable recovery
- Restored the engine, economy data, Garden catalog, and core suite from the user-provided executable archive; recorded original file hashes and archive provenance.
- Verified the unchanged recovered core before modifications, then reapplied v0.19 Ritual price scaling, prestige-root dependency, and natural-Omen Ascetic break behavior.
- Updated the recovered core test's older prestige-unlock expectation and added six integration/boundary tests. Core and v0.19 checks pass.
- v0.20-v0.28 remain test-only milestones pending integration. The recovered archive is not a v0.28 implementation.
- No balance data changes or broad progression simulations.

## v0.26
- Added Quiet Hunt run-local toggle, x1.5 base production, current-EPS one-hour toggle cost, and natural-Omen suppression.
- Added Veil x1.50-x1.75 production scaling, four-step defense probability, click/Omen break checks, counters, and 24-hour-unbuffed-EPS reactivation.
- Quiet Hunt and Veil multiply to x2.25 in the base deep-idle configuration.
- Added targeted tests.

## v0.25
- Added Garden contamination from Meddleweed, Crumbspore, and Doughshroom with cardinal-neighbor targeting and contamination immunity.
- Added Pebbles natural-death seed-unlock behavior.
- Added Meddleweed death conversion behavior.
- Added full-seed Garden sacrifice/reset for the adapted +10 Blood Dregs reward.
- Added targeted tests.

## v0.24
- Encoded the full 34-species Garden mutation candidate matrix from the frozen rule specification.
- Added 8-neighbor mature/total counting, weed/fungus protection checks, spontaneous Meddleweed, Wood Chips mutation loops, and Supreme Intellect loop hook.
- Added targeted tests.

## v0.23
- Added Garden freeze semantics and 10-minute soil-change lockout.
- Added soil ownership requirements.
- Added neighbor age/power/weed modifiers for Elderwort, Queenbeet Lump, Nursetulip, Shriekbulb, Tidygrass, Everdaisy, and Ichorpuff.
- Closed/offline time no longer advances Garden growth.
- Added targeted tests.

## v0.22
- Replaced approximate Exchange price movement with the frozen one-minute tick equations.
- Added weighted modes, global shocks, noise, fast/chaotic instability, high-value damping, and exact mode-duration selection.
- Added same-tick buy/sell restrictions and normalized profit ledger.
- Added broker limits/purchases, office sacrifices, and all three loan phase transitions.
- Added targeted tests.

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
