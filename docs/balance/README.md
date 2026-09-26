# Core pacing measurements

These are reproducible simulator studies, not human-play telemetry. Run them with:

```powershell
python -B -m alpha.balance
python -B -m alpha.balance --seeds 1 7 42 --policies adaptive --seconds 7200 --until-bundle --output docs/balance/core-first-bundle.json
```

Assumptions: fresh save, four taps per second, purchase decisions every five seconds, every visible Omen collected, no resets during a profile, and no advanced systems. The ledger check requires `bank + spending == earned` within floating-point tolerance.

The playable alpha uses one explicit onboarding balance change: a 23,000,000-echo cubic prestige scale capped at the first two fragments. This places fragments one and two at 23,000,000 and 184,000,000 lifetime echoes. Fragment three and every later fragment remain on the recovered 1,000,000,000,000-echo cubic scale; the simulator's default curve is unchanged.

## Results

| Profile | Seed 1 | Seed 7 | Seed 42 |
| --- | ---: | ---: | ---: |
| Greedy earnings at 30 min | 711,533 | 1,268,665 | 42,457,177 |
| Greedy earnings at 60 min | 13,378,565 | 24,857,213 | 151,019,601 |
| Adaptive earnings at 30 min | 2,828,999 | 4,157,109 | 55,443,939 |
| Adaptive earnings at 60 min | 53,000,231 | 92,731,485 | 245,301,855 |
| Two-fragment bundle, adaptive | 1h 20m 50s | 1h 11m 40s | 56m 30s |

The first hour varies substantially because Omen outcomes compound. The expanded seeds 1–20 sample reaches the bundle in 69m15s–89m50s, with an 82m15s median. Seed 42 is a deliberately retained reference case and lands earlier at 56m30s after favorable compounding. This deterministic sample validates the configured 60–90 minute automated-play target; it is not human telemetry or a stable population percentile.

Before the alpha change, the first useful Reawakening bundle required about 20.3–20.9 hours on the three original seeds. The capped starter curve reduces that onboarding wait without accelerating fragment three or later progression. A human player who misses Omens or taps less often may take longer, so a fresh-player session remains necessary before a public alpha.

## Reproduce the distribution

```powershell
python -B -m alpha.balance --seeds 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 --policies adaptive --seconds 7200 --until-bundle --output docs/balance/core-first-bundle-20-seeds.json
```

Raw runs are stored in [core-first-hour.json](core-first-hour.json), [core-first-bundle.json](core-first-bundle.json), and [core-first-bundle-20-seeds.json](core-first-bundle-20-seeds.json).
