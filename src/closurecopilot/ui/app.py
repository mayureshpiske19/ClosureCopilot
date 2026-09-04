"""ClosureCopilot — Streamlit dashboard.

Run:  streamlit run src/closurecopilot/ui/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# make `closurecopilot` importable when launched via `streamlit run`
SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import streamlit as st

from closurecopilot import config
from closurecopilot.orchestrator import Supervisor
from closurecopilot.rag import get_kb
from closurecopilot import llm

st.set_page_config(page_title="ClosureCopilot", page_icon="🛠️", layout="wide")

DOMAIN_ICON = {"timing": "⏱️", "power": "🔋", "area": "📐",
               "synthesis": "🧩", "upf": "⚡", "sdc": "📎"}
SEV_COLOR = {"High": "#e5484d", "Medium": "#f5a623", "Low": "#3fb950"}
LAYER_BADGE = {"RTL": "#8957e5", "SDC (constraints)": "#1f6feb",
               "UPF (power intent)": "#bf8700", "Synthesis setup": "#57606a"}


@st.cache_resource
def get_supervisor():
    return Supervisor()


def sev_pill(sev: str) -> str:
    return (f"<span style='background:{SEV_COLOR.get(sev,'#888')};color:#fff;"
            f"padding:2px 8px;border-radius:10px;font-size:0.75rem;'>{sev}</span>")


def layer_pill(layer: str) -> str:
    return (f"<span style='background:{LAYER_BADGE.get(layer,'#555')};color:#fff;"
            f"padding:2px 8px;border-radius:6px;font-size:0.8rem;'>Fix in {layer}</span>")


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("## 🛠️ ClosureCopilot")
    st.caption("AI-native multi-agent PPA closure copilot for RTL")
    online = config.is_online()
    st.markdown(f"**Engine:** {'🟢 Azure OpenAI' if online else '🟡 Offline (deterministic)'}")
    kb = get_kb()
    s = kb.stats()
    st.markdown(f"**RAG:** {s['global_chunks']} global · {s['design_chunks']} design-context chunks")
    st.divider()
    st.markdown("### Reports")
    use_samples = st.checkbox("Use bundled sample reports", value=True)
    uploads = st.file_uploader(
        "…or upload backend reports (STA / synth / power / area / UPF / SDC)",
        accept_multiple_files=True, type=["rpt", "log", "sdc", "upf", "txt"])
    run = st.button("▶ Analyze", type="primary", use_container_width=True)


# ------------------------------------------------------------------ header
st.markdown("# PPA Closure Analysis")
st.caption("Any backend report in → ranked, RTL-level fixes out. It tells you **where** to "
           "fix each issue: RTL, constraints (SDC), or UPF — with corrected snippets.")


def collect_inputs():
    named_texts, paths = [], []
    if uploads:
        for uf in uploads:
            named_texts.append((uf.name, uf.getvalue().decode("utf-8", "ignore")))
    if use_samples or not uploads:
        for p in sorted(Path(config.SAMPLES_DIR).glob("*")):
            if p.suffix.lower() in (".rpt", ".log", ".sdc", ".upf"):
                paths.append(p)
    return named_texts, paths


if run or "result" not in st.session_state:
    sup = get_supervisor()
    named_texts, paths = collect_inputs()
    findings = sup.ingest_texts(named_texts) + sup.ingest_paths(paths)
    st.session_state.result = sup.analyze(findings)

result = st.session_state.result

# ------------------------------------------------------------------ metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Findings", len(result.items))
c2.metric("High severity", sum(1 for it in result.items if it.finding.severity == "High"))
layers = {}
for it in result.items:
    if it.fix:
        layers[it.fix.layer] = layers.get(it.fix.layer, 0) + 1
c3.metric("RTL fixes", layers.get("RTL", 0))
c4.metric("Constraint/UPF fixes",
          layers.get("SDC (constraints)", 0) + layers.get("UPF (power intent)", 0))

st.info(f"**Supervisor summary** — {result.summary}")

# cross-domain insights
corr = get_supervisor()._correlations(result)
if corr:
    with st.container(border=True):
        st.markdown("#### 🔗 Cross-domain insights")
        for n in corr:
            st.markdown(f"- {n}")

# ------------------------------------------------------------------ findings
st.markdown("## Ranked findings & fixes")
domains = ["all"] + sorted({it.finding.domain for it in result.items})
pick = st.radio("Filter", domains, horizontal=True, label_visibility="collapsed")

for it in result.ranked():
    f, fx = it.finding, it.fix
    if pick != "all" and f.domain != pick:
        continue
    icon = DOMAIN_ICON.get(f.domain, "•")
    with st.container(border=True):
        top = st.columns([0.72, 0.28])
        with top[0]:
            st.markdown(f"{icon} **{f.title}**  {sev_pill(f.severity)}",
                        unsafe_allow_html=True)
            st.caption(f"📍 {f.location or '—'}   ·   source: {f.source}")
            st.write(f.detail)
        with top[1]:
            if fx:
                st.markdown(layer_pill(fx.layer), unsafe_allow_html=True)
                st.caption(f"confidence {fx.confidence:.0%}")
        if fx:
            st.markdown(f"**Why / how:** {fx.rationale}")
            if fx.snippet:
                lang = "tcl" if fx.layer in ("SDC (constraints)", "UPF (power intent)") \
                    else ("verilog" if fx.layer == "RTL" else "bash")
                st.code(fx.snippet, language=lang)
            if fx.tradeoff:
                td = "  ·  ".join(f"**{k}**: {v}" for k, v in fx.tradeoff.items())
                st.markdown(f"🔀 PPA trade-off — {td}")
            if fx.references:
                st.caption("📚 grounded in: " + ", ".join(fx.references))

# ------------------------------------------------------------------ chat
st.markdown("## Ask the copilot")
q = st.chat_input("e.g. Which issues should I fix in RTL vs constraints?")
if q:
    st.chat_message("user").write(q)
    kb = get_kb()
    chunks = kb.retrieve(q)
    ctx = "\n\n".join(f"[{c.store}] {c.title}\n{c.text}" for c in chunks)
    findings_ctx = "\n".join(
        f"- ({it.finding.domain}/{it.finding.severity}) {it.finding.title} "
        f"→ fix in {it.fix.layer}" for it in result.ranked())
    ans = llm.chat(
        system=("You are ClosureCopilot, a senior PPA-closure engineer. Answer using the "
                "current findings and the knowledge context. Be concise and specific."),
        user=f"QUESTION: {q}\n\nCURRENT FINDINGS:\n{findings_ctx}\n\nKNOWLEDGE:\n{ctx}")
    if not ans:
        # offline deterministic answer
        hits = [it for it in result.ranked()
                if q.lower() in (it.finding.title + it.finding.detail + it.fix.layer).lower()]
        hits = hits or result.ranked()[:5]
        ans = "**(offline mode)** Based on the current analysis:\n\n" + "\n".join(
            f"- {it.finding.title} → **fix in {it.fix.layer}** ({it.fix.rationale[:120]}…)"
            for it in hits[:6])
    st.chat_message("assistant").markdown(ans)
