# Core pacing measurements

These are reproducible simulator studies, not human-play telemetry. Run them with:

```powershell
python -B -m alpha.balance
python -B -m alpha.balance --seeds 1 7 42 --policies adaptive --seconds 86400 --until-bundle --output docs/balance/core-first-bundle.json
```

Assumptions: fresh save, four taps per second, purchase decisions every five seconds, every visible Omen collected, no resets during a profile, and no advanced systems. The ledger check requires `bank + spending == earned` within floating-point tolerance. The study uses the restored economy without balance changes.

## Results

| Profile | Seed 1 | Seed 7 | Seed 42 |
| --- | ---: | ---: | ---: |
| Greedy earnings at 30 min | 711,533 | 1,268,665 | 42,457,177 |
| Greedy earnings at 60 min | 13,378,565 | 24,857,213 | 151,019,601 |
| Adaptive earnings at 30 min | 2,828,999 | 4,157,109 | 55,443,939 |
| Adaptive earnings at 60 min | 53,000,231 | 92,731,485 | 245,301,855 |
| Two-fragment bundle, adaptive | 20h 20m 30s | 20h 55m 35s | 20h 29m 5s |

The first hour varies substantially because Omen outcomes compound. A three-seed sample is enough to expose that sensitivity, not enough to estimate stable percentiles.

The first useful Reawakening bundle currently requires about 20.3–20.9 hours of uninterrupted, highly active automated play. A human player who misses Omens or taps less often may take longer. This fails the current alpha pacing goal: a new player cannot reach offline progression in a reasonable first session.

## Decision required before alpha

Choose and document a target window for the first useful two-fragment bundle, then make an explicit versioned balance change and rerun seeded profiles. The recovered data cannot tell us the intended target. Reducing the prestige scale, changing the cube exponent, altering early production, or lowering the bundle cost have materially different effects on every later reset, so this should not be guessed during source recovery.

Raw runs are stored in [core-first-hour.json](core-first-hour.json) and [core-first-bundle.json](core-first-bundle.json).
