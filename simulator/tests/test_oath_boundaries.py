import random
import unittest
from unittest.mock import patch
import simulator as sim


class OathBoundaries(unittest.TestCase):
    def test_industry_price_applies_to_single_and_bulk_costs(self):
        plain=sim.State();industry=sim.State(oath_slots=[5,-1,-1])
        self.assertEqual(sim.next_cost(industry,1),93)
        expected=sum(round(100*1.15**n*.93+.499999999) for n in range(3))
        self.assertEqual(sim.exact_bulk_cost(industry,1,3),expected)
        self.assertLess(sim.exact_bulk_cost(industry,1,3),sim.exact_bulk_cost(plain,1,3))

    def test_factors_compose_across_slots(self):
        s=sim.State(oath_slots=[6,7,8]);s.owned[1]=10
        self.assertAlmostEqual(sim.oath_production_factor(s),.97*1.10)
        self.assertAlmostEqual(sim.oath_omen_spawn_factor(s),1.10*1.15)
        self.assertEqual(sim.oath_click_factor(s),1.15)
        self.assertEqual(sim.oath_insight_factor(s),1.10)

    def test_omen_wait_uses_frequency_factor(self):
        rng1=random.Random(8);rng2=random.Random(8)
        plain=sim.State();mother=sim.State(oath_slots=[8,-1,-1])
        self.assertAlmostEqual(sim.next_omen_wait(mother,rng1),sim.sample_omen_wait(rng2)/1.15)

    def test_scorn_forces_parasite_layer_and_payout(self):
        s=sim.State(oath_slots=[9,-1,-1])
        class Zero:
            def random(self):return 0.0
        sim.update_parasites(s,600,Zero());self.assertGreater(len(s.parasites),0)
        s.parasites=[{'phase':2,'entry':0,'stored':100,'shiny':False}]
        self.assertAlmostEqual(sim.pop_all_parasites(s),126.5)

    def test_order_hook_is_zero_without_complete_tens(self):
        s=sim.State(oath_slots=[10,-1,-1]);s.owned[0]=9
        self.assertEqual(sim.oath_order_dreg_seconds(s),0)
        s.owned[0]=30;self.assertEqual(sim.oath_order_dreg_seconds(s),10800)


if __name__=='__main__':unittest.main()
