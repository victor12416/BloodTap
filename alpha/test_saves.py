import json
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
import simulator as sim
from alpha import saves


class SaveTests(unittest.TestCase):
    def test_round_trip_and_atomic_backup(self):
        s=sim.State(bank=12345,owned=[2]*20,highest_owned=[3]*20,ascension_upgrades={'U363'})
        s.achievements={'own:1:0'}
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'save.json'
            saves.write(path,s,100)
            s.bank=6789;saves.write(path,s,100)
            recovered,_,_=saves.read(path,100)
            self.assertEqual(recovered.bank,6789)
            self.assertEqual(recovered.owned,s.owned)
            previous,_=saves.decode(path.with_suffix('.bak').read_text())
            self.assertEqual(previous.bank,12345)

    def test_offline_is_unlocked_and_clock_rollback_gives_nothing(self):
        for unlocked in (False,True):
            with tempfile.TemporaryDirectory() as folder:
                s=sim.State(owned=[0,10]+[0]*18,highest_owned=[0,10]+[0]*18)
                if unlocked:s.ascension_upgrades={'U363','U281'}
                path=Path(folder)/'save.json';saves.write(path,s,100)
                _,gain,_=saves.read(path,100+86400)
                self.assertEqual(gain,5940 if unlocked else 0)
                _,gain,away=saves.read(path,99)
                self.assertEqual((gain,away),(0,0))

    def test_invalid_imports(self):
        for key,value in [('bank',float('nan')),('owned',[-1]*20),('owned',[0]),
                          ('mouse_upgrades',True),('standard_tiers',['-1:0']),
                          ('ascension_upgrades',['__import__']),('prestige_purchases',1)]:
            doc=saves.document(sim.State(),100);doc['state'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):saves.decode(json.dumps(doc))
        doc=saves.document(sim.State(),100);doc['version']=2
        with self.assertRaises(ValueError):saves.decode(json.dumps(doc))

    def test_large_prestige_is_bounded_and_exact(self):
        s=sim.State(run_earned=1e270)
        result=sim.target_prestige(s)
        units=int(Decimal(str(s.run_earned)))//10**12
        self.assertLessEqual(result**3,units)
        self.assertGreater((result+1)**3,units)

    def test_invalid_write_keeps_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'save.json';s=sim.State();saves.write(p,s,100)
            original=p.read_bytes();s.bank=float('inf')
            with self.assertRaises(ValueError):saves.write(p,s,101)
            self.assertEqual(p.read_bytes(),original)

    def test_corrupt_save_is_not_overwritten_and_backup_stays_readable(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'save.json';s=sim.State(bank=123)
            saves.write(p,s,100);s.bank=456;saves.write(p,s,101)
            backup=p.with_suffix('.bak').read_bytes()
            p.write_text('{broken',encoding='utf-8')
            with self.assertRaises(ValueError):saves.read(p,200)
            with self.assertRaises(ValueError):saves.write(p,s,200)
            self.assertEqual(p.read_text(),'{broken')
            self.assertEqual(p.with_suffix('.bak').read_bytes(),backup)

    def test_closed_reward_is_not_repeated_after_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'save.json'
            s=sim.State(owned=[0,10]+[0]*18,highest_owned=[0,10]+[0]*18,
                        ascension_upgrades={'U363','U281'})
            saves.write(p,s,100)
            restored,gain,_=saves.read(p,100+86400)
            self.assertEqual(gain,5940)
            saves.write(p,restored,100+86400)
            again,gain,_=saves.read(p,100+86400)
            self.assertEqual(gain,0)
            self.assertEqual(again.bank,restored.bank)


if __name__=='__main__':unittest.main()
