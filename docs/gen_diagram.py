"""ClosureCopilot architecture — clean bus-routed diagram, edge-exact arrows (white PNG)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

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
BUS="#aab4c8"; ARR="#6b7789"

fig, ax = plt.subplots(figsize=(16.5, 12.8))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

PAD = 0.06  # tiny pad so nominal geometry == visual geometry

def box(x, y, w, h, title, color, bg, fs=13, sub=None):
    ax.add_patch(FancyBboxPatch((x+0.28, y-0.4), w, h,
        boxstyle=f"round,pad={PAD},rounding_size=1.0", lw=0, facecolor="#dde2ec", zorder=1))
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad={PAD},rounding_size=1.0", lw=1.8, edgecolor=color, facecolor=bg, zorder=2))
    if sub:
        ax.text(x+w/2, y+h*0.60, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=3)
        ax.text(x+w/2, y+h*0.25, sub, ha="center", va="center", color=MUT, fontsize=fs-4.0, zorder=3, family="monospace")
    else:
        ax.text(x+w/2, y+h/2, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=3)
    return dict(cx=x+w/2, l=x, r=x+w, t=y+h, b=y)

def hline(x1, x2, y, c=BUS, w=3.0):
    ax.plot([x1, x2], [y, y], color=c, lw=w, solid_capstyle="round", zorder=1)
def vline(x, y1, y2, c=BUS, w=3.0, dashed=False):
    ax.plot([x, x], [y1, y2], color=c, lw=w, solid_capstyle="round",
            linestyle=(0,(2.4,2.2)) if dashed else "solid", zorder=1)
def head(x, y, d="down", c=ARR, s=1.5):
    if d=="down":  pts=[(x, y),(x-s, y+1.7*s),(x+s, y+1.7*s)]
    if d=="up":    pts=[(x, y),(x-s, y-1.7*s),(x+s, y-1.7*s)]
    if d=="left":  pts=[(x, y),(x+1.7*s, y-s),(x+1.7*s, y+s)]
    if d=="right": pts=[(x, y),(x-1.7*s, y-s),(x-1.7*s, y+s)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=c, zorder=5))

# ---------- title ----------
ax.text(50, 97.6, "ClosureCopilot — Architecture & Data Flow", ha="center", color=INK,
        fontsize=26, fontweight="bold")
ax.text(50, 93.8, "any backend report in    →    ranked, fix-routed findings out", ha="center",
        color=MUT, fontsize=15, style="italic")

# ---------- 1) inputs ----------
inputs=["STA\nTiming","Synthesis\nlog","RTLA\npower","Area","UPF","SDC","P&R\ncongestion"]
n=len(inputs); iw=11.6; ig=1.7
ix0=(100-(n*iw+(n-1)*ig))/2
IN=[]
ax.text(50, 90.2, "BACKEND REPORTS  ·  data/samples", ha="center", color=SOFT, fontsize=11.5, fontweight="bold")
for i,t in enumerate(inputs):
    IN.append(box(ix0+i*(iw+ig), 83.0, iw, 6.4, t, INPUT, INPUT_BG, fs=11))
icx=[b["cx"] for b in IN]

# collector bus under inputs -> parser
busY=80.3
for cx in icx: vline(cx, IN[0]["b"], busY)      # from box bottom to bus
hline(icx[0], icx[-1], busY)

# ---------- 2) parser ----------
P=box(20, 72.4, 60, 6.4, "Ingestion / Parser Agent", PARSE, PARSE_BG, fs=15,
      sub="ingestion/parsers.py  ·  detect_type() → Finding")
vline(50, busY, P["t"]); head(50, P["t"], "down")     # bus -> parser TOP

# ---------- 3) supervisor + side ----------
S=box(35, 62.6, 30, 7.0, "Supervisor / Orchestrator", SUP, SUP_BG, fs=14.5, sub="orchestrator.py")
vline(50, P["b"], S["t"]); head(50, S["t"], "down")   # parser BOTTOM -> supervisor TOP

AZ_B=box(2, 62.9, 19, 6.6, "Azure OpenAI", AZ, AZ_BG, fs=12, sub="llm.py · optional")
KB_B=box(79, 62.9, 19, 6.6, "Grounded knowledge", KB, KB_BG, fs=11.5, sub="rag/ · design+global")
midS=(S["t"]+S["b"])/2
ax.plot([AZ_B["r"], S["l"]],[midS, midS], color=KB, lw=2.0, linestyle=(0,(2.4,2.2)), zorder=1)
head(S["l"], midS, "right", c=KB); ax.text((AZ_B["r"]+S["l"])/2, midS+1.4, "enrich", ha="center", color=SOFT, fontsize=10, style="italic")
ax.plot([KB_B["l"], S["r"]],[midS, midS], color=KB, lw=2.0, linestyle=(0,(2.4,2.2)), zorder=1)
head(S["r"], midS, "left", c=KB); ax.text((KB_B["l"]+S["r"])/2, midS+1.4, "ground", ha="center", color=SOFT, fontsize=10, style="italic")

# supervisor -> agent distribution bus
distY=58.4
vline(50, S["b"], distY)                          # supervisor BOTTOM -> bus

# ---------- 4) agents ----------
agents=["Power","Timing","Area","Synthesis","UPF","Constraints"]
m=len(agents); aw=12.6; ag=1.6
ax0=(100-(m*aw+(m-1)*ag))/2
AG=[]
for i,t in enumerate(agents):
    AG.append(box(ax0+i*(aw+ag), 51.4, aw, 5.8, t, AGENT, AGENT_BG, fs=12))
acx=[b["cx"] for b in AG]
hline(acx[0], acx[-1], distY)
for i,b in enumerate(AG):
    vline(acx[i], distY, b["t"]); head(acx[i], b["t"], "down")   # bus -> agent TOP
ax.text(50, 59.6, "SPECIALIST AGENTS  ·  agents/base.py", ha="center", color=SOFT, fontsize=10.5, fontweight="bold")

# agents -> collector bus -> fix
colY=48.2
for i,b in enumerate(AG): vline(acx[i], b["b"], colY)   # agent BOTTOM -> collector
hline(acx[0], acx[-1], colY)

# ---------- 5) fix router ----------
FX=box(24, 39.4, 52, 6.4, "Fix-Routing / Diagnosis Engine", FIX, FIX_BG, fs=15,
       sub="fix_router.py  ·  RTL | SDC | UPF | Synth  +  snippet + trade-off")
vline(50, colY, FX["t"]); head(50, FX["t"], "down")     # collector -> fix TOP

# ---------- 6) output ----------
O=box(29, 30.4, 42, 6.4, "Ranked findings — AnalysisResult", OUT, OUT_BG, fs=14,
      sub="Streamlit app · HTML dashboard · CLI")
vline(50, FX["b"], O["t"]); head(50, O["t"], "down")    # fix BOTTOM -> output TOP

# ---------- module lane ----------
ax.text(50, 25.8, "PRODUCT MODULES  ·  modules/  —  own analysis, reuse the Fix-Router",
        ha="center", color=SOFT, fontsize=10.5, fontweight="bold")
mods=[("Constraint\nPromotion","promotion.py"),("UPF\nSignoff","upf_signoff.py"),
      ("Regression\nDetective","regression.py"),("Physical-\nAware","physical.py")]
k=len(mods); mw=20; mg=3.0
mx0=(100-(k*mw+(k-1)*mg))/2
MD=[]
for i,(t,fn) in enumerate(mods):
    MD.append(box(mx0+i*(mw+mg), 17.6, mw, 6.6, t, MOD, MOD_BG, fs=12, sub=fn))
mcx=[b["cx"] for b in MD]

# dashed reuse: module tops -> bus -> LEFT riser -> into fix-router LEFT edge
reuseY=28.7
for i,b in enumerate(MD): vline(mcx[i], b["t"], reuseY, c=MOD, dashed=True)
hline(mcx[0], mcx[-1], reuseY, c=MOD, w=2.2)
riserX=mcx[0]
midFX=(FX["t"]+FX["b"])/2
ax.plot([riserX, riserX],[reuseY, midFX], color=MOD, lw=2.2, linestyle=(0,(2.4,2.2)), zorder=1)  # up
ax.plot([riserX, FX["l"]],[midFX, midFX], color=MOD, lw=2.2, linestyle=(0,(2.4,2.2)), zorder=1)   # into fix LEFT
head(FX["l"], midFX, "right", c=MOD)
ax.text(riserX+1.8, midFX+2.0, "reuse", ha="left", color=MOD, fontsize=10.5, style="italic")

# ---------- legend ----------
ly=11.5
ax.plot([9,15],[ly,ly],color=ARR,lw=3.0); head(15,ly,"right")
ax.text(16.5, ly, "main data flow", va="center", color=MUT, fontsize=11.5)
ax.plot([42,48],[ly,ly],color=KB,lw=2.0,linestyle=(0,(2.4,2.2)))
ax.text(49.5, ly, "optional / grounding / module reuse", va="center", color=MUT, fontsize=11.5)

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=175, facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png")
