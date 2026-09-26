import random
import unittest
from unittest.mock import patch
import simulator as sim


class BloodMoonBoundaries(unittest.TestCase):
    def test_research_does_not_advance_or_apply_to_past_time(self):
        s=sim.State(bank=1e20,elapsed=100,blood_moon_research_step=4)
        self.assertTrue(sim.buy_blood_moon_research(s))
        with patch.object(sim,'update_parasites'):
            sim.update_blood_moon(s,100,random.Random(7))
        self.assertEqual(s.blood_moon_stage,0)
        self.assertGreater(s.blood_moon_next_transition,100)

    def test_wait_survives_interval_partition(self):
        # Isolate the stage RNG from the still-approximate parasite layer.
        a=sim.State(blood_moon_target_stage=3)
        b=sim.State(blood_moon_target_stage=3)
        with patch.object(sim,'update_parasites'):
            a.elapsed=100
            sim.update_blood_moon(a,100,random.Random(17))
            rng=random.Random(17)
            for _ in range(1000):
                b.elapsed+=.1
                sim.update_blood_moon(b,.1,rng)
        self.assertEqual(a.blood_moon_stage,b.blood_moon_stage)
        self.assertAlmostEqual(a.blood_moon_next_transition,b.blood_moon_next_transition)

    def test_pledge_resumes_at_one_without_pre_expiry_progress(self):
        s=sim.State(elapsed=100,pledge_until=100,blood_moon_target_stage=3)
        with patch.object(sim,'update_parasites'):
            sim.update_blood_moon(s,100,random.Random(1))
        self.assertEqual(s.blood_moon_stage,1)
        self.assertGreater(s.blood_moon_next_transition,100)

    def test_pledge_and_permanent_suppression_cancel_scheduled_transition(self):
        s=sim.State(bank=1e9,blood_moon_stage=2,blood_moon_target_stage=3,
                    blood_moon_next_transition=10)
        self.assertTrue(sim.buy_pledge(s))
        self.assertEqual(s.blood_moon_next_transition,-1)
        s.permanent_suppression=True;s.blood_moon_stage=3;s.elapsed=1e6
        sim.update_blood_moon(s,1e6,random.Random(1))
        self.assertEqual(s.blood_moon_stage,0)

    def test_reawakening_clears_pending_transition(self):
        s=sim.State(run_earned=1e12,elapsed=100,blood_moon_next_transition=101)
        self.assertEqual(sim.reawaken(s),1)
        self.assertEqual(s.blood_moon_next_transition,-1)
        self.assertEqual(s.blood_moon_transition_after,100)


if __name__=='__main__':unittest.main()
