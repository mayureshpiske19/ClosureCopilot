"""Generate 1920x1080 video frames for the ClosureCopilot 2-minute video."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1920, 1080
OUT = "docs/video"
os.makedirs(OUT, exist_ok=True)

NAVY = (15, 43, 92); BLUE = (31, 111, 235); PURPLE = (137, 87, 229)
DARK = (26, 26, 26); GRAY = (87, 96, 106); LIGHT = (242, 244, 247)
WHITE = (255, 255, 255); GREEN = (45, 164, 78); RED = (229, 72, 77); ORANGE = (200, 134, 10)

FD = r"C:\Windows\Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


B = lambda s: font("segoeuib.ttf", s)      # bold
R = lambda s: font("segoeui.ttf", s)       # regular
SB = lambda s: font("seguisb.ttf", s) if os.path.exists(os.path.join(FD, "seguisb.ttf")) else B(s)


def new(bg=WHITE):
    return Image.new("RGB", (W, H), bg)


def rrect(d, xy, r, fill):
    d.rounded_rectangle(xy, radius=r, fill=fill)


def wrap(d, text, fnt, maxw):
    words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, fnt, color, maxw, lh):
    for ln in wrap(d, text, fnt, maxw):
        d.text((x, y), ln, font=fnt, fill=color); y += lh
    return y


def header(d, title, color=BLUE):
    d.rectangle([0, 0, W, 150], fill=color)
    d.text((70, 40), title, font=B(52), fill=WHITE)


def save(img, n):
    img.save(f"{OUT}/frame{n}.png")


# F1 — title
img = new(NAVY); d = ImageDraw.Draw(img)
d.rectangle([0, 700, W, 716], fill=BLUE)
d.text((130, 300), "ClosureCopilot", font=B(120), fill=WHITE)
d.text((136, 460), "A Multi-Agent Backend Closure Copilot for RTL", font=B(50), fill=(191, 212, 242))
d.text((136, 560), "It decides WHERE each fix belongs  —  RTL  ·  SDC  ·  UPF", font=R(38), fill=(159, 184, 224))
d.text((136, 900), "AI-Native Engineering    |    github.com/mayureshpiske19/ClosureCopilot",
       font=R(28), fill=(143, 166, 200))
save(img, 1)

# F2 — problem
img = new(); d = ImageDraw.Draw(img); header(d, "The problem: PPA closure doesn't scale", RED)
bullets = [
    "Power, Performance & Area closure is the biggest schedule risk in silicon.",
    "Run backend tools, wait hours, then face thousands of lines of reports.",
    "The bottleneck is judgment, not reading: RTL bug or missing constraint?",
    "That expertise lives only in senior engineers' heads — and doesn't scale.",
]
y = 280
for b in bullets:
    d.ellipse([90, y + 12, 118, y + 40], fill=RED)
    y = para(d, 150, y, b, R(42), DARK, 1650, 58) + 60
save(img, 2)

# F3 — architecture
img = new(); d = ImageDraw.Draw(img); header(d, "One copilot · 9 agents · any backend report", BLUE)
arch = Image.open("docs/architecture.png").convert("RGB")
scale = min(1720 / arch.width, 820 / arch.height)
arch = arch.resize((int(arch.width * scale), int(arch.height * scale)))
img.paste(arch, ((W - arch.width) // 2, 175))
save(img, 3)

# F4 — fix-layer routing
img = new(); d = ImageDraw.Draw(img); header(d, "The core idea: Fix-Layer Routing", PURPLE)
para(d, 70, 210, "For every issue, it decides WHERE the fix belongs — RTL · SDC · UPF · synth-setup.",
     B(40), DARK, 1780, 55)
rrect(d, [70, 340, 940, 720], 24, LIGHT)
d.text((110, 375), "Example 1 — fix in SDC (not RTL)", font=B(38), fill=BLUE)
para(d, 110, 450, "Config path cfg_reg -> status_reg fails setup. Quasi-static, sampled once per write.",
     R(32), DARK, 800, 46)
d.text((110, 620), "-> set_multicycle_path -setup 2 …", font=B(34), fill=GREEN)
rrect(d, [980, 340, 1850, 720], 24, LIGHT)
d.text((1020, 375), "Example 2 — fix in RTL", font=B(38), fill=PURPLE)
para(d, 1020, 450, "Deep combinational cone at alu.sv:210. Genuine logic depth, single cycle.",
     R(32), DARK, 800, 46)
d.text((1020, 620), "-> pipeline the datapath  (timing OK, area +2%)", font=B(34), fill=GREEN)
para(d, 70, 800, "Every fix ships with a corrected, copy-paste snippet + a cross-domain PPA trade-off.",
     B(38), DARK, 1780, 52)
save(img, 4)

# F5 — five modules
img = new(); d = ImageDraw.Draw(img); header(d, "Five modules, one dashboard", GREEN)
mods = [
    ("PPA Analyzer", "Ranks issues and routes each fix to RTL / SDC / UPF with a snippet + trade-off.", BLUE),
    ("Constraint Promotion", "Reconciles IP -> top constraints and generates corrected top-level SDC.", PURPLE),
    ("UPF Signoff", "Checks isolation, retention & clock-gating intent; emits corrected UPF.", ORANGE),
    ("Regression Detective", "Compares two runs; finds what regressed and the change behind it.", RED),
    ("Physical-Aware Feedback", "Turns place-and-route congestion into concrete RTL restructuring hints.", GREEN),
]
y = 210
for name, desc, col in mods:
    d.rectangle([70, y, 96, y + 130], fill=col)
    rrect(d, [110, y, 1850, y + 130], 16, LIGHT)
    d.text((150, y + 20), name, font=B(38), fill=col)
    para(d, 150, y + 74, desc, R(30), DARK, 1650, 40)
    y += 158
save(img, 5)

# F6 — how it works
img = new(); d = ImageDraw.Draw(img); header(d, "Grounded — and always-on", BLUE)
rrect(d, [70, 210, 940, 900], 24, LIGHT)
d.text((110, 250), "Dual-RAG knowledge", font=B(44), fill=BLUE)
d.text((110, 350), "1  Global PPA knowledge", font=B(34), fill=DARK)
para(d, 110, 410, "Low-power / timing / area methodology, tool-report semantics, fix patterns.",
     R(28), GRAY, 780, 40)
d.text((110, 540), "2  Design Context Memory", font=B(34), fill=DARK)
para(d, 110, 600, "A persistent memory of YOUR chip — specs, micro-arch, clocking, prior runs.",
     R(28), GRAY, 780, 40)
para(d, 110, 760, "Feedback reflects your design intent, and improves each iteration.",
     B(30), GREEN, 780, 42)
rrect(d, [980, 210, 1850, 900], 24, LIGHT)
d.text((1020, 250), "Built to run anywhere", font=B(44), fill=PURPLE)
for i, t in enumerate(["Python · multi-agent orchestration", "Azure OpenAI for reasoning",
                       "Streamlit product dashboard", "Deterministic OFFLINE mode"]):
    d.text((1020, 360 + i * 90), "•  " + t, font=B(34) if i == 3 else R(34), fill=DARK)
para(d, 1020, 760, "Runs reliably with or without credentials — the demo never breaks.",
     R(28), GRAY, 790, 40)
save(img, 6)

# F7 — why it wins
img = new(); d = ImageDraw.Draw(img); header(d, "Why it wins", PURPLE)
rrect(d, [70, 210, 1850, 520], 24, (238, 231, 250))
d.text((110, 245), "Unique", font=B(44), fill=PURPLE)
para(d, 110, 335, "Combines fix-layer routing + IP->top constraint promotion + run-to-run regression "
     "attribution for the RTL owner — a combination no existing point tool brings together.",
     R(34), DARK, 1680, 50)
rrect(d, [70, 560, 1850, 960], 24, (231, 243, 233))
d.text((110, 595), "Impact", font=B(44), fill=GREEN)
for i, t in enumerate([
        "Hours of manual, expert-only triage -> minutes of ranked, copy-paste fixes.",
        "Puts senior-level closure judgment in every RTL designer's hands.",
        "Catches unrealized intent & lost constraints before the next costly backend run."]):
    para(d, 110, 690 + i * 80, "•  " + t, R(32), DARK, 1680, 44)
save(img, 7)

# F8 — closing
img = new(NAVY); d = ImageDraw.Draw(img)
d.text((130, 380), "ClosureCopilot", font=B(110), fill=WHITE)
d.text((136, 540), "Close faster.  Fix smarter.", font=B(52), fill=(191, 212, 242))
d.text((136, 720), "github.com/mayureshpiske19/ClosureCopilot", font=R(34), fill=(159, 184, 224))
save(img, 8)

print("saved 8 frames to", OUT)
