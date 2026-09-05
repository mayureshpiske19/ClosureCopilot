"""Cover image for the 'SplitSense' idea."""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 900
FD = r"C:\Windows\Fonts"
B = lambda s: ImageFont.truetype(os.path.join(FD, "segoeuib.ttf"), s)
R = lambda s: ImageFont.truetype(os.path.join(FD, "segoeui.ttf"), s)

# background gradient (teal -> deep slate)
img = Image.new("RGB", (W, H))
top = (12, 40, 52); bot = (10, 16, 28)
px = img.load()
for y in range(H):
    t = y / H
    row = tuple(int(top[i] + (bot[i]-top[i])*t) for i in range(3))
    for x in range(W):
        px[x, y] = row
d = ImageDraw.Draw(img)

TEAL = (60, 210, 190); BLUE = (90, 160, 255); GREEN = (80, 220, 150)
GREY = (150, 165, 185); WHITE = (255, 255, 255); ORANGE = (240, 170, 70)

# Title
d.text((90, 70), "SplitSense", font=B(96), fill=WHITE)
d.text((96, 195), "AI-guided IP partitioning for backend closure", font=B(38), fill=TEAL)
d.text((96, 250), "— with a formal RTL2RTL safety net", font=R(32), fill=GREY)

def block(x, y, w, h, color, label, lab_size=26, fill=False):
    if fill:
        d.rounded_rectangle([x, y, x+w, y+h], radius=14, fill=color)
        d.text((x+w/2, y+h/2), label, anchor="mm", font=B(lab_size), fill=(15,20,30))
    else:
        d.rounded_rectangle([x, y, x+w, y+h], radius=14, outline=color, width=3)
        d.text((x+w/2, y+h/2), label, anchor="mm", font=B(lab_size), fill=color)

# LEFT: one big monolithic IP (hard to close)
bx, by, bw, bh = 120, 380, 360, 380
d.rounded_rectangle([bx, by, bx+bw, bh+by], radius=18, outline=ORANGE, width=4)
d.text((bx+bw/2, by-34), "Big IP  —  can't close", anchor="mm", font=B(28), fill=ORANGE)
d.text((bx+bw/2, by+bh/2-40), "timing X", anchor="mm", font=R(28), fill=(240,120,110))
d.text((bx+bw/2, by+bh/2+10), "congestion X", anchor="mm", font=R(28), fill=(240,120,110))
d.text((bx+bw/2, by+bh/2+60), "floorplan X", anchor="mm", font=R(28), fill=(240,120,110))

# ARROW
d.text((560, 545), "AI", anchor="mm", font=B(40), fill=TEAL)
d.line([520, 580, 700, 580], fill=TEAL, width=5)
d.polygon([(700,570),(724,580),(700,590)], fill=TEAL)
d.text((610, 620), "split · move · keep", anchor="mm", font=R(24), fill=GREY)

# RIGHT: partitioned blocks (closable)
ox, oy = 770, 360
sizes = [("A", 0, 0, 200, 180, TEAL), ("B", 220, 0, 180, 180, BLUE),
         ("C", 0, 200, 180, 200, GREEN), ("D", 200, 200, 220, 200, TEAL)]
for lab, dx, dy, w, h, c in sizes:
    block(ox+dx, oy+dy, w, h, c, lab, 40, fill=True)
d.text((ox+210, oy-34), "Partitioned  —  closes", anchor="mm", font=B(28), fill=GREEN)
# a "moved" logic dot going from C to D
d.text((ox+210, oy+412), "move logic block C -> D safely", anchor="mm", font=R(22), fill=GREY)

# bottom formal-guarantee banner
d.rounded_rectangle([90, 810, 1510, 878], radius=16, fill=(18, 60, 55))
d.text((110, 828), "RTL2RTL formal equivalence PASS   unsplit  =  split   —   AI proposes, formal proves",
       font=B(30), fill=(120, 230, 180))

img.save("docs/splitsense.png", "PNG")
print("saved docs/splitsense.png")
