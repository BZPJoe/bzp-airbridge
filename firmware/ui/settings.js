// BZP Airbridge local control panel. Uses ESPHome 2026.8 name-based REST IDs.
document.title = "BZP Airbridge • Remote Builder";
const favicon=document.createElement("link");favicon.rel="icon";favicon.href=AIRBRIDGE_ICON;document.head.append(favicon);
const viewport=document.createElement("meta"); viewport.name="viewport"; viewport.content="width=device-width,initial-scale=1"; document.head.append(viewport);
const preview=Boolean(window.AIRBRIDGE_PREVIEW);
document.body.innerHTML=`<main class="wrap">
<section class="hero"><img class="hero-logo" src="${HORTON_LOGO}" width="360" height="120" alt="Horton Systems"><h1>BZP Airbridge</h1><p>Local RF Control Bridge</p><img src="${AIRBRIDGE_ICON}" width="106" height="106" alt="Airbridge remote and radio icon" style="display:block;margin:18px auto 0"></section>
<section class="card"><h2>Bridge status</h2><p class="kicker">Your remote. Connected to your home.</p>
<div class="health"><div><small>Connection</small><strong id="connection" class="warn">Connecting</strong></div><span class="pulse" id="pulse"></span></div>
<div class="metrics"><div class="metric"><span>Power</span><strong id="power">—</strong></div><div class="metric"><span>Speed +</span><strong id="up">—</strong></div><div class="metric"><span>Speed −</span><strong id="down">—</strong></div></div>
</section>
<section class="card"><h2>Remote controls</h2><p class="kicker">Commands automatically enable transmission. Actual fan state is unconfirmed.</p>
<div class="health"><div><small>Radio transmission</small><strong id="txstate" class="warn">Disabled</strong></div></div>
<button id="tx" disabled>Enable transmission</button>
<div class="actions" style="margin-top:14px"><button data-command="Power toggle" disabled>Power</button><button data-command="Speed up" disabled>Speed +</button><button data-command="Speed down" disabled>Speed −</button></div></section>
<section class="card"><h2>Sync fan state</h2><p class="kicker">HomeKit resumes the last known state when Airbridge reconnects after a power loss.</p>
<dl class="system"><dt>Home Assistant estimate</dt><dd id="fan-estimate">Waiting for Home Assistant</dd></dl>
<form id="fan-sync-form"><label for="fan-sync-state">What is the fan doing now?</label><select id="fan-sync-state"><option value="Off">Off</option><option value="Low">On · Low</option><option value="Medium">On · Medium</option><option value="High">On · High</option></select><button id="fan-sync" disabled>Sync fan state</button></form>
<p id="fan-sync-status" class="notice" role="status" aria-live="polite">Choose the actual fan state if the estimate is wrong. Sync updates Home Assistant and HomeKit without sending a radio command.</p><p class="help">Requires the current Airbridge Home Assistant package. The estimate can differ if the fan changes while Airbridge is offline.</p></section>
<section class="card"><h2>Learn your remote</h2><p class="kicker">Select a command, start listening, then press that button on your original remote.</p>
<label for="slot">Command to learn</label><select id="slot"><option value="Learn power">Power toggle</option><option value="Learn speed up">Speed up</option><option value="Learn speed down">Speed down</option></select>
<button id="learn" disabled>Start 20-second capture</button>
<div id="capture-feedback" class="capture-feedback">
<svg class="capture-graphic" viewBox="0 0 120 100" width="100" height="84" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><rect x="16" y="18" width="38" height="67" rx="10"/><circle class="remote-key" cx="35" cy="38" r="7"/><path d="M27 60h16m-16 10h16"/><path class="signal signal-one" d="M66 31q15 19 0 38"/><path class="signal signal-two" d="M79 21q23 29 0 58"/><path class="signal signal-three" d="M93 11q31 39 0 78"/></g></svg>
<div><strong id="capture-title">Ready to learn</strong><p id="activity" role="status" aria-live="polite">Choose a command, then start capture.</p></div></div>
<div class="grid2"><button data-command="Save capture" disabled>Save capture</button><button data-command="Cancel capture" disabled>Cancel</button></div>
<p class="help">Learning disables transmission. Save only a capture from your remote. Allow 65 seconds for storage before unplugging.</p></section>
<section class="card"><h2>System</h2><p class="kicker">Device diagnostics and commissioning profile.</p><dl class="system"><dt>Wi-Fi signal</dt><dd id="wifi">—</dd><dt>Uptime</dt><dd id="uptime">—</dd><dt>Radio profile</dt><dd>See firmware configuration</dd><dt>Hardware</dt><dd>ESP32-C3 + CC1101</dd><dt>Fan compatibility</dt><dd>Power replay verified; state is estimated</dd></dl></section>
<section class="card"><h2>Home Assistant</h2><p class="kicker">Connect using the ESPHome integration.</p>
<dl class="system"><dt>Bridge address</dt><dd id="ha-address"></dd><dt>API port</dt><dd>6053</dd></dl>
<ol><li>In Home Assistant, add the ESPHome integration using the bridge address above.</li><li>With the bridge already running, hold its <strong>BOOT</strong> button for at least 2 seconds, then release. BOOT is the button marked BOOT beside the USB-C port—not RESET.</li><li>Within 30 seconds, click <strong>Reveal encryption key</strong> below, then copy it into Home Assistant.</li></ol>
<p class="help">Do not hold BOOT while powering on or resetting. Each physical press permits one reveal. The displayed key clears after 30 seconds or when you leave this tab. Use only on a trusted network: this page uses unencrypted HTTP, and another client could request the key during the unlock window.</p>
<button id="ha-reveal" data-pairing disabled>Reveal encryption key</button>
<div id="ha-secret" hidden><label for="ha-key">Encryption key</label><input id="ha-key" readonly autocomplete="off" spellcheck="false"><div class="grid2"><button id="ha-copy" data-pairing disabled>Copy key</button><button id="ha-hide" data-pairing disabled>Hide key</button></div></div>
<p id="ha-status" class="notice" role="status" aria-live="polite">Locked. Follow the BOOT-button steps above to reveal your key.</p></section>
<section class="card"><h2>Configure Wi-Fi</h2><p class="kicker">Connect Airbridge to your home’s 2.4 GHz network.</p>
<form id="wifi-form"><label for="wifi-ssid">Network name (SSID)</label><input id="wifi-ssid" name="ssid" autocomplete="off" maxlength="32" required placeholder="Enter network name">
<label for="wifi-password">Wi-Fi password</label><input id="wifi-password" name="password" type="password" autocomplete="new-password" minlength="8" maxlength="63" required placeholder="Enter network password">
<button type="submit" disabled>Configure Wi-Fi</button></form>
<p class="notice" id="wifi-status" role="status" aria-live="polite">Your current network stays saved until the new connection succeeds.</p>
<p class="help">Applying briefly disconnects this page. Reopen bzp-airbridge.local on the new network. If it cannot connect within 45 seconds, the bridge restores the previous network. Use only on a trusted local network; this device’s settings page uses HTTP.</p></section>
<section class="card"><h2>Software updates</h2><p class="kicker">GitHub update delivery is not implemented in this beta. ESPHome OTA is available.</p>
<dl class="system"><dt>Installed version</dt><dd id="version">—</dd><dt>Release source</dt><dd>Not configured</dd><dt>Auto updates</dt><dd id="auto-state">Off</dd></dl>
<button id="auto-updates" role="switch" aria-checked="false" disabled>Enable auto updates</button>
<button data-command="Check for updates" disabled>Check for updates</button>
<p class="notice" id="update-status" role="status" aria-live="polite">Release source not configured</p>
<p class="help">Your preference is saved on the device. Downloads and installation remain unavailable until a release source is configured.</p></section>
<section class="card"><h2>Device controls</h2><p class="kicker">Restart the bridge without erasing saved settings or remote commands.</p>
<button data-command="Reboot bridge" disabled>Reboot bridge</button>
<p class="help">The connection will briefly drop. Unsaved captures are discarded, and radio transmission is disabled after restart.</p></section>
<p class="foot">BZP Airbridge · Build your remote. Keep control local.</p></main>`;
const entities=new Map();let connected=false;let enabled=false;let busy=false;let listening=false;
const $=id=>document.getElementById(id);
let pairingBusy=false, pairingTimer;
$("ha-address").textContent=preview?"bzp-airbridge.local":location.hostname;
function hidePairingKey(){
  clearTimeout(pairingTimer);$("ha-key").value="";$("ha-secret").hidden=true;
  $("ha-copy").disabled=$("ha-hide").disabled=true;
}
$("ha-reveal").addEventListener("click",async()=>{
  if(preview||!connected||pairingBusy)return;
  hidePairingKey();pairingBusy=true;render();
  try{
    const response=await fetch("/airbridge/pairing",{method:"POST",headers:{"X-Airbridge-Request":"pairing"},body:"",cache:"no-store",signal:AbortSignal.timeout(8000)});
    const key=await response.text();
    if(!response.ok)throw Error(response.status===409?"Locked: hold BOOT for 2 seconds, release, then click Reveal within 30 seconds.":"Unable to reveal key. Try again after a physical BOOT press.");
    if(document.hidden)return;
    if(!/^[A-Za-z0-9+/]{43}=$/.test(key))throw Error("Invalid response from bridge.");
    $("ha-key").value=key;$("ha-secret").hidden=false;
    $("ha-status").textContent="Key revealed for 30 seconds. Paste it into Home Assistant. Keep it private.";
    pairingTimer=setTimeout(()=>{hidePairingKey();$("ha-status").textContent="Key hidden. Hold BOOT again for another reveal.";},30000);
  }catch(error){$("ha-status").textContent=error.message;}
  finally{pairingBusy=false;render();}
});
$("ha-hide").addEventListener("click",()=>{hidePairingKey();$("ha-status").textContent="Key hidden. Hold BOOT again for another reveal.";});
$("ha-copy").addEventListener("click",async()=>{
  const field=$("ha-key");if(!field.value)return;
  try{
    if(navigator.clipboard&&window.isSecureContext)await navigator.clipboard.writeText(field.value);
    else {field.focus();field.select();if(!document.execCommand("copy"))throw Error("manual");}
    $("ha-status").textContent="Copied. Paste into Home Assistant. Your clipboard keeps the key until replaced.";
  }catch{field.focus();field.select();$("ha-status").textContent="Key selected. Use your browser’s Copy command, then paste into Home Assistant.";}
});
document.addEventListener("visibilitychange",()=>{if(document.hidden){hidePairingKey();$("ha-status").textContent="Key hidden. Hold BOOT again for another reveal.";}});
window.addEventListener("pagehide",hidePairingKey);
function render(){
  $("capture-feedback").classList.toggle("listening",listening&&connected&&!preview);
  if(!connected&&!preview)$("capture-title").textContent="Waiting for connection";
  document.querySelectorAll("button:not([data-builder]):not([data-pairing])").forEach(b=>b.disabled=preview||!connected||busy);
  $("ha-reveal").disabled=preview||!connected||busy||pairingBusy;
  $("ha-copy").disabled=$("ha-hide").disabled=!$("ha-key").value;
  $("tx").disabled=preview||!connected||busy||!entities.has("Enable transmission");
  $("fan-sync").disabled=preview||!connected||busy||!entities.has("Fan state sync");
  document.querySelectorAll("[data-command]").forEach(b=>{
    const n=b.dataset.command; const slot={"Power toggle":"Power command saved","Speed up":"Speed up command saved","Speed down":"Speed down command saved"}[n];
    b.disabled=preview||!connected||busy||!entities.has(n)||(slot&&(listening||!isOn(entities.get(slot))));
  });
  $("txstate").textContent=enabled?"Enabled":"Disabled";
  $("txstate").className=enabled?"":"warn";
  $("tx").textContent=enabled?"Disable transmission":"Enable transmission";
  const auto=isOn(entities.get("Auto updates"));
  $("auto-state").textContent=auto?"On · awaiting release source":"Off";
  $("auto-updates").textContent=auto?"Disable auto updates":"Enable auto updates";
  $("auto-updates").setAttribute("aria-checked",String(Boolean(auto)));
  $("auto-updates").disabled=preview||!connected||busy||!entities.has("Auto updates");
}
function isOn(e){return e && (e.value===true||e.state==="ON"||e.value===1);}
function update(e){
  if(!e||typeof e.id!=="string")return;
  const name=e.name||e.id.split("/").pop();
  entities.set(name,{...entities.get(name),...e});
  if(name==="Enable transmission") enabled=isOn(entities.get(name));
  if(name==="Fan estimate"&&e.state!==undefined)$("fan-estimate").textContent=String(e.state);
  const ids={"Bridge activity":"activity","Wi-Fi signal":"wifi","Uptime":"uptime","Update status":"update-status","Firmware version":"version"};
  if(ids[name] && e.state!==undefined) $(ids[name]).textContent=String(e.state);
  if(name==="Bridge activity"&&e.state!==undefined){
    const state=String(e.state);
    listening=state.startsWith("Listening");
    $("capture-title").textContent=listening?"Press your remote button now":state.startsWith("Candidate received")?"Command received — ready to save":state.startsWith("Saved")?"Command saved":state.startsWith("Capture timed out")?"No command received — try again":state.startsWith("Capture cancelled")?"Capture cancelled":"Ready to learn";
  }
  for(const [n,id] of [["Power command saved","power"],["Speed up command saved","up"],["Speed down command saved","down"]]){
    if(name===n) $(id).textContent=isOn(entities.get(n))?"Saved":"Empty";
  }
  render();
}
async function command(name,action="press"){
  if(preview||!connected||busy)return;
  if(name==="Reboot bridge"&&!window.confirm("Reboot Airbridge now? Unsaved captures will be discarded. Saved settings and commands will be kept."))return;
  const entity=entities.get(name); if(!entity){$("activity").textContent="Control unavailable; reconnect to the bridge.";return;}
  busy=true;render();
  try{
    const path="/"+entity.id.split("/").map(encodeURIComponent).join("/")+"/"+action;
    const response=await fetch(path,{method:"POST",credentials:"same-origin",signal:AbortSignal.timeout(8000)});
    if(!response.ok)throw Error("Request failed ("+response.status+")");
    // Do not invent a resulting state. The device's event stream confirms it.
  }catch(error){$("activity").textContent=error.message;}
  finally{busy=false;render();}
}
document.querySelectorAll("[data-command]").forEach(b=>b.addEventListener("click",()=>command(b.dataset.command)));
$("fan-sync-form").addEventListener("submit",async event=>{
  event.preventDefault();
  const entity=entities.get("Fan state sync");
  if(preview||!connected||busy||!entity)return;
  busy=true;render();
  try{
    const path="/"+entity.id.split("/").map(encodeURIComponent).join("/")+"/set?"+new URLSearchParams({option:$("fan-sync-state").value});
    const response=await fetch(path,{method:"POST",signal:AbortSignal.timeout(8000)});
    if(!response.ok)throw Error("Sync request failed ("+response.status+")");
    $("fan-sync-status").textContent="Sync requested. The Home Assistant estimate above confirms the result. No radio command was sent.";
  }catch(error){$("fan-sync-status").textContent=error.message;}
  finally{busy=false;render();}
});
$("wifi-form").addEventListener("submit",async event=>{
  event.preventDefault();
  if(preview||!connected||busy)return;
  const ssid=$("wifi-ssid").value, password=$("wifi-password").value;
  if(new TextEncoder().encode(ssid).length>32){$("wifi-status").textContent="Network name must be at most 32 bytes.";return;}
  busy=true;render();
  try {
    const response=await fetch("/airbridge/wifi",{method:"POST",credentials:"same-origin",headers:{"X-Airbridge-Request":"wifi"},body:new URLSearchParams({ssid,password}),signal:AbortSignal.timeout(8000)});
    const message=await response.text();
    if(!response.ok)throw Error(message||"Network change failed");
    $("wifi-status").textContent=message;
  }catch(error){$("wifi-status").textContent=error.message+". If the page disconnected, check the new network before retrying.";}
  finally{$("wifi-password").value="";busy=false;render();}
});
$("learn").addEventListener("click",()=>command($("slot").value));
$("tx").addEventListener("click",()=>command("Enable transmission",enabled?"turn_off":"turn_on"));
$("auto-updates").addEventListener("click",()=>command("Auto updates",isOn(entities.get("Auto updates"))?"turn_off":"turn_on"));
if(preview){
  $("connection").textContent="Design preview";$("connection").className="warn";
  $("activity").textContent="Preview only — controls are disabled; no device is connected.";
  $("power").textContent=$("up").textContent=$("down").textContent="Empty";render();
}else{
  const events=new EventSource("/events");
  events.onopen=()=>{connected=true;$("connection").textContent="Connected";$("connection").className="";$("pulse").style.background="var(--green)";render();};
  events.onerror=()=>{connected=false;listening=false;$("connection").textContent="Reconnecting";$("connection").className="warn";$("pulse").style.background="var(--amber)";render();};
  for(const event of ["state","state_detail_all"]) events.addEventListener(event,e=>{try{update(JSON.parse(e.data));}catch(error){console.warn("Invalid state event",error);}});
}
