# BloodTap launch roadmap

## Phase 1 — Simulator correctness

Status: the recovered core and every preserved v0.19-v0.28 assertion pass. The full frozen rules were not recovered, so unasserted advanced behavior remains isolated and excluded from the playable preview.

- Finish v0.18 affordability scheduling.
- Fix Ritual free-purchase price scaling.
- Fix Ascetic Oath break semantics.
- Verify prestige-effectiveness dependencies.
- Replace approximate Blood Moon stage transitions with the specified stochastic transition.
- Bring Omen candidate selection closer to the pinned rule specification.
- Correct Exchange capacity/highest-owned tracking and tick rules.
- Complete Blood Garden mutation, contamination, neighbor, and soil behavior.
- Complete calendar/season effects.
- Add conservation/accounting and deterministic seeded tests.

**Exit condition:** systems used for balance studies have explicit rules and targeted tests; known approximations are isolated and labeled.

## Phase 2 — Progression validation

Status: fresh-run and first-useful-bundle profiles are reproducible. The approved capped starter-prestige curve puts the 20-seed automated sample at 69m15s–89m50s, with an 82m15s median. Human pacing remains to be measured.

Run only simulations that answer launch-relevant questions.

- 30- and 60-minute active-day profiles.
- 0 / 8 / 24-hour open-game schedules, with closed offline treated separately.
- Greedy, adaptive, and reserve-aware purchasing.
- Seeded distributions rather than single-seed conclusions.
- Measure first useful Reawakening bundle, not merely prestige level 1.
- Check early, midgame, repeated-Reawakening, synergy, and enhancement pacing.

**Exit condition:** progression has documented percentile ranges and any deliberate balance changes have a changelog.

## Phase 3 — Playable game core

Status: implemented in the local browser preview with versioned saves, backup/import/export safeguards, responsive desktop/mobile behavior, and automated browser coverage.

- Stable save schema and migrations.
- Large-number representation.
- Main click interaction.
- Producer shop.
- Upgrade shop.
- Achievements and Insight.
- Omens.
- Reawakening/ascension interface.
- Offline progress.
- Settings, import/export, reset safeguards.
- Responsive desktop/mobile layout.

## Phase 4 — Advanced systems

Status: simulator-only, limited to recovered and test-supported rules; intentionally unavailable in the playable preview.

- Blood Gardens.
- Hunter Rituals.
- Caryll Oaths.
- Chalice Exchange.
- Blood Moon / Nightmare Parasites.
- Calendar events.
- Unbound Rites and late-game progression.

## Phase 5 — Content and presentation

- Final original names and descriptions.
- Original UI/art direction.
- Audio and accessibility.
- Tutorial/onboarding.
- Number formatting and endgame readability.
- Performance work for long-running saves.

## Phase 6 — Alpha / beta

Status: automated save/economy tests, returning/offline cases, the 60–90 minute automated pacing target, and mobile browser flows pass. The local playable core is an alpha candidate; a real fresh-player session remains before public alpha release.

- Automated save and economy regression tests.
- Fresh-save playtest.
- Returning/offline player test.
- Long-save migration test.
- Mobile usability test.
- Balance telemetry that does not require personal data.
- Bug triage and release-blocker list.

## Phase 7 — Launch candidate

- Freeze economy/schema except release blockers.
- Versioned release notes.
- Backup/import/export validation.
- Production deployment.
- Post-launch bugfix branch and balance-change policy.
