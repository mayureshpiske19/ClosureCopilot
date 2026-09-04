"""ClosureCopilot — Backend Closure Copilot (product UI).

A unified multi-agent dashboard:
  Overview · PPA Analyzer · Constraint Promotion · UPF Signoff · Regression · Physical · Ask

Run:  streamlit run src/closurecopilot/ui/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from closurecopilot import config, llm
from closurecopilot.orchestrator import Supervisor
from closurecopilot.rag import get_kb
from closurecopilot.modules import promotion, regression, physical, upf_signoff

st.set_page_config(page_title="ClosureCopilot", page_icon="🛠️", layout="wide")

SEV_COLOR = {"High": "#e5484d", "Medium": "#f5a623", "Low": "#3fb950"}
LAYER_BADGE = {"RTL": "#8957e5", "SDC (constraints)": "#1f6feb",
               "UPF (power intent)": "#bf8700", "Synthesis setup": "#57606a"}
DOMAIN_ICON = {"timing": "⏱️", "power": "🔋", "area": "📐", "synthesis": "🧩",
               "upf": "⚡", "sdc": "📎", "promotion": "🔗", "regression": "📉",
               "physical": "🧱"}


@st.cache_resource
def get_supervisor():
    return Supervisor()


@st.cache_data(show_spinner=False)
def load_ppa():
    from closurecopilot.orchestrator import run_on_samples
    return run_on_samples()


@st.cache_data(show_spinner=False)
def load_modules():
    S = config.SAMPLES_DIR
    return {
        "promotion": promotion.run_on_samples(S),
        "regression": regression.run_on_samples(S),
        "physical": physical.run_on_samples(S),
        "upf": upf_signoff.run_on_samples(S),
    }


def sev_pill(sev):
    return (f"<span style='background:{SEV_COLOR.get(sev,'#888')};color:#fff;"
            f"padding:2px 8px;border-radius:10px;font-size:0.72rem;'>{sev}</span>")


def layer_pill(layer):
    return (f"<span style='background:{LAYER_BADGE.get(layer,'#555')};color:#fff;"
            f"padding:2px 8px;border-radius:6px;font-size:0.78rem;'>Fix in {layer}</span>")


def render_item(it):
    f, fx = it.finding, it.fix
    icon = DOMAIN_ICON.get(f.domain, "•")
    with st.container(border=True):
        c = st.columns([0.72, 0.28])
        with c[0]:
            st.markdown(f"{icon} **{f.title}**  {sev_pill(f.severity)}", unsafe_allow_html=True)
            st.caption(f"📍 {f.location or '—'}   ·   source: {f.source}")
            st.write(f.detail)
        with c[1]:
            if fx:
                st.markdown(layer_pill(fx.layer), unsafe_allow_html=True)
                st.caption(f"confidence {fx.confidence:.0%}")
        if fx:
            st.markdown(f"**Why / how:** {fx.rationale}")
            if fx.snippet:
                lang = ("tcl" if fx.layer in ("SDC (constraints)", "UPF (power intent)")
                        else "verilog" if fx.layer == "RTL" else "bash")
                st.code(fx.snippet, language=lang)
            if fx.tradeoff:
                st.markdown("🔀 PPA trade-off — " +
                            "  ·  ".join(f"**{k}**: {v}" for k, v in fx.tradeoff.items()))
            if fx.references:
                st.caption("📚 grounded in: " + ", ".join(fx.references))


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("## 🛠️ ClosureCopilot")
    st.caption("Backend Closure Copilot — a multi-agent PPA & constraints suite for RTL")
    online = config.is_online()
    st.markdown(f"**Engine:** {'🟢 Azure OpenAI' if online else '🟡 Offline (deterministic)'}")
    s = get_kb().stats()
    st.markdown(f"**RAG:** {s['global_chunks']} global · {s['design_chunks']} design-context")
    st.divider()
    st.caption("Agents")
    for a in get_supervisor().agents:
        st.markdown(f"- {a.name}")
    st.markdown("- 🔗 Constraint-Promotion Agent")
    st.markdown("- 📉 Regression-Detective Agent")
    st.markdown("- 🧱 Physical-Aware Agent")

# ------------------------------------------------------------------ header
st.markdown("# ClosureCopilot")
st.markdown("#### The backend closure copilot — it tells RTL designers **where** each fix "
            "belongs: RTL, constraints (SDC), or UPF.")

ppa = load_ppa()
mods = load_modules()

tabs = st.tabs(["📊 Overview", "🎯 PPA Analyzer", "🔗 Constraint Promotion",
                "⚡ UPF Signoff", "📉 Regression Detective", "🧱 Physical-Aware", "💬 Ask"])

# ---- Overview -----------------------------------------------------------
with tabs[0]:
    total = len(ppa.items) + sum(len(v) for v in mods.values())
    highs = (sum(1 for it in ppa.items if it.finding.severity == "High")
             + sum(1 for v in mods.values() for it in v if it.finding.severity == "High"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total findings", total)
    c2.metric("High severity", highs)
    c3.metric("Agents", len(get_supervisor().agents) + 3)
    c4.metric("Backend inputs", "7 report types")
    st.info(f"**Supervisor summary** — {ppa.summary}")
    st.markdown("#### Modules")
    grid = st.columns(5)
    cards = [("🎯 PPA Analyzer", len(ppa.items), "fix-routing across P/P/A"),
             ("🔗 Constraint Promotion", len(mods['promotion']), "IP→top reconcile"),
             ("⚡ UPF Signoff", len(mods['upf']), "power-intent checks"),
             ("📉 Regression Detective", len(mods['regression']), "commit attribution"),
             ("🧱 Physical-Aware", len(mods['physical']), "congestion→RTL")]
    for col, (title, n, sub) in zip(grid, cards):
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.markdown(f"### {n}")
                st.caption(sub)
    st.caption("Novel vs. internal prior art: fix-layer routing · UPF corrections · "
               "IP→top promotion · PPA commit attribution.")

# ---- PPA Analyzer -------------------------------------------------------
with tabs[1]:
    st.markdown("### PPA Analyzer — ranked findings with fix-routing")
    domains = ["all"] + sorted({it.finding.domain for it in ppa.items})
    pick = st.radio("Filter", domains, horizontal=True, label_visibility="collapsed")
    for it in ppa.ranked():
        if pick == "all" or it.finding.domain == pick:
            render_item(it)

# ---- Constraint Promotion ----------------------------------------------
with tabs[2]:
    st.markdown("### Constraint Promotion & Reconciliation (IP → Top)")
    st.caption("Reconciles block/IP SDC against the integrator's top SDC. "
               "🟢 No internal prior art found for this.")
    for it in sorted(mods["promotion"], key=lambda x: x.severity_rank):
        render_item(it)

# ---- UPF Signoff --------------------------------------------------------
with tabs[3]:
    st.markdown("### UPF / Low-Power Signoff")
    st.caption("The power-intent counterpart to an SDC checker.")
    st.markdown("#### Signoff checklist")
    for label, status, note in upf_signoff.checklist(mods["upf"]):
        st.markdown(f"- {status} — **{label}**")
    st.divider()
    for it in sorted(mods["upf"], key=lambda x: x.severity_rank):
        render_item(it)

# ---- Regression Detective ----------------------------------------------
with tabs[4]:
    st.markdown("### PPA Regression Detective — \"git-blame for PPA\"")
    st.caption("Diffs two backend runs and attributes each regression to the commit that "
               "last touched the block.")
    if not mods["regression"]:
        st.success("No regressions between the two runs.")
    for it in sorted(mods["regression"], key=lambda x: x.severity_rank):
        render_item(it)

# ---- Physical-Aware -----------------------------------------------------
with tabs[5]:
    st.markdown("### Physical-Aware RTL Feedback")
    st.caption("Reads P&R congestion and feeds back RTL restructuring hints "
               "(the physical→RTL gap).")
    for it in sorted(mods["physical"], key=lambda x: x.severity_rank):
        render_item(it)

# ---- Ask ----------------------------------------------------------------
with tabs[6]:
    st.markdown("### Ask the copilot")
    q = st.chat_input("e.g. Which issues should I fix in constraints vs RTL?")
    if q:
        st.chat_message("user").write(q)
        kb = get_kb()
        chunks = kb.retrieve(q)
        ctx = "\n\n".join(f"[{c.store}] {c.title}\n{c.text}" for c in chunks)
        allitems = list(ppa.ranked()) + [it for v in mods.values() for it in v]
        fctx = "\n".join(f"- ({it.finding.domain}/{it.finding.severity}) {it.finding.title} "
                         f"→ fix in {it.fix.layer}" for it in allitems)
        ans = llm.chat(
            system=("You are ClosureCopilot, a senior backend/PPA closure engineer. Answer "
                    "using the findings and knowledge context. Be concise and specific."),
            user=f"QUESTION: {q}\n\nFINDINGS:\n{fctx}\n\nKNOWLEDGE:\n{ctx}")
        if not ans:
            hits = [it for it in allitems
                    if any(w in (it.finding.title + it.finding.detail + it.fix.layer).lower()
                           for w in q.lower().split())] or allitems[:6]
            ans = "**(offline mode)** Based on the current analysis:\n\n" + "\n".join(
                f"- {it.finding.title} → **fix in {it.fix.layer}**" for it in hits[:8])
        st.chat_message("assistant").markdown(ans)
