# Engineering status

Current milestone: **v0.18 affordability frontier**

The v0.18 implementation separates the event scheduler's cheap question — "when could a visible purchase become affordable?" — from the expensive marginal-production optimizer used for actual purchase decisions.

Targeted local verification completed:

- Existing event-driven timing test: PASS
- v0.17 targeted correctness tests: PASS
- v0.18 targeted affordability tests: PASS

No broad progression simulation was required for this milestone.

## Immediate queue

1. Commit the current simulator/data/test baseline to this repository.
2. Correct Ritual free-purchase price scaling.
3. Correct Ascetic Oath break semantics.
4. Verify prestige-effectiveness root/dependency behavior.
5. Continue subsystem fidelity repairs before the next progression study.
