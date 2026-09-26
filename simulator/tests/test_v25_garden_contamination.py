from simulator import *
class R:
 def random(self):return 0.0
 def choice(self,x):return x[0]
s=State();s.producer_levels[2]=1
s.garden_plot[0]=[13,50];s.garden_plot[1]=[0,35];garden_contaminate(s,R());assert s.garden_plot[1][0]==13
s.garden_plot=[None]*36;s.garden_plot[0]=[13,50];s.garden_plot[1]=[20,80];garden_contaminate(s,R());assert s.garden_plot[1][0]==20
a=State(garden_unlocked_seeds=set(range(34)),blood_dregs=2);assert garden_sacrifice(a);assert a.blood_dregs==12 and a.garden_unlocked_seeds=={0} and a.garden_sacrifices==1
print('PASS: v0.25 Garden contamination/sacrifice rules')
