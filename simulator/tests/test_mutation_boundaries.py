import unittest
import simulator as sim


class ZeroRng:
    def random(self):return 0.0
    def choice(self,values):return values[0]


class HighRng:
    def random(self):return .999999
    def choice(self,values):return values[0]


class MutationBoundaries(unittest.TestCase):
    def garden(self):
        s=sim.State();s.producer_levels[2]=1
        return s

    def test_pair_mutation_uses_pre_loop_neighbors(self):
        s=self.garden();s.garden_plot[0]=[0,35];s.garden_plot[1]=[0,35]
        count=sim.garden_mutation_loop(s,ZeroRng(),0)
        self.assertGreater(count,0);self.assertEqual(s.garden_plot[6],[1,0.0])
        # New plants are not recursively counted during the same pass.
        self.assertTrue(all(tile is None or tile[0] in (0,1,13) for tile in s.garden_plot))

    def test_extra_loop_never_spawns_spontaneous_weeds(self):
        s=self.garden();self.assertEqual(sim.garden_mutation_loop(s,ZeroRng(),1),0)
        self.assertEqual(s.garden_plot,[None]*36)

    def test_primary_weed_spawn_respects_protection(self):
        s=self.garden();s.garden_plot[14]=[31,40]
        sim.garden_mutation_loop(s,ZeroRng(),0)
        self.assertIsNone(s.garden_plot[0])
        self.assertEqual(s.garden_plot[35],[13,0.0])

    def test_failed_rolls_do_not_change_plot(self):
        s=self.garden();s.garden_plot[0]=[0,35];s.garden_plot[1]=[0,35]
        before=[None if t is None else list(t) for t in s.garden_plot]
        self.assertEqual(sim.garden_mutation_loop(s,HighRng(),0),0)
        self.assertEqual(s.garden_plot,before)


if __name__=='__main__':unittest.main()
