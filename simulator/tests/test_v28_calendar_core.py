from simulator import *
s=State(bank=10**20);s.calendar_unlocked=True;s.oath_slots=[4,-1,-1]
c0=calendar_switch_cost(s);assert c0>=1e9
assert switch_calendar(s,0);assert s.calendar_state==0 and s.calendar_switches==1
assert abs(calendar_omen_spawn_factor(s)-.97)<1e-12
assert abs(calendar_drop_failure_factor(s)-.90)<1e-12
s.calendar_state=2;assert abs(calendar_omen_spawn_factor(s)-.955)<1e-12
s.eternal_calendar_enabled=False;s.calendar_until=s.elapsed+10;s.elapsed+=11;update_calendar(s);assert s.calendar_state==-1
e=State(calendar_unlocked=True,eternal_calendar_enabled=True,calendar_state=0,calendar_until=1);e.elapsed=999;update_calendar(e);assert e.calendar_state==0
print('PASS: v0.28 Calendar core/Oath hooks')
