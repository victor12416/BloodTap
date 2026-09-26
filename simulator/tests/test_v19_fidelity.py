from simulator import *
import random

x=State(bank=10**12,claimed_prestige=10)
assert not prestige_purchase_unlocked(x,0)
x.ascension_upgrades.add('U363')
assert prestige_purchase_unlocked(x,0)
assert buy_prestige_purchase(x)
assert x.prestige_purchases==1 and x.prestige_effectiveness==.05

r=State(bank=10**30)
r.producer_levels[7]=1
r.ritual_initialized=True
r.owned[1]=1; r.owned[7]=1000
r.ritual_energy=ritual_max_energy(r)
before=next_cost(r,1)
class SuccessRng:
    def random(self): return .99
    def choice(self, seq): return 1 if 1 in seq else seq[0]
assert cast_ritual(r,3,SuccessRng())
assert r.owned[1]==2
assert r.free[1]==0
assert next_cost(r,1)>before

o=State();o.producer_levels[6]=1;o.oath_slots=[0,-1,-1];o.oath_swaps=2;o.elapsed=1234
assert break_ascetic_on_natural_omen(o)
assert o.oath_slots==[-1,-1,-1] and o.oath_swaps==0 and o.oath_last_recharge==1234
f=State();f.producer_levels[6]=1;f.oath_slots=[0,-1,-1];f.oath_swaps=2
resolve_forced_omen(f,random.Random(1),'windfall')
assert f.oath_slots[0]==0 and f.oath_swaps==2
print('PASS: v0.19 fidelity corrections')
