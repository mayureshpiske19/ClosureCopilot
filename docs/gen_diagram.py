"""Generate the ClosureCopilot architecture diagram (PNG) for the submission."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# palette
C_BG = "#0d1117"; C_INPUT = "#1f6feb"; C_PARSE = "#238636"; C_SUP = "#8957e5"
C_AGENT = "#2d333b"; C_MOD = "#bb8009"; C_FIX = "#e5484d"; C_OUT = "#3fb950"
C_RAG = "#0e7490"; C_TXT = "#ffffff"; C_EDGE = "#8b949e"

fig, ax = plt.subplots(figsize=(16, 11))
fig.patch.set_facecolor(C_BG); ax.set_facecolor(C_BG)
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def box(x, y, w, h, text, color, fs=11, tc=C_TXT, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                 linewidth=1.2, edgecolor=C_EDGE, facecolor=color, mutation_aspect=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc,
            fontsize=fs, fontweight="bold" if bold else "normal", wrap=True)


def arrow(x1, y1, x2, y2, color=C_EDGE):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                 linewidth=1.4, color=color))


# title
ax.text(50, 97, "ClosureCopilot", ha="center", color=C_TXT, fontsize=26, fontweight="bold")
ax.text(50, 93.2, "Multi-Agent Backend Closure Copilot for RTL  —  it decides WHERE each fix belongs: RTL · SDC · UPF",
        ha="center", color="#c9d1d9", fontsize=12.5)

# inputs row
inputs = ["STA\nTiming", "Synthesis\nLog", "RTLA\nPower", "Area\nReport", "UPF", "SDC", "P&R\nCongestion"]
iw = 11.5; gap = 1.6; total = len(inputs) * iw + (len(inputs) - 1) * gap
x0 = (100 - total) / 2
ax.text(50, 88.5, "Backend reports (any tool)", ha="center", color="#8b949e", fontsize=11, style="italic")
for i, t in enumerate(inputs):
    box(x0 + i * (iw + gap), 80.5, iw, 6.2, t, C_INPUT, fs=10.5)

# ingestion
box(18, 71, 64, 6, "Ingestion / Parser Agent   —   tool-agnostic report normalizer", C_PARSE, fs=12)
for i in range(len(inputs)):
    arrow(x0 + i * (iw + gap) + iw / 2, 80.5, 50, 77.2)

# supervisor
box(30, 61.5, 40, 6.2, "Supervisor / Orchestrator Agent", C_SUP, fs=13)
arrow(50, 71, 50, 67.9)

# specialist agents
agents = ["Power", "Timing", "Area", "Synthesis", "UPF", "Constraints"]
aw = 13.5; agap = 1.3; atot = len(agents) * aw + (len(agents) - 1) * agap
ax0 = (100 - atot) / 2
ax.text(50, 57, "Specialist agents", ha="center", color="#8b949e", fontsize=10.5, style="italic")
for i, t in enumerate(agents):
    box(ax0 + i * (aw + agap), 49.5, aw, 5.6, t, C_AGENT, fs=10.5)
    arrow(50, 61.5, ax0 + i * (aw + agap) + aw / 2, 55.1)

# modules
mods = ["PPA\nAnalyzer", "Constraint\nPromotion", "UPF\nSignoff", "Regression\nDetective", "Physical-\nAware"]
mw = 16.5; mgap = 1.6; mtot = len(mods) * mw + (len(mods) - 1) * mgap
mx0 = (100 - mtot) / 2
ax.text(50, 45.2, "Product modules (one dashboard)", ha="center", color="#8b949e", fontsize=10.5, style="italic")
for i, t in enumerate(mods):
    box(mx0 + i * (mw + mgap), 37.5, mw, 6.4, t, C_MOD, fs=10.5)
    arrow(ax0 + atot / 2 * 0 + 50, 49.5, mx0 + i * (mw + mgap) + mw / 2, 43.9)

# fix routing engine
box(24, 28, 52, 6.2, "Fix-Routing / Diagnosis Engine   —   RTL  vs  SDC  vs  UPF  vs  Synth-setup", C_FIX, fs=12)
for i in range(len(mods)):
    arrow(mx0 + i * (mw + mgap) + mw / 2, 37.5, 50, 34.4)

# output
box(18, 18.5, 64, 6.4,
    "Ranked findings  +  corrected snippets (RTL / SDC / UPF)  +  cross-domain PPA trade-offs",
    C_OUT, fs=12, tc="#0d1117")
arrow(50, 28, 50, 24.9)

# designer
box(38, 9, 24, 5.6, "RTL Designer", "#30363d", fs=12)
arrow(50, 18.5, 50, 14.6)

# dual RAG panel (right of supervisor — that band is clear)
box(79.5, 61, 19, 7, "Dual-RAG\nGlobal PPA KB + Design Context", C_RAG, fs=9.5)
ax.add_patch(FancyArrowPatch((79.5, 64.5), (70, 64.5), arrowstyle="-|>", mutation_scale=13,
             linewidth=1.3, color=C_RAG, linestyle=(0, (4, 3))))
ax.text(89, 69, "grounds every agent", ha="center", color="#8b949e", fontsize=9, style="italic")

# azure openai note (left of supervisor)
box(1.5, 61, 16, 7, "Azure OpenAI\n(offline fallback)", "#30363d", fs=9.5)
ax.add_patch(FancyArrowPatch((17.5, 64.5), (30, 64.5), arrowstyle="-|>", mutation_scale=13,
             linewidth=1.3, color="#8b949e", linestyle=(0, (4, 3))))
ax.text(9.5, 69, "reasoning engine", ha="center", color="#8b949e", fontsize=9, style="italic")

plt.tight_layout()
out = "docs/architecture.png"
plt.savefig(out, dpi=170, facecolor=C_BG, bbox_inches="tight")
print("saved", out)
