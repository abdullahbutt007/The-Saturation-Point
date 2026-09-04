#!/usr/bin/env python3
"""Build the LinkedIn document-carousel (10 slides, 1080x1350) for
'The Saturation Point' — matches the dashboard's brand identity.
Outputs slide_01.png..slide_10.png and a combined carousel.pdf.
"""
import json
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
stats = json.loads((OUT / "stats.json").read_text())

W, H = 1080, 1350
MARGIN = 84

# -- palette (matches dashboard.html tokens) ---------------------------------
BG        = (16, 19, 31)     # --ink
BG2       = (23, 27, 48)     # --ink-2 (gradient partner)
SURFACE   = (23, 27, 48)
SURFACE2  = (29, 33, 56)
INK       = (243, 242, 250)  # --text-inv
INK2      = (201, 203, 224)
MUTED     = (171, 174, 201)  # --text-inv-soft
BORDER    = (255, 255, 255, 24)
ACCENT    = (255, 61, 104)   # --signal
ACCENT2   = (245, 185, 61)   # --gold
DANGER    = (255, 61, 104)
BLUE      = (245, 185, 61)
GRAY      = (69, 75, 110)
SAFE      = (76, 224, 163)

# -- fonts --------------------------------------------------------------------
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SERIF_BI = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"
F_SANS  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B= "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_MONO  = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
F_MONO_B= "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def dotgrid(draw, step=27, color=(255, 255, 255)):
    for gx in range(0, W, step):
        for gy in range(0, H, step):
            draw.point((gx, gy), fill=color + (14,) if len(color) == 3 else color)

def new_slide(rings=False):
    base = Image.new("RGB", (W, H))
    bdraw = ImageDraw.Draw(base)
    for i in range(H):
        t = i / (H - 1)
        bdraw.line([(0, i), (W, i)], fill=lerp_color(BG, BG2, t))
    img = base.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for gx in range(0, W, 27):
        for gy in range(0, H, 27):
            od.ellipse([gx, gy, gx+1.4, gy+1.4], fill=(255, 255, 255, 16))
    if rings:
        cx, cy = W - 210, 230
        for i, r in enumerate([70, 150, 230, 310]):
            col = ACCENT if i % 2 == 0 else ACCENT2
            alpha = 130 - i*22
            od.ellipse([cx-r, cy-r, cx+r, cy+r], outline=col + (max(alpha,30),), width=2)
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    return img, ImageDraw.Draw(img)

def grad_rect(img, box, c_top, c_bottom, radius=6):
    x0, y0, x1, y1 = box
    w_ = max(1, int(x1 - x0))
    h = max(1, int(y1 - y0))
    tmp = Image.new("RGB", (w_, h))
    tdraw = ImageDraw.Draw(tmp)
    for i in range(h):
        t = i / max(1, h - 1)
        tdraw.line([(0, i), (w_, i)], fill=lerp_color(c_top, c_bottom, t))
    mask = Image.new("L", (w_, h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle([0, 0, w_-1, h-1], radius=radius, fill=255)
    img.paste(tmp, (int(x0), int(y0)), mask)

def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def draw_multiline(draw, xy, text, fnt, fill, max_width, leading=1.28, align="left"):
    x, y = xy
    lines = wrap(draw, text, fnt, max_width)
    lh = int(fnt.size * leading)
    for ln in lines:
        if align == "center":
            w_ = draw.textlength(ln, font=fnt)
            draw.text((x + (max_width - w_) / 2, y), ln, font=fnt, fill=fill)
        else:
            draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y

def header(draw, kicker, page_no, total=10):
    fk = font(F_MONO, 20)
    draw.text((MARGIN, 64), kicker.upper(), font=fk, fill=MUTED)
    pg = f"{page_no:02d} / {total:02d}"
    w_ = draw.textlength(pg, font=fk)
    draw.text((W - MARGIN - w_, 64), pg, font=fk, fill=ACCENT)
    draw.line([(MARGIN, 104), (W - MARGIN, 104)], fill=(255, 255, 255, 20), width=1)

def footer(draw):
    fk = font(F_MONO, 17)
    label = "THE SATURATION POINT · UK TECH JOB MARKET 2026"
    draw.line([(MARGIN, H - 96), (W - MARGIN, H - 96)], fill=(255, 255, 255, 20), width=1)
    draw.text((MARGIN, H - 76), label, font=fk, fill=MUTED)

def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def hairline_border(draw, box, radius=14):
    rounded(draw, box, radius, outline=(255, 255, 255), width=1)
    # emulate translucent border by drawing a dim rectangle over solid outline
    # (Pillow draws solid colors; approximate translucency with a muted gray)

slides = []

# =============================================================================
# SLIDE 1 — Cover
# =============================================================================
img, d = new_slide(rings=True)
d.text((MARGIN, 120), "LABOUR MARKET BULLETIN", font=font(F_MONO, 22), fill=MUTED)
d.text((MARGIN, 152), "UK TECHNOLOGY SECTOR · SEPTEMBER 2026", font=font(F_MONO, 22), fill=MUTED)

# status pill
pill_text = "STATUS: SATURATED AT ENTRY LEVEL — TIGHT AT THE TOP"
pf = font(F_MONO, 19)
pw = d.textlength(pill_text, font=pf) + 40
rounded(d, [MARGIN, 210, MARGIN + pw, 210 + 46], 6, outline=ACCENT, width=2)
d.text((MARGIN + 20, 223), pill_text, font=pf, fill=ACCENT)

d.text((MARGIN, 290), "The", font=font(F_SERIF_BI, 138), fill=INK)
d.text((MARGIN, 420), "Saturation", font=font(F_SERIF_BI, 138), fill=INK)
d.text((MARGIN, 550), "Point.", font=font(F_SERIF_BI, 138), fill=ACCENT)

y = draw_multiline(d, (MARGIN, 720), "Why the UK tech job market feels nearly impossible to break into in 2026 — the numbers, in nine charts.", font(F_SANS, 34), INK2, W - 2*MARGIN, leading=1.35)

d.line([(MARGIN, 970), (W - MARGIN, 970)], fill=(255, 255, 255, 30), width=1)
y2 = 1000
labels = ["ONS", "ADZUNA", "CIPD", "LAYOFFS.FYI", "IT JOBS WATCH", "CV-LIBRARY", "HOME OFFICE"]
xx = MARGIN
fk = font(F_MONO, 18)
for i, lab in enumerate(labels):
    d.text((xx, y2), lab, font=fk, fill=MUTED)
    xx += d.textlength(lab, font=fk) + 34
    d.ellipse([xx-24, y2+8, xx-18, y2+14], fill=(ACCENT if i % 2 == 0 else ACCENT2))
    xx += 18

d.text((MARGIN, H - 150), "SWIPE FOR THE FULL PICTURE  →", font=font(F_MONO, 24), fill=ACCENT)
slides.append(img)

# =============================================================================
# SLIDE 2 — headline vacancy numbers
# =============================================================================
img, d = new_slide()
header(d, "01 · The headline", 2)
y = draw_multiline(d, (MARGIN, 150), "UK vacancies just hit a five-year low.", font(F_SERIF, 54), INK, W - 2*MARGIN, leading=1.15)
y = draw_multiline(d, (MARGIN, y + 26), "707,000 open roles nationwide, all sectors — down two quarters running, and the lowest count since Feb–Apr 2021.", font(F_SANS, 30), INK2, W - 2*MARGIN, leading=1.4)

# mini bar chart: 3 quarters
chart_top = y + 70
chart_h = 300
chart_left = MARGIN
chart_w = W - 2*MARGIN
quarters = ["MAR–MAY '25", "DEC'25–FEB'26", "MAR–MAY '26"]
vals = [738000, 726000, 707000]
maxv = 820000
bw = 170
gap = (chart_w - bw*3) / 2
colors = [GRAY, GRAY, DANGER]
for i, (q, v, c) in enumerate(zip(quarters, vals, colors)):
    bh = int(chart_h * v / maxv)
    x0 = chart_left + i*(bw+gap)
    y0 = chart_top + (chart_h - bh)
    if c == DANGER:
        grad_rect(img, [x0, y0, x0+bw, chart_top+chart_h], lerp_color(DANGER,(255,255,255),0.18), lerp_color(DANGER,(0,0,0),0.35), radius=6)
    else:
        rounded(d, [x0, y0, x0+bw, chart_top+chart_h], 6, fill=c)
    val_txt = f"{v:,}"
    fnt = font(F_MONO_B, 24)
    tw = d.textlength(val_txt, font=fnt)
    d.text((x0 + bw/2 - tw/2, y0 - 40), val_txt, font=fnt, fill=INK)
    fq = font(F_MONO, 16)
    for j, ln in enumerate(q.split(" ")):
        tw2 = d.textlength(ln, font=fq)
        d.text((x0 + bw/2 - tw2/2, chart_top + chart_h + 14 + j*22), ln, font=fq, fill=MUTED)

d.text((MARGIN, chart_top + chart_h + 90), "Source: ONS, Vacancies and jobs in the UK, June 2026", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 3 — two big stats
# =============================================================================
img, d = new_slide()
header(d, "01 · The headline", 3)
y = draw_multiline(d, (MARGIN, 150), "Two numbers explain the queue at every door.", font(F_SERIF, 52), INK, W - 2*MARGIN, leading=1.15)

box_y = 360
box_h = 380
gap = 28
box_w = (W - 2*MARGIN - gap) / 2
# left box
rounded(d, [MARGIN, box_y, MARGIN+box_w, box_y+box_h], 14, fill=SURFACE)
d.rounded_rectangle([MARGIN+28, box_y, MARGIN+box_w-28, box_y+3], radius=2, fill=BLUE)
t = "2.5"
fnt = font(F_MONO_B, 110)
tw = d.textlength(t, font=fnt)
d.text((MARGIN + box_w/2 - tw/2, box_y + 60), t, font=fnt, fill=BLUE)
draw_multiline(d, (MARGIN+40, box_y+220), "unemployed jobseekers for every open vacancy in the country", font(F_SANS, 26), INK2, box_w-80, align="center", leading=1.35)

x2 = MARGIN + box_w + gap
rounded(d, [x2, box_y, x2+box_w, box_y+box_h], 14, fill=SURFACE)
d.rounded_rectangle([x2+28, box_y, x2+box_w-28, box_y+3], radius=2, fill=DANGER)
t = "9.7%"
fnt = font(F_MONO_B, 92)
tw = d.textlength(t, font=fnt)
d.text((x2 + box_w/2 - tw/2, box_y + 60), t, font=fnt, fill=DANGER)
draw_multiline(d, (x2+40, box_y+220), "Computer Science graduate unemployment — worst of any degree subject", font(F_SANS, 26), INK2, box_w-80, align="center", leading=1.35)

draw_multiline(d, (MARGIN, box_y+box_h+50), "London youth unemployment (16–24) has climbed to 22.5% — the sharpest edge of a national trend.", font(F_SANS, 28), INK2, W-2*MARGIN, leading=1.4)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 4 — application flood
# =============================================================================
img, d = new_slide()
header(d, "02 · The applicant flood", 4)
y = draw_multiline(d, (MARGIN, 150), "Every vacancy now gets buried in applications.", font(F_SERIF, 50), INK, W - 2*MARGIN, leading=1.15)
y = draw_multiline(d, (MARGIN, y+24), "Average applications per UK vacancy nearly quadrupled year on year — and IT / software engineer is the single most applied-for job category in the country.", font(F_SANS, 28), INK2, W-2*MARGIN, leading=1.4)

chart_top = y + 60
bw = 220
gap2 = 120
xs = [MARGIN+60, MARGIN+60+bw+gap2]
vals = [12.6, 48.7]
labels2 = ["NOV 2023", "NOV 2024"]
maxv = 55
chart_h = 340
for x0, v, lab in zip(xs, vals, labels2):
    bh = int(chart_h * v/maxv)
    y0 = chart_top + (chart_h - bh)
    if v < 20:
        rounded(d, [x0, y0, x0+bw, chart_top+chart_h], 6, fill=GRAY)
    else:
        grad_rect(img, [x0, y0, x0+bw, chart_top+chart_h], lerp_color(ACCENT,(255,255,255),0.22), lerp_color(ACCENT,(0,0,0),0.3), radius=6)
    vt = f"{v:.1f}"
    fnt = font(F_MONO_B, 30)
    tw = d.textlength(vt, font=fnt)
    d.text((x0+bw/2-tw/2, y0-46), vt, font=fnt, fill=INK)
    fq = font(F_MONO, 18)
    tw2 = d.textlength(lab, font=fq)
    d.text((x0+bw/2-tw2/2, chart_top+chart_h+16), lab, font=fq, fill=MUTED)

# +286% callout
d.text((xs[1]+bw+30, chart_top+40), "+286%", font=font(F_MONO_B, 46), fill=DANGER)
d.text((xs[1]+bw+30, chart_top+100), "YoY", font=font(F_MONO, 22), fill=MUTED)

d.text((MARGIN, chart_top+chart_h+80), "Source: Tribepad platform data · CV-Library/Onrec, Q4 2025", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 5 — grad unemployment by subject
# =============================================================================
img, d = new_slide()
header(d, "03 · Who's hit hardest", 5)
y = draw_multiline(d, (MARGIN, 150), "Computer Science tops the unemployment table.", font(F_SERIF, 46), INK, W - 2*MARGIN, leading=1.15)
y = draw_multiline(d, (MARGIN, y+20), "Unemployment rate, 15 months after graduation:", font(F_SANS, 26), INK2, W-2*MARGIN, leading=1.3)

subs = [("Business & Management", 6.3), ("Economics", 6.8), ("Mathematics", 7.5),
        ("Finance & Accountancy", 8.1), ("Art", 8.5), ("Cinematics & Photography", 8.7),
        ("Computer Science", 9.7)]
top = y + 40
row_h = 74
maxv = 11
bar_left = MARGIN + 330
bar_max_w = W - MARGIN - bar_left - 110
for i, (name, val) in enumerate(subs):
    yy = top + i*row_h
    is_cs = name == "Computer Science"
    fnt = font(F_SANS_B if is_cs else F_SANS, 24)
    d.text((MARGIN, yy+10), name, font=fnt, fill=INK if is_cs else INK2)
    bw2 = int(bar_max_w * val/maxv)
    if is_cs:
        grad_rect(img, [bar_left, yy+6, bar_left+bw2, yy+34], lerp_color(DANGER,(255,255,255),0.18), lerp_color(DANGER,(0,0,0),0.32), radius=5)
    else:
        rounded(d, [bar_left, yy+6, bar_left+bw2, yy+34], 5, fill=GRAY)
    vt = f"{val:.1f}%"
    fnt2 = font(F_MONO_B, 22)
    d.text((bar_left+bw2+16, yy+8), vt, font=fnt2, fill=INK if is_cs else MUTED)

d.text((MARGIN, top + len(subs)*row_h + 40), "Source: Jisic graduate outcomes, 2023 cohort", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 6 — AI double effect
# =============================================================================
img, d = new_slide()
header(d, "04 · The AI effect", 6)
y = draw_multiline(d, (MARGIN, 150), "AI is doing two things at once.", font(F_SERIF, 52), INK, W - 2*MARGIN, leading=1.15)
y = draw_multiline(d, (MARGIN, y+24), "Quietly absorbing the tasks juniors used to learn on, while opening a narrow band of senior roles most candidates aren't qualified for yet.", font(F_SANS, 28), INK2, W-2*MARGIN, leading=1.4)

tiles = [("66%", "of UK enterprises are cutting entry-level hiring — AI now absorbs junior tasks"),
         ("3×", "the rate AI-related postings are growing at, vs. the average UK job category"),
         ("17%", "of employers expect to shrink headcount via AI within 12 months (CIPD)"),
         ("62%", "of those say clerical, junior and admin roles are most exposed")]
gtop = y + 50
gh = 230
gw = (W - 2*MARGIN - 20) / 2
positions = [(MARGIN, gtop), (MARGIN+gw+20, gtop), (MARGIN, gtop+gh+20), (MARGIN+gw+20, gtop+gh+20)]
for i, ((num, lbl), (x0, y0)) in enumerate(zip(tiles, positions)):
    accent_c = ACCENT if i % 2 == 0 else ACCENT2
    rounded(d, [x0, y0, x0+gw, y0+gh], 12, fill=SURFACE)
    d.rounded_rectangle([x0+26, y0, x0+gw-26, y0+3], radius=2, fill=accent_c)
    d.text((x0+30, y0+28), num, font=font(F_MONO_B, 56), fill=accent_c)
    draw_multiline(d, (x0+30, y0+110), lbl, font(F_SANS, 22), INK2, gw-60, leading=1.35)

d.text((MARGIN, gtop+2*gh+20+30), "Source: CompTIA, UK Tech Workforce 2026 · CIPD Labour Market Outlook", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 7 — layoffs
# =============================================================================
img, d = new_slide()
header(d, "05 · The layoffs wave", 7)
y = draw_multiline(d, (MARGIN, 150), "Layoffs are refilling the same applicant pool.", font(F_SERIF, 46), INK, W - 2*MARGIN, leading=1.15)
y = draw_multiline(d, (MARGIN, y+22), "Global tech layoffs, Q1 by year:", font(F_SANS, 26), INK2, W-2*MARGIN)

chart_top = y + 40
chart_h = 320
chart_w = W - 2*MARGIN
years = ["Q1 '23", "Q1 '24", "Q1 '25", "Q1 '26"]
vals3 = [167674, 57269, 29845, 70474]
maxv = 180000
pts = []
n = len(vals3)
seg = chart_w / (n-1)
for i, v in enumerate(vals3):
    px = MARGIN + i*seg
    py = chart_top + chart_h - int(chart_h * v/maxv)
    pts.append((px, py))
d.line(pts, fill=BLUE, width=5, joint="curve")
for (px, py), v, yr in zip(pts, vals3, years):
    d.ellipse([px-9, py-9, px+9, py+9], fill=BG, outline=BLUE, width=4)
    vt = f"{v:,}"
    fnt = font(F_MONO_B, 22)
    tw = d.textlength(vt, font=fnt)
    d.text((px-tw/2, py-46), vt, font=fnt, fill=INK)
    fq = font(F_MONO, 18)
    tw2 = d.textlength(yr, font=fq)
    d.text((px-tw2/2, chart_top+chart_h+20), yr, font=fq, fill=MUTED)

d.text((MARGIN, chart_top+chart_h+70), "+136% YoY", font=font(F_MONO_B, 34), fill=DANGER)
d.text((MARGIN, chart_top+chart_h+118), "Q1 2026 vs. Q1 2025 — nearly half attributed directly to AI/automation", font=font(F_SANS, 22), fill=INK2)
d.text((MARGIN, chart_top+chart_h+165), "Source: Layoffs.fyi tracker · Nikkei Asia", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 8 — salary landscape
# =============================================================================
img, d = new_slide()
header(d, "06 · The salary landscape", 8)
y = draw_multiline(d, (MARGIN, 150), "Pay is climbing — but only for people who already have the experience.", font(F_SERIF, 42), INK, W - 2*MARGIN, leading=1.18)

rows = [("Software Development", 33000, 82500), ("Cloud Engineering", 47500, 95000),
        ("Cybersecurity", 38500, 80000), ("Data & AI", 45000, 95000), ("DevOps & SRE", 44000, 92500)]
top = y + 50
row_h = 108
for i, (name, lo, hi) in enumerate(rows):
    yy = top + i*row_h
    rounded(d, [MARGIN, yy, W-MARGIN, yy+row_h-16], 10, fill=SURFACE)
    d.text((MARGIN+28, yy+18), name, font=font(F_SANS_B, 26), fill=INK)
    mult = hi/lo
    sub = f"£{lo:,.0f} entry  →  £{hi:,.0f} senior   ({mult:.1f}× )"
    d.text((MARGIN+28, yy+56), sub, font=font(F_MONO, 22), fill=ACCENT if mult>2.4 else INK2)

d.text((MARGIN, top+len(rows)*row_h+20), "Cybersecurity vacancies +12% YoY · Software Dev postings +71% YoY, only 366 live roles", font=font(F_SANS, 20), fill=INK2)
d.text((MARGIN, top+len(rows)*row_h+58), "Source: IT Job Board Salary Guide 2026 · IT Jobs Watch", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 9 — visa/policy tightening
# =============================================================================
img, d = new_slide()
header(d, "07 · Borders tightening", 9)
y = draw_multiline(d, (MARGIN, 150), "Even the side door is narrower now.", font(F_SERIF, 52), INK, W - 2*MARGIN, leading=1.15)
y = draw_multiline(d, (MARGIN, y+20), "UK Skilled Worker visa changes, 2025–26:", font(F_SANS, 26), INK2, W-2*MARGIN)

items = [("£41,700", "new general salary floor to sponsor a Skilled Worker visa"),
         ("111 roles removed", "occupations struck from the eligible sponsorship list"),
         ("B1 → B2", "required English proficiency raised, from Jan 2026"),
         ("5 → 10 years", "standard path to settlement roughly doubled"),
         ("~2,000", "sponsor licences revoked in 2025, mostly for coding errors")]
top = y + 40
row_h = 122
for i, (val, lbl) in enumerate(items):
    yy = top + i*row_h
    d.ellipse([MARGIN, yy+8, MARGIN+16, yy+24], outline=(ACCENT if i % 2 == 0 else ACCENT2), width=3)
    if i < len(items)-1:
        d.line([(MARGIN+8, yy+24), (MARGIN+8, yy+row_h+8)], fill=(255,255,255,30), width=2)
    d.text((MARGIN+40, yy-4), val, font=font(F_MONO_B, 32), fill=INK)
    draw_multiline(d, (MARGIN+40, yy+44), lbl, font(F_SANS, 23), INK2, W-2*MARGIN-40, leading=1.3)

d.text((MARGIN, top+len(items)*row_h+10), "Source: UK Home Office rule changes, via Centuro Global / IAS Services", font=font(F_MONO, 18), fill=MUTED)
footer(d)
slides.append(img)

# =============================================================================
# SLIDE 10 — the paradox + CTA
# =============================================================================
img, d = new_slide()
header(d, "08 · The verdict", 10)
y = draw_multiline(d, (MARGIN, 140), "The paradox, in two numbers.", font(F_SERIF, 54), INK, W - 2*MARGIN, leading=1.15)

box_y = 260
box_h = 220
gap = 24
box_w = (W - 2*MARGIN - gap) / 2
rounded(d, [MARGIN, box_y, MARGIN+box_w, box_y+box_h], 14, fill=SURFACE)
t="71%"; fnt=font(F_MONO_B,72); tw=d.textlength(t,font=fnt)
d.text((MARGIN+box_w/2-tw/2, box_y+36), t, font=fnt, fill=DANGER)
draw_multiline(d,(MARGIN+30,box_y+130),"of employers can't fill vacancies", font(F_SANS,22), INK2, box_w-60, align="center", leading=1.3)

x2=MARGIN+box_w+gap
rounded(d, [x2, box_y, x2+box_w, box_y+box_h], 14, fill=SURFACE)
t="2.5"; fnt=font(F_MONO_B,72); tw=d.textlength(t,font=fnt)
d.text((x2+box_w/2-tw/2, box_y+36), t, font=fnt, fill=BLUE)
draw_multiline(d,(x2+30,box_y+130),"jobseekers per open vacancy", font(F_SANS,22), INK2, box_w-60, align="center", leading=1.3)

vy = box_y+box_h+40
rounded(d, [MARGIN, vy, W-MARGIN, vy+280], 0, fill=None)
d.rectangle([MARGIN, vy, MARGIN+6, vy+280], fill=ACCENT)
draw_multiline(d, (MARGIN+34, vy+24), "It isn't a raw shortage of people. It's a mismatch: a narrow band of specialist, senior-leaning skills employers need, against a much larger pool of junior and generalist candidates chasing a shrinking number of entry doors.", font(F_SANS, 28), INK, W-2*MARGIN-60, leading=1.42)

cta_y = vy + 320
d.text((MARGIN, cta_y), "→ FULL INTERACTIVE BREAKDOWN + 3D SALARY EXPLORER", font=font(F_MONO_B, 24), fill=ACCENT)
d.text((MARGIN, cta_y+38), "link in the comments", font=font(F_SANS, 24), fill=INK2)
footer(d)
slides.append(img)

# =============================================================================
# Save PNGs + combined PDF
# =============================================================================
for i, s in enumerate(slides, start=1):
    s.save(OUT / f"slide_{i:02d}.png", "PNG")

slides[0].save(OUT / "carousel.pdf", save_all=True, append_images=slides[1:])
print(f"Wrote {len(slides)} slides + carousel.pdf")
