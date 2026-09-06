/* Remote Builder: no user-supplied HTML, no credentials in backups. */
function validateRemoteBackup(data) {
  if (!data || data.schema !== 2 || data.profile !== '433.937MHz ASK/OOK' ||
      !Array.isArray(data.remotes) || data.remotes.length !== 4 ||
      !Array.isArray(data.buttons) || data.buttons.length !== 8) throw Error('Unsupported backup schema or radio profile.');
  const name = x => typeof x === 'string' && new TextEncoder().encode(x).length <= 32 && !x.includes('\0');
  if (!data.remotes.every(name)) throw Error('Remote names must be at most 32 UTF-8 bytes.');
  data.buttons.forEach((b,i) => {
    if (!b || b.slot !== i || typeof b.active !== 'boolean' || !name(b.name) ||
        !Number.isInteger(b.remote) || b.remote < 0 || b.remote > 3 ||
        !Number.isInteger(b.icon) || b.icon < 0 || b.icon > 7 ||
        !Number.isInteger(b.order) || b.order < 0 || b.order > 7 ||
        (b.active && (!b.name.trim() || !data.remotes[b.remote].trim())) ||
        !Array.isArray(b.pulses) || b.pulses.length > 256) throw Error('Invalid button record.');
    if (b.pulses.length) {
      let total=0;
      if (!b.active || b.pulses.length < 16 || b.pulses[0] <= 0) throw Error('Invalid capture.');
      b.pulses.forEach((v,j) => {
        if (!Number.isInteger(v) || Math.abs(v)<50 || Math.abs(v)>30000 || (j && (v>0)===(b.pulses[j-1]>0))) throw Error('Invalid pulse timings.');
        total+=Math.abs(v);
      });
      if(total<3000 || total>500000)throw Error('Invalid capture duration.');
    }
  });
  return data;
}
if (typeof module !== 'undefined') module.exports={validateRemoteBackup};
if (typeof document !== 'undefined') (()=>{
  const section=document.createElement('section');section.className='card remote-builder';section.id='remote-builder';
  section.innerHTML=`<h2>Build your remote</h2><p class="kicker">Create the buttons first. Learn each one when you’re ready.</p>
  <label for="builder-remote">Remote</label><select id="builder-remote"></select>
  <label for="builder-name">Remote name</label><input id="builder-name" maxlength="32" placeholder="e.g. Living room lights">
  <div class="grid2"><button id="builder-rename">Save remote name</button><button id="builder-add">Add button</button></div>
  <div id="builder-keys" class="builder-keys"></div>
  <form id="builder-editor" hidden><h3>Edit button</h3><label for="builder-label">Button label</label><input id="builder-label" maxlength="32" required>
  <label for="builder-icon">Icon</label><select id="builder-icon"><option>Power</option><option>Plus</option><option>Minus</option><option>Light</option><option>Fan</option><option>Timer</option><option>Play</option><option>Stop</option></select>
  <label for="builder-position">Position</label><select id="builder-position"></select>
  <div class="grid2"><button type="submit">Save button</button><button type="button" id="builder-edit-cancel">Cancel edit</button></div></form>
  <div id="builder-feedback" class="capture-feedback"><svg class="capture-graphic" viewBox="0 0 120 100" width="80" height="70" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><rect x="16" y="18" width="38" height="67" rx="10"/><circle class="remote-key" cx="35" cy="38" r="7"/><path class="signal signal-one" d="M66 31q15 19 0 38"/><path class="signal signal-two" d="M79 21q23 29 0 58"/><path class="signal signal-three" d="M93 11q31 39 0 78"/></g></svg><div><strong id="builder-title">Ready to build</strong><p id="builder-status" role="status" aria-live="polite">Connecting to Remote Builder…</p></div></div>
  <div class="grid2"><button id="builder-save">Save learned command</button><button id="builder-cancel">Discard capture</button></div>
  <div class="grid2"><button id="builder-export">Export backup</button><button id="builder-import">Import backup</button></div><input id="builder-file" type="file" accept="application/json,.json" hidden>
  <p class="help">Four custom remotes · eight custom buttons total · fixed 433.937 MHz ASK/OOK profile. Your Vornado controls above stay separate. Backups may contain private RF codes—keep them out of public repositories.</p>`;
  document.querySelector('.wrap').insertBefore(section,document.querySelector('#wifi-form').closest('.card'));
  section.querySelectorAll('button').forEach(b=>b.dataset.builder='true');
  const el=id=>document.getElementById('builder-'+id);
  const glyphs=['⏻','+','−','☀','✣','◷','▶','■'];
  let data=null,selected=0,editing=-1,working=false,online=false;
  function message(text){el('status').textContent=text;}
  function snapshot(){return JSON.parse(JSON.stringify({schema:data.schema,profile:data.profile,remotes:data.remotes,buttons:data.buttons}));}
  function renderBuilder(){
    section.querySelectorAll('button').forEach(b=>b.disabled=preview||working||!online);
    if(!data)return;
    const locked=data.learning>=0 || data.candidate>=0;
    for(const id of ['rename','add','import'])el(id).disabled=preview||working||!online||locked;
    el('save').disabled=preview||working||!online||data.candidate<0;
    el('cancel').disabled=preview||working||!online||!locked;
    el('feedback').classList.toggle('listening',data.learning>=0&&online);
    el('title').textContent=data.learning>=0?'Press '+data.buttons[data.learning].name+' now · '+data.remaining+'s':data.candidate>=0?'Command received':'Remote Builder';
    el('keys').replaceChildren();
    const buttons=data.buttons.filter(b=>b.active&&b.remote===selected).sort((a,b)=>a.order-b.order||a.slot-b.slot);
    if(!buttons.length){const p=document.createElement('p');p.className='help';p.textContent='No buttons yet. Name this remote, then add your buttons.';el('keys').append(p);}
    for(const b of buttons){
      const card=document.createElement('div');card.className='builder-key';
      const label=document.createElement('strong');label.textContent=glyphs[b.icon]+' '+b.name;card.append(label);
      const meta=document.createElement('small');meta.textContent=(b.pulses.length?'Learned':'Not learned')+' · HA Custom button '+(b.slot+1);card.append(meta);
      const actions=document.createElement('div');actions.className='builder-key-actions';
      for(const [text,fn,disabled] of [
        ['Send',()=>request({op:'send',slot:b.slot}),locked||!b.pulses.length],
        [b.pulses.length?'Relearn':'Learn',()=>request({op:'learn',slot:b.slot}),locked],
        ['Edit',()=>edit(b.slot),locked],
        ['Delete',()=>remove(b.slot),locked]]) {
        const button=document.createElement('button');button.type='button';button.dataset.builder='true';button.textContent=text;
        button.disabled=preview||working||!online||disabled;button.onclick=fn;actions.append(button);
      }
      card.append(actions);el('keys').append(card);
    }
  }
  async function refresh(){
    if(preview)return;
    const r=await fetch('/airbridge/builder',{cache:'no-store',signal:AbortSignal.timeout(7000)});
    if(!r.ok)throw Error('Remote Builder unavailable: '+r.status);
    const next=validateRemoteBackup(await r.json());
    const first=!data;data=next;online=true;
    if(first){el('remote').replaceChildren(...data.remotes.map((n,i)=>new Option(n||'New remote '+(i+1),i)));el('name').value=data.remotes[selected];}
    renderBuilder();return next;
  }
  async function request(payload){
    if(preview||working||!online)return;
    working=true;renderBuilder();const revision=data.revision;
    try{
      const r=await fetch('/airbridge/builder',{method:'POST',headers:{'X-Airbridge-Request':'builder','Content-Type':'application/json'},body:JSON.stringify(payload),signal:AbortSignal.timeout(15000)});
      if(!r.ok)throw Error(await r.text());
      for(let i=0;i<12;i++){
        await new Promise(resolve=>setTimeout(resolve,350));await refresh();
        if(data.revision!==revision&&!data.pending){if(data.error)throw Error(data.error);message(data.status);return true;}
      }
      throw Error('Request outcome unknown. Refresh before retrying; do not repeat a toggle.');
    }catch(e){message(e.message);return false;}finally{working=false;renderBuilder();}
  }
  function edit(slot){
    editing=slot;const b=data.buttons[slot];el('editor').hidden=false;el('label').value=b.active?b.name:'';el('icon').selectedIndex=b.icon;
    el('position').replaceChildren(...Array.from({length:8},(_,i)=>new Option(String(i+1),i)));el('position').value=b.order;
    el('label').focus();
  }
  async function remove(slot){
    if(!confirm('Delete this button and its learned command? Export a backup first if needed.'))return;
    const next=snapshot();next.buttons[slot]={slot,name:'',remote:0,icon:0,order:slot,active:false,pulses:[]};await request({op:'replace',data:next});
  }
  el('remote').onchange=()=>{selected=Number(el('remote').value);el('name').value=data.remotes[selected];el('editor').hidden=true;renderBuilder();};
  el('rename').onclick=async()=>{
    const next=snapshot();next.remotes[selected]=el('name').value.trim();
    try{validateRemoteBackup(next);await request({op:'replace',data:next});el('remote').options[selected].text=data.remotes[selected]||'New remote '+(selected+1);}catch(e){message(e.message);}
  };
  el('add').onclick=()=>{
    if(!data.remotes[selected]){message('Save a remote name first.');return;}
    const slot=data.buttons.findIndex(b=>!b.active);if(slot<0){message('All eight custom slots are in use. Export a backup before deleting a button.');return;}edit(slot);
  };
  el('editor').onsubmit=async event=>{
    event.preventDefault();const next=snapshot(),b=next.buttons[editing];b.active=true;b.name=el('label').value.trim();b.remote=selected;b.icon=el('icon').selectedIndex;
    const order=Number(el('position').value),old=b.order;
    next.buttons.filter(x=>x.active&&x.remote===selected&&x.slot!==editing&&x.order===order).forEach(x=>x.order=old);
    b.order=order;
    try{validateRemoteBackup(next);if(await request({op:'replace',data:next}))el('editor').hidden=true;}catch(e){message(e.message);}
  };
  el('edit-cancel').onclick=()=>el('editor').hidden=true;
  el('save').onclick=()=>request({op:'save',slot:data.candidate});el('cancel').onclick=()=>request({op:'cancel'});
  el('export').onclick=()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(snapshot())],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='airbridge-private-remotes.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  };
  el('import').onclick=()=>el('file').click();
  el('file').onchange=async()=>{
    const file=el('file').files[0];if(!file)return;
    try{
      if(file.size>26000)throw Error('Backup exceeds 26 KB.');const next=validateRemoteBackup(JSON.parse(await file.text()));
      if(confirm('Replace all custom remotes and learned custom commands with this backup? Vornado commands will not change.')){
        await request({op:'replace',data:next});el('remote').replaceChildren(...data.remotes.map((n,i)=>new Option(n||'New remote '+(i+1),i)));el('remote').value=selected;el('name').value=data.remotes[selected];
      }
    }catch(e){message(e.message);}finally{el('file').value='';}
  };
  if(preview){
    data={schema:2,profile:'433.937MHz ASK/OOK',remotes:['Living room','','',''],buttons:Array.from({length:8},(_,slot)=>({slot,name:['Power','Brightness +','Brightness −'][slot]||'',remote:0,icon:slot,order:slot,active:slot<3,pulses:[]})),learning:-1,candidate:-1,remaining:0};
    el('remote').append(new Option('Living room','0'));el('name').value='Living room';message('Design preview — no device connected.');renderBuilder();
  }else{
    const poll=async()=>{try{await refresh();if(!working)message(data.error||data.status);}catch(e){online=false;renderBuilder();message('Connection unavailable. No commands sent.');}setTimeout(poll,2000);};poll();
  }
})();
