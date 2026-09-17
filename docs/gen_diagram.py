"""ClosureCopilot architecture — direct-arrow professional diagram (white PNG)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

INK="#1b2333"; MUT="#5c6a86"; SOFT="#94a0b5"
INPUT="#2563eb"; INPUT_BG="#eaf1ff"
PARSE="#0f9d58"; PARSE_BG="#e9f7ef"
SUP="#7c3aed"; SUP_BG="#f2ecfe"
AGENT="#334155"; AGENT_BG="#eef1f6"
FIX="#e11d48"; FIX_BG="#fdecf0"
OUT="#0f9d58"; OUT_BG="#e9f7ef"
KB="#0e8088"; KB_BG="#e6f8f7"
AZ="#64748b"; AZ_BG="#f2f4f8"
MOD="#d97706"; MOD_BG="#fff4e5"
CONN="#8d99b0"; GRND="#0e8088"; REUSE="#d97706"

fig, ax = plt.subplots(figsize=(17, 12.6))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def box(x, y, w, h, title, color, bg, fs=13, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=1.0",
        lw=1.9, edgecolor=color, facecolor=bg, zorder=3))
    if sub:
        ax.text(x+w/2, y+h*0.60, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=4)
        ax.text(x+w/2, y+h*0.26, sub, ha="center", va="center", color=MUT, fontsize=fs-4.2, zorder=4, family="monospace")
    else:
        ax.text(x+w/2, y+h/2, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=4)
    return dict(cx=x+w/2, l=x, r=x+w, t=y+h, b=y)

def seg(x1,y1,x2,y2,c=CONN,w=1.9,dashed=False):
    ax.plot([x1,x2],[y1,y2],color=c,lw=w,solid_capstyle="round",
            linestyle=(0,(3.0,2.2)) if dashed else "solid",zorder=2)

def head(x,y,d="down",c=CONN):
    a,b=0.60,1.85
    if d=="down":  pts=[(x,y),(x-a,y+b),(x+a,y+b)]
    if d=="up":    pts=[(x,y),(x-a,y-b),(x+a,y-b)]
    if d=="left":  pts=[(x,y),(x+b,y-a),(x+b,y+a)]
    if d=="right": pts=[(x,y),(x-b,y-a),(x-b,y+a)]
    ax.add_patch(Polygon(pts,closed=True,facecolor=c,edgecolor=c,lw=0,zorder=4))

def arrow_down(x, y_from, y_to, c=CONN):   # vertical arrow ending at y_to (a box top)
    seg(x, y_from, x, y_to, c=c); head(x, y_to, "down", c=c)

# ---------- title ----------
ax.text(50, 97.8, "ClosureCopilot — Architecture & Data Flow", ha="center", color=INK,
        fontsize=27, fontweight="bold")
ax.text(50, 94.0, "any backend report in    →    ranked, fix-routed findings out", ha="center",
        color=MUT, fontsize=15, style="italic")

# ---------- 1) inputs ----------
inputs=["STA\nTiming","Synthesis\nlog","RTLA\npower","Area","UPF","SDC","P&R\ncongestion"]
n=len(inputs); iw=11.6; ig=1.7
itot=n*iw+(n-1)*ig; ix0=(100-itot)/2
ax.text(ix0, 90.7, "BACKEND REPORTS  ·  data/samples", ha="left", color=SOFT, fontsize=11, fontweight="bold")
IN=[box(ix0+i*(iw+ig), 83.4, iw, 6.4, t, INPUT, INPUT_BG, fs=11) for i,t in enumerate(inputs)]

# ---------- 2) ingestion (spans full inputs width) — direct arrow from EACH input ----------
P=box(ix0, 74.4, itot, 6.2, "Ingestion / Parser Agent", PARSE, PARSE_BG, fs=15,
      sub="ingestion/parsers.py  ·  detect_type() → Finding")
for b in IN: arrow_down(b["cx"], b["b"], P["t"])

# ---------- 3) supervisor + side ----------
S=box(35, 63.8, 30, 7.0, "Supervisor / Orchestrator", SUP, SUP_BG, fs=14.5, sub="orchestrator.py")
arrow_down(50, P["b"], S["t"])
AZ_B=box(2, 64.1, 19, 6.4, "Azure OpenAI", AZ, AZ_BG, fs=12, sub="llm.py · optional")
KB_B=box(79, 64.1, 19, 6.4, "Grounded knowledge", KB, KB_BG, fs=11.5, sub="rag/ · design+global")
midS=(S["t"]+S["b"])/2
seg(AZ_B["r"], midS, S["l"], midS, c=GRND, w=1.6, dashed=True); head(S["l"], midS, "right", c=GRND)
ax.text((AZ_B["r"]+S["l"])/2, midS+1.5, "enrich", ha="center", color=SOFT, fontsize=10, style="italic")
seg(KB_B["l"], midS, S["r"], midS, c=GRND, w=1.6, dashed=True); head(S["r"], midS, "left", c=GRND)
ax.text((KB_B["l"]+S["r"])/2, midS+1.5, "ground", ha="center", color=SOFT, fontsize=10, style="italic")

# ---------- 4) agents — org-chart connector from supervisor ----------
agents=["Power","Timing","Area","Synthesis","UPF","Constraints"]
m=len(agents); aw=12.6; ag=1.6
atot=m*aw+(m-1)*ag; ax0=(100-atot)/2
ax.text(ax0, 61.7, "SPECIALIST AGENTS  ·  agents/base.py", ha="left", color=SOFT, fontsize=10.5, fontweight="bold")
AG=[box(ax0+i*(aw+ag), 51.8, aw, 5.8, t, AGENT, AGENT_BG, fs=12) for i,t in enumerate(agents)]
acx=[b["cx"] for b in AG]
trunkY=59.0
seg(50, S["b"], 50, trunkY)                 # supervisor down to trunk
seg(acx[0], trunkY, acx[-1], trunkY)        # horizontal trunk
for b in AG:
    seg(b["cx"], trunkY, b["cx"], b["t"]+0.0); head(b["cx"], b["t"], "down")

# ---------- 5) fix router (spans full agents width) — direct arrow from EACH agent ----------
FX=box(ax0, 42.0, atot, 6.4, "Fix-Routing / Diagnosis Engine", FIX, FIX_BG, fs=15,
       sub="fix_router.py  ·  RTL | SDC | UPF | Synth  +  snippet + trade-off")
for b in AG: arrow_down(b["cx"], b["b"], FX["t"])

# ---------- 6) output ----------
O=box(29, 32.6, 42, 6.4, "Ranked findings — AnalysisResult", OUT, OUT_BG, fs=14,
      sub="Streamlit app · HTML dashboard · CLI")
arrow_down(50, FX["b"], O["t"])

# ---------- module panel + single reuse arrow ----------
mods=[("Constraint\nPromotion","promotion.py"),("UPF\nSignoff","upf_signoff.py"),
      ("Regression\nDetective","regression.py"),("Physical-\nAware","physical.py")]
k=len(mods); mw=20; mg=3.0
mtot=k*mw+(k-1)*mg; mx0=(100-mtot)/2
pnl_l, pnl_r = mx0-3, mx0+mtot+3
ax.add_patch(FancyBboxPatch((pnl_l, 15.0), pnl_r-pnl_l, 11.4,
    boxstyle="round,pad=0.04,rounding_size=1.4", lw=1.5, edgecolor="#e6c48a",
    facecolor="#fffaf1", zorder=1))
ax.text((pnl_l+pnl_r)/2, 24.9, "PRODUCT MODULES  ·  modules/  —  own analysis, reuse the Fix-Router",
        ha="center", color="#b5791f", fontsize=10.5, fontweight="bold", zorder=2)
MD=[box(mx0+i*(mw+mg), 16.2, mw, 6.4, t, MOD, MOD_BG, fs=12, sub=fn) for i,(t,fn) in enumerate(mods)]
# single clean dashed reuse arrow up the left into the fix-router left edge
rx=pnl_l+3.2; midFX=(FX["t"]+FX["b"])/2
seg(rx, 26.4, rx, midFX, c=REUSE, w=1.7, dashed=True)
seg(rx, midFX, FX["l"], midFX, c=REUSE, w=1.7, dashed=True)
head(FX["l"], midFX, "right", c=REUSE)
ax.text(rx+1.6, (26.4+midFX)/2, "reuse", ha="left", va="center", color=REUSE, fontsize=11, style="italic", fontweight="bold")

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=180, facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png")
