# Engineering status

Executable status: **recovered core plus v0.19-v0.26 test-supported behavior**.

On 2026-09-26, the user supplied `BloodTap_VSCode_Current_Executable.zip`, restoring the engine, both data files, and a passing core suite. The archive explicitly says the later merged simulator was not persisted. v0.19-v0.26 preserved test cases now pass; v0.27-v0.28 are still pending. See [recovery notes](RECOVERY.md).

Historically reported milestones include:

- v0.19: Ritual free grants, Ascetic break behavior, prestige-root dependency.
- v0.20: Blood Moon stochastic stage transitions.
- v0.21-v0.22: Exchange capacity and exact market/broker/office/loan mechanics.
- v0.23-v0.25: Garden freeze/soil/neighbors, full mutation matrix, contamination and sacrifice.
- v0.26: Quiet Hunt and Veil.
- v0.27: all eleven Caryll Oath mechanical hooks, including Creation, Labor, Industry, Mother, Scorn and Order.
- v0.28: Calendar core lifecycle and exact Calendar-Oath timing/drop hooks.

Verified locally: recovered core script, v0.19-v0.21 milestone scripts, simulator boundary tests, alpha unit/integration tests, and a real-browser desktop/mobile flow. The core script's obsolete prestige-unlock assertion was updated to require U363. Both recovered JSON data files are unchanged.

Audit of the recovered baseline found that v0.27-v0.28 still lack later APIs and state. The v0.24 script passes against the two mutation rows it asserts, but the other matrix rules are still missing. Two later milestone scripts remain pending, not passing or silently skipped.

v0.20 validation: the existing milestone script and five boundary tests pass, including persisted geometric waits, research timing, pledge expiry, suppression, and reset. The parasite model remains approximate.

v0.21 validation: highest ownership is tracked on purchases and Ritual grants, preserved on losses, and reset on Reawakening. The existing script and four additional tests pass. Office stages 0, 3, and 5 are specified by the surviving tests; stages 1, 2, and 4 explicitly raise `NotImplementedError` because their bonuses were not recovered. This is a supported subset, not full Exchange parity.

v0.22 validation: the preserved milestone script and four transaction boundary tests pass. Same-tick trading, normalized profit, broker caps, the first office sacrifice, and the recovered first-loan phase schedule are implemented. Later office sacrifices, loans 2-3, and the claimed exact market equations remain unsupported because their frozen rules were not recovered. Passing the preserved script does not establish full Exchange parity.

v0.23 validation: Garden freeze, soil ownership/lockout, closed-time behavior, and the preserved neighbor examples pass, with four additional boundary tests. The recovered catalog supplies soil and plant strengths. Neighbor behavior outside the preserved examples is isolated in `garden_tile_modifiers`; it remains subject to correction if the frozen rules are recovered.

v0.24 validation: the preserved script and four loop boundary tests pass. The implementation restores paired starter-plant mutation, eight-Queenbeet Lump mutation, spontaneous Meddleweed, weed protection, snapshot-based loops, and two extra Wood Chips loops. The historical script title says “matrix,” but asserts only two mutation rows; the unrecovered full 34-species matrix is explicitly incomplete.

v0.25 validation: cardinal contamination from the three documented source species, the preserved immune Queenbeet case, Pebbles natural-death unlocks, Meddleweed conversion, and full-seed sacrifice/reset are restored. The preserved script and four boundary tests pass. The broader contamination-immunity set and source probabilities remain subject to the missing specification.

v0.26 validation: Quiet Hunt toggle cost/production and natural-Omen suppression are restored. Veil scaling, reinforcement defenses, click/Omen break hooks, counters, and reactivation cost are restored. The preserved script and five integration/boundary tests pass. The recovered tests constrain the four-reinforcement endpoint; intermediate defense probabilities remain subject to the missing specification.

Run `python -B -m simulator.verify` for the restored subset. `--all` also runs pending historical tests and currently exits with failure. CI tests the explicitly scoped restored subset.

Playable preview status: the local client implements the core clicker loop, shops, achievements/Insight, collectible Omens, Reawakening, permanent offline memories, validated saves, import/export, reset safeguards, responsive layout, and reduced motion. Fifteen alpha tests and the Chrome desktop/mobile flow pass.

Balance status: three one-hour profiles and three adaptive profiles through the first useful Reawakening bundle were run with four taps/second, five-second purchase decisions, and 100% Omen collection. The two-fragment bundle took 73,230-75,335 seconds (20h 20m 30s to 20h 55m 35s). See [the balance report](balance/README.md). This is too long for a reasonable first session; the intended target and balance lever were not recovered.

## Immediate queue

Two decisions block alpha readiness:

1. Set a target window and approved balance lever for the first useful two-fragment bundle. The current measured window is roughly 20.5 hours of highly active play.
2. Recover or redefine the missing v0.27-v0.28 rules, the other Garden mutation rows, and remaining Exchange rules before exposing advanced systems. The full frozen specification, including most of the mutation matrix and exact Exchange tick rules, is still missing.

1. Finish Garden passive-effect families and harvest/death reward integration.
2. Tighten natural Omen candidate/wrath parity and special outcomes.
3. Complete Calendar visitor/drop collections and carryover.
4. Complete Great One/aura plumbing and remaining parasite hooks.
5. Run conservation/accounting and fixed-seed stochastic verification.
6. Rerun seeded first-session and repeated-Reawakening profiles after an explicit balance decision.
