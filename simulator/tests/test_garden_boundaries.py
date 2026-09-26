import random
import unittest
import simulator as sim


class GardenBoundaries(unittest.TestCase):
    def garden(self):
        s=sim.State();s.producer_levels[2]=1;s.highest_owned[2]=300
        return s

    def test_soil_validation_and_lockout(self):
        s=self.garden()
        for soil in (-1,5,True,1.5):self.assertFalse(sim.garden_change_soil(s,soil))
        self.assertTrue(sim.garden_change_soil(s,4))
        self.assertEqual(s.garden_next_tick,300)
        s.elapsed=599;self.assertFalse(sim.garden_change_soil(s,3))
        s.elapsed=600;self.assertTrue(sim.garden_change_soil(s,3))
        low=self.garden();low.highest_owned[2]=49
        self.assertFalse(sim.garden_change_soil(low,1))

    def test_freeze_disables_effects_and_does_not_catch_up(self):
        s=self.garden();s.garden_plot[0]=[0,35]
        self.assertTrue(sim.garden_set_frozen(s,True));self.assertEqual(sim.garden_production_factor(s),1)
        s.elapsed=10000;sim.update_garden(s,random.Random(1),active=True)
        self.assertEqual(s.garden_plot[0][1],35)
        self.assertTrue(sim.garden_set_frozen(s,False))
        self.assertEqual(s.garden_next_tick,10300)

    def test_closed_time_discards_pending_ticks(self):
        s=self.garden();s.garden_plot[0]=[0,0];s.garden_next_tick=1;s.elapsed=1000
        sim.update_garden(s,random.Random(1),active=False)
        self.assertEqual(s.garden_plot[0][1],0)
        self.assertEqual(s.garden_next_tick,1300)

    def test_neighbor_modifiers_do_not_modify_source_tile(self):
        s=self.garden();s.garden_plot[0]=[0,35];s.garden_plot[1]=[16,60]
        age,power,weed=sim.garden_tile_modifiers(s)
        self.assertAlmostEqual(power[0],1.2);self.assertEqual(power[1],1)
        self.assertEqual((age[0],weed[0]),(1,1))


if __name__=='__main__':unittest.main()
