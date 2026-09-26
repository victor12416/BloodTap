from simulator import *
import random
s=State();s.producer_levels[2]=1;s.highest_owned[2]=300
s.garden_plot[0]=[0,35];assert abs(garden_production_factor(s)-1.01)<1e-12
s.garden_plot[1]=[16,60];f=garden_production_factor(s);assert abs(f-(1.012*.98))<1e-12
s.garden_plot=[None]*36;s.garden_plot[14]=[31,40];_,_,w=garden_tile_modifiers(s);assert w[0]==0 and w[35]==1
s.garden_plot[0]=[0,35];garden_set_frozen(s,True);assert garden_production_factor(s)==1 and not garden_change_soil(s,4)
garden_set_frozen(s,False);assert garden_change_soil(s,4)
s.garden_plot[0]=[0,0.0];s.elapsed=1000;s.garden_next_tick=1;update_garden(s,random.Random(1),active=False);assert s.garden_plot[0][1]==0
print('PASS: v0.23 Garden neighbor/freeze/soil rules')
