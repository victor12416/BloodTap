'use strict';
const $=id=>document.getElementById(id);
const SAVE_KEY='bloodtap-web-alpha-v1', STARTER_SCALE=23000000, STARTER_CAP=2, GROWTH=1.15;
const NAMES=['Messengers','Huntsmen','Blood Ministers','Hunter Workshops','Church Hunters','Tomb Prospectors','Byrgenwerth Scholars','Labyrinth Expeditions','Blood Saints','Research Hall Patients','Choir Scholars','Mensis Scholars','Ritualists','Nightmare Seekers','Kin of the Cosmos','Great One Communion','Nightmare Convergences','Eldritch Revelations','Great One Memories','Transcendent Selves'];
const REVEAL_AT=[0,0,0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,7,8,9];
const VEILED_NAMES=['Messengers','Huntsmen','Blood Ministers','Hunter Workshops','Church Hunters','Tomb Prospectors','Forbidden Scholars','Old Labyrinth Expeditions','Consecrated Vessels','Research Subjects','Upper Scholars','Hidden Scholars','Ritualists','Dream Seekers','Altered Kin','Unknown Communion','Converging Dreams','Forbidden Revelations','Ancient Memories','Something Beyond'];
const PRODUCER_LORE=[
'Pale attendants of the dream who gather what the Hunt leaves behind.',
'Common hunters scour the streets, returning with echoes taken from beasts and the mad.',
'Ministers administer sacred blood, drawing wealth and influence toward the growing blood ministry.',
'Craftsmen arm the Hunt with specialized weapons and tools, turning the beast scourge into an organized trade.',
'Church-sanctioned hunters contain outbreaks and protect the institution built around blood healing.',
'Chosen explorers descend into ancient tombs beneath the city and return with blood, relics, and dangerous knowledge.',
'Scholars pursue forbidden knowledge, convinced that humanity must elevate its mind to approach higher beings.',
'Expeditions push deeper into the old labyrinth, where ancient civilizations and eldritch traces predate the city above.',
'Cultivated vessels provide unusually potent blood, strengthening the authority and mysteries of the Church.',
'Human subjects endure experiments meant to cultivate inner eyes and force contact with something beyond mankind.',
'The Church’s highest scholars study the cosmos and seek audience with beings beyond ordinary human understanding.',
'Hidden scholars abandon restraint for ritual, attempting to beckon a higher presence through nightmare and sacrifice.',
'Forbidden rites turn accumulated blood and knowledge into attempts at direct contact with the eldritch truth.',
'Seekers deliberately enter nightmares, bringing back echoes and knowledge that should not exist in the waking world.',
'Humanity begins to give way to something else: beings altered by sustained contact with the cosmos.',
'Ritual and revelation now produce direct communion with beings whose existence once seemed impossible.',
'Separate nightmares begin to overlap, allowing the Hunt to draw power from realities beyond the waking world.',
'Knowledge itself becomes productive; each revelation exposes deeper laws governing blood, dreams, and the cosmos.',
'Fragments of beings beyond humanity persist through dreams and memory, feeding the Hunt across repeated cycles.',
'The final pursuit is no longer the Hunt. Humanity is being left behind in the attempt to become something greater.'
];
const VEILED_LORE=[
'Pale attendants gather what the Hunt leaves behind.',
'Hunters scour the streets and return with echoes taken from beasts and the mad.',
'Ministers administer sacred blood, drawing wealth and influence toward the blood ministry.',
'Craftsmen arm the Hunt with specialized weapons and tools.',
'Church-sanctioned hunters contain outbreaks and protect the blood ministry.',
'Explorers descend into old tombs beneath the city and return with blood and relics.',
'Their studies are forbidden to ordinary hunters. What they seek is not yet clear.',
'Expeditions descend below even the oldest tombs. Their reports are deliberately incomplete.',
'The Church guards these vessels closely and says little of their purpose.',
'Human subjects are changed in pursuit of a result the Church refuses to name.',
'These scholars study something above the city, but their work is kept from the Hunt.',
'Their rituals are hidden even from most of the Church.',
'Forbidden rites consume blood and knowledge for an unknown purpose.',
'Some hunters claim there are places reached only through sleep.',
'They were human once. Beyond that, the records become unreliable.',
'Something answers the rites. You cannot yet perceive what.',
'Separate dreams appear to touch one another in ways that should be impossible.',
'The truth is present, but your mind cannot yet hold its shape.',
'Something persists between dreams. Its origin remains beyond perception.',
'You can sense an ending beyond the Hunt, but cannot yet understand it.'
];
function visibleName(i){return insight()>=REVEAL_AT[i]?NAMES[i]:VEILED_NAMES[i];}
function visibleLore(i){return insight()>=REVEAL_AT[i]?PRODUCER_LORE[i]:VEILED_LORE[i];}
const HUNT_PHASES=[
{from:0,to:2,name:'The Hunt',detail:'Hunters, Messengers, and blood ministration define the night.'},
{from:3,to:5,name:'The Healing Church',detail:'The Hunt becomes organized while old tombs begin to yield dangerous relics.'},
{from:6,to:9,name:'Forbidden Inquiry',detail:'Scholarship and experimentation push beyond the accepted purpose of the Hunt.'},
{from:10,to:12,name:'Hidden Ritual',detail:'The highest scholars abandon restraint and turn knowledge into ritual.'},
{from:13,to:16,name:'The Nightmare',detail:'Dream and waking reality no longer remain cleanly separated.'},
{from:17,to:19,name:'Revelation',detail:'The Hunt gives way to truths no ordinary human was meant to perceive.'}
];
function huntPhase(){let highest=0;for(let i=0;i<state.owned.length;i++)if(state.owned[i]>0)highest=i;return HUNT_PHASES.find(p=>highest>=p.from&&highest<=p.to)||HUNT_PHASES[0];}
const TIER_NAMES=['Tempered Practice','Blood-Honed Methods','Church Sanction','Workshop Refinement','Forbidden Technique','Old Blood Infusion','Runic Inscription','Labyrinth Relic','Moonlit Revelation','Eldritch Method','Nightmare Practice','Ritual Communion','Cosmic Revelation','Formless Understanding','Transcendent Mastery'];
const TIER_LORE=[
'Hard-earned practice makes this work twice as effective.',
'Methods refined through blood and repeated Hunts double its yield.',
'Institutional knowledge and sanctioned methods double its effectiveness.',
'Specialized tools and disciplined craft double its production.',
'Knowledge once withheld from ordinary hunters doubles its power.',
'Old blood is deliberately worked into the process, doubling its yield.',
'Runes derived from inhuman knowledge double what this work can produce.',
'Relics recovered from the old labyrinth double its effectiveness.',
'Knowledge revealed beneath the moon doubles its production.',
'Methods shaped by contact with the eldritch truth double its yield.',
'Practices learned beyond the waking world double its production.',
'Ritual contact with higher beings doubles its effectiveness.',
'Cosmic understanding transforms the work and doubles its yield.',
'Knowledge no longer bound to ordinary form doubles its production.',
'The final boundary is crossed, doubling this producer’s yield once again.'
];
const PERMANENT={U363:['First Remembrance','Recall deeper truths from earlier Hunts, unlocking Dream Remembrance in each new Hunt.',1,null],U281:['Memory of the Sleeping Hunt','While absent, retain 5% of your normal Echo gathering for an hour, then 0.5%.',1,'U363'],U395:['Deep Remembrance','Recall enough of earlier Hunts to unlock stronger memories of absence.',3,'U363'],U274:['Lingering Hunt I','Retain 10 additional percentage points of Echo gathering while absent.',7,'U395'],U275:['Lingering Hunt II','Retain another 10 percentage points while absent.',49,'U274'],U353:['Unbroken Dream I','Double the time that absence retains its full remembered efficiency.',7,'U395'],U354:['Unbroken Dream II','Double that remembered window once again.',49,'U353']};
let D,state,quantity=1,lastFrame=performance.now(),lastSaved=Date.now(),omenUntil=0,confirmation=null,hadOmen=false;

function fresh(){return {v:1,bank:0,run_earned:0,previous_runs_earned:0,claimed_prestige:0,dream_fragments:0,owned:Array(20).fill(0),tiers:[],messenger_doublings:0,messenger_additive_stage:-1,mouse_upgrades:0,insight_amplifiers:0,relics:[],prestige_purchases:0,prestige_effectiveness:0,achievements:[],handmade_echoes:0,clicks:0,ascension:[],elapsed:0,buffs:[],clickBuffs:[],omen_last:'',omen_clicks:0,total_reawakenings:0,saved_at:Date.now()};}
const setOf=a=>new Set(a||[]);
function normalize(s){const f=fresh();s={...f,...s};s.owned=Array.from({length:20},(_,i)=>Math.max(0,Math.min(1000,Number(s.owned?.[i])||0)));for(const k of ['tiers','relics','achievements','ascension'])if(!Array.isArray(s[k]))s[k]=[];return s;}
function format(n){if(!Number.isFinite(n))return '∞';const a=Math.abs(n);if(a>=1e9)return n.toExponential(2).replace('e+','e');if(a>=1e6)return new Intl.NumberFormat('en',{notation:'compact',minimumFractionDigits:2,maximumFractionDigits:2}).format(n);if(a>=1e3)return new Intl.NumberFormat('en',{notation:'compact',minimumFractionDigits:2,maximumFractionDigits:2}).format(n);if(a>=100)return new Intl.NumberFormat('en',{minimumFractionDigits:1,maximumFractionDigits:1}).format(n);return new Intl.NumberFormat('en',{minimumFractionDigits:a>=10?1:0,maximumFractionDigits:2}).format(n);}
function node(tag,c,text){const n=document.createElement(tag);if(c)n.className=c;if(text!==undefined)n.textContent=text;return n;}
function err(m){$('error').textContent=m;$('error').hidden=false;setTimeout(()=>$('error').hidden=true,5000);}
function tierFactor(i){if(!i)return 1;const t=setOf(state.tiers);let f=1;for(let j=0;j<15;j++)if(t.has(i+':'+j))f*=2;return f;}
function messengerCoeff(){if(state.messenger_additive_stage<0)return 0;let a=.1;const mult=D.messenger.coefficient_multipliers;for(let j=0;j<Math.min(state.messenger_additive_stage,mult.length);j++)a*=mult[j];return a;}
function producerEPS(i){if(i===0)return state.owned[0]*(.1*2**state.messenger_doublings+messengerCoeff()*state.owned.slice(1).reduce((a,b)=>a+b,0));return state.owned[i]*D.producers[i].base_eps*tierFactor(i);}
function insight(){return state.achievements.length/25;}
function insightFactor(){let f=1;for(let j=0;j<state.insight_amplifiers;j++)f*=1+insight()*D.insight_amplifiers.coefficients[j];return f;}
function relicFactor(){const have=setOf(state.relics);return D.global_relics.reduce((f,r)=>have.has(r.id)?f*(1+r.bonus_percent/100):f,1);}
function prestigeFactor(){return 1+(state.claimed_prestige/100)*state.prestige_effectiveness;}
function activeFactor(channel){const now=state.elapsed;return channel.reduce((f,b)=>b.end>now?f*b.factor:f,1);}
function rawEPS(){return state.owned.reduce((a,_,i)=>a+producerEPS(i),0)*relicFactor()*insightFactor()*prestigeFactor();}
function eps(){return rawEPS()*activeFactor(state.buffs);}
function clickValue(){const base=2**state.messenger_doublings+messengerCoeff()*state.owned.slice(1).reduce((a,b)=>a+b,0);return (base+.01*state.mouse_upgrades*eps())*activeFactor(state.clickBuffs);}
function nextCost(i,n=state.owned[i]){return Math.ceil(D.producers[i].base_cost*GROWTH**n);}
function bulkCost(i,k){let x=0;for(let n=state.owned[i];n<state.owned[i]+k;n++)x+=nextCost(i,n);return x;}
function tierCost(i,t){return Math.ceil(D.producers[i].base_cost*D.standard_tiers.cost_base_multipliers[t]);}
function upgradeCount(){return state.tiers.length+state.messenger_doublings+Math.max(0,state.messenger_additive_stage+1)+state.mouse_upgrades+state.insight_amplifiers+state.relics.length+state.prestige_purchases;}
function markRecord(id){
const [kind,a,b]=id.split(':');const n=Number(a),j=Number(b);
if(kind==='earn'){const target=n===0?1:10**Math.floor(1.5*n+2);return ['Blood Drawn',format(target)+' Blood Echoes gathered during a single Hunt.'];}
if(kind==='eps'){const target=10**Math.floor(1.2*n);return ['The Hunt Quickens',format(target)+' Blood Echoes gathered each second before temporary signs.'];}
if(kind==='own'){const i=n,idx=j,target=i===0?D.achievements.messenger_thresholds[idx]:D.achievements.ownership_thresholds[idx];return [visibleName(i)+' Remembered',format(target)+' '+visibleName(i)+' brought into the Hunt.'];}
if(kind==='handmade'){const target=D.clicking.handmade_unlocks[n];return ['By the Hunter’s Hand',format(target)+' Blood Echoes drawn by your own hand.'];}
if(kind==='buildings'){const target=D.achievements.total_building_thresholds[n];return ['A Hunt Without End',format(target)+' agents serving the Hunt at once.'];}
if(kind==='upgrades'){const target=D.achievements.upgrade_count_thresholds[n];return ['Knowledge Accumulated',format(target)+' pieces of Hunter’s Knowledge acquired.'];}
return ['Unrecorded Mark','The Hunt remembers something that has not yet been named.'];
}
function renderMarks(){const box=$('marks-list');if(!box)return;box.replaceChildren();if(!state.achievements.length){box.append(node('p','muted','No Marks have been earned. The Hunt has proven nothing yet.'));return;}[...state.achievements].reverse().forEach(id=>{const [name,detail]=markRecord(id),row=node('div','mark-record');row.append(node('strong','',name),node('span','',detail));box.append(row);});}
function grant(){const a=setOf(state.achievements),add=x=>a.add(x);if(state.run_earned>=1)add('earn:0');for(let j=1;j<48;j++)if(state.run_earned>=10**Math.floor(1.5*j+2))add('earn:'+j);const r=rawEPS();for(let j=0;j<48;j++)if(r>=10**Math.floor(1.2*j))add('eps:'+j);for(let i=1;i<20;i++)D.achievements.ownership_thresholds.forEach((x,j)=>{if(state.owned[i]>=x)add('own:'+i+':'+j)});D.achievements.messenger_thresholds.forEach((x,j)=>{if(state.owned[0]>=x)add('own:0:'+j)});D.clicking.handmade_unlocks.forEach((x,j)=>{if(state.handmade_echoes>=x)add('handmade:'+j)});const total=state.owned.reduce((a,b)=>a+b,0);D.achievements.total_building_thresholds.forEach((x,j)=>{if(total>=x)add('buildings:'+j)});D.achievements.upgrade_count_thresholds.forEach((x,j)=>{if(upgradeCount()>=x)add('upgrades:'+j)});state.achievements=[...a];}
function earn(x){if(!Number.isFinite(x)||x<0)return;state.bank+=x;state.run_earned+=x;}
function targetPrestige(scale=1e12){return Math.floor(Math.cbrt((state.previous_runs_earned+state.run_earned)/scale)+1e-12);}
function alphaTarget(){return Math.max(targetPrestige(),Math.min(STARTER_CAP,targetPrestige(STARTER_SCALE)));}
function newFragments(){return Math.max(0,alphaTarget()-state.claimed_prestige);}
function nextFragmentAt(){const n=alphaTarget()+1;return (n<=STARTER_CAP?STARTER_SCALE:1e12)*n**3;}
function offlineSettings(){const a=setOf(state.ascension);if(!a.has('U281'))return [0,0];let e=.05,c=3600;if(a.has('U274'))e+=.10;if(a.has('U275'))e+=.10;if(a.has('U353'))c*=2;if(a.has('U354'))c*=2;return [Math.min(e,.91),c];}
function save(notice=false){state.saved_at=Date.now();localStorage.setItem(SAVE_KEY,JSON.stringify(state));lastSaved=Date.now();if(notice)state.notice='The Hunt has been recorded on this device.';}
function load(){try{const raw=localStorage.getItem(SAVE_KEY);if(!raw)return fresh();return normalize(JSON.parse(raw));}catch(e){err('Save could not be read; beginning a fresh Hunt.');return fresh();}}
function applyOffline(seconds){const [eff,cap]=offlineSettings();if(eff<=0)return 0;const gain=rawEPS()*eff*(Math.min(seconds,cap)+.1*Math.max(0,seconds-cap));earn(gain);return gain;}
function expire(){state.buffs=state.buffs.filter(b=>b.end>state.elapsed);state.clickBuffs=state.clickBuffs.filter(b=>b.end>state.elapsed);}
function addBuff(arr,factor,duration,name){const b=arr.find(x=>x.name===name);if(b)b.end+=duration;else arr.push({end:state.elapsed+duration,factor,name});}
function scheduleOmen(){omenUntil=0;state.omen_next=state.elapsed+300+Math.random()*180;}
const OMEN_TEXT={
frenzy:['Blood Moon','The moon burns close. Production ×7 for 77 seconds.'],
windfall:['Fresh Blood','A sudden bounty of Blood Echoes answers the Hunt.'],
click_frenzy:['Hunter’s Trance','Instinct overwhelms thought. Manual taps ×777 for 13 seconds.'],
building:['Resonant Hunt','One branch of the Hunt resonates with accumulated strength for 30 seconds.'],
chain:['Echoing Blood','One death calls to another, releasing a chained bounty of Blood Echoes.'],
storm:['Nightmare Torrent','The boundary thins and a violent torrent of Blood Echoes pours through.']
};
function insightStage(){const x=insight();return x<1?['Unseeing','The Hunt is all that can be perceived.']:x<3?['Awakening','Patterns begin to emerge behind blood and beast.']:x<6?['Perceptive','The world is becoming less certain.']:x<10?['Eyes Within','The unseen presses against the waking world.']:['Eldritch','The Hunt can no longer hide what lies beyond it.'];}
function resolveOmen(){if(!omenUntil)return;let choices=['frenzy','windfall'];if(state.run_earned>=1e5&&Math.random()<.03)choices.push('chain','storm');if(Math.random()<.10)choices.push('click_frenzy');if(state.owned.reduce((a,b)=>a+b,0)>=10&&Math.random()<.25)choices.push('building');if(state.omen_last&&Math.random()<.8)choices=choices.filter(x=>x!==state.omen_last);const c=choices[Math.floor(Math.random()*choices.length)];state.omen_last=c;state.omen_clicks++;if(c==='frenzy')addBuff(state.buffs,7,77,'frenzy');else if(c==='windfall')earn(Math.min(.15*state.bank,eps()*900)+13);else if(c==='click_frenzy')addBuff(state.clickBuffs,777,13,'click frenzy');else if(c==='building'){const eligible=state.owned.map((n,i)=>n>=10?i:-1).filter(i=>i>=0);if(eligible.length){const i=eligible[Math.floor(Math.random()*eligible.length)];addBuff(state.buffs,1+state.owned[i]/10,30,'building '+(i+1));}else addBuff(state.buffs,7,77,'frenzy');}else if(c==='chain')earn(Math.max(7,Math.min(eps()*21600,state.bank*.5)));else if(c==='storm')earn(eps()*60*150);const omen=OMEN_TEXT[c]||['Strange Sign','Something answered the Hunt.'];state.notice=omen[0]+': '+omen[1];omenUntil=0;scheduleOmen();grant();save();}
function upgrades(){const out=[];const d=state.messenger_doublings;if(d<3&&state.owned[0]>=D.messenger.doubling_unlocks[d])out.push({id:'md:'+d,name:'Messenger Communion',cost:D.messenger.doubling_costs[d],type:'md'});const ns=state.messenger_additive_stage+1;if(ns===0&&state.owned[0]>=25)out.push({id:'ma:0',name:'Hunter\'s Resonance',cost:1e5,type:'ma',stage:0});else if(ns>0&&ns<=D.messenger.coefficient_multiplier_thresholds.length&&state.owned[0]>=D.messenger.coefficient_multiplier_thresholds[ns-1])out.push({id:'ma:'+ns,name:'Hunter\'s Resonance',cost:[1e7,1e8,1e9,1e10,1e13,1e16,1e19,1e22,1e25,1e28,1e31][ns-1],type:'ma',stage:ns});const have=setOf(state.tiers);for(let i=1;i<20;i++)for(let t=0;t<15;t++)if(!have.has(i+':'+t)){if(state.owned[i]>=D.standard_tiers.unlock_owned[t])out.push({id:'t:'+i+':'+t,name:visibleName(i)+' · '+TIER_NAMES[t],cost:tierCost(i,t),type:'tier',i,t});break;}let j=state.mouse_upgrades;if(j<15&&state.handmade_echoes>=D.clicking.handmade_unlocks[j])out.push({id:'mouse',name:'Blood-Drunk Instinct · +1% production per tap',cost:D.clicking.mouse_upgrade_costs[j],type:'mouse'});j=state.insight_amplifiers;if(j<15&&state.achievements.length>=D.insight_amplifiers.achievement_unlocks[j])out.push({id:'insight',name:'Eyes on the Inside · amplify Insight',cost:D.insight_amplifiers.costs[j],type:'insight'});if(setOf(state.ascension).has('U363')){j=state.prestige_purchases;if(j<D.prestige_effectiveness_purchases.length){const p=D.prestige_effectiveness_purchases[j];out.push({id:'prestige',name:'Dream Remembrance '+(j+1),cost:p.cost,type:'prestige'});}}const rel=setOf(state.relics);D.global_relics.forEach((r,n)=>{if(!rel.has(r.id)&&state.run_earned>=r.run_earnings_unlock)out.push({id:'r:'+r.id,name:'Caryll Revelation '+(n+1)+' · +'+r.bonus_percent+'% production',cost:Math.ceil(r.cost),type:'relic',r});});return out.sort((a,b)=>a.cost-b.cost);}
function buyUpgrade(u){if(state.bank<u.cost)return;if(u.type==='tier')state.tiers.push(u.i+':'+u.t);else if(u.type==='md')state.messenger_doublings++;else if(u.type==='ma')state.messenger_additive_stage=u.stage;else if(u.type==='mouse')state.mouse_upgrades++;else if(u.type==='insight')state.insight_amplifiers++;else if(u.type==='relic')state.relics.push(u.r.id);else if(u.type==='prestige'){const p=D.prestige_effectiveness_purchases[state.prestige_purchases];state.prestige_purchases++;state.prestige_effectiveness=p.effectiveness;}state.bank-=u.cost;grant();save();render();}
function reawaken(){const target=alphaTarget(),gain=Math.max(0,target-state.claimed_prestige);if(!gain)return;state.previous_runs_earned+=state.run_earned;state.claimed_prestige=target;state.dream_fragments+=gain;state.total_reawakenings++;const keep={previous_runs_earned:state.previous_runs_earned,claimed_prestige:state.claimed_prestige,dream_fragments:state.dream_fragments,achievements:state.achievements,ascension:state.ascension,total_reawakenings:state.total_reawakenings,elapsed:state.elapsed};state={...fresh(),...keep,saved_at:Date.now()};state.notice='The Hunt ended, but the Dream did not. You carried '+gain+' new Remnants back with you.';scheduleOmen();save();render();}
function buyMemory(id){const m=PERMANENT[id],have=setOf(state.ascension);if(!m||have.has(id)||state.dream_fragments<m[2]||(m[3]&&!have.has(m[3])))return;state.dream_fragments-=m[2];state.ascension.push(id);save();render();}
function render(){if(!state||!D)return;$('bank').textContent=format(state.bank);$('eps').textContent=format(eps());$('tap-value').textContent=format(clickValue());$('achievements').textContent=format(state.achievements.length);renderMarks();$('insight').textContent=format(insight());const insightState=insightStage();$('insight').title=insightState[0]+' — '+insightState[1];$('insight-stage').textContent=insightState[0];$('records-marks').textContent=format(state.achievements.length);$('records-insight').textContent=format(insight());$('records-stage').textContent=insightState[0];$('records-insight-detail').textContent=insightState[1];$('total-owned').textContent=format(state.owned.reduce((a,b)=>a+b,0));const phase=huntPhase();$('phase-name').textContent=phase.name;$('phase-detail').textContent=phase.detail;$('fragments').textContent=format(state.dream_fragments);$('dream-badge').textContent=newFragments();$('dream-badge').hidden=newFragments()<1;const first=bulkCost(0,1);$('onboarding').textContent=!state.owned.some(Boolean)?(state.bank>=first?'You have enough Blood Echoes. Call your first Messenger below.':'Draw '+format(first-state.bank)+' more Blood Echoes, then call a Messenger.'):(newFragments()>=2?'The Dream can preserve two Remnants of this Hunt. Return when you are ready.':newFragments()===1?'The Dream can preserve one Remnant. Deepen the Hunt until it can preserve two.':'The Hunt now gathers Blood Echoes without your hand. Expand its reach, uncover Hunter\'s Knowledge, and heed strange signs before they vanish.');$('notice').textContent=state.notice||'';$('save-status').textContent=(Date.now()-lastSaved<2000)?'Progress saved':'Autosave · '+Math.floor((Date.now()-lastSaved)/1000)+'s ago';$('producers').replaceChildren();state.owned.forEach((owned,i)=>{const c=bulkCost(i,quantity),b=node('button','producer');b.append(node('span','number',String(i+1).padStart(2,'0')));const mid=node('span');mid.append(node('span','name',visibleName(i)),node('span','detail',visibleLore(i)),node('span','detail',format(producerEPS(i))+' echoes / second'));const right=node('span');right.append(node('span','cost',format(c)),node('span','count',owned+' owned'));b.append(mid,right);b.disabled=state.bank<c||owned+quantity>1000;b.onclick=()=>{if(!b.disabled){state.bank-=c;state.owned[i]+=quantity;grant();save();render();}};$('producers').append(b);});const ups=upgrades();$('upgrade-badge').textContent=ups.length;$('upgrade-badge').hidden=!ups.length;$('upgrades').replaceChildren();ups.forEach(u=>{const descriptions={md:'The Messengers answer more readily. Doubles Messenger production and the base value of every manual tap.',ma:'The Messengers carry the strength of the Hunt between hunters. Their production grows with your non-Messenger forces.',tier:u.type==='tier'?TIER_LORE[u.t]:'',mouse:'Instinct takes over where thought fails. Adds 1% of your current production to every manual tap.',insight:'Greater perception turns forbidden understanding into power. Amplifies the production bonus granted by Insight.',relic:'A revelation expressed through Caryll-like runic knowledge. Permanently increases all production for this Hunt.',prestige:'Something from earlier Hunts survives the dream. Activates a larger share of lifetime prestige as a production multiplier.'};const b=node('button','upgrade');b.append(node('span','name',u.name),node('span','detail',descriptions[u.type]||'Improves your vigil.'),node('small','',format(u.cost)+' echoes'));b.disabled=state.bank<u.cost;b.onclick=()=>buyUpgrade(u);$('upgrades').append(b);});$('upgrade-empty').hidden=ups.length>0;$('memories').replaceChildren();const have=setOf(state.ascension);Object.entries(PERMANENT).forEach(([id,m])=>{const b=node('button','memory-node',m[0]+(have.has(id)?' · remembered':' · '+m[2]+' Remnants'));b.append(node('small','',m[1]));b.disabled=have.has(id)||state.dream_fragments<m[2]||(m[3]&&!have.has(m[3]));b.onclick=()=>buyMemory(id);$('memories').append(b);});$('reawakening-info').textContent=format(state.run_earned)+' Blood Echoes gathered this Hunt · '+format(state.claimed_prestige)+' Remnants carried through the Dream. Return now to preserve '+format(newFragments())+' new Remnants. Next Remnant at '+format(nextFragmentAt())+' lifetime Blood Echoes.';$('reawaken').disabled=newFragments()<1;const [oe,oc]=offlineSettings();$('offline-info').textContent=oe?'Remembered Hunt: '+Math.round(oe*100)+'% Echo gathering while absent for '+format(oc/3600)+' hours, then one tenth of that rate.':'Echoes gathered in your absence require Memory of the Sleeping Hunt.';const has=omenUntil>state.elapsed;if(has&&!hadOmen)$('omen-announcement').textContent='A strange sign has appeared. Heed it before it fades.';hadOmen=has;$('omen').hidden=!has;$('omen-time').textContent=has?'· '+Math.ceil(omenUntil-state.elapsed)+'s':'';$('buffs').replaceChildren(...[...state.buffs,...state.clickBuffs].filter(b=>b.end>state.elapsed).map(b=>node('span','',((OMEN_TEXT[b.name]?.[0])||b.name)+' ×'+format(b.factor)+' · '+Math.ceil(b.end-state.elapsed)+'s')));}
function tick(now){if(state&&D){const dt=Math.min(10,Math.max(0,(now-lastFrame)/1000));lastFrame=now;if(dt){earn(eps()*dt);state.elapsed+=dt;expire();grant();if(!state.omen_next)scheduleOmen();if(!omenUntil&&state.elapsed>=state.omen_next)omenUntil=state.elapsed+30;if(omenUntil&&state.elapsed>=omenUntil)scheduleOmen();}if(Date.now()-lastSaved>=10000)save();render();}requestAnimationFrame(tick);}
function confirmAction(title,desc,word,cb){confirmation={word,cb};$('confirm-title').textContent=title;$('confirm-description').textContent=desc;$('confirm-input').value='';$('confirm-label').hidden=!word;$('confirm-input').placeholder=word?'Type '+word:'';$('confirm').showModal();}
$('confirm-form').onsubmit=e=>{e.preventDefault();if(!confirmation)return;if(confirmation.word&&$('confirm-input').value!==confirmation.word){err('Type '+confirmation.word+' to continue.');return;}const cb=confirmation.cb;confirmation=null;$('confirm').close();cb();};$('confirm-cancel').onclick=()=>$('confirm').close();
$('vessel').onclick=()=>{const v=clickValue();earn(v);state.handmade_echoes+=v;state.clicks++;grant();render();};$('omen').onclick=resolveOmen;$('insight-open').onclick=()=>{$('marks').showModal();renderMarks();};$('hunt-open').onclick=()=>{window.scrollTo({top:0,behavior:document.body.classList.contains('reduced-motion')?'auto':'smooth'});};$('marks-dock').onclick=()=>{$('marks').showModal();renderMarks();};$('upgrades-open').onclick=()=>$('knowledge').showModal();$('dream-open').onclick=()=>$('dream').showModal();$('settings-open').onclick=()=>$('settings').showModal();$('save-now').onclick=()=>{save(true);render();};
document.querySelectorAll('[data-quantity]').forEach(b=>b.onclick=()=>{quantity=Number(b.dataset.quantity);document.querySelectorAll('[data-quantity]').forEach(q=>q.setAttribute('aria-pressed',String(q===b)));render();});
$('reawaken').onclick=()=>confirmAction('Return to the Dream?','This Hunt will end. Blood Echoes, agents, and knowledge gained during this Hunt will be lost. Marks of the Hunt and remembered truths endure.','DREAM',reawaken);
$('reset').onclick=()=>confirmAction('Erase all progress?','This clears every Hunt, Mark of the Hunt, and remembered truth on this browser.','RESET',()=>{localStorage.removeItem(SAVE_KEY);state=fresh();scheduleOmen();save();render();});
$('export-save').onclick=()=>{save();const blob=new Blob([JSON.stringify(state,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='bloodtap-save.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
$('import-open').onclick=()=>$('import-file').click();$('import-file').onchange=async e=>{const f=e.target.files[0];e.target.value='';if(!f)return;try{const candidate=normalize(JSON.parse(await f.text()));confirmAction('Replace this Hunt?','Importing replaces the Hunt recorded in this browser.','',()=>{state=candidate;state.saved_at=Date.now();scheduleOmen();save();render();});}catch{err('That save file is not valid JSON.');}};
try{$('reduced-motion').checked=localStorage.getItem('bloodtap-reduced-motion')==='true';}catch{}document.body.classList.toggle('reduced-motion',$('reduced-motion').checked);$('reduced-motion').onchange=e=>{document.body.classList.toggle('reduced-motion',e.target.checked);localStorage.setItem('bloodtap-reduced-motion',String(e.target.checked));};
(async()=>{try{const r=await fetch('./economy_data.json',{cache:'no-store'});if(!r.ok)throw Error('economy data '+r.status);D=await r.json();state=load();const away=Math.max(0,(Date.now()-(state.saved_at||Date.now()))/1000);if(away>10){const g=applyOffline(away);state.elapsed+=away;if(g)state.notice='The Dream remembers. '+format(g)+' Blood Echoes gathered in your absence.';}scheduleOmen();grant();save();render();requestAnimationFrame(tick);}catch(e){err('BloodTap could not load: '+e.message);$('onboarding').textContent='The web alpha failed to load.';}})();
