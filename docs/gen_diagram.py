"""ClosureCopilot architecture — faithful recreation of architecture.drawio.

Top-down, layered layout matching the hand-tuned draw.io diagram:
  input wrappers -> Ingestion/Parser -> Supervisor (+Azure/Grounded KB)
  -> grouping layer (Collaterals / PPA / Equivalence) -> 7 leaf agents
  -> Fix-Router -> ranked output ; Closure Modules panel (right, reuse router)
  ; Vendor Tools -> MCP (roadmap) -> Supervisor.

Outputs both docs/architecture.png (raster, for deck/video) and
docs/architecture.svg (vector).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

INK = "#1b2333"; MUT = "#5c6a86"; SOFT = "#94a0b5"
INPUT = "#2563eb"; INPUT_BG = "#eaf1ff"
PARSE = "#0f9d58"; PARSE_BG = "#e9f7ef"
SUP = "#7c3aed"; SUP_BG = "#f2ecfe"
AGENT = "#334155"; AGENT_BG = "#eef1f6"
FIX = "#e11d48"; FIX_BG = "#fdecf0"
OUT = "#0f9d58"; OUT_BG = "#e9f7ef"
KB = "#0e8088"; KB_BG = "#e6f8f7"
AZ = "#64748b"; AZ_BG = "#f2f4f8"
MOD = "#d97706"; MOD_BG = "#fff4e5"
MCP = "#7c3aed"; MCP_BG = "#f3eeff"; TOOL = "#66707f"; TOOL_BG = "#edeff3"
GCOL = "#2563eb"; GCOL_BG = "#dae8fc"
GPPA = "#b7791f"; GPPA_BG = "#fff2cc"
GEQU = "#b85450"; GEQU_BG = "#f8cecc"
CONN = "#8d99b0"; GRND = "#0e8088"; REUSE = "#d97706"

fig, ax = plt.subplots(figsize=(18, 12.6))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def box(x, y, w, h, title, color, bg, fs=13, sub=None, dashed=False):
    ls = (0, (4, 2.5)) if dashed else "solid"
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.9",
        lw=1.9, edgecolor=color, facecolor=bg, zorder=3, linestyle=ls))
    if sub:
        ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
                color=INK, fontsize=fs, fontweight="bold", zorder=4)
        ax.text(x + w / 2, y + h * 0.26, sub, ha="center", va="center",
                color=MUT, fontsize=fs - 4.0, zorder=4, family="monospace")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center",
                color=INK, fontsize=fs, fontweight="bold", zorder=4)
    return dict(cx=x + w / 2, l=x, r=x + w, t=y + h, b=y, midy=y + h / 2)


def seg(x1, y1, x2, y2, c=CONN, w=1.9, dashed=False):
    ax.plot([x1, x2], [y1, y2], color=c, lw=w, solid_capstyle="round",
            linestyle=(0, (3.0, 2.2)) if dashed else "solid", zorder=2)


def head(x, y, d="down", c=CONN):
    a, b = 0.58, 1.75
    if d == "down":  pts = [(x, y), (x - a, y + b), (x + a, y + b)]
    if d == "up":    pts = [(x, y), (x - a, y - b), (x + a, y - b)]
    if d == "left":  pts = [(x, y), (x + b, y - a), (x + b, y + a)]
    if d == "right": pts = [(x, y), (x - b, y - a), (x - b, y + a)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=c, edgecolor=c, lw=0, zorder=4))


def adown(x, y_from, y_to, c=CONN):
    seg(x, y_from, x, y_to, c=c); head(x, y_to, "down", c=c)


def path(points, c=CONN, w=1.9, dashed=False, end="down"):
    for i in range(len(points) - 1):
        seg(*points[i], *points[i + 1], c=c, w=w, dashed=dashed)
    head(*points[-1], end, c=c)


# ---------- title ----------
ax.text(50, 97.8, "ClosureCopilot — Architecture & Data Flow", ha="center",
        color=INK, fontsize=27, fontweight="bold")
ax.text(50, 94.2, "any backend report in    →    ranked, fix-routed findings out",
        ha="center", color=MUT, fontsize=15, style="italic")

# ---------- MCP cluster (far left, roadmap) ----------
VT = box(1.5, 82.6, 13.5, 5.4, "Vendor EDA Tools", TOOL, TOOL_BG, fs=10.5,
         sub="Synopsys · Cadence")
MC = box(1.5, 73.6, 13.5, 6.4, "MCP Tool-Control", MCP, MCP_BG, fs=10.5,
         sub="roadmap · tools+docs", dashed=True)
seg(VT["cx"], VT["b"], MC["cx"], MC["t"], c=MCP, dashed=True); head(MC["cx"], MC["t"], "down", c=MCP)

# ---------- 1) input wrappers ----------
wrap = [
    ("Collaterals", "UPF · SDC", INPUT, INPUT_BG),
    ("PPA Reports", "STA · Synth · RTLA", INPUT, INPUT_BG),
    ("Equivalence", "Formal / LEC", INPUT, INPUT_BG),
    ("Design Context", "RTL · spec.md · uarch", KB, KB_BG),
]
wx0, ww, wgap, wy, wh = 18.0, 12.5, 2.0, 83.0, 6.2
WB = [box(wx0 + i * (ww + wgap), wy, ww, wh, t, c, bg, fs=12, sub=s)
      for i, (t, s, c, bg) in enumerate(wrap)]
ax.text(wx0, wy + wh + 0.7, "INPUTS  ·  wrappers", ha="left", color=SOFT,
        fontsize=10.5, fontweight="bold")

# ---------- 2) Ingestion / Parser (spans first three wrappers) ----------
p_l = WB[0]["l"]; p_r = WB[2]["r"]
P = box(p_l, 73.8, p_r - p_l, 6.0, "Ingestion / Parser Agent", PARSE, PARSE_BG, fs=15,
        sub="ingestion/parsers.py  ·  detect_type() -> Finding")
for b in WB[:3]:
    adown(b["cx"], b["b"], P["t"])

# ---------- 3) Supervisor + side blocks ----------
S = box(26.0, 63.0, 25.0, 6.6, "Supervisor / Orchestrator", SUP, SUP_BG, fs=14,
        sub="orchestrator.py")
adown(P["cx"], P["b"], S["t"])
AZ_B = box(1.5, 63.4, 16.0, 5.6, "Azure OpenAI", AZ, AZ_BG, fs=11.5, sub="llm.py · optional")
KB_B = box(79.0, 63.4, 19.0, 5.6, "Grounded knowledge", KB, KB_BG, fs=11.5, sub="rag/ · design+global")

seg(AZ_B["r"], AZ_B["midy"], S["l"], S["midy"] - 0.9, c=GRND, w=1.5, dashed=True)
head(S["l"], S["midy"] - 0.9, "right", c=GRND)
ax.text((AZ_B["r"] + S["l"]) / 2, S["midy"] + 0.6, "enrich", ha="center", color=SOFT,
        fontsize=10, style="italic")
seg(KB_B["l"], KB_B["midy"], S["r"], S["midy"], c=GRND, w=1.5, dashed=True)
head(S["r"], S["midy"], "left", c=GRND)
ax.text((KB_B["l"] + S["r"]) / 2, S["midy"] + 1.2, "ground", ha="center", color=SOFT,
        fontsize=10, style="italic")

# Design Context -> Grounded knowledge
dc = WB[3]
path([(dc["cx"], dc["b"]), (dc["cx"], 71.4), (KB_B["cx"], 71.4), (KB_B["cx"], KB_B["t"])],
     c=GRND, w=1.5, dashed=True, end="down")
ax.text(dc["cx"] + 0.5, 72.2, "context", ha="left", color=SOFT, fontsize=9.5, style="italic")

# MCP -> Supervisor (roadmap dashed)
path([(MC["r"], MC["midy"]), (20.5, MC["midy"]), (20.5, S["midy"] + 1.2), (S["l"], S["midy"] + 1.2)],
     c=MCP, w=1.5, dashed=True, end="right")
ax.text(21.0, S["midy"] + 4.5, "tools · docs", ha="left", color=MCP, fontsize=9.5, style="italic")

# ---------- 4) grouping layer + 7 leaf agents ----------
agents = ["Synthesis", "UPF", "Constraints", "Power", "Timing", "Area", "Formal"]
aw, ag = 8.2, 1.6; ax0 = 4.0
AG = [box(ax0 + i * (aw + ag), 42.8, aw, 5.8, a + "\nAgent", AGENT, AGENT_BG, fs=11.5)
      for i, a in enumerate(agents)]
acx = [b["cx"] for b in AG]
ax.text(ax0, 42.8 - 1.6, "SPECIALIST AGENTS  ·  agents/base.py (registry: agents.yaml)",
        ha="left", color=SOFT, fontsize=10, fontweight="bold")

groups = [
    ("Collaterals Check", GCOL, GCOL_BG, [0, 1, 2]),
    ("PPA Analysis", GPPA, GPPA_BG, [3, 4, 5]),
    ("Equivalence Check", GEQU, GEQU_BG, [6]),
]
gy, gh = 53.0, 5.0
GB = []
for name, c, bg, idx in groups:
    gl = AG[idx[0]]["l"]; gr = AG[idx[-1]]["r"]
    GB.append((box(gl, gy, gr - gl, gh, name, c, bg, fs=12.5), idx))

# supervisor -> groups (org-chart manifold)
trunkY = 60.0
gcx = [g["cx"] for g, _ in GB]
seg(S["cx"], S["b"], S["cx"], trunkY)
seg(min(gcx), trunkY, max(gcx), trunkY)
for g, _ in GB:
    seg(g["cx"], trunkY, g["cx"], g["t"]); head(g["cx"], g["t"], "down")

# groups -> their leaf agents (per-group sub-manifold)
for g, idx in GB:
    subY = g["b"] - 2.2
    childcx = [AG[i]["cx"] for i in idx]
    seg(g["cx"], g["b"], g["cx"], subY)
    if len(childcx) > 1:
        seg(min(childcx), subY, max(childcx), subY)
    for i in idx:
        seg(AG[i]["cx"], subY, AG[i]["cx"], AG[i]["t"]); head(AG[i]["cx"], AG[i]["t"], "down")

# ---------- 5) Fix-Router (spans all agents) ----------
FX = box(AG[0]["l"], 33.0, AG[-1]["r"] - AG[0]["l"], 6.0,
         "Fix-Routing / Diagnosis Engine", FIX, FIX_BG, fs=15,
         sub="fix_router.py  ·  RTL | SDC | UPF | Synth | Formal  +  snippet + trade-off")
for b in AG:
    adown(b["cx"], b["b"], FX["t"])

# ---------- 6) output ----------
O = box(FX["cx"] - 18.5, 24.0, 37.0, 6.0, "Ranked findings — AnalysisResult",
        OUT, OUT_BG, fs=14, sub="Streamlit app · HTML dashboard · CLI")
adown(FX["cx"], FX["b"], O["t"])

# ---------- Closure Modules panel (right, vertical) ----------
pnl_l, pnl_b, pnl_w, pnl_h = 74.0, 15.0, 24.5, 34.0
ax.add_patch(FancyBboxPatch((pnl_l, pnl_b), pnl_w, pnl_h,
    boxstyle="round,pad=0.04,rounding_size=1.2", lw=1.5, edgecolor="#e6c48a",
    facecolor="#fffaf1", zorder=1))
ax.text(pnl_l + pnl_w / 2, pnl_b + pnl_h - 2.0, "CLOSURE MODULES", ha="center",
        color="#b5791f", fontsize=11.5, fontweight="bold", zorder=2)
ax.text(pnl_l + pnl_w / 2, pnl_b + pnl_h - 4.1, "reuse the Fix-Router", ha="center",
        color="#b5791f", fontsize=9.5, style="italic", zorder=2)
mods = [("Constraint Promotion", "promotion.py"),
        ("UPF Signoff", "upf_signoff.py"),
        ("Regression Detective", "regression.py")]
mx, mw, mh = pnl_l + 1.8, pnl_w - 3.6, 6.0
MD = []
for i, (t, fn) in enumerate(mods):
    my = pnl_b + pnl_h - 9.0 - i * 8.0
    MD.append(box(mx, my, mw, mh, t, MOD, MOD_BG, fs=11, sub=fn))

# reuse arrow: panel -> fix router right edge
seg(pnl_l, FX["midy"], FX["r"], FX["midy"], c=REUSE, w=1.6, dashed=True)
head(FX["r"], FX["midy"], "left", c=REUSE)
ax.text((pnl_l + FX["r"]) / 2, FX["midy"] + 1.2, "reuse", ha="center", color=REUSE,
        fontsize=10.5, style="italic", fontweight="bold")

# reports arrow: parser -> panel
path([(P["r"], P["midy"]), (72.0, P["midy"]), (72.0, pnl_b + pnl_h + 1.5),
      (pnl_l + 6.0, pnl_b + pnl_h + 1.5), (pnl_l + 6.0, pnl_b + pnl_h)],
     c=MUT, w=1.4, dashed=False, end="down")
ax.text(72.5, 62.0, "reports", ha="left", color=MUT, fontsize=9.5, style="italic")

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=180, facecolor="white", bbox_inches="tight")
plt.savefig("docs/architecture.svg", facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png and docs/architecture.svg")
