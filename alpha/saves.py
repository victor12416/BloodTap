"""Versioned, validated JSON saves for the playable core (no pickle/code)."""
from pathlib import Path
import json
import math
import os
import time
import simulator as sim

VERSION=1
MAX_BYTES=1_000_000
NUMBERS={'bank':1e280,'run_earned':1e280,'previous_runs_earned':1e280,
         'handmade_echoes':1e280,'elapsed':1e10,'omen_next':1e10}
COUNTS={'claimed_prestige':10**100,'dream_fragments':10**100,'clicks':10**15,
        'total_reawakenings':10**9,'omen_clicks':10**12,'messenger_doublings':3,
        'messenger_additive_stage':11,'mouse_upgrades':15,'insight_amplifiers':15,
        'prestige_purchases':len(sim.DATA['prestige_effectiveness_purchases'])}
SETS=('standard_tiers','global_relics','achievements','ascension_upgrades')
FIELDS=set(NUMBERS)|set(COUNTS)|set(SETS)|{'owned','highest_owned','prod_buffs','click_buffs'}
ASCENSION=set(sim.ASCENSION_COSTS)-{'U181'}


def number(value,maximum,minimum=0):
    if type(value) not in (float,int) or not math.isfinite(value) or not minimum<=value<=maximum:
        raise ValueError('Save contains an invalid number')
    return value


def document(state,now=None):
    data={key:getattr(state,key) for key in FIELDS}
    for key in SETS:data[key]=sorted(data[key])
    return {'format':'bloodtap-core','version':VERSION,'saved_at':time.time() if now is None else now,'state':data}


def encode(state,now=None):
    value=document(state,now)
    decode(json.dumps(value,allow_nan=False))  # Validate before replacing a good save.
    return json.dumps(value,allow_nan=False,indent=2)+'\n'


def decode(text):
    if len(text.encode('utf-8'))>MAX_BYTES:raise ValueError('Save exceeds 1 MB')
    try:doc=json.loads(text)
    except (ValueError,RecursionError) as exc:raise ValueError('Invalid JSON save') from exc
    if not isinstance(doc,dict) or doc.get('format')!='bloodtap-core':raise ValueError('Not a BloodTap core save')
    version=doc.get('version')
    if type(version) is not int or version!=VERSION:raise ValueError('Unsupported save version; original file has not been changed')
    saved_at=number(doc.get('saved_at'),1e11)
    data=doc.get('state')
    if not isinstance(data,dict) or set(data)!=FIELDS:raise ValueError('Save fields do not match schema version 1')
    state=sim.State()
    for key,maximum in NUMBERS.items():setattr(state,key,number(data[key],maximum))
    for key,maximum in COUNTS.items():
        value=data[key]
        if type(value) is not int:raise ValueError('Save count must be an integer')
        setattr(state,key,number(value,maximum,-1 if key=='messenger_additive_stage' else 0))
    for key in ('owned','highest_owned'):
        value=data[key]
        if not isinstance(value,list) or len(value)!=20:raise ValueError('Expected 20 producer counts')
        if any(type(n) is not int or not 0<=n<=1000 for n in value):raise ValueError('Producer count out of alpha range')
        setattr(state,key,list(value))
    if any(h<n for h,n in zip(state.highest_owned,state.owned)):raise ValueError('Highest ownership is below current ownership')
    for key in SETS:
        value=data[key]
        if not isinstance(value,list) or len(value)>10000 or any(not isinstance(x,str) or len(x)>80 for x in value):
            raise ValueError('Invalid saved collection')
        setattr(state,key,set(value))
    allowed_tiers={f'{i}:{t}' for i in range(1,20) for t in range(15)}
    if not state.standard_tiers<=allowed_tiers:raise ValueError('Unknown producer tier')
    if not state.global_relics<=sim.RELIC_BY_ID.keys():raise ValueError('Unknown relic')
    if not state.ascension_upgrades<=ASCENSION:raise ValueError('Unsupported alpha ascension upgrade')
    for key in ('prod_buffs','click_buffs'):
        buffs=data[key]
        if not isinstance(buffs,list) or len(buffs)>30:raise ValueError('Invalid buffs')
        result=[]
        for b in buffs:
            if not isinstance(b,list) or len(b)!=3 or not isinstance(b[2],str) or len(b[2])>80:raise ValueError('Invalid buff')
            result.append([number(b[0],state.elapsed+86400),number(b[1],1000,.001),b[2]])
        setattr(state,key,result)
    if state.prestige_purchases:
        state.prestige_effectiveness=sim.DATA['prestige_effectiveness_purchases'][state.prestige_purchases-1]['effectiveness']
    if state.prestige_purchases and 'U363' not in state.ascension_upgrades:raise ValueError('Prestige purchases require U363')
    # Derived factors are never accepted directly from the file.
    if not math.isfinite(sim.current_eps(state)+sim.click_value(state)):raise ValueError('Save produces invalid income')
    return state,saved_at


def write(path,state,now=None):
    path=Path(path)
    text=encode(state,now)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix('.tmp')
    with temporary.open('w',encoding='utf-8',newline='\n') as stream:
        stream.write(text);stream.flush();os.fsync(stream.fileno())
    if path.exists():
        previous=path.read_text(encoding='utf-8')
        decode(previous)
        backup=path.with_suffix('.bak')
        backup_tmp=path.with_suffix('.bak.tmp')
        backup_tmp.write_text(previous,encoding='utf-8')
        os.replace(backup_tmp,backup)
    os.replace(temporary,path)


def read(path,now=None):
    path=Path(path)
    if path.stat().st_size>MAX_BYTES:raise ValueError('Save exceeds 1 MB')
    state,saved_at=decode(path.read_text(encoding='utf-8'))
    now=time.time() if now is None else now
    away=max(0,min(now-saved_at,1e10-state.elapsed))
    reward=sim.apply_closed_time(state,away)
    sim.expire_buffs(state)
    state.omen_next=0 # Closed time never collects natural Omens.
    sim.grant_achievements(state)
    return state,reward,away
