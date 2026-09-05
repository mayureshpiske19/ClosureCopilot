"""Cover image for 'The Overnight Architect' idea."""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1600, 900
FD = r"C:\Windows\Fonts"
B = lambda s: ImageFont.truetype(os.path.join(FD, "segoeuib.ttf"), s)
R = lambda s: ImageFont.truetype(os.path.join(FD, "segoeui.ttf"), s)

# night gradient background (deep indigo -> navy)
img = Image.new("RGB", (W, H))
top = (18, 22, 56); bot = (8, 12, 30)
px = img.load()
for y in range(H):
    t = y / H
    px_row = tuple(int(top[i] + (bot[i]-top[i])*t) for i in range(3))
    for x in range(W):
        px[x, y] = px_row
d = ImageDraw.Draw(img)

# stars
import random
random.seed(7)
for _ in range(140):
    x, y = random.randint(0, W), random.randint(0, int(H*0.62))
    r = random.choice([1,1,1,2])
    c = random.choice([(255,255,255),(200,210,255),(180,190,240)])
    d.ellipse([x,y,x+r,y+r], fill=c)

# crescent moon (top-right)
mx, my, mr = 1330, 170, 78
d.ellipse([mx-mr,my-mr,mx+mr,my+mr], fill=(245,240,210))
d.ellipse([mx-mr+34,my-mr-10,mx+mr+34,my+mr-10], fill=(15,19,48))

# Pareto curve panel (glass card, lower area)
cx, cy, cw, ch = 150, 470, 620, 330
d.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=22, fill=(255,255,255,0))
d.rounded_rectangle([cx,cy,cx+cw,cy+ch], radius=22, outline=(90,110,180), width=2)
# axes
ox, oy = cx+70, cy+ch-60
d.line([ox,cy+40, ox,oy], fill=(150,165,210), width=3)          # y axis
d.line([ox,oy, cx+cw-40,oy], fill=(150,165,210), width=3)       # x axis
d.text((cx+18, cy+150), "Power", font=R(24), fill=(170,185,225))
d.text((cx+cw-150, oy+18), "Performance", font=R(24), fill=(170,185,225))
# pareto front points + curve
pts = [(ox+60,oy-40),(ox+130,oy-110),(ox+220,oy-175),(ox+330,oy-215),(ox+440,oy-240)]
# faint dominated points
random.seed(3)
for _ in range(26):
    x = random.randint(ox+40, cx+cw-70); y = random.randint(cy+70, oy-20)
    d.ellipse([x-4,y-4,x+4,y+4], fill=(80,95,150))
# curve
for i in range(len(pts)-1):
    d.line([pts[i], pts[i+1]], fill=(120,200,255), width=4)
for (x,y) in pts:
    d.ellipse([x-9,y-9,x+9,y+9], fill=(80,220,160), outline=(255,255,255), width=2)
d.text((cx+18, cy+18), "Pareto front", font=B(26), fill=(120,220,170))

# headline text (right)
tx = 150
d.text((tx, 90), "The Overnight", font=B(96), fill=(255,255,255))
d.text((tx, 190), "Architect", font=B(96), fill=(255,255,255))
d.text((tx, 320), "You sleep.  It designs.", font=B(40), fill=(150,200,255))

# subline (right of the pareto card)
sx = 830
d.text((sx, 470), "Spec  +  PPA targets  in", font=B(34), fill=(210,220,245))
d.text((sx, 525), "→  explores micro-arch variants", font=R(30), fill=(180,195,230))
d.text((sx, 570), "→  generates real RTL", font=R(30), fill=(180,195,230))
d.text((sx, 615), "→  runs synthesis + STA", font=R(30), fill=(180,195,230))
d.text((sx, 660), "→  ranked Pareto front by morning", font=R(30), fill=(180,195,230))
d.text((sx, 730), "Real elaborated designs — not estimates.", font=B(28), fill=(120,220,170))

img.save("docs/overnight_architect.png", "PNG")
print("saved docs/overnight_architect.png")
