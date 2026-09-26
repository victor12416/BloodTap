# Engineering status

Executable status: **recovered core plus v0.19-v0.20 corrections**.

On 2026-09-26, the user supplied `BloodTap_VSCode_Current_Executable.zip`, restoring the engine, both data files, and a passing core suite. The archive explicitly says the later merged simulator was not persisted. v0.19-v0.20 have now been reapplied and verified; v0.21-v0.28 are still pending. See [recovery notes](RECOVERY.md).

Historically reported milestones include:

- v0.19: Ritual free grants, Ascetic break behavior, prestige-root dependency.
- v0.20: Blood Moon stochastic stage transitions.
- v0.21-v0.22: Exchange capacity and exact market/broker/office/loan mechanics.
- v0.23-v0.25: Garden freeze/soil/neighbors, full mutation matrix, contamination and sacrifice.
- v0.26: Quiet Hunt and Veil.
- v0.27: all eleven Caryll Oath mechanical hooks, including Creation, Labor, Industry, Mother, Scorn and Order.
- v0.28: Calendar core lifecycle and exact Calendar-Oath timing/drop hooks.

Verified locally: recovered core script, unchanged v0.19 milestone script, and six v0.19 integration/boundary tests. The core script's obsolete prestige-unlock assertion was updated to require U363. Both recovered JSON data files are unchanged. No broad progression simulation was run.

Audit of the recovered baseline: v0.20 and v0.28 fail assertions; v0.21-v0.23 lack `highest_owned`; v0.24-v0.27 lack their later APIs/state. These nine milestone scripts remain pending, not passing or silently skipped.

v0.20 validation: the existing milestone script and five boundary tests pass, including persisted geometric waits, research timing, pledge expiry, suppression, and reset. The parasite model remains approximate.

## Immediate queue

Prerequisite: reapply v0.21-v0.28 in order, using the preserved tests and documented rules. The data files are recovered, but the full frozen specification (including the mutation matrix and exact Exchange tick rules) is still missing; unresolved formulas must be specified explicitly before claiming fidelity.

1. Finish Garden passive-effect families and harvest/death reward integration.
2. Tighten natural Omen candidate/wrath parity and special outcomes.
3. Complete Calendar visitor/drop collections and carryover.
4. Complete Great One/aura plumbing and remaining parasite hooks.
5. Run conservation/accounting and fixed-seed stochastic verification.
6. Freeze the balance-relevant simulator subset and pivot to the playable BloodTap client.
