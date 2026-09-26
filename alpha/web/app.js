'use strict';
const $=id=>document.getElementById(id);
let state=null,quantity=1,queue=Promise.resolve(),confirmation=null,polling=false;
const format=n=>Math.abs(n)>=1e9?n.toExponential(2).replace('e+','e'):new Intl.NumberFormat('en',{maximumFractionDigits:n<10?1:0,notation:n>=1e4?'compact':'standard'}).format(n);
let errorTimer;
function error(message){document.querySelectorAll('.dialog-error').forEach(n=>n.textContent=message);$('error').textContent=message;$('error').hidden=false;clearTimeout(errorTimer);errorTimer=setTimeout(()=>$('error').hidden=true,6500);}
function node(tag,className,text){const n=document.createElement(tag);if(className)n.className=className;if(text!==undefined)n.textContent=text;return n;}
const producerNodes=[];
function render(next){
  state=next;
  for(const [id,key] of Object.entries({'bank':'bank','eps':'eps','tap-value':'click','achievements':'achievements','insight':'insight','total-owned':'owned','fragments':'fragments'}))$(id).textContent=format(state[key]);
  if(state.owned)$('onboarding').textContent='Your vigil gathers echoes automatically. Grow it, discover upgrades, and watch for Omens.';
  else $('onboarding').textContent='Tap the vessel to gather 15 echoes. Then hire a Whisperer to earn while you wait.';
  $('notice').textContent=state.notice;
  $('save-status').textContent=state.saved_seconds_ago<2?'Progress saved':'Autosave · '+Math.floor(state.saved_seconds_ago)+'s ago';
  state.producers.forEach((p,i)=>{
    let b=producerNodes[i];
    if(!b){b=node('button','producer');b.append(node('span','number',String(i+1).padStart(2,'0')));const center=node('span');center.append(node('span','name'),node('span','detail'));const right=node('span');right.append(node('span','cost'),node('span','count'));b.append(center,right);b.addEventListener('click',()=>act({action:'buy',producer:i,quantity}));$('producers').append(b);producerNodes[i]=b;}
    b.querySelector('.name').textContent=p.name;b.querySelector('.detail').textContent=format(p.production)+' base echoes / second';b.querySelector('.cost').textContent=format(p.costs[quantity]);b.querySelector('.count').textContent=p.owned+' owned';b.disabled=state.bank<p.costs[quantity]||p.owned+quantity>1000;b.setAttribute('aria-label',`Buy ${quantity} ${p.name} for ${format(p.costs[quantity])} echoes, ${p.owned} owned`);
  });
  // Preserve keyboard focus when a refreshed option still exists.
  const focusKey=document.activeElement?.dataset?.key;
  $('upgrades').replaceChildren();
  state.upgrades.forEach(u=>{const b=node('button','upgrade',u.name);b.dataset.key=u.id;b.append(node('small','',format(u.cost)+' echoes'));b.disabled=!u.affordable;b.addEventListener('click',()=>act({action:'upgrade',id:u.id}));$('upgrades').append(b);});
  $('upgrade-empty').hidden=state.upgrades.length>0;
  $('memories').replaceChildren();
  state.memories.forEach(m=>{const b=node('button','memory-node',m.name+(m.owned?' · owned':` · ${m.cost} fragments`));b.dataset.key=m.id;b.append(node('small','',m.description));b.disabled=m.owned||!m.unlocked||state.fragments<m.cost;b.addEventListener('click',()=>act({action:'ascension',id:m.id}));$('memories').append(b);});
  if(focusKey){for(const b of document.querySelectorAll('[data-key]'))if(b.dataset.key===focusKey&&!b.disabled){b.focus({preventScroll:true});break;}}
  $('reawakening-info').textContent=`${format(state.earned)} earned this run · ${format(state.prestige)} lifetime prestige. Reawaken now for ${format(state.new_fragments)} new fragments. First useful bundle: 2 fragments for First memory + Sleeping vigil.`;
  $('reawaken').disabled=state.new_fragments<1;
  $('offline-info').textContent=state.offline_efficiency?`Offline: ${Math.round(state.offline_efficiency*100)}% production for ${format(state.offline_cap/3600)} hours, then one tenth of that rate.`:'Offline earnings unlock with Sleeping vigil after Reawakening.';
  $('omen').hidden=state.omen_seconds<=0;$('omen-time').textContent=`· ${Math.ceil(state.omen_seconds)}s`;
  $('buffs').replaceChildren(...state.buffs.map(b=>node('span','',`${b.name} ×${format(b.factor)} · ${Math.ceil(b.seconds)}s`)));
}
async function request(body){
  const response=await fetch('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const result=await response.json();if(!response.ok)throw new Error(result.error||'Request failed');render(result);
}
function act(body){queue=queue.then(()=>request(body)).catch(e=>error(e.message));return queue;}
async function refresh(){if(polling)return;polling=true;try{await queue;const response=await fetch('/api/state');const result=await response.json();if(!response.ok)throw new Error(result.error);render(result);}catch(e){$('save-status').textContent='Disconnected';error('Connection lost. Keep the BloodTap server running.');}finally{polling=false;}}
function confirmAction(title,description,word,callback){confirmation={word,callback};$('confirm-title').textContent=title;$('confirm-description').textContent=description;$('confirm-input').value='';$('confirm-label').hidden=!word;$('confirm-input').placeholder=word?'Type '+word:'';$('confirm').showModal();(word?$('confirm-input'):$('confirm-submit')).focus();}
$('confirm-form').addEventListener('submit',event=>{event.preventDefault();if(!confirmation)return;if(confirmation.word&&$('confirm-input').value!==confirmation.word){error('Type '+confirmation.word+' to continue.');return;}const callback=confirmation.callback;confirmation=null;$('confirm').close();callback();});
$('confirm-cancel').addEventListener('click',()=>$('confirm').close());
$('vessel').addEventListener('click',()=>act({action:'click'}));$('omen').addEventListener('click',()=>act({action:'omen'}));
document.querySelectorAll('[data-quantity]').forEach(b=>b.addEventListener('click',()=>{quantity=Number(b.dataset.quantity);document.querySelectorAll('[data-quantity]').forEach(q=>q.setAttribute('aria-pressed',String(q===b)));if(state)render(state);}));
$('import-open').addEventListener('click',()=>$('import-file').click());
$('settings-open').addEventListener('click',()=>$('settings').showModal());$('save-now').addEventListener('click',()=>act({action:'save'}));
$('reawaken').addEventListener('click',()=>confirmAction('Begin another vigil?',`Receive ${format(state.new_fragments)} fragments. Echoes, producers, and run upgrades reset. Achievements and permanent memories remain. Type REAWAKEN to continue.`,'REAWAKEN',()=>act({action:'reawaken',confirmation:'REAWAKEN'})));
$('reset').addEventListener('click',()=>confirmAction('Erase all progress?','This clears every run, achievement, and permanent memory. Export a save first. Type RESET to confirm.','RESET',()=>act({action:'reset',confirmation:'RESET'})));
$('import-file').addEventListener('change',async event=>{const file=event.target.files[0];event.target.value='';if(!file)return;if(file.size>1000000){error('Save exceeds 1 MB.');return;}const text=await file.text();confirmAction('Replace this vigil?','Importing replaces your current progress. Your previous local save is kept as a backup.','',()=>act({action:'import',save:text}));});
try{$('reduced-motion').checked=localStorage.getItem('bloodtap-reduced-motion')==='true';}catch{}
document.body.classList.toggle('reduced-motion',$('reduced-motion').checked);
$('reduced-motion').addEventListener('change',event=>{document.body.classList.toggle('reduced-motion',event.target.checked);try{localStorage.setItem('bloodtap-reduced-motion',String(event.target.checked));}catch{}});
refresh();setInterval(refresh,1000);
