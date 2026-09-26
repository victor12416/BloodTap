import unittest
import simulator as sim


class ZeroRng:
    def random(self):return 0.0
    def choice(self,values):return values[0]


class HighRng:
    def random(self):return .999999
    def choice(self,values):return values[-1]


class ContaminationBoundaries(unittest.TestCase):
    def garden(self):
        s=sim.State();s.producer_levels[2]=1
        return s

    def test_only_cardinal_mature_sources_contaminate(self):
        s=self.garden();s.garden_plot[7]=[13,50]
        for slot in (0,1,2,6,8,12,13,14):s.garden_plot[slot]=[0,35]
        self.assertEqual(sim.garden_contaminate(s,ZeroRng()),1)
        changed=[slot for slot in (1,6,8,13) if s.garden_plot[slot][0]==13]
        self.assertEqual(len(changed),1)
        self.assertTrue(all(s.garden_plot[slot][0]==0 for slot in (0,2,12,14)))
        immature=self.garden();immature.garden_plot[0]=[13,49];immature.garden_plot[1]=[0,35]
        self.assertEqual(sim.garden_contaminate(immature,ZeroRng()),0)

    def test_failed_roll_and_immune_target_are_unchanged(self):
        s=self.garden();s.garden_plot[0]=[13,50];s.garden_plot[1]=[0,35]
        self.assertEqual(sim.garden_contaminate(s,HighRng()),0)
        s.garden_plot[1]=[20,80]
        self.assertEqual(sim.garden_contaminate(s,ZeroRng()),0)

    def test_pebbles_death_unlock_and_meddleweed_conversion(self):
        s=self.garden();s.garden_soil=3;s.garden_plot[0]=[8,100]
        self.assertTrue(sim._garden_natural_death(s,0,ZeroRng()))
        self.assertIn(8,s.garden_unlocked_seeds);self.assertIsNone(s.garden_plot[0])
        s.garden_plot[0]=[13,100];sim._garden_natural_death(s,0,ZeroRng())
        self.assertEqual(s.garden_plot[0],[12,0.0])

    def test_sacrifice_is_all_or_nothing_and_resets_run_garden(self):
        s=sim.State(blood_dregs=2,garden_unlocked_seeds=set(range(33)))
        before=(s.blood_dregs,set(s.garden_unlocked_seeds))
        self.assertFalse(sim.garden_sacrifice(s));self.assertEqual((s.blood_dregs,s.garden_unlocked_seeds),before)
        s.garden_unlocked_seeds=set(range(34));s.garden_plot[0]=[1,20];s.garden_soil=4;s.garden_frozen=True
        self.assertTrue(sim.garden_sacrifice(s))
        self.assertEqual((s.blood_dregs,s.garden_unlocked_seeds,s.garden_sacrifices),(12,{0},1))
        self.assertEqual(s.garden_plot,[None]*36);self.assertFalse(s.garden_frozen)


if __name__=='__main__':unittest.main()
