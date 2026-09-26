import math
from simulator import *
import simulator as sim

def run():
    s=State(bank=1000)
    assert exact_bulk_cost(s,0,10)==308
    # Click starts at 1.
    assert click_value(State())==1
    # First 3 Messenger upgrades double click and B00 base.
    x=State();x.owned[0]=10;x.messenger_doublings=3
    assert click_value(x)==8
    assert math.isclose(producer_eps(x,0),8.0)
    # Finger additive is shared by B00 and clicks.
    x=State();x.owned[0]=25;x.owned[1]=10;x.messenger_additive_stage=0
    assert math.isclose(messenger_coefficient(x),0.1)
    # Mouse adds 1% of current EPS.
    x=State();x.owned[1]=10;x.mouse_upgrades=1
    assert math.isclose(click_value(x),1+0.01*raw_eps(x))
    # Handmade unlock family.
    x=State();click(x,1000);assert mouse_unlocked(x,0)
    # Insight = achievements/25 and amplifier multiplies.
    x=State();x.achievements={str(i) for i in range(25)};x.insight_amplifiers=1
    assert math.isclose(insight(x),1)
    assert math.isclose(insight_factor(x),1.1)
    # Prestige and offline parity.
    for p in (1,10,100,365,1000):
        x=State(run_earned=1e12*p**3);assert target_prestige(x)==p
    assert math.isclose(offline_gain(1,86400),594)
    # Global relics multiply independently.
    x=State();x.owned[1]=10
    base=raw_eps(x)
    r=DATA["global_relics"][0];x.global_relics.add(r["id"])
    assert math.isclose(raw_eps(x),base*(1+r["bonus_percent"]/100),rel_tol=1e-12)
    # v0.19: claimed prestige alone does not unlock the chain; U363 does.
    x=State(bank=1e12);assert not prestige_purchase_unlocked(x,0)
    x.claimed_prestige=10;assert not prestige_purchase_unlocked(x,0)
    x.ascension_upgrades.add("U363");assert prestige_purchase_unlocked(x,0)
    assert buy_prestige_purchase(x);assert math.isclose(x.prestige_effectiveness,.05)
    # Omen timer distribution sanity against verified reference mean.
    rng=random.Random(12345)
    waits=[sample_omen_wait(rng) for _ in range(20000)]
    assert 443 < sum(waits)/len(waits) < 450
    # Windfall cap and buff channels are stateful.
    x=State(bank=1e9);x.owned[1]=100
    base=raw_eps(x);sim._add_buff(x,"production",7,77,"frenzy")
    assert math.isclose(current_eps(x),base*7)
    sim._add_buff(x,"click",777,13,"click_frenzy")
    assert click_value(x)>=777
    # Blood Dreg timing/level core.
    x=State(run_earned=1e9);update_dreg_unlock(x)
    assert x.dreg_cycle_started==0
    x.elapsed=82800
    rr=random.Random(1);assert harvest_dreg_if_ready(x,rr)
    assert x.blood_dregs==1
    x.owned[2]=1;assert buy_best_level(x);assert sum(x.producer_levels)==1
    x=State();x.producer_levels[7]=1;x.owned[7]=10
    assert rituals_unlocked(x);update_ritual_energy(x,1);assert x.ritual_energy==ritual_max_energy(x)
    x.producer_levels[6]=1;assert oaths_unlocked(x);assert set_oath(x,0,0)
    x.owned[1]=10;assert oath_production_factor(x)>1
    x=State();x.producer_levels[5]=1;x.owned[1]=10
    rr=random.Random(2);init_exchange(x,rr);assert x.exchange_unlocked
    assert len(x.exchange_values)==18 and min(x.exchange_values)>=1
    x=State(bank=1e9);x.producer_levels[2]=1;x.owned[2]=10
    rr=random.Random(3);assert garden_available(x);assert garden_plant(x,0,0)
    x.garden_plot[0][1]=35
    assert garden_production_factor(x)>1
    assert garden_harvest(x,0,rr,False)
    assert 0 in x.garden_unlocked_seeds
    x=State(bank=1e15);assert buy_blood_moon_research(x);assert x.blood_moon_research_step==0
    x.elapsed=1800;x.bank=1e15;assert buy_blood_moon_research(x)
    y=State();y.blood_moon_stage=3
    rr=random.Random(4);update_parasites(y,600,rr);assert len(y.parasites)<=10
    x=State(run_earned=1e12);g=reawaken(x)
    assert g==1 and x.claimed_prestige==1 and x.run_earned==0 and x.previous_runs_earned==1e12
    baseline_ascension_spend(x);assert "U363" in x.ascension_upgrades
    y=State(bank=1e12,dream_fragments=2000,ascension_upgrades={"U363","U395","U181"})
    assert switch_calendar(y,0);assert y.calendar_state==0 and y.calendar_switches==1
    z=State(claimed_prestige=1,ascension_upgrades={"U281"})
    z.owned[1]=10
    before=z.run_earned
    g=apply_closed_time(z,86400)
    assert g>0 and z.run_earned>before
    no=State();no.owned[1]=10
    assert apply_closed_time(no,86400)==0
    r=State(bank=1e9);r.owned[1]=10
    assert omen_bank_reserve(r)>0
    a=State(bank=1e8);a.owned[1]=10
    # Adaptive policy must be callable and preserve non-negative bank.
    adaptive_greedy_step(a,4)
    assert a.bank>=0
    q=State();q.owned[0]=1
    delay=next_purchase_delay(q,4,"greedy",900)
    assert 1<=delay<=900
    v=State(bank=1e8);v.owned[1]=10
    adaptive_greedy_step(v,4)
    assert v.bank>=0
    print("PASS: recovered core tests with v0.19 prestige-root correction")

if __name__=="__main__":run()
