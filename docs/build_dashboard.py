"""Build a self-contained HTML dashboard from results.json (data embedded, works offline)."""
import os, json

HERE = os.path.dirname(__file__)
data = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
payload = json.dumps(data)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ClosureCopilot — Results Dashboard</title>
<style>
  :root{
    --bg:#0b1220; --bg2:#0f1830; --card:#151f38; --card2:#1a2647;
    --ink:#eef2fb; --mut:#9aa7c4; --line:#25335a;
    --blue:#4b8cff; --cyan:#3ccdd8; --green:#38cd8c; --amber:#f0b445; --red:#e5566a; --violet:#9678f0;
    --rtl:#9678f0; --sdc:#4b8cff; --upf:#f0b445; --synth:#7c8aa5;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:'Segoe UI',system-ui,Arial,sans-serif;background:
     radial-gradient(1200px 600px at 80% -10%, #16224480, transparent),
     linear-gradient(180deg,var(--bg),var(--bg2));color:var(--ink);min-height:100vh}
  .wrap{max-width:1280px;margin:0 auto;padding:28px 26px 70px}
  header.top{display:flex;align-items:center;gap:16px;margin-bottom:6px}
  .logo{width:46px;height:46px;border-radius:12px;background:linear-gradient(135deg,var(--blue),var(--violet));
     display:flex;align-items:center;justify-content:center;font-size:24px}
  h1{font-size:30px;margin:0;font-weight:800;letter-spacing:.3px}
  .sub{color:var(--cyan);font-weight:600;margin:2px 0 0}
  .foot-note{color:var(--mut);font-size:12px;margin-top:4px}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0}
  .kpi{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--line);
     border-radius:16px;padding:18px 20px}
  .kpi .n{font-size:34px;font-weight:800}
  .kpi .l{color:var(--mut);font-size:13px;margin-top:2px}
  .summary{background:#12203f;border:1px solid var(--line);border-left:4px solid var(--blue);
     border-radius:12px;padding:16px 20px;margin:6px 0 10px;line-height:1.55}
  .corr{background:#122b25;border:1px solid #1d4a3d;border-left:4px solid var(--green);
     border-radius:12px;padding:14px 20px;margin:10px 0 4px}
  .corr h3{margin:0 0 6px;font-size:15px;color:var(--green)}
  .corr li{margin:4px 0;color:#cfe9df}
  .tabs{display:flex;flex-wrap:wrap;gap:8px;margin:24px 0 8px}
  .tab{padding:10px 16px;border-radius:10px;background:var(--card);border:1px solid var(--line);
     color:var(--mut);cursor:pointer;font-weight:600;font-size:14px;transition:.15s}
  .tab:hover{color:var(--ink)}
  .tab.active{background:linear-gradient(135deg,var(--blue),var(--violet));color:#fff;border-color:transparent}
  .panel{display:none;animation:fade .2s ease}
  .panel.active{display:block}
  @keyframes fade{from{opacity:0;transform:translateY(4px)}to{opacity:1}}
  .filters{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0}
  .chip{padding:6px 12px;border-radius:20px;background:var(--card);border:1px solid var(--line);
     color:var(--mut);cursor:pointer;font-size:13px}
  .chip.active{background:#1c2a4d;color:var(--ink);border-color:var(--blue)}
  .card{background:linear-gradient(180deg,var(--card),#131d36);border:1px solid var(--line);
     border-radius:14px;padding:16px 18px;margin:12px 0}
  .row{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}
  .title{font-weight:700;font-size:16px}
  .loc{color:var(--mut);font-size:12.5px;margin:4px 0 8px}
  .detail{color:#d4ddf2;font-size:14px;line-height:1.5}
  .pill{display:inline-block;padding:3px 10px;border-radius:20px;font-size:11.5px;font-weight:700;color:#0b1220}
  .sev-High{background:var(--red);color:#fff}.sev-Medium{background:var(--amber)}.sev-Low{background:var(--green)}
  .layer{display:inline-block;padding:4px 11px;border-radius:8px;font-size:12.5px;font-weight:700;color:#fff}
  .conf{color:var(--mut);font-size:12px;margin-top:5px;text-align:right}
  .why{margin:12px 0 6px;font-size:14px}.why b{color:var(--cyan)}
  pre{background:#0a122b;border:1px solid var(--line);border-radius:10px;
     padding:12px 14px;overflow:auto;font-family:'Cascadia Code',Consolas,monospace;font-size:13px;
     color:#d7e3ff;margin:8px 0}
  .trade{margin:8px 0;font-size:13.5px;color:#cdd8f0}
  .trade b{color:#fff}
  .refs{color:var(--mut);font-size:12px;margin-top:8px}
  .checklist{display:grid;gap:10px;margin:12px 0}
  .chk{display:flex;gap:12px;align-items:center;background:var(--card);border:1px solid var(--line);
     border-radius:12px;padding:14px 18px}
  .chk .st{font-weight:800}.pass{color:var(--green)}.fail{color:var(--red)}
  .bars{display:flex;gap:8px;align-items:flex-end;height:160px;margin:10px 0 4px}
  .bar{flex:1;border-radius:8px 8px 0 0;background:linear-gradient(180deg,var(--blue),#2a5bd0);
     position:relative;min-height:6px}
  .bar span{position:absolute;top:-22px;left:0;right:0;text-align:center;font-size:12px;color:var(--mut)}
  .bar em{position:absolute;bottom:-22px;left:0;right:0;text-align:center;font-size:11px;color:var(--mut);font-style:normal}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
  .sec-h{font-size:13px;color:var(--mut);text-transform:uppercase;letter-spacing:1px;margin:6px 0}
  @media(max-width:820px){.kpis{grid-template-columns:1fr 1fr}.grid2{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="logo">🛠️</div>
    <div>
      <h1>ClosureCopilot</h1>
      <div class="sub">Backend Closure Results — it decides WHERE each fix belongs: RTL · SDC · UPF</div>
      <div class="foot-note" id="modeline"></div>
    </div>
  </header>

  <div class="kpis" id="kpis"></div>
  <div class="summary" id="summary"></div>
  <div id="corr"></div>

  <div class="tabs" id="tabs"></div>

  <div id="panels"></div>

  <div class="foot-note" style="margin-top:30px;text-align:right">
    ClosureCopilot · Mayuresh Piske · © 2026 Microsoft
  </div>
</div>

<script>
const DATA = __PAYLOAD__;

const LAYER_COLORS = {"RTL":"#9678f0","SDC (constraints)":"#4b8cff","UPF (power intent)":"#f0b445","Synthesis setup":"#7c8aa5"};
const DOMAIN_ICON = {timing:"⏱️",power:"🔋",area:"📐",synthesis:"🧩",upf:"⚡",sdc:"📎",promotion:"🔗",regression:"📉",physical:"🧱"};
const esc = s => (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

function lang(layer){return layer && layer.startsWith("RTL")?"verilog":(layer&&(layer.startsWith("SDC")||layer.startsWith("UPF")))?"tcl":"bash";}

function itemCard(it){
  const f=it, fx=it.fix||{};
  const icon=DOMAIN_ICON[f.domain]||"•";
  const lc=LAYER_COLORS[fx.layer]||"#555";
  let td="";
  if(fx.tradeoff){td=Object.entries(fx.tradeoff).map(([k,v])=>`<b>${esc(k)}</b>: ${esc(String(v))}`).join(" &nbsp;·&nbsp; ");}
  return `<div class="card" data-domain="${f.domain}" data-layer="${fx.layer||''}">
    <div class="row">
      <div style="flex:1">
        <div class="title">${icon} ${esc(f.title)} <span class="pill sev-${f.severity}">${f.severity}</span></div>
        <div class="loc">📍 ${esc(f.location||'—')} &nbsp;·&nbsp; source: ${esc(f.source||'')}</div>
        <div class="detail">${esc(f.detail)}</div>
      </div>
      <div style="text-align:right;min-width:150px">
        ${fx.layer?`<span class="layer" style="background:${lc}">Fix in ${esc(fx.layer)}</span>
        <div class="conf">confidence ${Math.round((fx.confidence||0)*100)}%</div>`:''}
      </div>
    </div>
    ${fx.rationale?`<div class="why"><b>Why / how:</b> ${esc(fx.rationale)}</div>`:''}
    ${fx.snippet?`<pre>${esc(fx.snippet)}</pre>`:''}
    ${td?`<div class="trade">🔀 PPA trade-off — ${td}</div>`:''}
    ${(fx.references&&fx.references.length)?`<div class="refs">📚 grounded in: ${esc(fx.references.join(", "))}</div>`:''}
  </div>`;
}

// KPIs
const modTot = Object.values(DATA.modules).reduce((a,v)=>a+v.length,0);
const total = DATA.ppa.length + modTot;
const highs = DATA.ppa.filter(x=>x.severity==='High').length
  + Object.values(DATA.modules).flat().filter(x=>x.severity==='High').length;
const allItems = DATA.ppa.concat(Object.values(DATA.modules).flat());
const layerCount = {};
allItems.forEach(x=>{if(x.fix){layerCount[x.fix.layer]=(layerCount[x.fix.layer]||0)+1;}});
const rtl = layerCount['RTL']||0;
const cons = (layerCount['SDC (constraints)']||0)+(layerCount['UPF (power intent)']||0);

document.getElementById('modeline').textContent =
  `Engine: ${DATA.mode==='offline'?'🟡 Offline (deterministic)':'🟢 Azure OpenAI'} · RAG: ${DATA.kb.global_chunks} global + ${DATA.kb.design_chunks} design-context chunks`;

document.getElementById('kpis').innerHTML = [
  ['Total findings',total],['High severity',highs],['RTL fixes',rtl],['Constraint / UPF fixes',cons]
].map(([l,n])=>`<div class="kpi"><div class="n">${n}</div><div class="l">${l}</div></div>`).join('');

document.getElementById('summary').innerHTML = `<b style="color:#fff">Supervisor summary</b><br>${esc(DATA.summary)}`;

if(DATA.correlations && DATA.correlations.length){
  document.getElementById('corr').innerHTML =
   `<div class="corr"><h3>🔗 Cross-domain insights</h3><ul>${DATA.correlations.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></div>`;
}

// Tabs
const TABS = [
  {id:'overview', label:'📊 Overview'},
  {id:'ppa', label:'🎯 PPA Analyzer'},
  {id:'promotion', label:'🔗 Constraint Promotion'},
  {id:'upf', label:'⚡ UPF Signoff'},
  {id:'regression', label:'📉 Regression Detective'},
  {id:'physical', label:'🧱 Physical-Aware'},
];
const tabsEl=document.getElementById('tabs'), panelsEl=document.getElementById('panels');
tabsEl.innerHTML = TABS.map((t,i)=>`<div class="tab ${i===0?'active':''}" data-t="${t.id}">${t.label}</div>`).join('');

// Panels
function severityBars(){
  const groups={High:0,Medium:0,Low:0}; allItems.forEach(x=>groups[x.severity]=(groups[x.severity]||0)+1);
  const max=Math.max(...Object.values(groups),1);
  const colors={High:'var(--red)',Medium:'var(--amber)',Low:'var(--green)'};
  return `<div class="bars">${Object.entries(groups).map(([k,v])=>
    `<div class="bar" style="height:${Math.max(v/max*140,6)}px;background:${colors[k]}"><span>${v}</span><em>${k}</em></div>`).join('')}</div>`;
}
function layerBars(){
  const order=['RTL','SDC (constraints)','UPF (power intent)','Synthesis setup'];
  const max=Math.max(...order.map(o=>layerCount[o]||0),1);
  return `<div class="bars">${order.map(o=>
    `<div class="bar" style="height:${Math.max((layerCount[o]||0)/max*140,6)}px;background:${LAYER_COLORS[o]}">
      <span>${layerCount[o]||0}</span><em>${o.split(' ')[0]}</em></div>`).join('')}</div>`;
}
const modCards = [
  ['🎯 PPA Analyzer', DATA.ppa.length, 'fix-routing across P/P/A'],
  ['🔗 Constraint Promotion', DATA.modules.promotion.length, 'IP→top reconcile'],
  ['⚡ UPF Signoff', DATA.modules.upf.length, 'power-intent checks'],
  ['📉 Regression Detective', DATA.modules.regression.length, 'commit attribution'],
  ['🧱 Physical-Aware', DATA.modules.physical.length, 'congestion→RTL'],
];

const overview = `
  <div class="grid2">
    <div class="card"><div class="sec-h">Findings by severity</div>${severityBars()}</div>
    <div class="card"><div class="sec-h">Fixes by layer</div>${layerBars()}</div>
  </div>
  <div class="sec-h" style="margin-top:18px">Modules</div>
  <div class="kpis" style="grid-template-columns:repeat(5,1fr)">
    ${modCards.map(([t,n,s])=>`<div class="kpi"><div style="font-weight:700;font-size:13px">${t}</div>
      <div class="n" style="font-size:28px">${n}</div><div class="l">${s}</div></div>`).join('')}
  </div>`;

function ppaPanel(){
  const domains=['all',...new Set(DATA.ppa.map(x=>x.domain))];
  return `<div class="filters" id="ppaF">${domains.map((d,i)=>
    `<div class="chip ${i===0?'active':''}" data-d="${d}">${d}</div>`).join('')}</div>
    <div id="ppaList">${DATA.ppa.map(itemCard).join('')}</div>`;
}
function modPanel(key){ return DATA.modules[key].map(itemCard).join('') || '<div class="card">No items.</div>'; }
function upfPanel(){
  const chk = DATA.upf_checklist.map(c=>{
    const pass=c.status.includes('PASS');
    return `<div class="chk"><span class="st ${pass?'pass':'fail'}">${pass?'✅ PASS':'❌ FAIL'}</span>
      <div><b>${esc(c.label)}</b></div></div>`;}).join('');
  return `<div class="sec-h">Signoff checklist</div><div class="checklist">${chk}</div>
    <div class="sec-h" style="margin-top:14px">Findings</div>${modPanel('upf')}`;
}

const PANEL_HTML = {
  overview, ppa:ppaPanel(), promotion:modPanel('promotion'),
  upf:upfPanel(), regression:modPanel('regression')||'<div class="card">No regressions.</div>',
  physical:modPanel('physical'),
};
panelsEl.innerHTML = TABS.map((t,i)=>
  `<div class="panel ${i===0?'active':''}" data-p="${t.id}">${PANEL_HTML[t.id]}</div>`).join('');

// interactions
tabsEl.addEventListener('click',e=>{
  const t=e.target.closest('.tab'); if(!t)return;
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  t.classList.add('active');
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.dataset.p===t.dataset.t));
});
panelsEl.addEventListener('click',e=>{
  const c=e.target.closest('#ppaF .chip'); if(!c)return;
  document.querySelectorAll('#ppaF .chip').forEach(x=>x.classList.remove('active'));
  c.classList.add('active');
  const d=c.dataset.d;
  document.querySelectorAll('#ppaList .card').forEach(card=>{
    card.style.display=(d==='all'||card.dataset.domain===d)?'':'none';});
});
</script>
</body>
</html>"""

html = HTML.replace("__PAYLOAD__", payload)
out = os.path.join(HERE, "dashboard.html")
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, f"({len(html)//1024} KB)")
