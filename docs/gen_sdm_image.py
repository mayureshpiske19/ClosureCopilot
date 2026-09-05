"""Cover image for 'SiliconDesignMind' idea."""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

W, H = 1600, 900
FD = r"C:\Windows\Fonts"
B = lambda s: ImageFont.truetype(os.path.join(FD, "segoeuib.ttf"), s)
R = lambda s: ImageFont.truetype(os.path.join(FD, "segoeui.ttf"), s)

img = Image.new("RGB", (W, H))
top = (16, 24, 54); bot = (8, 12, 26)
px = img.load()
for y in range(H):
    t = y / H
    row = tuple(int(top[i] + (bot[i]-top[i])*t) for i in range(3))
    for x in range(W):
        px[x, y] = row
d = ImageDraw.Draw(img)

BLUE=(90,160,255); TEAL=(60,210,190); GREEN=(80,220,150); PURPLE=(150,120,240)
GREY=(150,165,190); WHITE=(255,255,255); GOLD=(240,190,90)

# Title
d.text((90, 66), "SiliconMind", font=B(92), fill=WHITE)
d.text((96, 186), "The living knowledge network for Microsoft silicon designers",
       font=B(32), fill=TEAL)

# Central brain/hub node
cx, cy = 800, 560
d.ellipse([cx-70, cy-70, cx+70, cy+70], fill=(40, 60, 120), outline=BLUE, width=4)
d.text((cx, cy), "AI", anchor="mm", font=B(48), fill=WHITE)

# Surrounding designer/knowledge nodes in a ring
nodes = [
    ("Bug fixes", GREEN), ("ECOs", BLUE), ("Methodology", PURPLE),
    ("Patents", GOLD), ("Papers", TEAL), ("Skills", BLUE),
    ("Reviews", GREEN), ("Design methods", PURPLE),
]
N = len(nodes)
Rr = 300
pts = []
for i, (label, col) in enumerate(nodes):
    ang = -math.pi/2 + i * (2*math.pi/N)
    nx = cx + int(Rr*math.cos(ang))
    ny = cy + int(Rr*0.62*math.sin(ang))
    pts.append((nx, ny, label, col))

# edges first
for (nx, ny, label, col) in pts:
    d.line([cx, cy, nx, ny], fill=(70, 85, 130), width=2)
# nodes
for (nx, ny, label, col) in pts:
    w = d.textlength(label, font=R(24)) + 34
    d.rounded_rectangle([nx-w/2, ny-24, nx+w/2, ny+24], radius=12, fill=(24, 32, 60), outline=col, width=2)
    d.text((nx, ny), label, anchor="mm", font=R(24), fill=col)

# left tagline block
d.text((90, 250), "Self-feeding.  Design-aware.  Proactive.", font=B(30), fill=GREY)

# bottom banner
d.rounded_rectangle([90, 812, 1510, 878], radius=16, fill=(20, 40, 70))
d.text((110, 830),
       "Hit a bug -> it hands you the proven fix, and the expert who found it -- across every HW team.",
       font=B(28), fill=(150, 200, 255))

img.save("docs/siliconmind.png", "PNG")
print("saved docs/siliconmind.png")
