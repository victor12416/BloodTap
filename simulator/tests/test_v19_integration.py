"""Integration and boundary checks for the first reapplied milestone."""
import math
import random
import unittest
from unittest.mock import patch

import simulator as sim


class RitualSuccess:
    def random(self):
        return .99

    def choice(self, candidates):
        return 1 if 1 in candidates else candidates[0]


class FidelityIntegrationTests(unittest.TestCase):
    def test_natural_omen_breaks_ascetic_in_every_slot(self):
        for slot in range(3):
            with self.subTest(slot=slot):
                s=sim.State(elapsed=1234, oath_swaps=2)
                s.producer_levels[6]=1
                s.oath_slots[slot]=0
                with patch.object(sim, 'choose_omen', return_value='windfall'):
                    sim.resolve_omen(s, random.Random(1))
                self.assertEqual(s.oath_slots, [-1]*3)
                self.assertEqual(s.oath_swaps, 0)
                self.assertEqual(s.oath_last_recharge, 1234)
                self.assertEqual(s.omen_clicks, 1)
                s.elapsed=1234+57600-1
                sim.update_oath_swaps(s)
                self.assertEqual(s.oath_swaps, 0)
                s.elapsed+=1
                sim.update_oath_swaps(s)
                self.assertEqual(s.oath_swaps, 1)

    def test_break_preserves_other_oaths_and_is_idempotent(self):
        s=sim.State(oath_slots=[1,0,2], oath_swaps=2, elapsed=100)
        self.assertTrue(sim.break_ascetic_on_natural_omen(s))
        self.assertEqual(s.oath_slots, [1,-1,2])
        s.elapsed=200
        self.assertFalse(sim.break_ascetic_on_natural_omen(s))
        self.assertEqual(s.oath_last_recharge, 100)

    def test_forced_outcomes_preserve_ascetic_and_swaps(self):
        for outcome in ('frenzy','clot','windfall','ruin'):
            with self.subTest(outcome=outcome):
                s=sim.State(bank=1e6, oath_slots=[0,-1,-1], oath_swaps=2,
                            elapsed=100, oath_last_recharge=10)
                sim.resolve_forced_omen(s, random.Random(1), outcome)
                self.assertEqual(s.oath_slots, [0,-1,-1])
                self.assertEqual((s.oath_swaps,s.oath_last_recharge), (2,10))

    def test_ritual_grant_increases_price_without_spending_bank(self):
        s=sim.State(bank=1e30)
        s.producer_levels[7]=1
        s.owned[7]=1000
        s.owned[1]=3
        s.free[1]=1  # Existing permanent free ownership remains untouched.
        s.ritual_initialized=True
        s.ritual_energy=sim.ritual_max_energy(s)
        before=s.bank
        self.assertTrue(sim.cast_ritual(s,3,RitualSuccess()))
        self.assertEqual((s.owned[1],s.free[1]),(4,1))
        self.assertEqual(s.bank,before)
        expected=math.ceil(sim.DATA['producers'][1]['base_cost']*sim.GROWTH**3)
        self.assertEqual(sim.next_cost(s,1),expected)

    def test_locked_prestige_purchase_does_not_spend(self):
        s=sim.State(bank=1e12,claimed_prestige=10)
        self.assertFalse(sim.buy_prestige_purchase(s))
        self.assertEqual((s.bank,s.prestige_purchases,s.prestige_effectiveness),
                         (1e12,0,0))

    def test_root_unlocks_only_current_valid_tier(self):
        s=sim.State(ascension_upgrades={'U363'})
        self.assertTrue(sim.prestige_purchase_unlocked(s,0))
        for tier in (-1,1,len(sim.DATA['prestige_effectiveness_purchases'])):
            self.assertFalse(sim.prestige_purchase_unlocked(s,tier))

    def test_optional_prestige_scale_does_not_change_recovered_default(self):
        s=sim.State(run_earned=240_000_000)
        self.assertEqual(sim.target_prestige(s),0)
        self.assertEqual(sim.target_prestige(s,30_000_000),2)
        with self.assertRaises(ValueError):sim.target_prestige(s,True)


if __name__=='__main__':
    unittest.main()
