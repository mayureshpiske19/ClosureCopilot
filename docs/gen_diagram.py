"""ClosureCopilot architecture — clean bus-routed technical diagram (white PNG)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

# palette
INK="#1b2333"; MUT="#5c6a86"; SOFT="#8a94a8"
INPUT="#2563eb"; INPUT_BG="#e8f0ff"
PARSE="#0f9d58"; PARSE_BG="#e6f6ec"
SUP="#7c3aed"; SUP_BG="#f0e9fe"
AGENT="#334155"; AGENT_BG="#eef1f6"
FIX="#e11d48"; FIX_BG="#fdeaef"
OUT="#0f9d58"; OUT_BG="#e6f6ec"
KB="#0e8088"; KB_BG="#e3f7f6"
AZ="#64748b"; AZ_BG="#f1f3f8"
MOD="#d97706"; MOD_BG="#fff3e2"
BUS="#b7c0d3"; ARR="#7b869c"

fig, ax = plt.subplots(figsize=(15.5, 11.6))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def box(x, y, w, h, title, color, bg, fs=11, sub=None, tsub=SOFT):
    # soft shadow
    ax.add_patch(FancyBboxPatch((x+0.25, y-0.35), w, h, boxstyle="round,pad=0.3,rounding_size=1.4",
                 linewidth=0, facecolor="#dfe3ec", zorder=1))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.4",
                 linewidth=1.6, edgecolor=color, facecolor=bg, zorder=2))
    if sub:
        ax.text(x+w/2, y+h*0.60, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=3)
        ax.text(x+w/2, y+h*0.26, sub, ha="center", va="center", color=tsub, fontsize=fs-3.0, zorder=3, family="monospace")
    else:
        ax.text(x+w/2, y+h/2, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=3)

def hline(x1, x2, y, c=BUS, w=2.4):
    ax.plot([x1, x2], [y, y], color=c, lw=w, solid_capstyle="round", zorder=1)
def vline(x, y1, y2, c=BUS, w=2.4, dashed=False):
    ax.plot([x, x], [y1, y2], color=c, lw=w, solid_capstyle="round",
            linestyle=(0,(2.5,2.5)) if dashed else "solid", zorder=1)
def head(x, y, d="down", c=ARR, s=1.0):
    # arrowhead triangle pointing d at (x,y)
    if d=="down":  pts=[(x, y),(x-0.9*s, y+1.5*s),(x+0.9*s, y+1.5*s)]
    if d=="up":    pts=[(x, y),(x-0.9*s, y-1.5*s),(x+0.9*s, y-1.5*s)]
    if d=="left":  pts=[(x, y),(x+1.5*s, y-0.9*s),(x+1.5*s, y+0.9*s)]
    if d=="right": pts=[(x, y),(x-1.5*s, y-0.9*s),(x-1.5*s, y+0.9*s)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=c, zorder=4))

# ---------------- title ----------------
ax.text(50, 97.4, "ClosureCopilot — Architecture & Data Flow", ha="center", color=INK,
        fontsize=23, fontweight="bold")
ax.text(50, 93.6, "any backend report in   →   ranked, fix-routed findings out", ha="center",
        color=MUT, fontsize=13, style="italic")

# ---------------- 1) inputs ----------------
inputs=["STA\nTiming","Synthesis\nlog","RTLA\npower","Area","UPF","SDC","P&R\ncongestion"]
n=len(inputs); iw=11.4; ig=1.7
ix0=(100-(n*iw+(n-1)*ig))/2
icx=[ix0+iw/2+i*(iw+ig) for i in range(n)]
ax.text(50, 90.0, "BACKEND REPORTS  ·  data/samples", ha="center", color=SOFT, fontsize=10.5, fontweight="bold")
for i,t in enumerate(inputs):
    box(ix0+i*(iw+ig), 83.4, iw, 6.0, t, INPUT, INPUT_BG, fs=9.5)
# collector bus under inputs
busY=80.4
for cx in icx: vline(cx, 83.4, busY)          # stubs down
hline(icx[0], icx[-1], busY)                  # horizontal bus
vline(50, busY, 78.6); head(50, 78.6, "down") # single feeder into parser

# ---------------- 2) parser ----------------
box(21, 72.6, 58, 6.0, "Ingestion / Parser Agent", PARSE, PARSE_BG, fs=13,
    sub="ingestion/parsers.py  ·  detect_type() → Finding")
vline(50, 72.6, 70.4); head(50, 70.4, "down")  # parser -> supervisor

# ---------------- 3) supervisor + side ----------------
box(35, 63.8, 30, 6.4, "Supervisor / Orchestrator", SUP, SUP_BG, fs=12.5, sub="orchestrator.py")
# side: azure (left) + knowledge (right), dashed connectors
box(3, 63.9, 18, 6.2, "Azure OpenAI", AZ, AZ_BG, fs=10, sub="llm.py · optional")
box(79, 63.9, 18, 6.2, "Grounded knowledge", KB, KB_BG, fs=10, sub="rag/ · design+global")
# az -> sup (dashed, arrow into supervisor left)
ax.plot([21,35],[67,67],color=KB,lw=1.8,linestyle=(0,(2.5,2.5)),zorder=1); head(35,67,"right",c=KB)
ax.text(28,68.2,"enrich",ha="center",color=SOFT,fontsize=8.5,style="italic")
# kb -> sup (dashed, arrow into supervisor right)
ax.plot([79,65],[67,67],color=KB,lw=1.8,linestyle=(0,(2.5,2.5)),zorder=1); head(65,67,"left",c=KB)
ax.text(72,68.2,"ground",ha="center",color=SOFT,fontsize=8.5,style="italic")

# supervisor -> agent distribution bus
distY=58.6
vline(50, 63.8, distY)                          # supervisor down to bus

# ---------------- 4) agents ----------------
agents=["Power","Timing","Area","Synthesis","UPF","Constraints"]
m=len(agents); aw=12.2; ag=1.6
ax0=(100-(m*aw+(m-1)*ag))/2
acx=[ax0+aw/2+i*(aw+ag) for i in range(m)]
hline(acx[0], acx[-1], distY)                   # distribution bus
for i,t in enumerate(agents):
    box(ax0+i*(aw+ag), 51.8, aw, 5.4, t, AGENT, AGENT_BG, fs=10)
    vline(acx[i], distY, 57.2); head(acx[i], 57.2, "down")  # bus -> each agent
ax.text(50, 59.7, "SPECIALIST AGENTS  ·  agents/base.py", ha="center", color=SOFT, fontsize=9.5, fontweight="bold")

# agents -> collector bus -> fix
colY=48.4
for cx in acx: vline(cx, 51.8, colY)            # each agent down to collector
hline(acx[0], acx[-1], colY)
vline(50, colY, 45.6); head(50, 45.6, "down")   # single feeder into fix-router

# ---------------- 5) fix router ----------------
box(24, 39.6, 52, 6.0, "Fix-Routing / Diagnosis Engine", FIX, FIX_BG, fs=13,
    sub="fix_router.py  ·  RTL | SDC | UPF | Synth  +  snippet + trade-off")
vline(50, 39.6, 37.2); head(50, 37.2, "down")   # fix -> output

# ---------------- 6) output ----------------
box(29, 30.8, 42, 6.0, "Ranked findings — AnalysisResult", OUT, OUT_BG, fs=12,
    sub="Streamlit app · HTML dashboard · CLI")

# ---------------- module lane ----------------
ax.text(50, 26.2, "PRODUCT MODULES  ·  modules/  —  own analysis, reuse the Fix-Router",
        ha="center", color=SOFT, fontsize=10, fontweight="bold")
mods=[("Constraint\nPromotion","promotion.py"),("UPF\nSignoff","upf_signoff.py"),
      ("Regression\nDetective","regression.py"),("Physical-\nAware","physical.py")]
k=len(mods); mw=19.5; mg=3.0
mx0=(100-(k*mw+(k-1)*mg))/2
mcx=[mx0+mw/2+i*(mw+mg) for i in range(k)]
for i,(t,fn) in enumerate(mods):
    box(mx0+i*(mw+mg), 18.5, mw, 6.4, t, MOD, MOD_BG, fs=10.5, sub=fn)
# dashed reuse: modules up to a bus, then a LEFT-side riser into the fix-router
# (routed left of the Output box so nothing overlaps)
reuseY=28.0
for cx in mcx: vline(cx, 24.9, reuseY, c=MOD, dashed=True)
hline(mcx[0], mcx[-1], reuseY, c=MOD, w=1.8)
riserX=mcx[0]
ax.plot([riserX, riserX],[reuseY, 42.6], color=MOD, lw=1.8, linestyle=(0,(2.5,2.5)), zorder=0)  # up
ax.plot([riserX, 24],[42.6, 42.6], color=MOD, lw=1.8, linestyle=(0,(2.5,2.5)), zorder=0)          # into fix-router
head(24, 42.6, "right", c=MOD)
ax.text(riserX+1.5, 38.5, "reuse", ha="left", color=MOD, fontsize=9, style="italic")

# ---------------- legend ----------------
ly=11.0
ax.plot([8,14],[ly,ly],color=ARR,lw=2.4); head(14,ly,"right")
ax.text(15.2, ly, "main data flow", va="center", color=MUT, fontsize=10)
ax.plot([40,46],[ly,ly],color=KB,lw=1.8,linestyle=(0,(2.5,2.5)))
ax.text(47.2, ly, "optional / grounding / module reuse", va="center", color=MUT, fontsize=10)

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=170, facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png")
