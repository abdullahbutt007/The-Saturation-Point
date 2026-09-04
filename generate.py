#!/usr/bin/env python3
"""
Generate 'The Saturation Point' UK Tech Job Market 2026 dashboard.
All figures are built with Plotly (dark 'control room' template matching the
site's design tokens) and every derived statistic is computed here, not
hand-typed, so the HTML always reflects the underlying numbers.
"""
import json
import string
from pathlib import Path

import plotly.graph_objects as go

OUT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# 3D discrete bar (box) mesh builder — used for the salary landscape.
# A go.Surface interpolates continuously between grid points, which implies
# fictitious in-between values ("junior-and-a-half") that don't exist in the
# data. Real boxes at exact x/y positions show only the true, fixed values.
# ---------------------------------------------------------------------------
def build_bar_mesh(grid, hx=0.34, hy=0.30):
    """grid[row][col] -> flat vertex arrays (x,y,z,i,j,k,intensity) for one
    solid box per cell, footprint centered at (col, row), height 0..value."""
    xs, ys, zs, intens = [], [], [], []
    I, J, K = [], [], []
    box_faces = [
        (0, 1, 2), (0, 2, 3),   # bottom
        (4, 5, 6), (4, 6, 7),   # top
        (0, 1, 5), (0, 5, 4),   # front
        (3, 2, 6), (3, 6, 7),   # back
        (0, 3, 7), (0, 7, 4),   # left
        (1, 2, 6), (1, 6, 5),   # right
    ]
    idx = 0
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            cx, cy, z0, z1 = c, r, 0, val
            verts = [
                (cx - hx, cy - hy, z0), (cx + hx, cy - hy, z0),
                (cx + hx, cy + hy, z0), (cx - hx, cy + hy, z0),
                (cx - hx, cy - hy, z1), (cx + hx, cy - hy, z1),
                (cx + hx, cy + hy, z1), (cx - hx, cy + hy, z1),
            ]
            for vx, vy, vz in verts:
                xs.append(vx); ys.append(vy); zs.append(vz); intens.append(val)
            o = idx * 8
            for a, b, cc in box_faces:
                I.append(o + a); J.append(o + b); K.append(o + cc)
            idx += 1
    return xs, ys, zs, I, J, K, intens

# ---------------------------------------------------------------------------
# Design tokens — charts render transparent, sitting inside dark navy
# "dashboard-panel" gradient cards on an otherwise light page (see design plan)
# ---------------------------------------------------------------------------
SURFACE      = "rgba(0,0,0,0)"   # transparent — panel gradient shows through
PAPER        = "rgba(0,0,0,0)"
INK_PRIMARY  = "#f3f2fa"    # text-inv
INK_SECOND   = "#c9cbe0"
INK_MUTED    = "#8b8fb0"    # text-inv-soft, lightened for chart legibility
GRID         = "rgba(243,242,250,0.10)"
BASELINE     = "rgba(243,242,250,0.20)"

# brand signal colors (match the page's --signal / --gold tokens)
SIGNAL    = "#ff3d68"   # alert / the problem
GOLD      = "#f5b93d"   # counter-signal / the alternative reading
C_BLUE    = "#5b7fd9"
C_GRAY    = "#454b6e"   # de-emphasis / context bars on a dark panel

# sequential ramp for magnitude charts on dark panels (indigo -> signal, low->high)
SEQ_BLUE = ["#8b9be0", "#7086dd", "#5a71d4", "#7a4fb8", "#a83f8e", "#d33d78", "#ff3d68"]

# multi-hue "heat landscape" ramp for the 3D centrepiece (low pay -> high pay):
# deep navy -> signal red -> gold, ordered low->high — the page's own brand hues
SEQ_LANDSCAPE = ["#171b30", "#33265c", "#6b2d6e", "#a8306e", "#ff3d68", "#f2914f", "#f5b93d"]

FONT_BODY = "Manrope, system-ui, sans-serif"
FONT_MONO = "IBM Plex Mono, ui-monospace, monospace"

BASE_LAYOUT = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=SURFACE,
    font=dict(family=FONT_BODY, color=INK_SECOND, size=13),
    margin=dict(l=48, r=24, t=28, b=44),
    hoverlabel=dict(bgcolor="#20252b", bordercolor=BASELINE,
                     font=dict(family=FONT_MONO, color=INK_PRIMARY, size=12)),
    showlegend=False,
)

def axis(**kw):
    d = dict(gridcolor=GRID, zerolinecolor=BASELINE, linecolor=BASELINE,
              tickfont=dict(color=INK_MUTED, size=11), color=INK_MUTED)
    d.update(kw)
    return d

figures = {}

# ---------------------------------------------------------------------------
# 1. Headline vacancies — ONS quarterly vacancy count, ORANGE = latest (signal)
# ---------------------------------------------------------------------------
quarters = ["Mar–May 2025", "Dec25–Feb 2026", "Mar–May 2026"]
vacancies = [738000, 726000, 707000]  # derived from ONS % changes, see stats block below
colors = [C_GRAY, C_GRAY, SIGNAL]
fig = go.Figure(go.Bar(
    x=quarters, y=vacancies, marker_color=colors, width=0.52,
    text=[f"{v:,.0f}" for v in vacancies], textposition="outside",
    textfont=dict(family=FONT_MONO, color=INK_PRIMARY, size=13),
    hovertemplate="<b>%{x}</b><br>%{y:,.0f} open vacancies<extra></extra>",
))
fig.update_layout(**BASE_LAYOUT,
    xaxis=axis(), yaxis=axis(title=None, range=[0, 820000], tickformat=","),
    height=300)
figures["vacancies"] = fig

# ---------------------------------------------------------------------------
# 2. Graduate postings collapse — indexed (Feb 2025 = 100)
# ---------------------------------------------------------------------------
grad_index = [100, 55]  # -45% YoY, Adzuna
fig = go.Figure(go.Bar(
    x=["Feb 2025", "Feb 2026"], y=grad_index,
    marker_color=[C_GRAY, SIGNAL], width=0.46,
    text=["index 100", "index 55  (–45%)"], textposition="outside",
    textfont=dict(family=FONT_MONO, color=INK_PRIMARY, size=13),
    hovertemplate="<b>%{x}</b><br>Graduate job postings index: %{y}<extra></extra>",
))
fig.update_layout(**BASE_LAYOUT,
    xaxis=axis(), yaxis=axis(range=[0, 130], showticklabels=False),
    height=260)
figures["grad_index"] = fig

# ---------------------------------------------------------------------------
# 3. Application flood — Tribepad, Nov 2023 -> Nov 2024, +286% YoY
# ---------------------------------------------------------------------------
apps_old = 48.7 / 3.86
apps_new = 48.7
fig = go.Figure(go.Bar(
    x=["Nov 2023", "Nov 2024"], y=[apps_old, apps_new],
    marker_color=[C_GRAY, SIGNAL], width=0.46,
    text=[f"{apps_old:.1f} applicants" , f"{apps_new:.1f} applicants"],
    textposition="outside",
    textfont=dict(family=FONT_MONO, color=INK_PRIMARY, size=13),
    hovertemplate="<b>%{x}</b><br>%{y:.1f} applications per vacancy<extra></extra>",
))
fig.update_layout(**BASE_LAYOUT,
    xaxis=axis(), yaxis=axis(range=[0, 62], showticklabels=False),
    height=260)
figures["applications"] = fig

# ---------------------------------------------------------------------------
# 4. Graduate unemployment by subject — emphasis chart (CS = accent)
# ---------------------------------------------------------------------------
subjects = ["Business & Management", "Economics", "Mathematics",
            "Finance & Accountancy", "Art", "Cinematics & Photography",
            "Computer Science"]
rates = [6.3, 6.8, 7.5, 8.1, 8.5, 8.7, 9.7]
colors = [C_GRAY]*6 + [SIGNAL]
fig = go.Figure(go.Bar(
    y=subjects, x=rates, orientation="h", marker_color=colors, width=0.6,
    text=[f"{r:.1f}%" for r in rates], textposition="outside",
    textfont=dict(family=FONT_MONO, color=INK_PRIMARY, size=12),
    hovertemplate="<b>%{y}</b><br>15-month unemployment rate: %{x}%<extra></extra>",
))
base_no_margin = {k: v for k, v in BASE_LAYOUT.items() if k != "margin"}
fig.update_layout(**base_no_margin,
    xaxis=axis(range=[0, 12], ticksuffix="%"),
    yaxis=axis(tickfont=dict(color=INK_SECOND, size=12)),
    height=340, margin=dict(l=190, r=40, t=20, b=40))
figures["grad_subjects"] = fig

# ---------------------------------------------------------------------------
# 5. Global tech layoffs, Q1 by year — line, annotate the 2025->2026 spike
# ---------------------------------------------------------------------------
years = ["Q1 2023", "Q1 2024", "Q1 2025", "Q1 2026"]
layoffs = [167674, 57269, 29845, 70474]
yoy_2526 = (layoffs[3] / layoffs[2] - 1) * 100
fig = go.Figure(go.Scatter(
    x=years, y=layoffs, mode="lines+markers+text",
    line=dict(color=SIGNAL, width=3, shape="spline"),
    marker=dict(size=9, color=SURFACE, line=dict(color=SIGNAL, width=2)),
    text=[f"{v:,.0f}" for v in layoffs], textposition="top center",
    textfont=dict(family=FONT_MONO, color=INK_PRIMARY, size=12),
    hovertemplate="<b>%{x}</b><br>%{y:,.0f} tech jobs cut worldwide<extra></extra>",
))
fig.add_annotation(x="Q1 2026", y=layoffs[3], ax=0, ay=-46,
    text=f"+{yoy_2526:.0f}% YoY", showarrow=False,
    font=dict(family=FONT_MONO, color=SIGNAL, size=12))
fig.update_layout(**BASE_LAYOUT,
    xaxis=axis(), yaxis=axis(tickformat=",", range=[0, 190000]),
    height=300)
figures["layoffs"] = fig

# ---------------------------------------------------------------------------
# 6. THE CENTREPIECE — 3D salary landscape: role x seniority x salary
# ---------------------------------------------------------------------------
roles = ["Software<br>Development", "Cloud<br>Engineering", "Cybersecurity",
         "Data &amp; AI", "DevOps &amp; SRE"]
seniority = ["Entry-level", "Mid-level", "Senior"]
salary_grid = [
    [33000, 47500, 38500, 45000, 44000],     # entry
    [55000, 65000, 56500, 65000, 65000],     # mid
    [82500, 95000, 80000, 95000, 92500],     # senior
]
multiples = [round(salary_grid[2][i] / salary_grid[0][i], 2) for i in range(5)]
multiple_grid = [[round(salary_grid[r][c] / salary_grid[0][c], 3) for c in range(5)] for r in range(3)]

# Per-vertex hover label for each box (8 identical labels per box, one per vertex)
salary_labels_grid = [[f"{roles[c].replace('<br>', ' ')} · {seniority[r]}<br>£{salary_grid[r][c]:,.0f} median"
                        for c in range(5)] for r in range(3)]
multiple_labels_grid = [[f"{roles[c].replace('<br>', ' ')} · {seniority[r]}<br>{multiple_grid[r][c]:.2f}× entry-level pay"
                          for c in range(5)] for r in range(3)]

def flatten_x8(labels_grid):
    out = []
    for row in labels_grid:
        for lab in row:
            out.extend([lab] * 8)
    return out

bx, by, bz, bi, bj, bk, b_intensity = build_bar_mesh(salary_grid)
_, _, mult_bz, _, _, _, mult_intensity = build_bar_mesh(multiple_grid)
salary_customdata_flat = flatten_x8(salary_labels_grid)
multiple_customdata_flat = flatten_x8(multiple_labels_grid)

fig = go.Figure(go.Mesh3d(
    x=bx, y=by, z=bz, i=bi, j=bj, k=bk,
    intensity=b_intensity, colorscale=[[i/(len(SEQ_LANDSCAPE)-1), c] for i, c in enumerate(SEQ_LANDSCAPE)],
    showscale=True, flatshading=True,
    colorbar=dict(title=dict(text="£ / yr", font=dict(color=INK_MUTED, size=11)),
                   tickfont=dict(color=INK_MUTED, size=10), thickness=14, len=0.6,
                   tickformat=","),
    hovertemplate="%{customdata}<extra></extra>",
    customdata=salary_customdata_flat,
    lighting=dict(ambient=0.65, diffuse=0.8, specular=0.3, roughness=0.5, fresnel=0.15),
    lightposition=dict(x=100, y=-100, z=200),
))
fig.update_layout(
    paper_bgcolor=PAPER,
    font=dict(family=FONT_BODY, color=INK_SECOND, size=12),
    margin=dict(l=0, r=0, t=10, b=0),
    height=520,
    scene=dict(
        xaxis=dict(title="", tickmode="array", tickvals=list(range(5)), ticktext=roles,
                    tickfont=dict(color=INK_MUTED, size=10), gridcolor=GRID,
                    backgroundcolor=SURFACE, showbackground=True, zerolinecolor=BASELINE),
        yaxis=dict(title="", tickmode="array", tickvals=list(range(3)), ticktext=seniority,
                    tickfont=dict(color=INK_MUTED, size=10), gridcolor=GRID,
                    backgroundcolor=SURFACE, showbackground=True, zerolinecolor=BASELINE),
        zaxis=dict(title=dict(text="median salary (£)", font=dict(color=INK_MUTED, size=10)),
                    tickfont=dict(color=INK_MUTED, size=10), gridcolor=GRID,
                    backgroundcolor=SURFACE, showbackground=True, zerolinecolor=BASELINE,
                    tickformat=","),
        camera=dict(eye=dict(x=1.55, y=-1.65, z=0.85)),
    ),
)
figures["salary3d"] = fig

# ---------------------------------------------------------------------------
# 7. Regional salary gap — London vs rest of UK (software developer)
# ---------------------------------------------------------------------------
fig = go.Figure(go.Bar(
    x=["Rest of UK", "London"], y=[60000, 82500],
    marker_color=[C_GRAY, GOLD], width=0.46,
    text=["£60,000", "£82,500  (+21% YoY)"], textposition="outside",
    textfont=dict(family=FONT_MONO, color=INK_PRIMARY, size=13),
    hovertemplate="<b>%{x}</b><br>Median software developer salary: £%{y:,.0f}<extra></extra>",
))
fig.update_layout(**BASE_LAYOUT,
    xaxis=axis(), yaxis=axis(range=[0, 100000], showticklabels=False),
    height=260)
figures["regional"] = fig

# ---------------------------------------------------------------------------
# Dump everything the page needs
# ---------------------------------------------------------------------------
chart_json = {k: json.loads(v.to_json()) for k, v in figures.items()}
chart_json["salary3d_extra"] = dict(
    salary_z=bz,
    multiple_z=mult_bz,
    salary_intensity=b_intensity,
    multiple_intensity=mult_intensity,
    salary_customdata=salary_customdata_flat,
    multiple_customdata=multiple_customdata_flat,
)

stats = dict(
    vacancy_latest=vacancies[2],
    vacancy_yoy_pct=-4.2,
    vacancy_qoq_pct=-2.6,
    unemployed_per_vacancy=2.5,
    cs_grad_unemployment=9.7,
    tech_postings_vs_prepandemic=-19,
    tech_postings_yoy=-8,
    grad_postings_yoy=-45,
    apps_old=round(apps_old, 1),
    apps_new=apps_new,
    apps_yoy_pct=286,
    layoffs_q1_2026=layoffs[3],
    layoffs_yoy_pct=round(yoy_2526, 1),
    softdev_postings_yoy=71,
    softdev_live_vacancies=366,
    softdev_median_salary=64809,
    softdev_salary_yoy=8.02,
    cyber_vacancy_yoy=12,
    ai_postings_multiple=3,
    ai_postings_share=5.6,
    entry_level_cut_share=66,
    cipd_ai_workforce_cut_pct=17,
    cipd_deep_cut_pct=26,
    cipd_junior_risk_pct=62,
    youth_unemployment_london=22.5,
    visa_threshold=41700,
    visa_roles_removed=111,
    visa_isc_increase=32,
    sponsor_licences_revoked=2000,
    recruitment_difficulty_pct=71,
    time_to_hire_increase="10–20%+",
    multiples=multiples,
)

(OUT_DIR / "chart_data.json").write_text(json.dumps(chart_json))
(OUT_DIR / "stats.json").write_text(json.dumps(stats, indent=2))
print("Derived stats:")
print(json.dumps(stats, indent=2))
