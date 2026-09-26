from simulator import *
s=State(bank=10**9)
assert buy_producer(s,1,10)
assert s.highest_owned[1]==10 and exchange_capacity(s,0)==10
s.owned[1]=3;assert exchange_capacity(s,0)==10
s.producer_levels[1]=2;assert exchange_capacity(s,0)==30
s.exchange_office_stage=3;assert exchange_capacity(s,0)==180
s.exchange_office_stage=5;assert exchange_capacity(s,0)==285
r=State(run_earned=1e12,highest_owned=[5]*20,exchange_office_stage=5)
assert reawaken(r)==1
assert r.highest_owned==[0]*20 and r.exchange_office_stage==0
print('PASS: v0.21 Exchange capacity/highest-owned rules')
