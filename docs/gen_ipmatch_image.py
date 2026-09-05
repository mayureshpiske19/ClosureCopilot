"""Professional cover image for 'IPMatch' — correct soft vs hard IP matching criteria."""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1600, 900
FD = r"C:\Windows\Fonts"
def _f(n, s): return ImageFont.truetype(os.path.join(FD, n), s)
B  = lambda s: _f("segoeuib.ttf", s)
SB = lambda s: _f("seguisb.ttf", s) if os.path.exists(os.path.join(FD,"seguisb.ttf")) else _f("segoeuib.ttf", s)
R  = lambda s: _f("segoeui.ttf", s)

BG1=(11,18,38); BG2=(19,29,60)
INK=(15,22,40); WHITE=(255,255,255); MUTE=(150,165,195)
BLUE=(72,140,255); CYAN=(60,205,220); GREEN=(56,205,140); AMBER=(240,180,70); VIOLET=(150,120,240)
CARD=(24,34,66); CARD2=(28,40,78); LINE=(70,90,150)

img = Image.new("RGB", (W, H)); px = img.load()
for y in range(H):
    t=y/H; row=tuple(int(BG1[i]+(BG2[i]-BG1[i])*t) for i in range(3))
    for x in range(W): px[x,y]=row
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,8], fill=BLUE)

d.text((70, 44), "IPMatch", font=B(80), fill=WHITE)
d.text((76, 150), "AI-powered IP discovery & best-fit matching for SoC designers", font=SB(31), fill=CYAN)

def rrect(x,y,w,h,fill=None,outline=LINE,width=2,radius=18):
    d.rounded_rectangle([x,y,x+w,y+h], radius=radius, fill=fill, outline=outline, width=width)

def arrow(x1,y1,x2,y2,col=CYAN,w=5):
    d.line([x1,y1,x2,y2], fill=col, width=w)
    ang=math.atan2(y2-y1,x2-x1); L=16; a=0.5
    d.polygon([(x2,y2),(x2-L*math.cos(ang-a), y2-L*math.sin(ang-a)),
               (x2-L*math.cos(ang+a), y2-L*math.sin(ang+a))], fill=col)

py = 300; ph = 470
# LEFT: spec with soft + hard sub-panels
lx, lw = 70, 400
rrect(lx, py, lw, ph, fill=CARD)
d.text((lx+26, py+18), "1 · Your spec", font=B(27), fill=WHITE)

# soft sub-card
sc_y = py+58
rrect(lx+18, sc_y, lw-36, 196, fill=(18,28,56), outline=CYAN, width=2, radius=14)
d.text((lx+38, sc_y+14), "Soft IP  ·  AXI5 subordinate", font=SB(23), fill=CYAN)
d.text((lx+38, sc_y+48), "match on:", font=R(19), fill=MUTE)
for i,(k,v) in enumerate([("Functionality","protocol-complete"),("Timing","meets budget"),
                          ("Logic depth","low"),("Area","within budget")]):
    yy=sc_y+76+i*24
    d.text((lx+38, yy), k, font=R(20), fill=(200,210,235))
    d.text((lx+lw-38, yy), v, anchor="ra", font=R(20), fill=WHITE)
d.text((lx+38, sc_y+174), "node-independent \u2014 synthesizable RTL", font=R(16), fill=MUTE)

# hard sub-card
hc_y = sc_y+212
rrect(lx+18, hc_y, lw-36, 168, fill=(18,28,56), outline=AMBER, width=2, radius=14)
d.text((lx+38, hc_y+14), "Hard IP  ·  SRAM memory macro", font=SB(23), fill=AMBER)
d.text((lx+38, hc_y+48), "match on:", font=R(19), fill=MUTE)
for i,(k,v) in enumerate([("Process node","5 nm (fixed)"),("Size / area","2K x 64"),
                          ("Timing","fixed access time")]):
    yy=hc_y+78+i*24
    d.text((lx+38, yy), k, font=R(20), fill=(200,210,235))
    d.text((lx+lw-38, yy), v, anchor="ra", font=R(20), fill=WHITE)

# CENTER engine
ex, ew = 610, 260
eng_y=py+150; eng_h=180
rrect(ex, eng_y, ew, eng_h, fill=(34,52,110), outline=BLUE, width=3, radius=22)
d.text((ex+ew/2, eng_y+58), "IPMatch", anchor="mm", font=B(36), fill=WHITE)
d.text((ex+ew/2, eng_y+104), "AI matching engine", anchor="mm", font=R(23), fill=CYAN)
d.text((ex+ew/2, eng_y+138), "search · score · gap · license", anchor="mm", font=R(19), fill=MUTE)

# RIGHT results
rx, rw = 1120, 410
rrect(rx, py, rw, ph, fill=CARD2)
d.text((rx+24, py+18), "2 · Ranked best-fit IP", font=B(27), fill=WHITE)
results=[("AXI5_SoftIP_v3","98%",GREEN,"soft · functionality + timing fit"),
         ("SRAM_2Kx64_5nm","95%",CYAN,"hard macro · 5nm, size + access fit"),
         ("AXI4_SoftIP_v2","70%",AMBER,"soft · needs AXI5 protocol bridge")]
yy=py+62
for name,score,col,note in results:
    rrect(rx+20, yy, rw-40, 122, fill=(18,26,52), outline=(46,62,108), width=1, radius=14)
    d.text((rx+40, yy+15), name, font=SB(24), fill=WHITE)
    pw=90
    d.rounded_rectangle([rx+rw-20-pw-16, yy+13, rx+rw-20-16, yy+47], radius=12, fill=col)
    d.text((rx+rw-20-16-pw/2, yy+30), score, anchor="mm", font=B(23), fill=INK)
    frac=int(score.strip('%'))/100
    d.rounded_rectangle([rx+40, yy+62, rx+rw-60, yy+72], radius=5, fill=(40,54,92))
    d.rounded_rectangle([rx+40, yy+62, rx+40+int((rw-100)*frac), yy+72], radius=5, fill=col)
    d.text((rx+40, yy+84), note, font=R(19), fill=MUTE); yy+=138

# arrows
mid_y=eng_y+eng_h/2
arrow(lx+lw+10, mid_y, ex-12, mid_y, col=CYAN, w=5)
arrow(ex+ew+10, mid_y, rx-12, mid_y, col=GREEN, w=5)

# bottom sources strip
sy=792
rrect(70, sy, 1460, 66, fill=(18,30,60), outline=(46,62,108), width=1, radius=14)
d.text((92, sy+20), "Searches:", font=B(23), fill=WHITE)
srcs=[("Azure repos",CYAN),("ADO",BLUE),("Past & derivative projects",VIOLET),("Licensed 3rd-party",AMBER)]
sx=92 + d.textlength("Searches:", font=B(23)) + 24
for label,col in srcs:
    tw=d.textlength(label, font=R(22)); w=tw+36
    rrect(sx, sy+15, w, 36, fill=(22,32,62), outline=col, width=2, radius=11)
    d.text((sx+w/2, sy+33), label, anchor="mm", font=R(22), fill=col)
    sx+=w+16

img.save("docs/ipmatch.png", "PNG")
print("saved docs/ipmatch.png")
