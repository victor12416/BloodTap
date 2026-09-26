import unittest
import simulator as sim
from simulator.tests.test_v19_integration import RitualSuccess


class OwnershipBoundaries(unittest.TestCase):
    def test_independent_state_and_rejected_purchases(self):
        a=sim.State(bank=1e9);b=sim.State()
        for producer,count in ((-1,1),(20,1),(1,-1),(1,0),(True,1),(1,1.5)):
            self.assertFalse(sim.buy_producer(a,producer,count))
        self.assertEqual(a.bank,1e9)
        self.assertEqual(a.highest_owned,[0]*20)
        self.assertTrue(sim.buy_producer(a,1,10))
        self.assertEqual(b.highest_owned,[0]*20)
        a.owned[1]=2
        self.assertEqual(sim.exchange_capacity(a,0),10)

    def test_ritual_grant_updates_highest_ownership(self):
        s=sim.State(bank=1e30)
        s.producer_levels[7]=1;s.owned[7]=1000;s.owned[1]=3
        s.ritual_energy=sim.ritual_max_energy(s)
        self.assertTrue(sim.cast_ritual(s,3,RitualSuccess()))
        self.assertEqual(s.highest_owned[1],4)

    def test_reset_keeps_permanent_progress_but_clears_capacity(self):
        s=sim.State(run_earned=1e12,highest_owned=[10]*20,exchange_office_stage=5,
                    producer_levels=[2]*20,ascension_upgrades={'U363'})
        self.assertEqual(sim.reawaken(s),1)
        self.assertEqual(s.highest_owned,[0]*20)
        self.assertEqual(s.exchange_office_stage,0)
        self.assertEqual(s.producer_levels,[2]*20)
        self.assertIn('U363',s.ascension_upgrades)

    def test_unrecovered_office_values_are_not_guessed(self):
        for stage in (1,2,4):
            with self.assertRaises(NotImplementedError):
                sim.exchange_capacity(sim.State(exchange_office_stage=stage),0)


if __name__=='__main__':unittest.main()
