from simulator import *
import math
# Oaths 6-11 targeted factors.
s=State();s.oath_slots=[5,-1,-1]
assert abs(oath_producer_price_factor(s)-.93)<1e-12
assert abs(oath_prestige_effectiveness_factor(s)-.70)<1e-12
s.oath_slots=[6,-1,-1];assert abs(oath_click_factor(s)-1.15)<1e-12 and abs(oath_production_factor(s)-.97)<1e-12
s.oath_slots=[7,-1,-1];assert abs(oath_production_factor(s)-1.10)<1e-12 and abs(oath_omen_spawn_factor(s)-1.10)<1e-12
s.oath_slots=[8,-1,-1];assert abs(oath_insight_factor(s)-1.10)<1e-12 and abs(oath_omen_spawn_factor(s)-1.15)<1e-12
s.oath_slots=[9,-1,-1];assert oath_force_wrath(s) and abs(oath_parasite_spawn_factor(s)-2.5)<1e-12 and abs(oath_parasite_payout_factor(s)-1.15)<1e-12
s.oath_slots=[10,-1,-1];s.owned[0]=10;assert oath_order_dreg_seconds(s)==3600
s.owned[0]=9;assert oath_order_dreg_seconds(s)==0
print('PASS: v0.27 Caryll Oaths 6-11')
