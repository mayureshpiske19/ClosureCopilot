"""Generate the ClosureCopilot architecture diagram (clean white PNG) — accurate flow."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

C_INPUT="#1f6feb"; C_PARSE="#2da44e"; C_SUP="#8957e5"; C_AGENT="#5b6570"
C_FIX="#e5484d"; C_OUT="#2da44e"; C_KB="#0e8088"; C_AZ="#8a94a0"; C_MOD="#c8860a"
C_EDGE="#8a94a0"; C_TXT="#ffffff"; C_DARK="#1a1a1a"; C_MUT="#57606a"

fig, ax = plt.subplots(figsize=(16, 11))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def box(x, y, w, h, text, color, fs=11, tc=C_TXT, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.35,rounding_size=1.1",
                 linewidth=1, edgecolor="#c8ccd2", facecolor=color))
    if sub:
        ax.text(x + w/2, y + h*0.62, text, ha="center", va="center", color=tc, fontsize=fs, fontweight="bold")
        ax.text(x + w/2, y + h*0.28, sub, ha="center", va="center", color=tc, fontsize=fs-2.5)
    else:
        ax.text(x + w/2, y + h/2, text, ha="center", va="center", color=tc, fontsize=fs, fontweight="bold")


def arrow(x1, y1, x2, y2, color=C_EDGE, dashed=False, w=1.4):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                 linewidth=w, color=color, linestyle=(0,(3,3)) if dashed else "solid"))


def clamp(v, lo, hi): return max(lo, min(hi, v))

# title
ax.text(50, 97, "ClosureCopilot — Architecture & Data Flow", ha="center", color=C_DARK,
        fontsize=23, fontweight="bold")
ax.text(50, 93, "any backend report in  →  ranked, fix-routed findings out", ha="center",
        color=C_MUT, fontsize=12.5, style="italic")

# 1) inputs
inputs = ["STA\nTiming","Synthesis\nlog","RTLA\npower","Area","UPF","SDC","P&R\ncongestion"]
iw, ig = 11.2, 1.5
ix0 = (100-(len(inputs)*iw+(len(inputs)-1)*ig))/2
icx = [ix0+iw/2+i*(iw+ig) for i in range(len(inputs))]
ax.text(50, 89.4, "Backend reports (data/samples)", ha="center", color="#8a94a0", fontsize=10.5, style="italic")
for i,t in enumerate(inputs):
    box(ix0+i*(iw+ig), 82.5, iw, 6, t, C_INPUT, fs=9.5)

# 2) parser
box(20, 73.5, 60, 5.8, "Ingestion / Parser Agent", C_PARSE, fs=13, sub="ingestion/parsers.py  ·  detect_type() → Finding objects")
for cx in icx: arrow(cx, 82.5, clamp(cx,22,78), 79.3)

# 3) supervisor + side panels
box(34, 63.8, 32, 6.4, "Supervisor / Orchestrator", C_SUP, fs=13, sub="orchestrator.py")
arrow(50, 73.5, 50, 70.2)
# optional LLM (left) and grounded KB (right) — dashed = optional/grounding
box(2, 63.9, 17, 6.2, "Azure OpenAI", C_AZ, fs=10, sub="llm.py · optional")
box(81, 63.9, 17, 6.2, "Grounded knowledge", C_KB, fs=10, sub="rag/ · design + global")
arrow(19, 67, 34, 67, dashed=True); ax.text(26.5, 68.4, "enrich", ha="center", color="#8a94a0", fontsize=8.5, style="italic")
arrow(81, 67, 66, 67, dashed=True); ax.text(73.5, 68.4, "ground", ha="center", color="#8a94a0", fontsize=8.5, style="italic")

# 4) specialist agents
agents = ["Power","Timing","Area","Synthesis","UPF","Constraints"]
aw, ag = 12, 1.4
ax0 = (100-(len(agents)*aw+(len(agents)-1)*ag))/2
acx = [ax0+aw/2+i*(aw+ag) for i in range(len(agents))]
ax.text(50, 60.4, "Specialist agents  (agents/base.py)", ha="center", color="#8a94a0", fontsize=10, style="italic")
for i,t in enumerate(agents):
    box(ax0+i*(aw+ag), 54, aw, 5.4, t, C_AGENT, fs=10)
    arrow(50, 63.8, acx[i], 59.4)

# 5) fix router
box(24, 44.5, 52, 6, "Fix-Routing / Diagnosis Engine", C_FIX, fs=13,
    sub="fix_router.py  ·  RTL | SDC | UPF | Synth  +  snippet + trade-off")
for cx in acx: arrow(cx, 54, clamp(cx,26,74), 50.5)

# 6) output
box(28, 34.5, 44, 5.8, "Ranked findings (AnalysisResult)", C_OUT, fs=12.5,
    sub="Streamlit app  ·  HTML dashboard  ·  CLI")
arrow(50, 44.5, 50, 40.3)

# ---- side lane: modules reuse the fix-router ----
ax.text(50, 28.5, "Product modules (modules/) — own analysis, reuse the Fix-Router",
        ha="center", color="#8a94a0", fontsize=10.5, style="italic")
mods = [("Constraint\nPromotion","promotion.py"),("UPF\nSignoff","upf_signoff.py"),
        ("Regression\nDetective","regression.py"),("Physical-\nAware","physical.py")]
mw, mg = 20, 2.2
mx0 = (100-(len(mods)*mw+(len(mods)-1)*mg))/2
for i,(t,fn) in enumerate(mods):
    mx = mx0+i*(mw+mg)
    box(mx, 20.5, mw, 6.4, t, C_MOD, fs=10.5, sub=fn)
    # dashed link up to fix-router
    arrow(mx+mw/2, 26.9, mx+mw/2, 29.3, color=C_MOD, dashed=True)
# a bracket note that they feed output
ax.text(50, 16.8, "↑ all reuse fix_router.py, and surface in the same dashboard",
        ha="center", color="#8a94a0", fontsize=9.5, style="italic")

# legend
ax.add_patch(FancyArrowPatch((7,10.5),(13,10.5),arrowstyle="-|>",mutation_scale=12,color=C_EDGE,linewidth=1.4))
ax.text(14, 10.5, "main pipeline", va="center", color=C_MUT, fontsize=9.5)
ax.add_patch(FancyArrowPatch((34,10.5),(40,10.5),arrowstyle="-|>",mutation_scale=12,color=C_EDGE,linewidth=1.4,linestyle=(0,(3,3))))
ax.text(41, 10.5, "optional / grounding / module link", va="center", color=C_MUT, fontsize=9.5)

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=170, facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png")
