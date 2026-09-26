import random
import unittest
from unittest.mock import patch
import simulator as sim


class FixedRng:
    def __init__(self,value):self.value=value
    def random(self):return self.value


class QuietVeilBoundaries(unittest.TestCase):
    def test_quiet_toggle_costs_current_eps_each_direction(self):
        s=sim.State(bank=1e9,quiet_hunt_unlocked=True);s.owned[1]=10
        first=sim.current_eps(s)*3600
        self.assertTrue(sim.toggle_quiet_hunt(s));self.assertEqual(s.bank,1e9-first)
        second=sim.current_eps(s)*3600
        self.assertTrue(sim.toggle_quiet_hunt(s));self.assertEqual(s.bank,1e9-first-second)
        poor=sim.State(quiet_hunt_unlocked=True);poor.owned[1]=1
        self.assertFalse(sim.toggle_quiet_hunt(poor));self.assertFalse(poor.quiet_hunt_active)

    def test_quiet_suppresses_natural_but_not_forced_omens(self):
        s=sim.State(bank=1000,quiet_hunt_unlocked=True,quiet_hunt_active=True,omen_next=1,elapsed=2)
        sim.process_omens(s,random.Random(1));self.assertEqual(s.omen_clicks,0);self.assertGreater(s.omen_next,2)
        before=s.bank;sim.resolve_forced_omen(s,random.Random(1),'windfall')
        self.assertGreater(s.bank,before)

    def test_veil_defense_consumes_reinforcement_then_breaks(self):
        s=sim.State(veil_unlocked=True,veil_active=True,veil_reinforcements=4)
        self.assertFalse(sim.veil_break_check(s,FixedRng(.1)))
        self.assertEqual((s.veil_reinforcements,s.veil_defenses,s.veil_breaks),(3,1,0))
        self.assertTrue(sim.veil_break_check(s,FixedRng(.9)))
        self.assertEqual((s.veil_active,s.veil_breaks),(False,1))
        self.assertFalse(sim.veil_break_check(s,FixedRng(0)))

    def test_click_and_natural_omen_use_break_check(self):
        click_state=sim.State(veil_unlocked=True,veil_active=True);click_state.owned[1]=1
        sim.click(click_state,rng=FixedRng(.9));self.assertFalse(click_state.veil_active)
        omen=sim.State(veil_unlocked=True,veil_active=True)
        with patch.object(sim,'choose_omen',return_value='windfall'):
            sim.resolve_omen(omen,FixedRng(.9))
        self.assertFalse(omen.veil_active);self.assertEqual(omen.omen_clicks,1)

    def test_reactivation_uses_unveiled_raw_eps(self):
        s=sim.State(bank=1e9,veil_unlocked=True,veil_active=False,veil_reinforcements=4);s.owned[1]=10
        cost=sim.raw_eps(s)*86400
        self.assertTrue(sim.reactivate_veil(s));self.assertEqual(s.bank,1e9-cost)
        self.assertAlmostEqual(sim.raw_eps(s),10*1.75)
        self.assertFalse(sim.reactivate_veil(s))


if __name__=='__main__':unittest.main()
