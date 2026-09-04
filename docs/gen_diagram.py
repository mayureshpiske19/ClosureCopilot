"""Generate the ClosureCopilot architecture diagram (clean white PNG)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

C_INPUT="#1f6feb"; C_PARSE="#2da44e"; C_SUP="#8957e5"; C_AGENT="#5b6570"
C_MOD="#c8860a"; C_FIX="#e5484d"; C_OUT="#2da44e"; C_RAG="#0e8088"
C_AZ="#5b6570"; C_DES="#6e7781"; C_EDGE="#8a94a0"; C_TXT="#ffffff"; C_DARK="#1a1a1a"

fig, ax = plt.subplots(figsize=(16, 10.5))
fig.patch.set_facecolor("white"); ax.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")


def box(x, y, w, h, text, color, fs=11, tc=C_TXT):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.35,rounding_size=1.1",
                 linewidth=1, edgecolor="#c8ccd2", facecolor=color))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc,
            fontsize=fs, fontweight="bold")


def arrow(x1, y1, x2, y2, color=C_EDGE, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13,
                 linewidth=1.3, color=color,
                 linestyle=(0, (4, 3)) if dashed else "solid"))


def clamp(v, lo, hi):
    return max(lo, min(hi, v))

# title
ax.text(50, 97, "ClosureCopilot", ha="center", color=C_DARK, fontsize=25, fontweight="bold")
ax.text(50, 93, "Multi-Agent Backend Closure Copilot for RTL  —  decides WHERE each fix belongs: RTL | SDC | UPF",
        ha="center", color="#57606a", fontsize=12)

# inputs
inputs = ["STA\nTiming", "Synthesis\nLog", "RTLA\nPower", "Area\nReport", "UPF", "SDC", "P&R\nCongestion"]
iw, ig = 11.5, 1.4
ix0 = (100 - (len(inputs) * iw + (len(inputs) - 1) * ig)) / 2
icx = [ix0 + iw / 2 + i * (iw + ig) for i in range(len(inputs))]
ax.text(50, 89.6, "Backend reports (any tool)", ha="center", color="#8a94a0", fontsize=10.5, style="italic")
for i, t in enumerate(inputs):
    box(ix0 + i * (iw + ig), 82.5, iw, 6, t, C_INPUT, fs=10)

# parser
box(18, 73.5, 64, 5.6, "Ingestion / Parser Agent  —  tool-agnostic report normalizer", C_PARSE, fs=12)
for cx in icx:
    arrow(cx, 82.5, clamp(cx, 20, 80), 79.1)

# supervisor + side panels
box(33, 64, 34, 6.2, "Supervisor / Orchestrator", C_SUP, fs=13)
arrow(50, 73.5, 50, 70.2)
box(2.5, 64.2, 15.5, 6, "Azure OpenAI\n(offline fallback)", C_AZ, fs=8.5)
box(82, 64.2, 15.5, 6, "Dual-RAG\nGlobal + Design KB", C_RAG, fs=8.5)
arrow(18, 67.2, 33, 67.1, dashed=True)
arrow(82, 67.2, 67, 67.1, dashed=True)

# agents
agents = ["Power", "Timing", "Area", "Synthesis", "UPF", "Constraints"]
aw, ag = 12, 1.4
ax0 = (100 - (len(agents) * aw + (len(agents) - 1) * ag)) / 2
acx = [ax0 + aw / 2 + i * (aw + ag) for i in range(len(agents))]
ax.text(50, 61, "Specialist agents", ha="center", color="#8a94a0", fontsize=10, style="italic")
for i, t in enumerate(agents):
    box(ax0 + i * (aw + ag), 54.5, aw, 5.4, t, C_AGENT, fs=10)
    arrow(50, 64, acx[i], 59.9)

# fix engine
box(24, 45, 52, 5.6, "Fix-Routing / Diagnosis Engine  —  RTL | SDC | UPF | Synth-setup", C_FIX, fs=11.5)
for cx in acx:
    arrow(cx, 54.5, clamp(cx, 26, 74), 50.6)

# modules
mods = ["PPA\nAnalyzer", "Constraint\nPromotion", "UPF\nSignoff", "Regression\nDetective", "Physical-\nAware"]
mw, mg = 16, 1.6
mx0 = (100 - (len(mods) * mw + (len(mods) - 1) * mg)) / 2
mcx = [mx0 + mw / 2 + i * (mw + mg) for i in range(len(mods))]
ax.text(50, 42.4, "Product modules (one dashboard)", ha="center", color="#8a94a0", fontsize=10, style="italic")
for i, t in enumerate(mods):
    box(mx0 + i * (mw + mg), 35, mw, 6.2, t, C_MOD, fs=10)
    arrow(50, 45, mcx[i], 41.2)

# output
box(18, 25.5, 64, 6, "Ranked findings  +  corrected snippets (RTL / SDC / UPF)  +  PPA trade-offs",
    C_OUT, fs=11.5)
for cx in mcx:
    arrow(cx, 35, clamp(cx, 20, 80), 31.5)

# designer
box(38, 16, 24, 5.6, "RTL Designer", C_DES, fs=12)
arrow(50, 25.5, 50, 21.6)

plt.tight_layout()
plt.savefig("docs/architecture.png", dpi=170, facecolor="white", bbox_inches="tight")
print("saved docs/architecture.png")
