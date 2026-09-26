"""BloodTap simulator: recovered executable baseline plus v0.19 repairs.

Source and data provenance are recorded in docs/archive/manifest.json.
Later milestone tests remain pending; see docs/STATUS.md.
"""
from dataclasses import dataclass, field
from typing import List, Set
import json, math, random, bisect
from pathlib import Path

DATA=json.loads((Path(__file__).with_name("economy_data.json")).read_text(encoding="utf-8"))
GARDEN=json.loads((Path(__file__).with_name("garden_data.json")).read_text(encoding="utf-8"))
GROWTH=DATA["price_growth"]
RELIC_BY_ID={r["id"]:r for r in DATA.get("global_relics",[])}

@dataclass
class State:
    bank: float=0.0
    run_earned: float=0.0
    previous_runs_earned: float=0.0
    claimed_prestige: int=0
    dream_fragments: int=0
    owned: List[int]=field(default_factory=lambda:[0]*20)
    free: List[int]=field(default_factory=lambda:[0]*20)
    producer_levels: List[int]=field(default_factory=lambda:[0]*20)
    standard_tiers: Set[str]=field(default_factory=set)
    messenger_doublings: int=0
    messenger_additive_stage: int=-1
    mouse_upgrades: int=0
    insight_amplifiers: int=0
    global_relics: Set[str]=field(default_factory=set)
    prestige_purchases: int=0
    achievements: Set[str]=field(default_factory=set)
    handmade_echoes: float=0.0
    clicks: int=0
    global_factor: float=1.0
    prestige_effectiveness: float=0.0
    insight_effectiveness: float=1.0
    elapsed: float=0.0
    purchase_log: list=field(default_factory=list)
    omen_clicks: int=0
    omen_last: str=""
    omen_next: float=0.0
    prod_buffs: list=field(default_factory=list)   # [end_time,factor,label]
    click_buffs: list=field(default_factory=list)  # [end_time,factor,label]
    omen_log: list=field(default_factory=list)
    blood_dregs: int=0
    dreg_unlocked_at: float=-1.0
    dreg_cycle_started: float=-1.0
    dregs_harvested: int=0
    ritual_energy: float=0.0
    ritual_initialized: bool=False
    ritual_casts: int=0
    ritual_successes: int=0
    ritual_backfires: int=0
    oath_slots: list=field(default_factory=lambda:[-1,-1,-1])
    oath_swaps: int=3
    oath_last_recharge: float=0.0
    exchange_unlocked: bool=False
    exchange_ticks: int=0
    exchange_last_tick: float=0.0
    exchange_values: list=field(default_factory=lambda:[0.0]*18)
    exchange_velocity: list=field(default_factory=lambda:[0.0]*18)
    exchange_modes: list=field(default_factory=lambda:[0]*18)
    exchange_mode_time: list=field(default_factory=lambda:[0]*18)
    exchange_stock: list=field(default_factory=lambda:[0]*18)
    exchange_profit: float=0.0
    exchange_brokers: int=0
    exchange_highest_raw_eps: float=0.0
    garden_unlocked_seeds: set=field(default_factory=lambda:{0})
    garden_plot: list=field(default_factory=lambda:[None]*36)
    garden_soil: int=0
    garden_next_tick: float=0.0
    garden_harvest_count: int=0
    blood_moon_research_step: int=-1
    blood_moon_research_ready_at: float=-1.0
    blood_moon_stage: int=0
    blood_moon_target_stage: int=0
    pledge_count: int=0
    pledge_until: float=0.0
    permanent_suppression: bool=False
    parasites: list=field(default_factory=list)
    parasites_popped: int=0
    calendar_state: int=-1
    calendar_switches: int=0
    calendar_until: float=0.0
    ascension_upgrades: set=field(default_factory=set)
    total_reawakenings: int=0

def next_cost(s,i,discount=1.0):
    p=DATA["producers"][i]
    return math.ceil(p["base_cost"]*GROWTH**max(0,s.owned[i]-s.free[i])*discount)

def exact_bulk_cost(s,i,k,discount=1.0):
    p=DATA["producers"][i]; total=0
    for n in range(s.owned[i],s.owned[i]+k):
        total+=math.ceil(p["base_cost"]*GROWTH**max(0,n-s.free[i])*discount)
    return total

def standard_tier_factor(s,i):
    if i==0:return 1.0
    f=1.0
    for t in range(15):
        if f"{i}:{t}" in s.standard_tiers:f*=2
    return f

def messenger_coefficient(s):
    if s.messenger_additive_stage<0:return 0.0
    a=DATA["messenger"]["base_additive_coefficient"]
    # Stage 0 is the initial +0.1-per-non-Messenger upgrade.
    # Later stages apply x5, x10, then repeated x20 multipliers.
    for j in range(min(s.messenger_additive_stage,len(DATA["messenger"]["coefficient_multipliers"]))):
        a*=DATA["messenger"]["coefficient_multipliers"][j]
    return a

def producer_eps(s,i):
    p=DATA["producers"][i]; level=1+0.01*s.producer_levels[i]
    if i==0:
        n=sum(s.owned[1:])
        base=.1*(2**s.messenger_doublings)+messenger_coefficient(s)*n
        return s.owned[0]*base*level
    return s.owned[i]*p["base_eps"]*standard_tier_factor(s,i)*level

def insight(s): return len(s.achievements)/25.0

def insight_factor(s):
    out=1.0; ins=insight(s)
    cfg=DATA["insight_amplifiers"]
    for j in range(s.insight_amplifiers):
        out*=1+ins*cfg["coefficients"][j]*s.insight_effectiveness
    return out

def prestige_factor(s):
    return 1+(s.claimed_prestige/100.0)*s.prestige_effectiveness

def relic_factor(s):
    out=1.0
    for rid in s.global_relics:
        r=RELIC_BY_ID.get(rid)
        if r: out*=1+r["bonus_percent"]/100.0
    return out

def oath_production_factor(s):
    ascetic=(.15,.10,.05); decadence=(.07,.05,.02)
    out=1.0
    for slot,oath in enumerate(s.oath_slots):
        if oath==0: out*=1+ascetic[slot]
        elif oath==1: out*=1-decadence[slot]
    return out

def garden_stage_strength(plant,age):
    m=plant["mature"]
    if age>=m:return 1.0
    if age>=.666*m:return .50
    if age>=.333*m:return .25
    return .10

def garden_production_factor(s):
    if s.producer_levels[2]<1:return 1.0
    soil=GARDEN["soils"][s.garden_soil]["effect"]
    additive=0.0;mult=1.0
    for tile in s.garden_plot:
        if tile is None:continue
        pid,age=tile;p=GARDEN["plants"][pid];strength=soil*garden_stage_strength(p,age)
        if p["effect"]=="prod":additive+=p["power"]*strength
        elif p["effect"]=="prod_mult":mult*=1+p["power"]*strength
    return (1+additive)*mult

def blood_moon_global_factor(s):
    out=1.0
    for step,pct in ((1,.01),(2,.02),(4,.03),(6,.04),(8,.05)):
        if s.blood_moon_research_step>=step:out*=1+pct
    if s.permanent_suppression:out*=.95
    return out

def raw_eps(s):
    return sum(producer_eps(s,i) for i in range(20))*s.global_factor*relic_factor(s)*insight_factor(s)*prestige_factor(s)*oath_production_factor(s)*garden_production_factor(s)*blood_moon_global_factor(s)

def production_buff_factor(s):
    out=1.0
    for end,factor,label in s.prod_buffs:
        if end>s.elapsed: out*=factor
    return out

def click_buff_factor(s):
    out=1.0
    for end,factor,label in s.click_buffs:
        if end>s.elapsed: out*=factor
    return out

def current_eps(s):
    return raw_eps(s)*production_buff_factor(s)

def click_value(s):
    # Production-derived clicking uses current EPS, then the separate
    # click-buff channel multiplies the completed click value.
    n=sum(s.owned[1:])
    base=1*(2**s.messenger_doublings)+messenger_coefficient(s)*n
    return (base + 0.01*s.mouse_upgrades*current_eps(s))*click_buff_factor(s)

def _grant_achievements_pass(s):
    before=len(s.achievements)
    # 48 cumulative-run earnings achievements.
    if s.run_earned>=1:s.achievements.add("earn:0")
    for j in range(1,48):
        if s.run_earned>=10**math.floor(1.5*j+2):s.achievements.add(f"earn:{j}")
    # 48 raw-production achievements.
    eps=raw_eps(s)
    for j in range(48):
        if eps>=10**math.floor(1.2*j):s.achievements.add(f"eps:{j}")
    # 19 ordinary producer ownership ladders.
    th=DATA["achievements"]["ownership_thresholds"]
    for i in range(1,20):
        for j,x in enumerate(th):
            if s.owned[i]>=x:s.achievements.add(f"own:{i}:{j}")
    # Messenger has its own ownership ladder.
    for j,x in enumerate(DATA["achievements"]["messenger_thresholds"]):
        if s.owned[0]>=x:s.achievements.add(f"own:0:{j}")
    # Handmade/clicking achievement family that unlocks mouse upgrades.
    for j,x in enumerate(DATA["clicking"]["handmade_unlocks"]):
        if s.handmade_echoes>=x:s.achievements.add(f"handmade:{j}")
    # Broad deterministic construction/upgrade count families.
    total=sum(s.owned)
    for j,x in enumerate(DATA["achievements"]["total_building_thresholds"]):
        if total>=x:s.achievements.add(f"buildings:{j}")
    u=upgrade_count(s)
    for j,x in enumerate(DATA["achievements"]["upgrade_count_thresholds"]):
        if u>=x:s.achievements.add(f"upgrades:{j}")
    return len(s.achievements)-before

def grant_achievements(s):
    """Resolve achievement -> Insight -> EPS achievement cascades to a fixed point."""
    total=0
    for _ in range(8):
        gained=_grant_achievements_pass(s)
        total+=gained
        if gained==0:
            break
    return total


def upgrade_count(s):
    return len(s.standard_tiers)+s.messenger_doublings+max(0,s.messenger_additive_stage+1)+s.mouse_upgrades+s.insight_amplifiers+len(s.global_relics)+s.prestige_purchases

def earn_passive(s,seconds):
    gross=current_eps(s)
    withheld=store_parasite_withheld(s,gross,seconds)
    g=gross*seconds-withheld
    s.bank+=g;s.run_earned+=g;update_dreg_unlock(s);return g

def click(s,count=1):
    total=0.0
    for _ in range(count):
        v=click_value(s);s.bank+=v;s.run_earned+=v;s.handmade_echoes+=v;s.clicks+=1;total+=v;update_dreg_unlock(s)
    grant_achievements(s);return total

def buy_producer(s,i,k=1,discount=1.0):
    c=exact_bulk_cost(s,i,k,discount)
    if s.bank<c:return False
    s.bank-=c;s.owned[i]+=k;s.purchase_log.append((s.elapsed,"producer",i,k,c));grant_achievements(s);return True

def tier_cost(i,t):
    return math.ceil(DATA["producers"][i]["base_cost"]*DATA["standard_tiers"]["cost_base_multipliers"][t])

def tier_unlocked(s,i,t):return i>0 and s.owned[i]>=DATA["standard_tiers"]["unlock_owned"][t]

def buy_tier(s,i,t):
    key=f"{i}:{t}"
    if key in s.standard_tiers or not tier_unlocked(s,i,t):return False
    c=tier_cost(i,t)
    if s.bank<c:return False
    s.bank-=c;s.standard_tiers.add(key);s.purchase_log.append((s.elapsed,"tier",i,t,c));grant_achievements(s);return True

def messenger_upgrade_options(s):
    out=[]
    # First 3 doublings: unlock 1,1,10 Messengers.
    d=s.messenger_doublings
    if d<3 and s.owned[0]>=DATA["messenger"]["doubling_unlocks"][d]:
        out.append(("messenger_double",d,DATA["messenger"]["doubling_costs"][d]))
    # Additive chain: stage 0 at 25; later stages at 50..550.
    next_stage=s.messenger_additive_stage+1
    if next_stage==0 and s.owned[0]>=25:out.append(("messenger_add",0,100000))
    elif next_stage>0 and next_stage<=len(DATA["messenger"]["coefficient_multiplier_thresholds"]):
        threshold=DATA["messenger"]["coefficient_multiplier_thresholds"][next_stage-1]
        # Prices from the pinned reference finger chain.
        finger_prices=[1e7,1e8,1e9,1e10,1e13,1e16,1e19,1e22,1e25,1e28,1e31]
        if s.owned[0]>=threshold:out.append(("messenger_add",next_stage,finger_prices[next_stage-1]))
    return out

def buy_messenger_upgrade(s,kind,stage,cost):
    if s.bank<cost:return False
    s.bank-=cost
    if kind=="messenger_double":s.messenger_doublings+=1
    else:s.messenger_additive_stage=stage
    s.purchase_log.append((s.elapsed,kind,stage,cost));grant_achievements(s);return True

def mouse_unlocked(s,j):
    return j<len(DATA["clicking"]["handmade_unlocks"]) and s.handmade_echoes>=DATA["clicking"]["handmade_unlocks"][j]

def buy_mouse(s):
    j=s.mouse_upgrades
    if j>=15 or not mouse_unlocked(s,j):return False
    c=DATA["clicking"]["mouse_upgrade_costs"][j]
    if s.bank<c:return False
    s.bank-=c;s.mouse_upgrades+=1;s.purchase_log.append((s.elapsed,"mouse",j,c));grant_achievements(s);return True

def insight_amp_unlocked(s,j):
    return j<15 and len(s.achievements)>=DATA["insight_amplifiers"]["achievement_unlocks"][j]

def buy_insight_amp(s):
    j=s.insight_amplifiers
    if not insight_amp_unlocked(s,j):return False
    c=DATA["insight_amplifiers"]["costs"][j]
    if s.bank<c:return False
    s.bank-=c;s.insight_amplifiers+=1;s.purchase_log.append((s.elapsed,"insight",j,c));grant_achievements(s);return True

def income_rate(s,cps):
    return current_eps(s)+cps*click_value(s)

def _score_mutation(s,cost,cps,apply,undo):
    before=income_rate(s,cps); apply();grant_achievements(s);after=income_rate(s,cps);undo()
    # Achievements are persistent; candidate scoring must not leak hypothetical awards.
    # Caller snapshots/restores achievements around this helper.
    return (after-before)/cost if cost else 0



def relic_unlocked(s,r):
    return s.run_earned>=r["run_earnings_unlock"]

def buy_relic(s,r):
    if r["id"] in s.global_relics or not relic_unlocked(s,r): return False
    c=math.ceil(r["cost"])
    if s.bank<c:return False
    s.bank-=c;s.global_relics.add(r["id"])
    s.purchase_log.append((s.elapsed,"relic",r["id"],c))
    grant_achievements(s);return True

def prestige_purchase_unlocked(s,j):
    # Run purchases require the permanent root, not just claimed prestige.
    return "U363" in s.ascension_upgrades and j==s.prestige_purchases and 0<=j<len(DATA["prestige_effectiveness_purchases"])

def buy_prestige_purchase(s):
    j=s.prestige_purchases
    if not prestige_purchase_unlocked(s,j):return False
    cfg=DATA["prestige_effectiveness_purchases"][j]
    if s.bank<cfg["cost"]:return False
    s.bank-=cfg["cost"];s.prestige_purchases+=1
    s.prestige_effectiveness=cfg["effectiveness"]
    s.purchase_log.append((s.elapsed,"prestige_effectiveness",cfg["id"],cfg["cost"]))
    grant_achievements(s);return True

def purchase_options(s,cps):
    opts=[]
    base_income=income_rate(s,cps)
    # Producers
    for i in range(20):
        c=next_cost(s,i)
        if c<=s.bank:
            ach=set(s.achievements);before=base_income;s.owned[i]+=1;grant_achievements(s);after=income_rate(s,cps);s.owned[i]-=1;s.achievements=ach
            opts.append(((after-before)/c,("producer",i),c))
    # Standard tiers
    for i in range(1,20):
        for t in range(15):
            key=f"{i}:{t}"
            if key not in s.standard_tiers:
                if tier_unlocked(s,i,t):
                    c=tier_cost(i,t)
                    if c<=s.bank:
                        ach=set(s.achievements);before=base_income;s.standard_tiers.add(key);grant_achievements(s);after=income_rate(s,cps);s.standard_tiers.remove(key);s.achievements=ach
                        opts.append(((after-before)/c,("tier",i,t),c))
                break
    # Messenger specials
    for kind,stage,c in messenger_upgrade_options(s):
        if c<=s.bank:
            ach=set(s.achievements);before=income_rate(s,cps)
            if kind=="messenger_double":s.messenger_doublings+=1
            else:
                old=s.messenger_additive_stage;s.messenger_additive_stage=stage
            grant_achievements(s);after=income_rate(s,cps)
            if kind=="messenger_double":s.messenger_doublings-=1
            else:s.messenger_additive_stage=old
            s.achievements=ach;opts.append(((after-before)/c,(kind,stage),c))
    # Mouse
    j=s.mouse_upgrades
    if j<15 and mouse_unlocked(s,j):
        c=DATA["clicking"]["mouse_upgrade_costs"][j]
        if c<=s.bank:
            ach=set(s.achievements);before=base_income;s.mouse_upgrades+=1;grant_achievements(s);after=income_rate(s,cps);s.mouse_upgrades-=1;s.achievements=ach
            opts.append(((after-before)/c,("mouse",j),c))
    # Global relics with fully captured deterministic run-earnings unlocks.
    for r in DATA.get("global_relics",[]):
        if r["id"] not in s.global_relics and relic_unlocked(s,r):
            c=math.ceil(r["cost"])
            if c<=s.bank:
                ach=set(s.achievements);before=income_rate(s,cps)
                s.global_relics.add(r["id"]);grant_achievements(s);after=income_rate(s,cps)
                s.global_relics.remove(r["id"]);s.achievements=ach
                opts.append(((after-before)/c,("relic",r["id"]),c))
    # Run-local prestige-effectiveness chain (only after prestige exists).
    j=s.prestige_purchases
    if prestige_purchase_unlocked(s,j):
        cfg=DATA["prestige_effectiveness_purchases"][j];c=cfg["cost"]
        if c<=s.bank:
            old=s.prestige_effectiveness;ach=set(s.achievements);before=income_rate(s,cps)
            s.prestige_effectiveness=cfg["effectiveness"];s.prestige_purchases+=1;grant_achievements(s);after=income_rate(s,cps)
            s.prestige_purchases-=1;s.prestige_effectiveness=old;s.achievements=ach
            opts.append(((after-before)/c,("prestige_effectiveness",j),c))
    # Insight amplifier
    j=s.insight_amplifiers
    if insight_amp_unlocked(s,j):
        c=DATA["insight_amplifiers"]["costs"][j]
        if c<=s.bank:
            ach=set(s.achievements);before=base_income;s.insight_amplifiers+=1;grant_achievements(s);after=income_rate(s,cps);s.insight_amplifiers-=1;s.achievements=ach
            opts.append(((after-before)/c,("insight",j),c))
    return opts

def greedy_step(s,cps):
    opts=purchase_options(s,cps)
    if not opts:return False
    _,choice,c=max(opts,key=lambda x:x[0])
    if choice[0]=="producer":return buy_producer(s,choice[1])
    if choice[0]=="tier":return buy_tier(s,choice[1],choice[2])
    if choice[0] in ("messenger_double","messenger_add"):return buy_messenger_upgrade(s,choice[0],choice[1],c)
    if choice[0]=="mouse":return buy_mouse(s)
    if choice[0]=="relic":
        r=next(x for x in DATA["global_relics"] if x["id"]==choice[1]);return buy_relic(s,r)
    if choice[0]=="prestige_effectiveness":return buy_prestige_purchase(s)
    if choice[0]=="insight":return buy_insight_amp(s)
    return False

def target_prestige(s):
    lifetime=s.previous_runs_earned+s.run_earned
    a=int((lifetime/1e12)**(1/3)) if lifetime>0 else 0
    while 1e12*(a+1)**3<=lifetime:a+=1
    while 1e12*a**3>lifetime:a-=1
    return a

def new_fragments(s):return max(0,target_prestige(s)-s.claimed_prestige)

def offline_gain(unbuffed_eps,seconds,efficiency=.05,cap=3600):
    return unbuffed_eps*efficiency*(min(seconds,cap)+.1*max(0,seconds-cap))









# ---------- Event-driven timing ----------
def next_purchase_delay(s,cps,policy="greedy",cap=900.0):
    """Conservative jump to when any currently visible purchase may be affordable."""
    opts=purchase_options(s,cps)
    if not opts:return cap
    income=max(current_eps(s)+max(0.0,cps)*click_value(s),1e-300)
    waits=[]
    for score,choice,cost in opts:
        if policy=="reserve":reserve=omen_bank_reserve(s)
        elif policy=="adaptive":reserve=adaptive_required_reserve(s,score)
        else:reserve=0.0
        waits.append(max(0.0,cost+reserve-s.bank)/income)
    return max(1.0,min(cap,min(waits)))

# ---------- Strategy / offline layer ----------
def offline_settings(s):
    """Return (efficiency, full-rate cap seconds) from owned permanent nodes."""
    if "U281" not in s.ascension_upgrades:
        return (0.0, 0.0)
    # Baseline first offline node: 5%, 1 hour.
    efficiency=.05
    cap=3600.0
    # Hooks for the verified Sleeping Vigil / Enduring Dream branches.
    vigil=("U274","U275","U276","U277","U278","U279","U280")
    enduring=("U353","U354","U355","U356","U357","U358","U359")
    efficiency += .10*sum(uid in s.ascension_upgrades for uid in vigil)
    cap *= 2**sum(uid in s.ascension_upgrades for uid in enduring)
    return min(efficiency,.91),cap

def apply_closed_time(s,seconds):
    """Advance wall time and award only permanent-unlocked closed production."""
    efficiency,cap=offline_settings(s)
    gain=offline_gain(raw_eps(s),seconds,efficiency,cap) if efficiency>0 else 0.0
    s.bank+=gain
    s.run_earned+=gain
    s.elapsed+=seconds
    process_dreg_auto(s)
    update_calendar(s)
    update_oath_swaps(s)
    update_dreg_unlock(s)
    grant_achievements(s)
    return gain

def omen_bank_reserve(s):
    """Bank needed to avoid reducing the ordinary windfall cap."""
    return current_eps(s)*6000.0

def reserve_greedy_step(s,cps,reserve_fraction=1.0):
    """Greedy purchase, but do not spend below the Omen windfall reserve."""
    reserve=omen_bank_reserve(s)*reserve_fraction
    opts=[x for x in purchase_options(s,cps) if s.bank-x[2]>=reserve]
    if not opts:
        return False
    _,choice,c=max(opts,key=lambda x:x[0])
    if choice[0]=="producer":return buy_producer(s,choice[1])
    if choice[0]=="tier":return buy_tier(s,choice[1],choice[2])
    if choice[0] in ("messenger_double","messenger_add"):return buy_messenger_upgrade(s,choice[0],choice[1],c)
    if choice[0]=="mouse":return buy_mouse(s)
    if choice[0]=="relic":
        return buy_relic(s,RELIC_BY_ID[choice[1]])
    if choice[0]=="prestige_effectiveness":return buy_prestige_purchase(s)
    if choice[0]=="insight":return buy_insight_amp(s)
    return False

def adaptive_required_reserve(s,score):
    reserve=omen_bank_reserve(s)
    payback=(1/score) if score>0 else float("inf")
    if payback<=300:return 0.0
    if payback<=900:return reserve*.25
    if payback<=1800:return reserve*.50
    if payback<=3600:return reserve*.75
    return reserve

def _execute_choice(s,choice,c):
    if choice[0]=="producer":return buy_producer(s,choice[1])
    if choice[0]=="tier":return buy_tier(s,choice[1],choice[2])
    if choice[0] in ("messenger_double","messenger_add"):return buy_messenger_upgrade(s,choice[0],choice[1],c)
    if choice[0]=="mouse":return buy_mouse(s)
    if choice[0]=="relic":return buy_relic(s,RELIC_BY_ID[choice[1]])
    if choice[0]=="prestige_effectiveness":return buy_prestige_purchase(s)
    if choice[0]=="insight":return buy_insight_amp(s)
    return False

def adaptive_greedy_step(s,cps):
    # v0.13 chose the absolute best candidate and stopped if that single item
    # violated the reserve. v0.15 instead chooses the best candidate that
    # actually satisfies its own payback-adjusted reserve.
    viable=[]
    for score,choice,c in purchase_options(s,cps):
        if s.bank-c>=adaptive_required_reserve(s,score):
            viable.append((score,choice,c))
    if not viable:return False
    score,choice,c=max(viable,key=lambda x:x[0])
    return _execute_choice(s,choice,c)

def buy_until_stable(s,cps,policy="greedy"):
    fn={"greedy":greedy_step,"reserve":reserve_greedy_step,"adaptive":adaptive_greedy_step}[policy]
    n=0
    while fn(s,cps):
        n+=1
        if n>5000:raise RuntimeError("purchase loop failed to stabilize")
    return n

# ---------- Rites of the Calendar ----------
CALENDAR_NAMES=("Night of the Hunt","Festival of Blood","Masquerade of Yharnam","Night of Spirits","Vermin Hunt")

def calendar_unlocked(s):return "U181" in s.ascension_upgrades
def calendar_oath_multiplier(s):
    for slot,oath in enumerate(s.oath_slots):
        if oath==4:return (2.0,1.5,1.25)[slot]
    return 1.0
def calendar_switch_cost(s):return 1e9+raw_eps(s)*60*(1.5**s.calendar_switches)*calendar_oath_multiplier(s)
def switch_calendar(s,state):
    if not calendar_unlocked(s) or not 0<=state<5:return False
    c=calendar_switch_cost(s)
    if s.bank<c:return False
    s.bank-=c;s.calendar_state=state;s.calendar_switches+=1;s.calendar_until=s.elapsed+86400;return True
def update_calendar(s):
    if s.calendar_state>=0 and s.elapsed>=s.calendar_until:s.calendar_state=-1;s.calendar_until=0.0

# ---------- Blood Moon research + Nightmare Parasites ----------
_BM_COSTS=(1e15,1e15,2e15,4e15,8e15,1.6e16,3.2e16,6.4e16,1.28e17,2.56e17)

def blood_moon_next_step(s):return s.blood_moon_research_step+1

def blood_moon_can_buy(s):
    j=blood_moon_next_step(s)
    if j>=len(_BM_COSTS):return False
    if j>0 and s.elapsed<s.blood_moon_research_ready_at:return False
    return s.bank>=_BM_COSTS[j]

def buy_blood_moon_research(s):
    if not blood_moon_can_buy(s):return False
    j=blood_moon_next_step(s);s.bank-=_BM_COSTS[j];s.blood_moon_research_step=j
    if j in (5,7,9):
        s.blood_moon_target_stage={5:1,7:2,9:3}[j]
        if not s.permanent_suppression and s.pledge_until<=s.elapsed:s.blood_moon_stage=s.blood_moon_target_stage
    if j<9:s.blood_moon_research_ready_at=s.elapsed+1800
    return True

def parasite_capacity(s):return 10

def parasite_attached(s):return [p for p in s.parasites if p["phase"]==2]

def parasite_withheld_fraction(s):
    return min(1.0,.05*len(parasite_attached(s)))

def update_parasites(s,dt,rng):
    if s.permanent_suppression or s.pledge_until>s.elapsed or s.blood_moon_stage<=0:return
    frames=max(0,int(dt*30));cap=parasite_capacity(s)
    # Equivalent probability of >=1 spawn opportunity per empty slot over dt.
    pframe=.00001*s.blood_moon_stage
    pspan=1-(1-pframe)**frames
    empty=max(0,cap-len(s.parasites))
    for _ in range(empty):
        if rng.random()<pspan:
            s.parasites.append({"phase":1,"entry":10.0,"stored":0.0,"shiny":rng.random()<.0001})
    for p in s.parasites:
        if p["phase"]==1:
            p["entry"]-=dt
            if p["entry"]<=0:p["phase"]=2

def store_parasite_withheld(s,gross,dt):
    attached=parasite_attached(s)
    if not attached:return 0.0
    withheld=gross*parasite_withheld_fraction(s)*dt
    # Reference parity: the global withered amount is added to each attached parasite.
    for p in attached:p["stored"]+=withheld
    return withheld

def pop_all_parasites(s):
    total=0.0
    for p in s.parasites:
        if p["phase"]==2:
            total+=p["stored"]*1.10*(3 if p["shiny"] else 1)
    s.bank+=total;s.run_earned+=total;s.parasites_popped+=len(s.parasites);s.parasites=[]
    return total

def buy_pledge(s):
    price=8**min(s.pledge_count+2,14)
    if s.bank<price:return False
    s.bank-=price;pop_all_parasites(s);s.pledge_count+=1;s.pledge_until=s.elapsed+1800;s.blood_moon_stage=0
    return True

def update_blood_moon(s,dt,rng):
    if s.pledge_until and s.elapsed>=s.pledge_until and not s.permanent_suppression:
        s.pledge_until=0
        if s.blood_moon_target_stage>0:s.blood_moon_stage=max(1,s.blood_moon_target_stage)
    update_parasites(s,dt,rng)

def baseline_blood_moon_policy(s):
    # Buy sequential research when affordable/ready. Parasites are allowed;
    # harvesting strategy is deferred until they can actually exist.
    while buy_blood_moon_research(s):pass

# ---------- Blood Gardens ----------
def garden_available(s):return s.producer_levels[2]>=1

def garden_seed_cost(s,pid):
    p=GARDEN["plants"][pid]
    return max(p["minimum_cost"],current_eps(s)*60*p["cost_minutes"])

def garden_plant(s,slot,pid):
    if not garden_available(s) or pid not in s.garden_unlocked_seeds or s.garden_plot[slot] is not None:return False
    if pid==21:return False
    cost=garden_seed_cost(s,pid)
    if s.bank<cost:return False
    s.bank-=cost;s.garden_plot[slot]=[pid,0.0];return True

def garden_harvest(s,slot,rng,replant=True):
    tile=s.garden_plot[slot]
    if tile is None:return False
    pid,age=tile;p=GARDEN["plants"][pid];mature=age>=p["mature"]
    if mature:s.garden_unlocked_seeds.add(pid);s.garden_harvest_count+=1
    # Economically important mature harvest rewards.
    if mature:
        if pid==8:gain=min(.03*s.bank,current_eps(s)*1800)
        elif pid in (9,10):gain=min(.03*s.bank,current_eps(s)*180)
        elif pid==20:gain=min(.04*s.bank,current_eps(s)*3600)
        elif pid==22:gain=min(.08*s.bank,current_eps(s)*7200)
        else:gain=0
        if gain:s.bank+=gain;s.run_earned+=gain
        if pid==21:s.blood_dregs+=1
    s.garden_plot[slot]=None
    if replant and pid in s.garden_unlocked_seeds:garden_plant(s,slot,pid)
    return True

def garden_tick(s,rng,active=True):
    if not garden_available(s):return
    soil=GARDEN["soils"][s.garden_soil]
    for slot,tile in enumerate(list(s.garden_plot)):
        if tile is None:continue
        pid,age=tile;p=GARDEN["plants"][pid]
        # randomFloor(x): floor(x) plus Bernoulli(frac(x)).
        x=p["age_tick"]+p["age_random"]*rng.random()
        inc=math.floor(x)+(1 if rng.random()<(x-math.floor(x)) else 0)
        age+=inc
        # Immortal reference species: elderwort and everdaisy.
        if pid in (7,32):age=min(age,p["mature"]+1)
        if age>=100 and pid not in (7,32):
            # Fungus death rewards.
            if pid==23:
                gain=min(.01*s.bank,current_eps(s)*60)*rng.random();s.bank+=gain;s.run_earned+=gain
            elif pid==27:
                gain=min(.03*s.bank,current_eps(s)*300)*rng.random();s.bank+=gain;s.run_earned+=gain
            s.garden_plot[slot]=None
        else:s.garden_plot[slot]=[pid,age]
    # Baseline strategy harvests mature starter crop and replants it.
    if active:
        for slot,tile in enumerate(list(s.garden_plot)):
            if tile and tile[0]==0 and tile[1]>=GARDEN["plants"][0]["mature"]:
                garden_harvest(s,slot,rng,True)

def update_garden(s,rng,active=True):
    if not garden_available(s):return
    if s.garden_next_tick<=0:s.garden_next_tick=s.elapsed+GARDEN["soils"][s.garden_soil]["tick"]
    # Starter passive-production policy: fill affordable empty plots with starter seed.
    if active:
        for slot in range(36):
            if s.garden_plot[slot] is None and s.bank>=garden_seed_cost(s,0):garden_plant(s,slot,0)
    while s.elapsed>=s.garden_next_tick:
        garden_tick(s,rng,active)
        s.garden_next_tick+=GARDEN["soils"][s.garden_soil]["tick"]

# ---------- Chalice Exchange ----------
def exchange_available(s): return s.producer_levels[5]>=1

def init_exchange(s,rng):
    if not exchange_available(s) or s.exchange_unlocked:return
    s.exchange_unlocked=True;s.exchange_last_tick=s.elapsed
    for i in range(18):
        rest=10+10*i+(s.producer_levels[5]-1)
        s.exchange_values[i]=float(rest)
        s.exchange_velocity[i]=rng.uniform(-.1,.1)
        s.exchange_modes[i]=rng.randrange(6)
        s.exchange_mode_time[i]=rng.randrange(10,691)
    for _ in range(15):exchange_tick(s,rng,allow_trade=False)

def exchange_tick(s,rng,allow_trade=True):
    if not s.exchange_unlocked:return
    s.exchange_ticks+=1
    s.exchange_highest_raw_eps=max(s.exchange_highest_raw_eps,raw_eps(s))
    for i in range(18):
        if s.owned[min(i+1,19)]<=0:continue
        rest=10+10*i+(s.producer_levels[5]-1)
        v=s.exchange_values[i];d=s.exchange_velocity[i]
        d*=.97
        mode=s.exchange_modes[i];r=rng.random()
        if mode==0:d=d*.95+.05*(r-.5)
        elif mode==1:d=d*.99+.05*(r-.1)
        elif mode==2:d=d*.99-.05*(r-.1)
        elif mode==3:d+=.15*(r-.1);v+=rng.random()*5
        elif mode==4:d-=.15*(r-.1);v-=rng.random()*5
        else:d+=.3*(r-.5)
        v+=(rest-v)*.01
        if rng.random()<.1:d+=rng.uniform(-.3,.3)
        v=max(1,v+d)
        s.exchange_values[i]=v;s.exchange_velocity[i]=d
        s.exchange_mode_time[i]-=1
        if s.exchange_mode_time[i]<=0:
            s.exchange_modes[i]=rng.randrange(6);s.exchange_mode_time[i]=rng.randrange(10,691)
    if allow_trade:exchange_mean_reversion_policy(s)

def exchange_capacity(s,i):
    pi=min(i+1,19)
    return math.ceil(s.owned[pi]+s.producer_levels[pi]*10)

def exchange_buy_price(s,i):
    return s.exchange_highest_raw_eps*s.exchange_values[i]*(1+.20*(.95**s.exchange_brokers))

def exchange_sell_price(s,i):
    return s.exchange_highest_raw_eps*s.exchange_values[i]

def exchange_mean_reversion_policy(s):
    # Conservative policy: buy only well below resting value; sell well above.
    for i in range(18):
        pi=min(i+1,19)
        if s.owned[pi]<=0:continue
        rest=10+10*i+(s.producer_levels[5]-1)
        v=s.exchange_values[i]
        if v<=rest*.70:
            price=exchange_buy_price(s,i);cap=exchange_capacity(s,i)
            qty=min(cap-s.exchange_stock[i],int((s.bank*.10)//price) if price>0 else 0)
            if qty>0:s.bank-=qty*price;s.exchange_stock[i]+=qty;s.exchange_profit-=qty*price
        elif v>=rest*1.30 and s.exchange_stock[i]>0:
            qty=s.exchange_stock[i];gain=qty*exchange_sell_price(s,i)
            s.bank+=gain;s.run_earned+=gain;s.exchange_stock[i]=0;s.exchange_profit+=gain

def update_exchange(s,rng,active=True):
    init_exchange(s,rng)
    if not s.exchange_unlocked:return
    while s.elapsed-s.exchange_last_tick>=60:
        s.exchange_last_tick+=60
        exchange_tick(s,rng,allow_trade=active)

# ---------- Level-1 minigames: Hunter Rituals and Caryll Oaths ----------
def rituals_unlocked(s): return s.producer_levels[7]>=1
def oaths_unlocked(s): return s.producer_levels[6]>=1

def ritual_max_energy(s):
    if not rituals_unlocked(s): return 0
    T=max(s.owned[7],1); L=max(s.producer_levels[7],1)
    return math.floor(4 + T**.6 + 15*math.log((T+10*(L-1))/15+1))

def update_ritual_energy(s,seconds):
    """Advance Ritual energy without iterating 30 simulated frames per second."""
    if not rituals_unlocked(s): return
    m=ritual_max_energy(s)
    if not s.ritual_initialized:
        s.ritual_energy=float(m); s.ritual_initialized=True; return
    frames=max(0,int(seconds*30))
    if frames<=0 or s.ritual_energy>=m:return

    D=max(m,100)
    e=max(0.0,s.ritual_energy)

    # Source equation:
    #   dE/frame = .002 * max(.002, sqrt(E/D))
    # The floor branch is linear until E reaches 4e-6*D.
    threshold=4e-6*D
    if e<threshold:
        per_frame=.000004
        frames_to_threshold=max(0,math.ceil((threshold-e)/per_frame))
        used=min(frames,frames_to_threshold)
        e+=used*per_frame
        frames-=used

    # Above the floor, integrate dE/dn=.002*sqrt(E/D):
    # sqrt(E_new)=sqrt(E_old)+.001*n/sqrt(D)
    if frames>0 and e<m:
        root=math.sqrt(max(e,0.0))+.001*frames/math.sqrt(D)
        e=root*root
    s.ritual_energy=min(float(m),e)

def ritual_cost(s,r):
    m=ritual_max_energy(s)
    a,b=((2,.40),(10,.60),(8,.20),(20,.75),(10,.10),(10,.20),(3,.05),(20,.10),(5,.20))[r]
    return math.floor(a+m*b)

def resolve_forced_omen(s,rng,choice):
    before=s.bank
    if choice=="frenzy": _add_buff(s,"production",7,77,"frenzy")
    elif choice=="clot": _add_buff(s,"production",.5,66,"clot")
    elif choice=="windfall":
        gain=min(.15*s.bank,current_eps(s)*900)+13;s.bank+=gain;s.run_earned+=gain
    elif choice=="ruin":
        loss=min(s.bank,min(.05*s.bank,current_eps(s)*600)+13);s.bank-=loss
    s.omen_log.append((s.elapsed,"forced:"+choice,s.bank-before))

def cast_ritual(s,r,rng):
    if not rituals_unlocked(s):return False
    c=ritual_cost(s,r)
    if s.ritual_energy<c:return False
    if r==2 and not (s.prod_buffs or s.click_buffs):return False
    if r==7:return False # waits for parasite layer
    s.ritual_energy-=c;s.ritual_casts+=1
    fail=rng.random()<.15
    if fail:s.ritual_backfires+=1
    else:s.ritual_successes+=1
    if r==0:
        if not fail:
            gain=max(7,min(.15*s.bank,1800*current_eps(s)));s.bank+=gain;s.run_earned+=gain
        else:
            _add_buff(s,"production",.5,900,"ritual_backfire")
            s.bank-=min(s.bank,min(.15*s.bank,900*current_eps(s))+13)
    elif r==1:
        resolve_forced_omen(s,rng,rng.choice(["clot","windfall","ruin"] if fail else ["frenzy","windfall"]))
    elif r==2:
        for b in s.prod_buffs+s.click_buffs:
            remain=max(0,b[0]-s.elapsed)
            b[0]+=min(300,remain*.10) if not fail else -min(600,remain*.20)
    elif r==3:
        owned=[i for i,n in enumerate(s.owned) if n>0]
        if fail:
            if owned:s.owned[rng.choice(owned)]-=1
        else:
            candidates=[i for i in range(20) if s.owned[i]<400 and next_cost(s,i)<=2*s.bank]
            if candidates:
                # A no-cost Ritual grant still advances normal price scaling.
                i=rng.choice(candidates);s.owned[i]+=1
    grant_achievements(s);return True

def update_oath_swaps(s):
    if not oaths_unlocked(s):return
    while s.oath_swaps<3:
        need=(57600,14400,3600)[s.oath_swaps]
        if s.elapsed-s.oath_last_recharge<need:break
        s.oath_last_recharge+=need;s.oath_swaps+=1

def set_oath(s,slot,oath):
    if not oaths_unlocked(s) or not 0<=slot<3 or not -1<=oath<11:return False
    if oath>=0 and oath in s.oath_slots:return False
    if s.oath_slots[slot]==oath:return True
    update_oath_swaps(s)
    if s.oath_swaps<=0:return False
    s.oath_slots[slot]=oath;s.oath_swaps-=1;s.oath_last_recharge=s.elapsed;return True

def baseline_minigame_policy(s,rng,active=True):
    if oaths_unlocked(s) and s.oath_slots[0]<0:set_oath(s,0,0)
    if active and rituals_unlocked(s):
        m=ritual_max_energy(s)
        if s.ritual_energy>=max(ritual_cost(s,0),m*.95):cast_ritual(s,0,rng)

# ---------- Blood Dreg / producer-level core ----------
def lifetime_earned(s):
    return s.previous_runs_earned+s.run_earned

def update_dreg_unlock(s):
    if s.dreg_unlocked_at<0 and lifetime_earned(s)>=1e9:
        s.dreg_unlocked_at=s.elapsed
        s.dreg_cycle_started=s.elapsed

def process_dreg_auto(s):
    update_dreg_unlock(s)
    if s.dreg_cycle_started<0:return
    while s.elapsed-s.dreg_cycle_started>=86400:
        s.blood_dregs+=1;s.dregs_harvested+=1
        s.dreg_cycle_started+=86400

def harvest_dreg_if_ready(s,rng,allow_mature_risk=False):
    update_dreg_unlock(s)
    if s.dreg_cycle_started<0:return False
    age=s.elapsed-s.dreg_cycle_started
    success=False
    if age>=82800:success=True
    elif allow_mature_risk and age>=72000:success=(rng.random()<.5)
    if success:
        s.blood_dregs+=1;s.dregs_harvested+=1;s.dreg_cycle_started=s.elapsed
    return success

def level_cost(s,i):return s.producer_levels[i]+1

def buy_best_level(s):
    # Greedy marginal raw-EPS per Blood Dreg. Levels persist across Reawakening.
    best=None
    for i in range(20):
        c=level_cost(s,i)
        if c>s.blood_dregs or s.owned[i]<=0:continue
        before=raw_eps(s);s.producer_levels[i]+=1;after=raw_eps(s);s.producer_levels[i]-=1
        score=(after-before)/c
        if best is None or score>best[0]:best=(score,i,c)
    if best is None:return False
    _,i,c=best;s.blood_dregs-=c;s.producer_levels[i]+=1
    s.purchase_log.append((s.elapsed,"producer_level",i,s.producer_levels[i],c))
    return True

# ---------- Reawakening ----------
ASCENSION_COSTS={"U363":1,"U395":3,"U264":100,"U323":9,"U282":77,"U281":1,"U274":7,"U275":49,"U353":7,"U354":49,"U253":25,"U254":25,"U181":1111}

def buy_ascension_upgrade(s,uid):
    c=ASCENSION_COSTS.get(uid)
    if c is None or uid in s.ascension_upgrades or s.dream_fragments<c:return False
    req={"U395":"U363","U264":"U395","U323":"U395","U282":"U363","U281":"U363","U274":"U395","U275":"U274","U353":"U395","U354":"U353","U253":"U395","U254":"U253","U181":"U395"}
    if uid in req and req[uid] not in s.ascension_upgrades:return False
    s.dream_fragments-=c;s.ascension_upgrades.add(uid);return True

def reawaken(s):
    gain=new_fragments(s)
    if gain<=0:return 0
    target=target_prestige(s);s.previous_runs_earned+=s.run_earned;s.claimed_prestige=target;s.dream_fragments+=gain;s.total_reawakenings+=1
    s.bank=0.0;s.run_earned=0.0;s.owned=[0]*20;s.free=[0]*20;s.standard_tiers=set();s.messenger_doublings=0;s.messenger_additive_stage=-1
    s.mouse_upgrades=0;s.insight_amplifiers=0;s.global_relics=set();s.prestige_purchases=0;s.prestige_effectiveness=0.0;s.handmade_echoes=0.0;s.clicks=0
    s.prod_buffs=[];s.click_buffs=[];s.omen_last="";s.omen_next=0.0;s.blood_moon_research_step=-1;s.blood_moon_research_ready_at=-1.0;s.blood_moon_stage=0;s.blood_moon_target_stage=0;s.pledge_count=0;s.pledge_until=0;s.permanent_suppression=False;s.parasites=[]
    s.ritual_energy=0;s.ritual_initialized=False;s.ritual_casts=0;s.oath_slots=[-1,-1,-1];s.oath_swaps=3;s.oath_last_recharge=s.elapsed
    s.exchange_unlocked=False;s.exchange_ticks=0;s.exchange_last_tick=s.elapsed;s.exchange_values=[0.0]*18;s.exchange_velocity=[0.0]*18;s.exchange_modes=[0]*18;s.exchange_mode_time=[0]*18;s.exchange_stock=[0]*18;s.exchange_profit=0;s.exchange_highest_raw_eps=0
    s.garden_plot=[None]*36;s.garden_soil=0;s.garden_next_tick=0;s.calendar_state=-1;s.calendar_switches=0;s.calendar_until=0
    return gain

def baseline_ascension_spend(s):
    for uid in ("U363","U395","U281","U323","U264","U282","U274","U275","U353","U354","U253","U254","U181"):buy_ascension_upgrade(s,uid)

# ---------- Natural Omen engine ----------
# Reference natural timer is a frame hazard from 300s to 900s:
# hazard(t)=((t-300)/600)^5.  Build its discrete 30 FPS CDF once.
_OMEN_TIMES=[]
_OMEN_CDF=[]
_survive=1.0
for _frame in range(300*30,900*30+1):
    _t=_frame/30.0
    _h=max(0.0,(_t-300.0)/600.0)**5
    _p=_survive*_h
    if _p>0:
        _OMEN_TIMES.append(_t);_OMEN_CDF.append((_OMEN_CDF[-1] if _OMEN_CDF else 0.0)+_p)
    _survive*=1-_h
    if _survive<1e-15:break
if _OMEN_CDF:
    _z=_OMEN_CDF[-1]
    _OMEN_CDF=[x/_z for x in _OMEN_CDF]

def sample_omen_wait(rng):
    u=rng.random();i=bisect.bisect_left(_OMEN_CDF,u)
    return _OMEN_TIMES[min(i,len(_OMEN_TIMES)-1)]

def expire_buffs(s):
    s.prod_buffs=[b for b in s.prod_buffs if b[0]>s.elapsed]
    s.click_buffs=[b for b in s.click_buffs if b[0]>s.elapsed]

def _add_buff(s,channel,factor,duration,label):
    arr=s.prod_buffs if channel=="production" else s.click_buffs
    # Same common buff extends duration rather than multiplying itself.
    for b in arr:
        if b[2]==label:
            b[0]+=duration
            return
    arr.append([s.elapsed+duration,factor,label])

def choose_omen(s,rng):
    # Stage-0 favorable natural Omen pool from pinned 2.058 source.
    choices=["frenzy","windfall"]
    if s.run_earned>=100000 and rng.random()<0.03:
        choices.extend(["chain","storm"])
    if rng.random()<0.10:
        choices.append("click_frenzy")
    if sum(s.owned)>=10 and rng.random()<0.25:
        choices.append("building")
    if s.omen_last and rng.random()<0.80 and s.omen_last in choices:
        choices=[x for x in choices if x!=s.omen_last]
    if rng.random()<0.0001:
        choices.append("blab")
    return rng.choice(choices)

def break_ascetic_on_natural_omen(s):
    """Unslot Ascetic and restart swap recharge on a natural Omen."""
    if 0 not in s.oath_slots:return False
    s.oath_slots=[-1 if oath==0 else oath for oath in s.oath_slots]
    s.oath_swaps=0
    s.oath_last_recharge=s.elapsed
    return True


def resolve_omen(s,rng):
    break_ascetic_on_natural_omen(s)
    choice=choose_omen(s,rng);s.omen_last=choice;s.omen_clicks+=1
    before=s.bank
    if choice=="frenzy":
        _add_buff(s,"production",7.0,77.0,"frenzy")
    elif choice=="windfall":
        gain=min(.15*s.bank,current_eps(s)*900.0)+13.0
        s.bank+=gain;s.run_earned+=gain
    elif choice=="click_frenzy":
        _add_buff(s,"click",777.0,13.0,"click_frenzy")
    elif choice=="building":
        eligible=[i for i,n in enumerate(s.owned) if n>=10]
        if eligible:
            i=rng.choice(eligible);_add_buff(s,"production",1+s.owned[i]/10.0,30.0,f"building:{i}")
        else:_add_buff(s,"production",7.0,77.0,"frenzy")
    elif choice=="chain":
        # Reference-adapted chain payout state machine. Natural first link uses
        # the favorable digit (7). This compact implementation resolves the
        # chain immediately because link screen-time is negligible relative
        # to the progression checkpoints, while preserving payout arithmetic.
        digit=7
        bank=max(s.bank,1.0)
        depth=max(0,math.ceil(math.log10(bank))-10)
        max_payout=min(current_eps(s)*21600.0,s.bank*.5)
        total=0.0
        while True:
            payout=max(digit,min(math.floor((digit/9.0)*(10**depth)),max_payout))
            if payout<=0:break
            total+=payout;depth+=1
            if rng.random()<.01 or payout>=max_payout:break
        s.bank+=total;s.run_earned+=total
    elif choice=="storm":
        # Seven-second storm. Approximate the many tiny clickable drops with
        # the exact per-click payout form and a conservative 50% catch policy.
        # This is explicitly a policy assumption, not source parity.
        drops=round(7*30*.5*.5)
        total=sum(max(current_eps(s)*60*rng.randint(1,7),rng.randint(1,7)) for _ in range(drops))
        s.bank+=total;s.run_earned+=total
    # blab intentionally pays nothing.
    s.omen_log.append((s.elapsed,choice,s.bank-before))
    grant_achievements(s)

def init_omens(s,rng):
    s.omen_next=s.elapsed+sample_omen_wait(rng)

def process_omens(s,rng):
    while s.elapsed>=s.omen_next:
        resolve_omen(s,rng)
        s.omen_next+=sample_omen_wait(rng)

def simulate(seconds,cps=4.0,step=5.0,checkpoints=(300,1800,3600,14400),seed=1,omens=True):
    s=State();out=[];next_cp=0;rng=random.Random(seed)
    if omens:init_omens(s,rng)
    checkpoints=sorted(x for x in checkpoints if x<=seconds)
    while s.elapsed<seconds-1e-9:
        dt=min(step,seconds-s.elapsed)
        # Passive production for the interval.
        earn_passive(s,dt)
        # Deterministic fractional-click accumulator.
        target_clicks=int((s.elapsed+dt)*cps)-int(s.elapsed*cps)
        if target_clicks>0:click(s,target_clicks)
        s.elapsed+=dt;expire_buffs(s);update_calendar(s);update_blood_moon(s,dt,rng);update_ritual_energy(s,dt);update_oath_swaps(s);update_garden(s,rng,active=cps>0);update_exchange(s,rng,active=cps>0)
        baseline_blood_moon_policy(s)
        if omens:process_omens(s,rng)
        baseline_minigame_policy(s,rng,active=cps>0);grant_achievements(s)
        while greedy_step(s,cps):pass
        while next_cp<len(checkpoints) and s.elapsed>=checkpoints[next_cp]-1e-9:
            out.append(snapshot(s,checkpoints[next_cp],cps));next_cp+=1
    return s,out

def snapshot(s,t,cps):
    return {"seconds":t,"bank":s.bank,"earned":s.run_earned,"raw_eps":raw_eps(s),"click_value":click_value(s),
            "income_rate":income_rate(s,cps),"achievements":len(s.achievements),"insight":insight(s),
            "upgrades":upgrade_count(s),"relics":len(s.global_relics),"buildings":sum(s.owned),"highest_producer":max((i for i,n in enumerate(s.owned) if n),default=-1),
            "prestige_if_reset":target_prestige(s),"omens":s.omen_clicks,"omen_log":list(s.omen_log)}
