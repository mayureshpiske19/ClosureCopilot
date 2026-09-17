"""Build a premium, self-contained HTML dashboard from results.json (embedded, offline)."""
import os, json

HERE = os.path.dirname(__file__)
data = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
payload = json.dumps(data)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>ClosureCopilot — Backend Closure Console</title>
<style>
:root{
  --nav:#0b1533; --nav2:#0e1c44; --navln:#22315f; --navink:#cdd8f5; --navmut:#7f8fbf;
  --bg:#f5f7fc; --panel:#ffffff; --ink:#141a2b; --mut:#5c6a86; --soft:#8593ad;
  --line:#e6eaf3; --line2:#eef1f8;
  --brand:#4f46e5; --brand2:#7c3aed; --teal:#0ea5a4; --sky:#2563eb;
  --high:#e11d48; --med:#e08600; --low:#16a34a;
  --rtl:#7c3aed; --sdc:#2563eb; --upf:#d97706; --synth:#64748b;
  --sh1:0 1px 2px rgba(20,26,43,.06),0 1px 3px rgba(20,26,43,.05);
  --sh2:0 6px 22px rgba(20,26,43,.08),0 2px 6px rgba(20,26,43,.05);
  --r:14px;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,-apple-system,Arial,sans-serif;background:var(--bg);
  color:var(--ink);display:flex;min-height:100vh;-webkit-font-smoothing:antialiased}
::selection{background:#dfe0ff}
/* ---------- sidebar ---------- */
.sidebar{width:264px;flex:0 0 264px;background:linear-gradient(180deg,var(--nav),var(--nav2));
  color:var(--navink);padding:22px 16px;position:sticky;top:0;height:100vh;display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:12px;padding:4px 8px 18px;border-bottom:1px solid var(--navln)}
.brand .mk{width:40px;height:40px;border-radius:11px;background:linear-gradient(135deg,var(--brand),var(--brand2));
  display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 6px 16px rgba(79,70,229,.4)}
.brand h1{font-size:18px;margin:0;font-weight:800;letter-spacing:.2px;color:#fff}
.brand .tg{font-size:11px;color:var(--navmut);margin-top:2px;font-weight:600}
.nav{margin:14px 0;display:flex;flex-direction:column;gap:3px}
.navi{display:flex;align-items:center;gap:11px;padding:10px 12px;border-radius:10px;cursor:pointer;
  color:var(--navink);font-size:13.5px;font-weight:600;transition:.14s;border:1px solid transparent}
.navi .ic{width:20px;text-align:center;font-size:15px;opacity:.9}
.navi .ct{margin-left:auto;font-size:11px;color:var(--navmut);background:#1a2a55;padding:1px 8px;border-radius:20px}
.navi:hover{background:#152451}
.navi.active{background:linear-gradient(135deg,rgba(79,70,229,.28),rgba(124,58,237,.22));
  border-color:#3b3f8f;color:#fff}
.navi.active .ct{background:#4f46e5;color:#fff}
.side-card{margin-top:auto;background:#0c1730;border:1px solid var(--navln);border-radius:12px;padding:13px 14px;font-size:12px}
.side-card .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--med);margin-right:7px}
.side-card .k{color:var(--navmut);margin-top:8px}
.side-card b{color:#fff}
.credit{color:var(--navmut);font-size:11px;text-align:center;margin-top:12px}
/* ---------- main ---------- */
.main{flex:1;min-width:0;display:flex;flex-direction:column}
.topbar{background:var(--panel);border-bottom:1px solid var(--line);padding:16px 30px;
  display:flex;align-items:center;gap:18px;position:sticky;top:0;z-index:5;box-shadow:var(--sh1)}
.topbar .pt{font-size:19px;font-weight:800;letter-spacing:.2px}
.topbar .ps{font-size:12.5px;color:var(--mut);margin-top:1px}
.badge-live{margin-left:auto;font-size:12px;font-weight:700;color:var(--teal);
  background:#e6fbfa;border:1px solid #bdeeec;padding:6px 12px;border-radius:20px}
.content{padding:26px 30px 60px;max-width:1180px}
/* ---------- kpis ---------- */
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px;
  box-shadow:var(--sh1);position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--brand)}
.kpi.k2::before{background:var(--high)} .kpi.k3::before{background:var(--rtl)} .kpi.k4::before{background:var(--sdc)}
.kpi .n{font-size:32px;font-weight:800;letter-spacing:-.5px}
.kpi .l{color:var(--mut);font-size:12.5px;margin-top:3px;font-weight:600}
.kpi .hint{color:var(--soft);font-size:11px;margin-top:6px}
/* ---------- cards / panels ---------- */
.panel{display:none;animation:fade .18s ease}.panel.active{display:block}
@keyframes fade{from{opacity:0;transform:translateY(5px)}to{opacity:1}}
.band{background:linear-gradient(120deg,#eef1ff,#f6f0ff);border:1px solid #e3e5fb;border-radius:var(--r);
  padding:16px 20px;margin-bottom:16px}
.band .lab{font-size:11px;font-weight:800;letter-spacing:1px;color:var(--brand);text-transform:uppercase}
.band p{margin:6px 0 0;line-height:1.55;font-size:14px;color:#2a3350}
.corr{background:#eafcf3;border:1px solid #bfead2;border-radius:var(--r);padding:14px 20px;margin-bottom:16px}
.corr h3{margin:0 0 6px;font-size:13px;color:#0a7a44;text-transform:uppercase;letter-spacing:.6px}
.corr li{margin:4px 0;color:#155e3b;font-size:13.5px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.sec-h{font-size:11px;color:var(--soft);text-transform:uppercase;letter-spacing:1.1px;font-weight:800;margin:2px 0 10px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px;
  margin:14px 0;box-shadow:var(--sh1);transition:box-shadow .15s,transform .15s}
.card:hover{box-shadow:var(--sh2)}
.chart-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px;box-shadow:var(--sh1)}
.row{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}
.title{font-weight:700;font-size:15.5px;letter-spacing:.1px}
.loc{color:var(--mut);font-size:12px;margin:5px 0 9px;font-family:'Cascadia Code',Consolas,monospace}
.detail{color:#39435c;font-size:13.5px;line-height:1.55}
.pill{display:inline-block;padding:3px 9px;border-radius:6px;font-size:10.5px;font-weight:800;
  text-transform:uppercase;letter-spacing:.4px;vertical-align:middle;margin-left:6px}
.sev-High{background:#fdeaef;color:var(--high);border:1px solid #f6c9d4}
.sev-Medium{background:#fdf2e2;color:var(--med);border:1px solid #f5dcb0}
.sev-Low{background:#e8f8ee;color:var(--low);border:1px solid #c2ecd0}
.layer{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:9px;font-size:12.5px;font-weight:800;color:#fff;white-space:nowrap}
.layer::before{content:"";width:7px;height:7px;border-radius:50%;background:rgba(255,255,255,.85)}
.conf{color:var(--soft);font-size:11.5px;margin-top:6px;text-align:right;font-weight:600}
.why{margin:13px 0 4px;font-size:13.5px;color:#2b3450;line-height:1.55}
.why b{color:var(--brand)}
pre{background:#0d1730;border:1px solid #1c2c56;border-radius:10px;padding:13px 15px;overflow:auto;
  font-family:'Cascadia Code',Consolas,monospace;font-size:12.5px;color:#d8e3ff;margin:11px 0;line-height:1.5}
.trade{margin:10px 0 2px;font-size:13px;color:#42506e}
.trade .tk{display:inline-block;background:#f1f3fa;border:1px solid var(--line);border-radius:7px;
  padding:3px 9px;margin:3px 5px 0 0;font-size:12px}
.trade .tk b{color:var(--ink)}
.refs{color:var(--soft);font-size:11.5px;margin-top:10px;border-top:1px solid var(--line2);padding-top:9px}
/* filters */
.filters{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 6px}
.chip{padding:7px 14px;border-radius:8px;background:var(--panel);border:1px solid var(--line);
  color:var(--mut);cursor:pointer;font-size:12.5px;font-weight:600;box-shadow:var(--sh1);transition:.13s}
.chip:hover{color:var(--ink)}
.chip.active{background:var(--brand);color:#fff;border-color:var(--brand)}
/* checklist */
.chk{display:flex;gap:12px;align-items:center;background:var(--panel);border:1px solid var(--line);
  border-radius:12px;padding:14px 18px;margin:9px 0;box-shadow:var(--sh1)}
.chk .st{font-weight:800;font-size:13px;padding:5px 12px;border-radius:8px}
.pass{color:var(--low);background:#e8f8ee;border:1px solid #c2ecd0}
.fail{color:var(--high);background:#fdeaef;border:1px solid #f6c9d4}
/* charts */
.bars{display:flex;gap:14px;align-items:flex-end;height:150px;padding:22px 6px 0;position:relative}
.bars .base{position:absolute;left:0;right:0;bottom:0;border-top:1px solid var(--line)}
.bar{flex:1;border-radius:7px 7px 0 0;min-height:6px;position:relative;transition:height .4s}
.bar span{position:absolute;top:-21px;left:0;right:0;text-align:center;font-size:13px;font-weight:800;color:var(--ink)}
.bar em{position:absolute;bottom:-24px;left:0;right:0;text-align:center;font-size:11px;color:var(--mut);font-style:normal;font-weight:600}
/* ask */
.askbar{display:flex;gap:10px;margin:12px 0}
.askbar input{flex:1;padding:13px 16px;border-radius:11px;border:1px solid var(--line);background:var(--panel);
  color:var(--ink);font-size:14px;font-family:inherit;box-shadow:var(--sh1)}
.askbar input:focus{outline:none;border-color:var(--brand);box-shadow:0 0 0 3px #e5e4ff}
.askbar button{padding:13px 26px;border:0;border-radius:11px;cursor:pointer;font-weight:800;color:#fff;
  background:linear-gradient(135deg,var(--brand),var(--brand2));box-shadow:0 6px 16px rgba(79,70,229,.35)}
.ans{background:linear-gradient(120deg,#eef1ff,#f6f0ff);border:1px solid #e3e5fb;border-radius:var(--r);padding:16px 20px;margin:6px 0 4px}
.ans .loc{color:var(--brand);font-weight:700}
.ans ul{margin:6px 0}
@media(max-width:1000px){.kpis{grid-template-columns:1fr 1fr}.grid2{grid-template-columns:1fr}
  .sidebar{display:none}}
</style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand"><div class="mk">◆</div>
      <div><h1>ClosureCopilot</h1><div class="tg">BACKEND CLOSURE CONSOLE</div></div></div>
    <nav class="nav" id="nav"></nav>
    <div class="side-card">
      <div><span class="dot"></span><b id="engineName">Offline</b> engine</div>
      <div class="k">Knowledge base</div>
      <div><b id="kbline"></b></div>
    </div>
    <div class="credit">ClosureCopilot · Mayuresh Piske<br>© 2026 Microsoft</div>
  </aside>

  <div class="main">
    <div class="topbar">
      <div><div class="pt" id="pageTitle">Overview</div>
        <div class="ps" id="pageSub">Ranked backend findings with fix-layer routing</div></div>
      <div class="badge-live">● Live analysis</div>
    </div>
    <div class="content">
      <div class="kpis" id="kpis"></div>
      <div id="panels"></div>
    </div>
  </div>

<script>
const DATA = __PAYLOAD__;
const LAYER_COLORS={"RTL":"#7c3aed","SDC (constraints)":"#2563eb","UPF (power intent)":"#d97706","Synthesis setup":"#64748b"};
const DOMAIN_ICON={timing:"⏱",power:"⚡",area:"▦",synthesis:"◈",upf:"⏻",sdc:"◇",promotion:"⇗",regression:"↯",physical:"▤"};
const esc=s=>(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");

const allItems=DATA.ppa.concat(Object.values(DATA.modules).flat());
const layerCount={}; allItems.forEach(x=>{if(x.fix)layerCount[x.fix.layer]=(layerCount[x.fix.layer]||0)+1;});

function lyr(fx){const c=LAYER_COLORS[fx.layer]||"#555";
  return `<span class="layer" style="background:${c}">Fix in ${esc(fx.layer)}</span>`;}
function tradeHtml(t){return Object.entries(t).map(([k,v])=>`<span class="tk"><b>${esc(k)}</b> ${esc(String(v))}</span>`).join("");}
function itemCard(it){const f=it,fx=it.fix||{};const icon=DOMAIN_ICON[f.domain]||"•";
  return `<div class="card" data-domain="${f.domain}" data-layer="${fx.layer||''}">
    <div class="row"><div style="flex:1">
      <div class="title"><span style="color:${LAYER_COLORS[fx.layer]||'#4f46e5'}">${icon}</span> ${esc(f.title)}
        <span class="pill sev-${f.severity}">${f.severity}</span></div>
      <div class="loc">▸ ${esc(f.location||'—')} &nbsp; · &nbsp; ${esc(f.source||'')}</div>
      <div class="detail">${esc(f.detail)}</div></div>
      <div style="text-align:right;min-width:160px">${fx.layer?lyr(fx)+`<div class="conf">confidence ${Math.round((fx.confidence||0)*100)}%</div>`:''}</div>
    </div>
    ${fx.rationale?`<div class="why"><b>Diagnosis:</b> ${esc(fx.rationale)}</div>`:''}
    ${fx.snippet?`<pre>${esc(fx.snippet)}</pre>`:''}
    ${fx.tradeoff?`<div class="trade">PPA trade-off &nbsp;${tradeHtml(fx.tradeoff)}</div>`:''}
    ${(fx.references&&fx.references.length)?`<div class="refs">Grounded in — ${esc(fx.references.join(" · "))}</div>`:''}
  </div>`;}

// KPIs
const modTot=Object.values(DATA.modules).reduce((a,v)=>a+v.length,0);
const total=DATA.ppa.length+modTot;
const highs=allItems.filter(x=>x.severity==='High').length;
const rtl=layerCount['RTL']||0;
const cons=(layerCount['SDC (constraints)']||0)+(layerCount['UPF (power intent)']||0);
document.getElementById('engineName').textContent=DATA.mode==='offline'?'Offline':'Azure OpenAI';
document.getElementById('kbline').textContent=`${DATA.kb.global_chunks} global · ${DATA.kb.design_chunks} design-context`;
document.getElementById('kpis').innerHTML=[
 ['Total findings',total,'across 7 backend report types','k1'],
 ['High severity',highs,'need attention first','k2'],
 ['RTL fixes',rtl,'routed to source code','k3'],
 ['Constraint / UPF fixes',cons,'SDC & power-intent','k4'],
].map(([l,n,h,c])=>`<div class="kpi ${c}"><div class="n">${n}</div><div class="l">${l}</div><div class="hint">${h}</div></div>`).join('');

// nav / tabs
const TABS=[
 {id:'overview',ic:'▣',label:'Overview',sub:'Ranked backend findings with fix-layer routing',ct:''},
 {id:'ppa',ic:'◎',label:'PPA Analyzer',sub:'Power · Performance · Area — with corrected snippets',ct:DATA.ppa.length},
 {id:'promotion',ic:'⇗',label:'Constraint Promotion',sub:'Reconcile IP / block SDC up to the top level',ct:DATA.modules.promotion.length},
 {id:'upf',ic:'⏻',label:'UPF Signoff',sub:'Isolation · retention · clock-gating realization',ct:DATA.modules.upf.length},
 {id:'regression',ic:'↯',label:'Regression Detective',sub:'Diff two runs · attribute the regression',ct:DATA.modules.regression.length},
 {id:'physical',ic:'▤',label:'Physical-Aware',sub:'Congestion → RTL restructuring hints',ct:DATA.modules.physical.length},
 {id:'ask',ic:'✦',label:'Ask',sub:'Ask the copilot about your findings',ct:''},
];
document.getElementById('nav').innerHTML=TABS.map((t,i)=>
 `<div class="navi ${i===0?'active':''}" data-t="${t.id}"><span class="ic">${t.ic}</span>${t.label}
   ${t.ct!==''?`<span class="ct">${t.ct}</span>`:''}</div>`).join('');

// panels
function bars(groups,colors){const max=Math.max(...Object.values(groups),1);
 return `<div class="bars"><div class="base"></div>${Object.entries(groups).map(([k,v])=>
  `<div class="bar" style="height:${Math.max(v/max*120,6)}px;background:${colors[k]}"><span>${v}</span><em>${k}</em></div>`).join('')}</div>`;}
function severityCard(){const g={High:0,Medium:0,Low:0};allItems.forEach(x=>g[x.severity]=(g[x.severity]||0)+1);
 return `<div class="chart-card"><div class="sec-h">Findings by severity</div>
  ${bars(g,{High:'#e11d48',Medium:'#e08600',Low:'#16a34a'})}</div>`;}
function layerChartCard(){const o=['RTL','SDC (constraints)','UPF (power intent)','Synthesis setup'];
 const g={};o.forEach(k=>g[k.split(' ')[0]]=layerCount[k]||0);
 return `<div class="chart-card"><div class="sec-h">Fixes by layer</div>
  ${bars(g,{RTL:'#7c3aed','SDC':'#2563eb','UPF':'#d97706','Synthesis':'#64748b'})}</div>`;}
const modCards=[
 ['◎ PPA Analyzer',DATA.ppa.length,'fix-routing P/P/A','#4f46e5'],
 ['⇗ Constraint Promotion',DATA.modules.promotion.length,'IP→top reconcile','#2563eb'],
 ['⏻ UPF Signoff',DATA.modules.upf.length,'power-intent checks','#d97706'],
 ['↯ Regression Detective',DATA.modules.regression.length,'change attribution','#e11d48'],
 ['▤ Physical-Aware',DATA.modules.physical.length,'congestion→RTL','#0ea5a4'],
];
const overview=`
 <div class="band"><div class="lab">Supervisor summary</div><p>${esc(DATA.summary)}</p></div>
 ${(DATA.correlations&&DATA.correlations.length)?`<div class="corr"><h3>◆ Cross-domain insight</h3>
   <ul>${DATA.correlations.map(c=>`<li>${esc(c)}</li>`).join('')}</ul></div>`:''}
 <div class="grid2">${severityCard()}${layerChartCard()}</div>
 <div class="sec-h" style="margin-top:20px">Modules</div>
 <div class="kpis" style="grid-template-columns:repeat(5,1fr)">
   ${modCards.map(([t,n,s,c])=>`<div class="kpi" style="box-shadow:var(--sh1)">
     <div style="font-weight:800;font-size:13px;color:${c}">${t}</div>
     <div class="n" style="font-size:26px">${n}</div><div class="hint">${s}</div></div>`).join('')}
 </div>`;
function ppaPanel(){const domains=['all',...new Set(DATA.ppa.map(x=>x.domain))];
 return `<div class="filters" id="ppaF">${domains.map((d,i)=>
   `<div class="chip ${i===0?'active':''}" data-d="${d}">${d}</div>`).join('')}</div>
   <div id="ppaList">${DATA.ppa.map(itemCard).join('')}</div>`;}
function modPanel(k){return DATA.modules[k].map(itemCard).join('')||'<div class="card">No items.</div>';}
function upfPanel(){const chk=DATA.upf_checklist.map(c=>{const p=c.status.includes('PASS');
   return `<div class="chk"><span class="st ${p?'pass':'fail'}">${p?'PASS':'FAIL'}</span><b>${esc(c.label)}</b></div>`;}).join('');
 return `<div class="sec-h">Signoff checklist</div>${chk}<div class="sec-h" style="margin-top:16px">Findings</div>${modPanel('upf')}`;}
function askPanel(){const ex=["Which issues should I fix in constraints vs RTL?","What are the high clock power problems?",
   "Show me everything about dma_ctrl","Which fixes go in UPF?","What timing violations exist?"];
 return `<div class="card"><div class="sec-h">Ask the copilot — offline, over ${allItems.length} findings</div>
   <div class="askbar"><input id="askIn" placeholder="e.g. Which issues should I fix in constraints vs RTL?"/>
   <button id="askBtn">Ask ✦</button></div>
   <div class="filters">${ex.map(q=>`<div class="chip" data-q="${q.replace(/"/g,'&quot;')}">${q}</div>`).join('')}</div></div>
   <div id="askOut"></div>`;}
const PANEL_HTML={overview,ppa:ppaPanel(),promotion:modPanel('promotion'),upf:upfPanel(),
  regression:modPanel('regression')||'<div class="card">No regressions.</div>',physical:modPanel('physical'),ask:askPanel()};
document.getElementById('panels').innerHTML=TABS.map((t,i)=>
  `<div class="panel ${i===0?'active':''}" data-p="${t.id}">${PANEL_HTML[t.id]}</div>`).join('');

// interactions
const navEl=document.getElementById('nav'),panelsEl=document.getElementById('panels');
navEl.addEventListener('click',e=>{const t=e.target.closest('.navi');if(!t)return;
  document.querySelectorAll('.navi').forEach(x=>x.classList.remove('active'));t.classList.add('active');
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.dataset.p===t.dataset.t));
  const tab=TABS.find(x=>x.id===t.dataset.t);
  document.getElementById('pageTitle').textContent=tab.label;
  document.getElementById('pageSub').textContent=tab.sub;
  window.scrollTo({top:0,behavior:'smooth'});});
panelsEl.addEventListener('click',e=>{const c=e.target.closest('#ppaF .chip');if(!c)return;
  document.querySelectorAll('#ppaF .chip').forEach(x=>x.classList.remove('active'));c.classList.add('active');
  const d=c.dataset.d;document.querySelectorAll('#ppaList .card').forEach(card=>{
    card.style.display=(d==='all'||card.dataset.domain===d)?'':'none';});});

// Ask
const STOP=new Set("the a an of to in on is are and or for with by as at be this that it its what which how show me my all i should do does can you give find are there about".split(" "));
function runAsk(q){const out=document.getElementById('askOut');if(!out)return;
  const kw=(q.toLowerCase().match(/[a-z_][a-z0-9_]+/g)||[]).filter(t=>!STOP.has(t));
  const ql=q.toLowerCase();
  const wantLayer=/constraint|sdc/.test(ql)?'SDC (constraints)':(/\bupf\b|power intent|isolation|retention/.test(ql)?'UPF (power intent)':(/\brtl\b/.test(ql)?'RTL':null));
  let sc=allItems.map(it=>{const hay=(it.title+" "+it.detail+" "+it.location+" "+(it.fix?it.fix.layer+" "+it.fix.rationale:"")).toLowerCase();
    let s=kw.reduce((a,t)=>a+(hay.includes(t)?1:0),0);if(wantLayer&&it.fix&&it.fix.layer===wantLayer)s+=2;return{it,s};})
    .filter(x=>x.s>0).sort((a,b)=>b.s-a.s);
  if(!sc.length)sc=allItems.slice(0,6).map(it=>({it,s:0}));
  const hits=sc.slice(0,8).map(x=>x.it),byL={};
  hits.forEach(it=>{if(it.fix)(byL[it.fix.layer]=byL[it.fix.layer]||[]).push(it.title);});
  const ans=Object.entries(byL).map(([L,a])=>`<b style="color:${LAYER_COLORS[L]||'#4f46e5'}">Fix in ${esc(L)}:</b>
    <ul>${a.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`).join('');
  out.innerHTML=`<div class="ans"><div class="loc">◆ Offline answer · matched ${hits.length} finding(s)</div>${ans||'No matching findings.'}</div>`+hits.map(itemCard).join('');
  out.scrollIntoView({behavior:'smooth',block:'nearest'});}
panelsEl.addEventListener('click',e=>{const b=e.target.closest('#askBtn'),c=e.target.closest('[data-p="ask"] .chip');
  if(b){const v=document.getElementById('askIn').value.trim();if(v)runAsk(v);}
  else if(c){const q=c.dataset.q,inp=document.getElementById('askIn');if(inp)inp.value=q;runAsk(q);}});
panelsEl.addEventListener('keydown',e=>{if(e.target.id==='askIn'&&e.key==='Enter'){const v=e.target.value.trim();if(v)runAsk(v);}});
</script>
</body>
</html>"""

html = HTML.replace("__PAYLOAD__", payload)
out = os.path.join(HERE, "dashboard.html")
open(out, "w", encoding="utf-8").write(html)
print("wrote", out, f"({len(html)//1024} KB)")
