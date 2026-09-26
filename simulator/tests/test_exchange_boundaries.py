import math
import random
import unittest
import simulator as sim


class ExchangeBoundaries(unittest.TestCase):
    def market(self):
        s=sim.State(bank=100000,exchange_unlocked=True,exchange_highest_raw_eps=100)
        s.highest_owned[1]=10;s.exchange_values[0]=10
        return s

    def test_trade_validation_and_capacity(self):
        s=self.market()
        for item,quantity in ((-1,1),(18,1),(0,0),(0,-1),(0,1.5),(True,1)):
            self.assertFalse(sim.exchange_buy(s,item,quantity))
        self.assertFalse(sim.exchange_sell(s,0,1))
        self.assertFalse(sim.exchange_buy(s,0,11))
        self.assertTrue(sim.exchange_buy(s,0,10))
        self.assertFalse(sim.exchange_buy(s,0,1))

    def test_same_tick_blocks_only_opposite_side(self):
        s=self.market()
        self.assertTrue(sim.exchange_buy(s,0,1))
        self.assertTrue(sim.exchange_buy(s,0,1))
        self.assertFalse(sim.exchange_sell(s,0,1))
        sim.exchange_tick(s,random.Random(2),allow_trade=False)
        self.assertTrue(sim.exchange_sell(s,0,2))
        self.assertIs(type(s.exchange_profit),float)
        self.assertTrue(math.isfinite(s.exchange_profit))

    def test_broker_cap_and_known_office_sacrifice(self):
        s=sim.State(bank=1e9,exchange_highest_raw_eps=100)
        s.highest_owned[0]=100;s.producer_levels[0]=2
        self.assertEqual(sim.exchange_max_brokers(s),12)
        for _ in range(12):self.assertTrue(sim.exchange_buy_broker(s))
        self.assertFalse(sim.exchange_buy_broker(s))
        o=sim.State();o.owned[0]=100;o.highest_owned[0]=100;o.producer_levels[0]=2
        self.assertTrue(sim.exchange_upgrade_office(o))
        self.assertEqual((o.owned[0],o.highest_owned[0],o.exchange_office_stage),(0,100,1))
        with self.assertRaises(NotImplementedError):sim.exchange_upgrade_office(o)

    def test_loan_boundaries_and_large_time_jump(self):
        s=sim.State(bank=1000,exchange_office_stage=1)
        self.assertFalse(sim.exchange_take_loan(s,-1))
        with self.assertRaises(NotImplementedError):sim.exchange_take_loan(s,1)
        self.assertTrue(sim.exchange_take_loan(s,0));self.assertFalse(sim.exchange_take_loan(s,0))
        s.elapsed=21600;sim.update_exchange_loans(s)
        self.assertEqual((s.exchange_loan_phase[0],s.exchange_loan_until[0]),(0,0))


if __name__=='__main__':unittest.main()
