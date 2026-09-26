from simulator import *
import random, math
s=State(bank=10**12);s.producer_levels[5]=1;s.owned[1]=10;s.highest_owned[1]=10
init_exchange(s,random.Random(3));assert s.exchange_ticks==15
assert all(10<=t<=699 for t in s.exchange_mode_time)
s.exchange_highest_raw_eps=100;s.exchange_values[0]=10;s.bank=100000
assert exchange_buy(s,0,1);assert not exchange_sell(s,0,1)
exchange_tick(s,random.Random(4),allow_trade=False);assert exchange_sell(s,0,1)
assert isinstance(s.exchange_profit,float)
b=State(bank=10**9);b.exchange_highest_raw_eps=100;b.highest_owned[0]=100;b.producer_levels[0]=2
assert exchange_max_brokers(b)==12;assert exchange_buy_broker(b);assert b.exchange_brokers==1
o=State();o.owned[0]=100;o.highest_owned[0]=100;o.producer_levels[0]=2
assert exchange_upgrade_office(o);assert o.exchange_office_stage==1 and o.owned[0]==0 and o.highest_owned[0]==100
l=State(bank=1000,exchange_office_stage=1);assert exchange_take_loan(l,0);assert l.bank==800 and l.exchange_loan_phase[0]==1
l.elapsed=7200;update_exchange_loans(l);assert l.exchange_loan_phase[0]==2
l.elapsed=21600;update_exchange_loans(l);assert l.exchange_loan_phase[0]==0
print('PASS: v0.22 exact Exchange mechanics')
