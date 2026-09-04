# ClosureCopilot

**An AI-Native, Multi-Agent Assistant for RTL PPA Closure**

> Feed it any backend report — RTLA power, synthesis, STA timing, area, UPF, or SDC —
> and a crew of AI agents analyzes **Power, Performance, and Area together**, then tells
> the RTL engineer **exactly where to fix each issue: RTL, constraints (SDC), or UPF** —
> with corrected, copy-paste-ready snippets. Including IP→top constraint promotion.

---

## Why it matters
Power, performance and area (PPA) closure is the #1 grind in silicon design. RTL
engineers wait hours/days for backend runs, then struggle to read reports and trace
issues back to RTL. **No tool reasons across all three PPA domains at RTL stage, or
decides whether a fix belongs in RTL, constraints, or UPF.** ClosureCopilot does.

## What makes it unique
1. **Cross-domain PPA trade-off reasoning** — fixing timing may cost power/area; it ranks by net PPA.
2. **Fix-routing** — RTL vs SDC vs UPF vs synth-setup (the senior-engineer judgment).
3. **Corrected snippets** — ready-to-apply SDC / UPF / RTL fixes.
4. **Constraint promotion** — IP → subsystem → top.
5. **Dual-RAG** — global PPA knowledge + a persistent *Design Context Memory* (specs,
   micro-arch, past reports) so feedback is grounded in *your* design and improves over time.

## Architecture
```
Designer ──> Supervisor / Orchestrator
                 ├─ Ingestion / Parser  (tool-agnostic normalizer)
                 ├─ Power Agent
                 ├─ Timing Agent
                 ├─ Area Agent
                 ├─ Constraints (SDC) Agent
                 ├─ UPF Agent
                 ├─ Synthesis Agent
                 ├─ Constraint-Promotion Agent
                 ├─ RTL Analyzer Agent   (maps findings -> RTL file/line)
                 └─ Fix-Routing / Diagnosis Engine
Knowledge:  Global PPA RAG  +  Design Context Memory (RAG)
Tools:      MCP layer wrapping backend tools (replay-safe for demo)
```

## Tech stack
Python 3.12 · Streamlit UI · ChromaDB (dual RAG) · Azure OpenAI (with a deterministic
**offline mode** so the demo runs even without credentials).

## Quick start
```powershell
# from the ClosureCopilot folder
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# copy env template and (optionally) add Azure OpenAI creds
Copy-Item .env.example .env

# run the app
streamlit run src/closurecopilot/ui/app.py
```
Without Azure credentials the app runs in **offline mode** with deterministic analysis
over the bundled sample reports in `data/samples/`.

## Status
Prototype under active development. See the project plan for phases.
