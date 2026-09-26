import random
import tempfile
from pathlib import Path
import unittest
from alpha.game import Game, alpha_new_fragments, alpha_target_prestige
from alpha import saves
import simulator as sim


class GameTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.now=100.0
        self.game=Game(Path(self.temp.name)/'save.json',rng=random.Random(1),clock=lambda:self.now,wall=lambda:self.now)

    def test_click_buy_upgrade_and_reload(self):
        g=self.game
        for _ in range(15):g.action({'action':'click'})
        g.action({'action':'buy','producer':0})
        self.assertEqual((g.state.bank,g.state.owned[0]),(0,1))
        self.now+=5;g.advance();self.assertAlmostEqual(g.state.bank,.5)
        g.state.bank=100
        g.action({'action':'upgrade','id':'messenger_double:0','cost':-99999})
        self.assertEqual(g.state.bank,0);self.assertEqual(g.state.messenger_doublings,1)
        state,_,_=saves.read(g.path,self.now)
        self.assertEqual(state.owned[0],1)
        self.assertEqual(state.messenger_doublings,1)

    def test_buff_expiry_splits_income(self):
        g=self.game;g.state.owned[1]=10;g.state.highest_owned[1]=10
        sim._add_buff(g.state,'production',7,2,'frenzy')
        self.now+=5;g.advance()
        self.assertEqual(g.state.bank,170) # 2*70 + 3*10
        self.assertEqual(g.state.prod_buffs,[])

    def test_omen_requires_collection_and_cannot_be_collected_twice(self):
        g=self.game;g.state.omen_next=1
        self.now+=2;g.advance();self.assertGreater(g.snapshot()['omen_seconds'],0)
        self.assertEqual(g.state.omen_clicks,0)
        g.action({'action':'omen'});self.assertEqual(g.state.omen_clicks,1)
        with self.assertRaises(ValueError):g.action({'action':'omen'})

    def test_invalid_import_and_reset_leave_state_unchanged(self):
        g=self.game;g.state.bank=99
        with self.assertRaises(ValueError):g.action({'action':'import','save':'{}'})
        with self.assertRaises(ValueError):g.action({'action':'reset'})
        self.assertEqual(g.state.bank,99)
        g.action({'action':'reset','confirmation':'RESET'})
        self.assertEqual(g.state.bank,0)
        backup,_=saves.decode(g.path.with_suffix('.bak').read_text())
        self.assertEqual(backup.bank,99)

    def test_reawakening_and_first_useful_bundle(self):
        g=self.game;g.state.run_earned=8e12
        with self.assertRaises(ValueError):g.action({'action':'reawaken'})
        g.action({'action':'reawaken','confirmation':'REAWAKEN'})
        self.assertEqual(g.state.dream_fragments,2)
        g.action({'action':'ascension','id':'U363'})
        g.action({'action':'ascension','id':'U281'})
        self.assertEqual(g.state.dream_fragments,0)
        self.assertEqual(sim.offline_settings(g.state),(.05,3600))

    def test_starter_prestige_accelerates_only_first_bundle(self):
        g=self.game
        g.state.run_earned=22_999_999
        self.assertEqual(alpha_new_fragments(g.state),0)
        g.state.run_earned=23_000_000
        self.assertEqual(alpha_new_fragments(g.state),1)
        g.state.run_earned=184_000_000
        self.assertEqual(alpha_target_prestige(g.state),2)
        self.assertEqual(alpha_new_fragments(g.state),2)
        g.action({'action':'reawaken','confirmation':'REAWAKEN'})
        self.assertEqual((g.state.claimed_prestige,g.state.dream_fragments),(2,2))
        self.assertEqual(alpha_new_fragments(g.state),0)

        # The starter curve is capped; fragment three keeps the recovered
        # cubic threshold of 27e12 lifetime echoes.
        g.state.run_earned=27_000_000_000_000-g.state.previous_runs_earned
        self.assertEqual(alpha_target_prestige(g.state),3)
        self.assertEqual(alpha_new_fragments(g.state),1)


if __name__=='__main__':unittest.main()
