from simulator import *
import random
s=State(bank=10**20);s.blood_moon_research_step=4;s.blood_moon_research_ready_at=0
assert buy_blood_moon_research(s)
assert s.blood_moon_target_stage==1 and s.blood_moon_stage==0
s.elapsed=120;update_blood_moon(s,120,random.Random(7));assert s.blood_moon_stage==1
p=State(blood_moon_stage=0,blood_moon_target_stage=3,pledge_until=100);p.elapsed=100
update_blood_moon(p,0,random.Random(1));assert p.pledge_until==0 and p.blood_moon_stage==1
c=State(blood_moon_stage=3,blood_moon_target_stage=3,permanent_suppression=True);c.elapsed=1000
update_blood_moon(c,1000,random.Random(2));assert c.blood_moon_stage==0
print('PASS: v0.20 Blood Moon stage transitions')
