"""Playable-core actions backed by the restored simulator."""
import random
import time
from pathlib import Path
import simulator as sim
from alpha import saves

NAMES=('Whisperers','Lantern Keepers','Crimson Orchards','Grave Delvers','Night Forges',
       'Echo Vaults','Silent Choirs','Star Observatories','Relic Caravans','Ichor Foundries',
       'Dusk Portals','Dream Wheels','Hollow Crucibles','Lumen Groves','Omen Spires',
       'Endless Vigils','Rune Archives','Dream Confluences','Ancient Memories','Awakened Selves')
PERMANENT={
    'U363':('First memory','Unlock resonance upgrades in each new run.',None),
    'U281':('Sleeping vigil','Earn 5% offline for an hour, then 0.5%.','U363'),
    'U395':('Deep memory','Unlock stronger offline paths.','U363'),
    'U274':('Long vigil I','Add 10 percentage points to offline production.','U395'),
    'U275':('Long vigil II','Add another 10 percentage points.','U274'),
    'U353':('Enduring dream I','Double the full-efficiency offline window.','U395'),
    'U354':('Enduring dream II','Double that window again.','U353'),
}

# Alpha onboarding accelerator. It affects only the first useful two-fragment
# bundle; later fragments continue on the recovered 1e12 cubic prestige curve.
STARTER_PRESTIGE_SCALE=23_000_000
STARTER_PRESTIGE_CAP=2


def alpha_target_prestige(state):
    starter=min(STARTER_PRESTIGE_CAP,sim.target_prestige(state,STARTER_PRESTIGE_SCALE))
    return max(sim.target_prestige(state),starter)


def alpha_new_fragments(state):
    return max(0,alpha_target_prestige(state)-state.claimed_prestige)


def alpha_next_fragment_threshold(state):
    next_level=alpha_target_prestige(state)+1
    scale=STARTER_PRESTIGE_SCALE if next_level<=STARTER_PRESTIGE_CAP else int(sim.DATA['prestige']['scale'])
    return scale*next_level**int(sim.DATA['prestige']['exponent'])


class Game:
    def __init__(self,path,rng=None,clock=time.monotonic,wall=time.time):
        self.path=Path(path);self.rng=rng or random.Random();self.clock=clock;self.wall=wall
        self.notice='Tap the vessel. Gather echoes. Hire your first Whisperer.'
        if self.path.exists():
            self.state,gain,away=saves.read(self.path,self.wall())
            self.notice=f'Welcome back. {away:.0f} seconds away; {gain:.3g} echoes earned offline.'
        else:self.state=sim.State()
        self.last_tick=self.clock();self.last_saved=self.last_tick
        self.omen_until=0.0
        sim.init_omens(self.state,self.rng)
        self.save()

    def save(self):
        # Keep runtime logs bounded; they are not part of save schema v1.
        self.state.purchase_log=self.state.purchase_log[-100:]
        self.state.omen_log=self.state.omen_log[-100:]
        saves.write(self.path,self.state,self.wall());self.last_saved=self.clock()

    def advance(self):
        now=self.clock();dt=max(0,now-self.last_tick);self.last_tick=now
        s=self.state
        if dt>10:
            gain=sim.apply_closed_time(s,dt)
            sim.expire_buffs(s);sim.init_omens(s,self.rng);self.omen_until=0
            if gain:self.notice=f'While away, your vigil earned {gain:.3g} echoes.'
        else:
            end=s.elapsed+dt
            while s.elapsed<end:
                boundaries=[b[0] for b in s.prod_buffs+s.click_buffs if s.elapsed<b[0]<end]
                stop=min(boundaries,default=end)
                sim.earn_passive(s,stop-s.elapsed);s.elapsed=stop;sim.expire_buffs(s)
            if self.omen_until and s.elapsed>=self.omen_until:
                self.omen_until=0;sim.init_omens(s,self.rng)
            if not self.omen_until and s.elapsed>=s.omen_next:self.omen_until=s.elapsed+30
        sim.grant_achievements(s)
        if now-self.last_saved>=10:self.save()

    def upgrades(self):
        s=self.state;out=[]
        def add(key,name,cost,kind,args=()):
            out.append({'id':key,'name':name,'cost':cost,'kind':kind,'args':args,'affordable':s.bank>=cost})
        for kind,stage,cost in sim.messenger_upgrade_options(s):
            add(f'{kind}:{stage}','Whispering chorus' if kind=='messenger_double' else 'Shared whispers',cost,kind,(stage,))
        for i in range(1,20):
            for t in range(15):
                if f'{i}:{t}' not in s.standard_tiers and sim.tier_unlocked(s,i,t):
                    add(f'tier:{i}:{t}',f'{NAMES[i]} · tier {t+1}',sim.tier_cost(i,t),'tier',(i,t))
                    break
        j=s.mouse_upgrades
        if sim.mouse_unlocked(s,j):add('mouse','Blood pulse · +1% production per tap',sim.DATA['clicking']['mouse_upgrade_costs'][j],'mouse')
        j=s.insight_amplifiers
        if sim.insight_amp_unlocked(s,j):add('insight','Eyes within · amplify Insight',sim.DATA['insight_amplifiers']['costs'][j],'insight')
        j=s.prestige_purchases
        if sim.prestige_purchase_unlocked(s,j):add('prestige',f'Memory resonance {j+1}',sim.DATA['prestige_effectiveness_purchases'][j]['cost'],'prestige')
        for n,r in enumerate(sim.DATA['global_relics']):
            if r['id'] not in s.global_relics and sim.relic_unlocked(s,r):
                add('relic:'+r['id'],f'Blood seal {n+1} · +{r["bonus_percent"]}% production',r['cost'],'relic',(r['id'],))
        return sorted(out,key=lambda item:item['cost'])

    def action(self,body):
        if not isinstance(body,dict):raise ValueError('Expected an action object')
        kind=body.get('action');s=self.state;changed=False
        if kind=='click':
            sim.click(s,rng=self.rng);changed=True
        elif kind=='buy':
            i=body.get('producer');quantity=body.get('quantity',1)
            if type(i) is not int or not 0<=i<20 or type(quantity) is not int or quantity not in (1,10,100):raise ValueError('Invalid producer purchase')
            if s.owned[i]+quantity>1000:raise ValueError('Alpha ownership limit: 1,000 per producer')
            changed=sim.buy_producer(s,i,quantity)
        elif kind=='upgrade':
            option=next((u for u in self.upgrades() if u['id']==body.get('id')),None)
            if option:
                k=option['kind'];args=option['args']
                if k=='tier':changed=sim.buy_tier(s,*args)
                elif k.startswith('messenger_'):changed=sim.buy_messenger_upgrade(s,k,args[0],option['cost'])
                elif k=='mouse':changed=sim.buy_mouse(s)
                elif k=='insight':changed=sim.buy_insight_amp(s)
                elif k=='prestige':changed=sim.buy_prestige_purchase(s)
                elif k=='relic':changed=sim.buy_relic(s,sim.RELIC_BY_ID[args[0]])
        elif kind=='omen':
            if not self.omen_until or s.elapsed>=self.omen_until:raise ValueError('This Omen has faded')
            sim.resolve_omen(s,self.rng);self.notice='Omen: '+s.omen_last.replace('_',' ')
            self.omen_until=0;sim.init_omens(s,self.rng);changed=True
        elif kind=='reawaken':
            if body.get('confirmation')!='REAWAKEN':raise ValueError('Reawakening requires confirmation')
            gain=sim.reawaken(s,alpha_target_prestige(s))
            if gain:
                self.omen_until=0;sim.init_omens(s,self.rng)
                self.notice=f'Reawakened with {gain} new fragments. Choose your memories below.';changed=True
        elif kind=='ascension':
            uid=body.get('id')
            if not isinstance(uid,str) or uid not in PERMANENT:raise ValueError('Unknown core memory')
            changed=sim.buy_ascension_upgrade(s,uid)
        elif kind=='save':self.save();self.notice='Progress saved.';changed=True
        elif kind=='reset':
            if body.get('confirmation')!='RESET':raise ValueError('Type RESET to erase this run and all memories')
            self.save();self.state=sim.State();sim.init_omens(self.state,self.rng)
            self.omen_until=0;self.notice='A new vigil begins.';self.save();changed=True
        elif kind=='import':
            text=body.get('save')
            if not isinstance(text,str):raise ValueError('Choose a JSON save file')
            candidate,saved_at=saves.decode(text)
            away=max(0,min(self.wall()-saved_at,1e10-candidate.elapsed))
            sim.apply_closed_time(candidate,away);sim.expire_buffs(candidate)
            sim.init_omens(candidate,self.rng)
            saves.encode(candidate,self.wall())
            self.save();saves.write(self.path,candidate,self.wall())
            self.state=candidate;self.omen_until=0;self.notice='Save imported.';changed=True
        else:raise ValueError('Unknown action')
        if not changed:raise ValueError('Not yet unlocked or not enough echoes')
        if kind in ('buy','upgrade','reawaken','ascension'):self.save()
        return self.snapshot()

    def snapshot(self):
        s=self.state;efficiency,cap=sim.offline_settings(s)
        producers=[]
        for i in range(20):
            costs={str(q):sim.exact_bulk_cost(s,i,q) for q in (1,10,100)}
            producers.append({'id':i,'name':NAMES[i],'owned':s.owned[i],'costs':costs,
                              'production':sim.producer_eps(s,i)})
        memories=[]
        for uid,(name,description,req) in PERMANENT.items():
            memories.append({'id':uid,'name':name,'description':description,'cost':sim.ASCENSION_COSTS[uid],
                             'owned':uid in s.ascension_upgrades,'unlocked':req is None or req in s.ascension_upgrades})
        return {'bank':s.bank,'earned':s.run_earned,'eps':sim.current_eps(s),'click':sim.click_value(s),
                'achievements':len(s.achievements),'insight':sim.insight(s),'owned':sum(s.owned),
                'fragments':s.dream_fragments,'prestige':s.claimed_prestige,'new_fragments':alpha_new_fragments(s),
                'next_fragment_at':alpha_next_fragment_threshold(s),
                'offline_efficiency':efficiency,'offline_cap':cap,'producers':producers,'upgrades':self.upgrades(),
                'memories':memories,'notice':self.notice,'omen_seconds':max(0,self.omen_until-s.elapsed),
                'buffs':[{'name':b[2].replace('_',' '),'factor':b[1],'seconds':max(0,b[0]-s.elapsed)} for b in s.prod_buffs+s.click_buffs],
                'saved_seconds_ago':max(0,self.clock()-self.last_saved)}
