from simulator import *
class R:
 def __init__(self,x):self.x=x
 def random(self):return self.x
s=State(bank=10**9,quiet_hunt_unlocked=True);s.owned[1]=10
base=current_eps(s);cost=base*3600;assert toggle_quiet_hunt(s);assert s.quiet_hunt_active and abs(current_eps(s)/base-1.5)<1e-12 and s.bank==10**9-cost
v=State(veil_unlocked=True,veil_active=True,veil_reinforcements=4);v.owned[1]=10
base=raw_eps(v)/1.75;assert abs(raw_eps(v)/base-1.75)<1e-12
assert not veil_break_check(v,R(.1));assert v.veil_active and v.veil_defenses==1
assert veil_break_check(v,R(.9));assert not v.veil_active and v.veil_breaks==1
c=State(quiet_hunt_unlocked=True,quiet_hunt_active=True,veil_unlocked=True,veil_active=True);c.owned[1]=10
qv=raw_eps(c);c.quiet_hunt_active=False;c.veil_active=False;plain=raw_eps(c);assert abs(qv/plain-2.25)<1e-12
print('PASS: v0.26 Quiet Hunt/Veil rules')
