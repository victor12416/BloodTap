# Engineering status

Executable status: **recovered core plus v0.19-v0.28 test-supported behavior**.

On 2026-09-26, the user supplied `BloodTap_VSCode_Current_Executable.zip`, restoring the engine, both data files, and a passing core suite. The archive explicitly says the later merged simulator was not persisted. Every preserved v0.19-v0.28 assertion now passes against the reconstructed, explicitly limited implementation. See [recovery notes](RECOVERY.md).

Historically reported milestones include:

- v0.19: Ritual free grants, Ascetic break behavior, prestige-root dependency.
- v0.20: Blood Moon stochastic stage transitions.
- v0.21-v0.22: Exchange capacity and exact market/broker/office/loan mechanics.
- v0.23-v0.25: Garden freeze/soil/neighbors, full mutation matrix, contamination and sacrifice.
- v0.26: Quiet Hunt and Veil.
- v0.27: all eleven Caryll Oath mechanical hooks, including Creation, Labor, Industry, Mother, Scorn and Order.
- v0.28: Calendar core lifecycle and exact Calendar-Oath timing/drop hooks.

Verified locally: recovered core script, v0.19-v0.21 milestone scripts, simulator boundary tests, alpha unit/integration tests, and a real-browser desktop/mobile flow. The core script's obsolete prestige-unlock assertion was updated to require U363. Both recovered JSON data files are unchanged.

The v0.24 script passes against the two mutation rows it asserts, but the other matrix rules are still missing. The v0.27 script asserts Oaths 6-11; unasserted mechanics for earlier Oaths remain subject to recovery. The v0.28 script covers Calendar switching, two Omen timing factors, one drop-failure factor, expiry, and eternal mode. Passing all milestone scripts is a precise test-supported claim, not full parity with the missing specification.

v0.20 validation: the existing milestone script and five boundary tests pass, including persisted geometric waits, research timing, pledge expiry, suppression, and reset. The parasite model remains approximate.

v0.21 validation: highest ownership is tracked on purchases and Ritual grants, preserved on losses, and reset on Reawakening. The existing script and four additional tests pass. Office stages 0, 3, and 5 are specified by the surviving tests; stages 1, 2, and 4 explicitly raise `NotImplementedError` because their bonuses were not recovered. This is a supported subset, not full Exchange parity.

v0.22 validation: the preserved milestone script and four transaction boundary tests pass. Same-tick trading, normalized profit, broker caps, the first office sacrifice, and the recovered first-loan phase schedule are implemented. Later office sacrifices, loans 2-3, and the claimed exact market equations remain unsupported because their frozen rules were not recovered. Passing the preserved script does not establish full Exchange parity.

v0.23 validation: Garden freeze, soil ownership/lockout, closed-time behavior, and the preserved neighbor examples pass, with four additional boundary tests. The recovered catalog supplies soil and plant strengths. Neighbor behavior outside the preserved examples is isolated in `garden_tile_modifiers`; it remains subject to correction if the frozen rules are recovered.

v0.24 validation: the preserved script and four loop boundary tests pass. The implementation restores paired starter-plant mutation, eight-Queenbeet Lump mutation, spontaneous Meddleweed, weed protection, snapshot-based loops, and two extra Wood Chips loops. The historical script title says “matrix,” but asserts only two mutation rows; the unrecovered full 34-species matrix is explicitly incomplete.

v0.25 validation: cardinal contamination from the three documented source species, the preserved immune Queenbeet case, Pebbles natural-death unlocks, Meddleweed conversion, and full-seed sacrifice/reset are restored. The preserved script and four boundary tests pass. The broader contamination-immunity set and source probabilities remain subject to the missing specification.

v0.26 validation: Quiet Hunt toggle cost/production and natural-Omen suppression are restored. Veil scaling, reinforcement defenses, click/Omen break hooks, counters, and reactivation cost are restored. The preserved script and five integration/boundary tests pass. The recovered tests constrain the four-reinforcement endpoint; intermediate defense probabilities remain subject to the missing specification.

v0.27 validation: the preserved Oaths 6-11 factors now affect producer prices, prestige effectiveness, clicks, production, Omen timing, Insight, forced wrath, parasites, and the Order Dreg-time hook. The preserved script and five integration tests pass. The Order helper is not applied to the Dreg cycle because the trigger semantics were not recovered; Oaths not asserted by this script remain outside the fidelity claim.

v0.28 validation: the Calendar can be unlocked by its ascension upgrade or the preserved direct test flag, charges the escalating switch cost, expires after one day unless eternal mode is enabled, and composes the preserved Night of the Hunt and Masquerade timing factors with Omen scheduling. Communion scales those recovered timing and drop-failure reductions by slot. The preserved script and five boundary tests pass. Visitor/drop collections, carryover, the other Calendar effects, and any rules not asserted by the surviving script remain unavailable.

Run `python -B -m simulator.verify` for the recovered and test-supported contract. `--all` also discovers any preserved milestone script outside the declared set. CI tests the same declared contract.

Playable alpha-candidate status: the local client implements the core clicker loop, stage-aware onboarding, shops, achievements/Insight, collectible Omens, Reawakening progress, permanent offline memories, validated saves, import/export, reset safeguards, responsive layout, and reduced motion. Nineteen alpha tests and the Chrome desktop/mobile flow pass.

Balance status: the playable alpha now uses a versioned 23,000,000-echo cubic prestige scale capped at its first two fragments. The 20-seed adaptive sample, with four taps/second and 100% Omen collection, reaches the useful bundle in 69m15s–89m50s with an 82m15s median. Later fragments retain the recovered scale. See [the balance report](balance/README.md). Human pacing remains unmeasured.

## Immediate queue

The local playable core is an alpha candidate. Run a real fresh-player session to validate comprehension, interaction, and human pacing before a public alpha release. Advanced systems remain gated until the unasserted Calendar and Oath hooks, other Garden mutation rows, and remaining Exchange rules are recovered or explicitly redefined; the full frozen specification is still missing.

1. Finish Garden passive-effect families and harvest/death reward integration.
2. Tighten natural Omen candidate/wrath parity and special outcomes.
3. Complete Calendar visitor/drop collections and carryover.
4. Complete Great One/aura plumbing and remaining parasite hooks.
5. Run conservation/accounting and fixed-seed stochastic verification.
6. Run a human fresh-session playtest, then profile repeated Reawakenings before expanding permanent progression.
