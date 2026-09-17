"""ClosureCopilot architecture — professional bus diagram with sharp thin arrows."""
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
CONN="#9aa6bb"      # connector lines + arrowheads (one calm slate)
GRND="#0e8088"      # grounding dashed
REUSE="#d97706"     # module reuse dashed

fig, ax = plt.subplots(figsize=(16.5, 12.6))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

def box(x, y, w, h, title, color, bg, fs=13, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=1.1",
        lw=1.8, edgecolor=color, facecolor=bg, zorder=3,
        path_effects=None))
    if sub:
        ax.text(x+w/2, y+h*0.60, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=4)
        ax.text(x+w/2, y+h*0.26, sub, ha="center", va="center", color=MUT, fontsize=fs-4.2, zorder=4, family="monospace")
    else:
        ax.text(x+w/2, y+h/2, title, ha="center", va="center", color=INK, fontsize=fs, fontweight="bold", zorder=4)
    return dict(cx=x+w/2, l=x, r=x+w, t=y+h, b=y)

def line(x1, y1, x2, y2, c=CONN, w=1.7, dashed=False):
    ax.plot([x1, x2], [y1, y2], color=c, lw=w, solid_capstyle="round",
            linestyle=(0,(3.2,2.4)) if dashed else "solid", zorder=2)

def head(x, y, d="down", c=CONN):
    # sharp, thin arrowhead (narrow base, long point)
    a, b = 0.62, 1.9   # half-width, length
    if d=="down":  pts=[(x, y),(x-a, y+b),(x+a, y+b)]
    if d=="up":    pts=[(x, y),(x-a, y-b),(x+a, y-b)]
    if d=="left":  pts=[(x, y),(x+b, y-a),(x+b, y+a)]
    if d=="right": pts=[(x, y),(x-b, y-a),(x-b, y+a)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=c, lw=0, zorder=4))

# ---------- title ----------
ax.text(50, 97.6, "ClosureCopilot — Architecture & Data Flow", ha="center", color=INK,
        fontsize=26, fontweight="bold")
ax.text(50, 93.9, "any backend report in    →    ranked, fix-routed findings out", ha="center",
        color=MUT, fontsize=15, style="italic")

# ---------- 1) inputs ----------
inputs=["STA\nTiming","Synthesis\nlog","RTLA\npower","Area","UPF","SDC","P&R\ncongestion"]
n=len(inputs); iw=11.6; ig=1.7
ix0=(100-(n*iw+(n-1)*ig))/2
ax.text(50, 90.2, "BACKEND REPORTS  ·  data/samples", ha="center", color=SOFT, fontsize=11, fontweight="bold")
IN=[box(ix0+i*(iw+ig), 83.0, iw, 6.4, t, INPUT, INPUT_BG, fs=11) for i,t in enumerate(inputs)]
icx=[b["cx"] for b in IN]
busY=80.2
for cx in icx: line(cx, IN[0]["b"], cx, busY)
line(icx[0], busY, icx[-1], busY)

# ---------- 2) parser ----------
P=box(20, 72.2, 60, 6.4, "Ingestion / Parser Agent", PARSE, PARSE_BG, fs=15,
      sub="ingestion/parsers.py  ·  detect_type() → Finding")
line(50, busY, 50, P["t"]); head(50, P["t"], "down")

# ---------- 3) supervisor + side ----------
S=box(35, 62.4, 30, 7.0, "Supervisor / Orchestrator", SUP, SUP_BG, fs=14.5, sub="orchestrator.py")
line(50, P["b"], 50, S["t"]); head(50, S["t"], "down")
AZ_B=box(2, 62.7, 19, 6.6, "Azure OpenAI", AZ, AZ_BG, fs=12, sub="llm.py · optional")
KB_B=box(79, 62.7, 19, 6.6, "Grounded knowledge", KB, KB_BG, fs=11.5, sub="rag/ · design+global")
midS=(S["t"]+S["b"])/2
line(AZ_B["r"], midS, S["l"], midS, c=GRND, w=1.5, dashed=True); head(S["l"], midS, "right", c=GRND)
ax.text((AZ_B["r"]+S["l"])/2, midS+1.5, "enrich", ha="center", color=SOFT, fontsize=10, style="italic")
line(KB_B["l"], midS, S["r"], midS, c=GRND, w=1.5, dashed=True); head(S["r"], midS, "left", c=GRND)
ax.text((KB_B["l"]+S["r"])/2, midS+1.5, "ground", ha="center", color=SOFT, fontsize=10, style="italic")

# supervisor -> distribution bus -> agents
distY=58.2
line(50, S["b"], 50, distY)

# ---------- 4) agents ----------
agents=["Power","Timing","Area","Synthesis","UPF","Constraints"]
m=len(agents); aw=12.6; ag=1.6
ax0=(100-(m*aw+(m-1)*ag))/2
ax.text(50, 59.6, "SPECIALIST AGENTS  ·  agents/base.py", ha="center", color=SOFT, fontsize=10.5, fontweight="bold")
AG=[box(ax0+i*(aw+ag), 51.2, aw, 5.8, t, AGENT, AGENT_BG, fs=12) for i,t in enumerate(agents)]
acx=[b["cx"] for b in AG]
line(acx[0], distY, acx[-1], distY)
for i,b in enumerate(AG):
    line(acx[i], distY, acx[i], b["t"]); head(acx[i], b["t"], "down")

# agents -> collector -> fix
colY=48.0
for i,b in enumerate(AG): line(acx[i], b["b"], acx[i], colY)
line(acx[0], colY, acx[-1], colY)

# ---------- 5) fix router ----------
FX=box(24, 39.2, 52, 6.4, "Fix-Routing / Diagnosis Engine", FIX, FIX_BG, fs=15,
       sub="fix_router.py  ·  RTL | SDC | UPF | Synth  +  snippet + trade-off")
line(50, colY, 50, FX["t"]); head(50, FX["t"], "down")

# ---------- 6) output ----------
O=box(29, 30.2, 42, 6.4, "Ranked findings — AnalysisResult", OUT, OUT_BG, fs=14,
      sub="Streamlit app · HTML dashboard · CLI")
line(50, FX["b"], 50, O["t"]); head(50, O["t"], "down")

# ---------- module panel + single reuse arrow ----------
mods=[("Constraint\nPromotion","promotion.py"),("UPF\nSignoff","upf_signoff.py"),
      ("Regression\nDetective","regression.py"),("Physical-\nAware","physical.py")]
k=len(mods); mw=20; mg=3.0
mtot=k*mw+(k-1)*mg; mx0=(100-mtot)/2
# subtle container panel behind modules
pnl_l, pnl_r = mx0-3, mx0+mtot+3
ax.add_patch(FancyBboxPatch((pnl_l, 15.5), pnl_r-pnl_l, 11.0,
    boxstyle="round,pad=0.05,rounding_size=1.4", lw=1.4, edgecolor="#e6c48a",
    facecolor="#fffaf1", zorder=1))
ax.text((pnl_l+pnl_r)/2, 25.2, "PRODUCT MODULES  ·  modules/  —  own analysis, reuse the Fix-Router",
        ha="center", color="#b5791f", fontsize=10.5, fontweight="bold", zorder=2)
MD=[box(mx0+i*(mw+mg), 16.8, mw, 6.4, t, MOD, MOD_BG, fs=12, sub=fn) for i,(t,fn) in enumerate(mods)]
# one clean dashed reuse arrow: panel top-left -> up -> into fix-router left edge
rx=pnl_l+3.5; midFX=(FX["t"]+FX["b"])/2
line(rx, 26.5, rx, midFX, c=REUSE, w=1.6, dashed=True)
line(rx, midFX, FX["l"], midFX, c=REUSE, w=1.6, dashed=True)
head(FX["l"], midFX, "right", c=REUSE)
ax.text(rx+1.6, midFX+2.2, "reuse", ha="left", color=REUSE, fontsize=10.5, style="italic")

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=180, facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png")
