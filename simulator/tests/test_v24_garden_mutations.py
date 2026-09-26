import simulator as sim
from simulator import *
class R:
    def random(self):return 0.0
    def choice(self,x):return x[0]
s=State();s.producer_levels[2]=1
s.garden_plot[0]=[0,35];s.garden_plot[1]=[0,35];garden_mutation_loop(s,R(),0)
assert s.garden_plot[6] is not None
a=State();a.producer_levels[2]=1;garden_mutation_loop(a,R(),1);assert all(x is None for x in a.garden_plot)
garden_mutation_loop(a,R(),0);assert all(x is not None and x[0]==13 for x in a.garden_plot)
t=[0]*34;m=[0]*34;t[20]=m[20]=8
assert (21,.001) in sim._garden_mutation_candidates(t,m)
print('PASS: v0.24 Garden mutation matrix/loops')
