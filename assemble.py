#!/usr/bin/env python3
"""Assemble the final self-contained dashboard.html from chart_data.json + stats.json."""
import json
import string
from pathlib import Path

OUT_DIR = Path(__file__).parent
chart_data = json.loads((OUT_DIR / "chart_data.json").read_text())
stats = json.loads((OUT_DIR / "stats.json").read_text())

CHART_JSON = json.dumps(chart_data)

TEMPLATE = r"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<title>The Saturation Point</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.24.1/plotly.min.js"></script>
<style>
  :root{
    --ink:#10131f; --ink-2:#171b30;
    --paper:#f6f5fb; --paper-2:#ffffff;
    --text:#14162a; --text-soft:#4b4e68;
    --text-inv:#f3f2fa; --text-inv-soft:#abaec9;
    --line:rgba(20,22,42,0.12); --line-inv:rgba(243,242,250,0.14);
    --signal:#ff3d68; --signal-ink:#ffffff;
    --gold:#f5b93d;
    --surface:#ffffff; --surface-2:#edecf6;
    --shadow:0 20px 50px -25px rgba(14,17,32,0.35);
    --radius:14px; --maxw:1180px;
    --font-display:"Bricolage Grotesque","Manrope",sans-serif;
    --font-body:"Manrope",system-ui,-apple-system,"Segoe UI",sans-serif;
    --font-mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
  }
  @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      --paper:#0e1120; --paper-2:#14172b; --text:#f3f2fa; --text-soft:#abaec9;
      --line:rgba(243,242,250,0.14); --surface:#171b30; --surface-2:#1d2138;
      --shadow:0 20px 50px -20px rgba(0,0,0,0.6);
    }
  }
  :root[data-theme="dark"]{
    --paper:#0e1120; --paper-2:#14172b; --text:#f3f2fa; --text-soft:#abaec9;
    --line:rgba(243,242,250,0.14); --surface:#171b30; --surface-2:#1d2138;
    --shadow:0 20px 50px -20px rgba(0,0,0,0.6);
  }
  *{box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  @media (prefers-reduced-motion: reduce){ html{scroll-behavior:auto;} *{animation-duration:.001ms !important;transition-duration:.001ms !important;scroll-behavior:auto !important;} }
  body{margin:0;background:var(--paper);color:var(--text);font-family:var(--font-body);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased;}
  h1,h2,h3,h4{font-family:var(--font-display);font-weight:700;line-height:1.06;letter-spacing:-0.01em;text-wrap:balance;margin:0;}
  a{color:inherit;}
  .mono{font-family:var(--font-mono);font-variant-numeric:tabular-nums;}
  .wrap{max-width:var(--maxw);margin:0 auto;padding:0 clamp(20px,5vw,48px);}

  .eyebrow{font-family:var(--font-mono);font-size:.78rem;letter-spacing:.13em;text-transform:uppercase;color:var(--signal);display:inline-flex;align-items:center;gap:10px;font-weight:600;}
  .eyebrow::before{content:"";width:22px;height:2px;background:var(--signal);display:inline-block;}

  header.mast{position:sticky;top:0;z-index:50;background:color-mix(in srgb, var(--paper) 88%, transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);}
  .nav{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:16px clamp(20px,5vw,48px);max-width:var(--maxw);margin:0 auto;}
  .brand{font-family:var(--font-display);font-weight:800;font-size:1.25rem;letter-spacing:-0.01em;background:linear-gradient(120deg, var(--text) 45%, var(--signal) 90%);-webkit-background-clip:text;background-clip:text;color:transparent;white-space:nowrap;}
  nav.links{display:flex;align-items:center;gap:clamp(14px,2.4vw,26px);flex-wrap:wrap;}
  nav.links a{text-decoration:none;font-size:.86rem;font-weight:600;color:var(--text-soft);}
  nav.links a:hover{color:var(--text);}
  .nav-pill{font-family:var(--font-mono);font-size:.72rem;letter-spacing:.05em;color:var(--signal);border:1px solid color-mix(in srgb, var(--signal) 35%, transparent);background:color-mix(in srgb, var(--signal) 10%, transparent);padding:5px 10px;border-radius:999px;white-space:nowrap;}
  @media (max-width:920px){ nav.links{display:none;} }

  .btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:12px 22px;border-radius:999px;font-weight:700;font-size:.92rem;text-decoration:none;cursor:pointer;border:1px solid transparent;transition:transform .15s ease;}
  .btn:hover{transform:translateY(-1px);}
  .btn-primary{background:var(--signal);color:var(--signal-ink);box-shadow:0 10px 30px -12px rgba(255,61,104,.55);}
  .btn-ghost{background:transparent;color:var(--text);border-color:var(--line);}

  .hero{padding:clamp(48px,8vw,88px) 0 clamp(40px,6vw,64px);overflow:hidden;}
  .hero-grid{display:grid;grid-template-columns:1.15fr .85fr;gap:clamp(28px,5vw,56px);align-items:center;}
  .hero h1{font-size:clamp(2.3rem,5vw,3.7rem);margin:16px 0 18px;}
  .hero h1 em{font-style:normal;color:var(--signal);}
  .hero p.lede{font-size:clamp(1.02rem,1.5vw,1.18rem);color:var(--text-soft);max-width:46ch;margin:0 0 26px;}
  .hero-ctas{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:30px;}
  .hero-meta{display:flex;gap:clamp(18px,3.5vw,34px);flex-wrap:wrap;padding-top:20px;border-top:1px solid var(--line);}
  .hero-meta div{display:flex;flex-direction:column;gap:4px;}
  .hero-meta .num{font-family:var(--font-mono);font-weight:600;font-size:1.05rem;color:var(--text);}
  .hero-meta .lbl{font-size:.78rem;color:var(--text-soft);}

  .hero-visual{position:relative;aspect-ratio:1/1;border-radius:20px;background:linear-gradient(160deg, var(--ink), var(--ink-2));box-shadow:var(--shadow);overflow:hidden;}
  .hero-visual .inner{position:absolute;inset:20px 16px 46px;}
  .hero-visual .tag{position:absolute;left:18px;bottom:18px;font-family:var(--font-mono);font-size:.7rem;letter-spacing:.06em;color:rgba(243,242,250,.8);background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);padding:6px 10px;border-radius:999px;}
  @media (max-width:880px){ .hero-grid{grid-template-columns:1fr;} .hero-visual{order:-1;max-width:420px;margin:0 auto;} }

  .section-head{max-width:60ch;margin-bottom:clamp(24px,4vw,36px);}
  .section-head h2{font-size:clamp(1.6rem,2.8vw,2.2rem);margin-top:12px;}
  .section-head p{color:var(--text-soft);margin-top:10px;font-size:1rem;}

  .band{padding:clamp(48px,7vw,80px) 0;border-bottom:1px solid var(--line);}
  .band-alt{background:var(--surface);}

  /* dark data panel — hosts every chart */
  .dashboard-panel{position:relative;background:linear-gradient(160deg, var(--ink), var(--ink-2));border-radius:20px;padding:clamp(20px,3vw,30px);box-shadow:var(--shadow);}
  .dash-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px;}
  .stat-tile{background:rgba(255,255,255,.04);border:1px solid var(--line-inv);border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:6px;min-height:96px;justify-content:space-between;}
  .stat-tile .stat-label{font-size:.78rem;color:var(--text-inv-soft);}
  .stat-tile .stat-value{font-family:var(--font-mono);font-size:1.5rem;font-weight:700;color:var(--text-inv);line-height:1.1;}
  .stat-tile .stat-delta{font-size:.78rem;font-weight:600;}
  .up{color:#4ce0a3;} .down{color:var(--signal);} .neutral{color:var(--text-inv-soft);font-weight:500;}
  .dash-charts{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  .dash-charts.single{grid-template-columns:1fr;}
  .chart-card{background:rgba(255,255,255,.03);border:1px solid var(--line-inv);border-radius:12px;padding:16px 16px 6px;}
  .chart-head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:4px;gap:8px;flex-wrap:wrap;}
  .chart-head h3{font-family:var(--font-body);font-size:.92rem;font-weight:700;color:var(--text-inv);}
  .chart-sub{font-family:var(--font-mono);font-size:.68rem;color:var(--text-inv-soft);}
  .demo-source{margin-top:16px;font-size:.76rem;color:var(--text-inv-soft);}
  @media (max-width:720px){ .dash-stats{grid-template-columns:1fr;} .dash-charts{grid-template-columns:1fr;} }

  /* light card grid (AI section) */
  .why-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}
  .why-card{padding:20px;border-radius:var(--radius);background:var(--surface);border:1px solid var(--line);}
  .why-card .why-num{font-family:var(--font-mono);color:var(--signal);font-size:1.6rem;font-weight:700;}
  .why-card p{color:var(--text-soft);font-size:.92rem;margin:8px 0 0;line-height:1.45;}
  @media (max-width:880px){ .why-grid{grid-template-columns:1fr 1fr;} }
  @media (max-width:520px){ .why-grid{grid-template-columns:1fr;} }

  /* process list (visa timeline) */
  .process-list{display:grid;grid-template-columns:repeat(5,1fr);gap:18px;}
  .process-step{padding-top:16px;border-top:2px solid var(--signal);}
  .process-num{font-family:var(--font-mono);font-size:.78rem;color:var(--signal);font-weight:600;margin-bottom:8px;display:block;}
  .process-step .pv{font-family:var(--font-mono);font-weight:700;font-size:1.15rem;color:var(--text);display:block;margin-bottom:6px;}
  .process-step p{color:var(--text-soft);font-size:.85rem;margin:0;line-height:1.4;}
  @media (max-width:880px){ .process-list{grid-template-columns:1fr 1fr;} }
  @media (max-width:520px){ .process-list{grid-template-columns:1fr;} }

  /* compact data table */
  .dash-table-wrap{overflow-x:auto;border:1px solid var(--line-inv);border-radius:12px;margin-top:16px;}
  table.dash-table{width:100%;border-collapse:collapse;font-size:.86rem;min-width:480px;}
  table.dash-table th,table.dash-table td{padding:10px 14px;text-align:left;white-space:nowrap;}
  table.dash-table thead th{font-family:var(--font-mono);font-size:.68rem;text-transform:uppercase;letter-spacing:.04em;color:var(--text-inv-soft);background:rgba(255,255,255,.04);}
  table.dash-table tbody tr{border-top:1px solid var(--line-inv);}
  table.dash-table td{color:var(--text-inv-soft);}
  table.dash-table td.mono{font-family:var(--font-mono);color:var(--text-inv);}
  table.dash-table td.hot{color:var(--gold);font-family:var(--font-mono);font-weight:700;}

  .toggle-row{display:flex;gap:0;border:1px solid var(--line-inv);border-radius:999px;overflow:hidden;width:fit-content;margin-bottom:14px;}
  .toggle-btn{font-family:var(--font-mono);font-size:.74rem;letter-spacing:.02em;color:var(--text-inv-soft);background:transparent;border:none;padding:9px 16px;cursor:pointer;}
  .toggle-btn+.toggle-btn{border-left:1px solid var(--line-inv);}
  .toggle-btn.active{background:rgba(255,61,104,.16);color:var(--signal);}
  .hint{font-family:var(--font-mono);font-size:.7rem;color:var(--text-inv-soft);float:right;padding-top:12px;}

  /* verdict / about-card */
  .about-card{background:linear-gradient(160deg, var(--ink), var(--ink-2));border-radius:20px;padding:clamp(26px,4vw,38px);color:var(--text-inv);box-shadow:var(--shadow);}
  .paradox{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;}
  .paradox .side{background:rgba(255,255,255,.04);border:1px solid var(--line-inv);border-radius:12px;padding:20px;text-align:center;}
  .paradox .side .num{font-family:var(--font-mono);font-weight:700;font-size:2.4rem;}
  .paradox .side .lbl{font-size:.82rem;color:var(--text-inv-soft);margin-top:6px;}
  .about-card p.verdict-text{font-size:1.05rem;line-height:1.6;color:var(--text-inv);max-width:70ch;margin:0 0 22px;}
  .about-card p.verdict-text b{color:var(--gold);}
  .chip-row{display:flex;flex-wrap:wrap;gap:10px;}
  .chip{font-family:var(--font-mono);font-size:.78rem;padding:9px 14px;border-radius:999px;background:rgba(255,255,255,.06);border:1px solid var(--line-inv);color:var(--text-inv);}
  @media (max-width:640px){ .paradox{grid-template-columns:1fr;} }

  details.faq-item{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:0 22px;}
  details.faq-item summary{cursor:pointer;padding:18px 0;font-weight:700;font-size:.98rem;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:16px;}
  details.faq-item summary::-webkit-details-marker{display:none;}
  details.faq-item summary::after{content:"+";font-family:var(--font-mono);font-size:1.2rem;color:var(--text-soft);}
  details.faq-item[open] summary::after{content:"\2212";}
  .src-grid{display:flex;flex-wrap:wrap;gap:8px;padding-bottom:20px;}
  .src-grid a{font-size:.78rem;color:var(--text-soft);text-decoration:none;background:var(--surface-2);border-radius:999px;padding:6px 12px;}
  .src-grid a:hover{color:var(--text);}
  .fine{color:var(--text-soft);font-size:.82rem;}
  .methodology{max-width:70ch;line-height:1.55;margin-top:14px;}

  footer{border-top:1px solid var(--line);padding:30px 0 40px;}
  .footer-row{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;}
</style>
</head>
<body>

<header class="mast">
  <div class="nav">
    <span class="brand">The Saturation Point</span>
    <nav class="links">
      <a href="#vacancies">Vacancies</a>
      <a href="#applicants">Applicants</a>
      <a href="#ai">AI</a>
      <a href="#layoffs">Layoffs</a>
      <a href="#salaries">Salaries</a>
      <a href="#visa">Visa</a>
      <a href="#verdict">Verdict</a>
    </nav>
    <span class="nav-pill">UK TECH &middot; 2026</span>
  </div>
</header>

<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Labour Market Briefing &middot; UK Tech &middot; 2026</span>
      <h1>The UK tech job market is <em>saturated</em>.</h1>
      <p class="lede">Tech postings are down 19% on pre-pandemic levels, and 66% of UK enterprises are now cutting entry-level hiring as AI absorbs junior work.</p>
      <div class="hero-ctas">
        <a href="#vacancies" class="btn btn-primary">See the numbers &darr;</a>
        <a href="#verdict" class="btn btn-ghost">Read the verdict</a>
      </div>
      <div class="hero-meta">
        <div><span class="num">&minus;19%</span><span class="lbl">tech postings vs. pre-pandemic</span></div>
        <div><span class="num">66%</span><span class="lbl">enterprises cutting entry-level hiring</span></div>
        <div><span class="num">9.7%</span><span class="lbl">CS graduate unemployment</span></div>
        <div><span class="num">&minus;45%</span><span class="lbl">graduate postings, YoY</span></div>
      </div>
    </div>
    <div class="hero-visual">
      <div class="inner" id="chart-hero"></div>
      <span class="tag">TECH &middot; GRADUATE POSTINGS INDEX</span>
    </div>
  </div>
</section>

<section class="band" id="vacancies">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">01 &mdash; Supply</span>
      <h2>Doors are closing.</h2>
      <p>Vacancies just hit a five-year low, and graduate postings collapsed even faster.</p>
    </div>
    <div class="dashboard-panel">
      <div class="dash-stats">
        <div class="stat-tile"><span class="stat-label">UK vacancies, Mar&ndash;May 2026</span><span class="stat-value">707,000</span><span class="stat-delta down">&#9660; lowest since 2021</span></div>
        <div class="stat-tile"><span class="stat-label">Tech postings vs. pre-pandemic</span><span class="stat-value">&minus;19%</span><span class="stat-delta down">&#9660; 8% lower YoY too</span></div>
        <div class="stat-tile"><span class="stat-label">Graduate postings, YoY</span><span class="stat-value">&minus;45%</span><span class="stat-delta down">&#9660; below 10,000, first time on record</span></div>
      </div>
      <div class="dash-charts">
        <div class="chart-card"><div class="chart-head"><h3>UK vacancies, by quarter</h3><span class="chart-sub">ONS</span></div><div id="chart-vacancies"></div></div>
        <div class="chart-card"><div class="chart-head"><h3>Graduate postings index</h3><span class="chart-sub">Feb 2025 = 100</span></div><div id="chart-grad-index"></div></div>
      </div>
      <p class="demo-source">Source: ONS, Vacancies and jobs in the UK, June 2026 &middot; Adzuna, Feb 2026 UK job market report</p>
    </div>
  </div>
</section>

<section class="band band-alt" id="applicants">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">02 &mdash; Demand for every role</span>
      <h2>Every vacancy gets buried.</h2>
      <p>Applications per role have multiplied &mdash; and Computer Science graduates are absorbing the sharpest edge of it.</p>
    </div>
    <div class="dashboard-panel">
      <div class="dash-stats">
        <div class="stat-tile"><span class="stat-label">Applications per vacancy</span><span class="stat-value">48.7</span><span class="stat-delta down">&#9650; 286% YoY</span></div>
        <div class="stat-tile"><span class="stat-label">Most applied-for category</span><span class="stat-value">IT / Software</span><span class="stat-delta neutral">#1 in the UK &middot; CV-Library</span></div>
        <div class="stat-tile"><span class="stat-label">London youth unemployment</span><span class="stat-value">22.5%</span><span class="stat-delta down">ages 16&ndash;24</span></div>
      </div>
      <div class="dash-charts">
        <div class="chart-card"><div class="chart-head"><h3>Applications per vacancy</h3><span class="chart-sub">Tribepad</span></div><div id="chart-applications"></div></div>
        <div class="chart-card"><div class="chart-head"><h3>Graduate unemployment by subject</h3><span class="chart-sub">15mo post-grad</span></div><div id="chart-grad-subjects"></div></div>
      </div>
      <p class="demo-source">Source: Tribepad platform data, Nov 2023&ndash;Nov 2024 &middot; CV-Library/Onrec, Q4 2025 &middot; Jisic graduate outcomes, 2023 cohort</p>
    </div>
  </div>
</section>

<section class="band" id="ai">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">03 &mdash; The AI effect</span>
      <h2>AI is doing two things at once.</h2>
      <p>Absorbing the tasks juniors used to learn on, while opening a narrow band of senior roles most people aren't qualified for yet.</p>
    </div>
    <div class="why-grid">
      <div class="why-card"><span class="why-num">66%</span><p>of UK enterprises are cutting entry-level hiring &mdash; AI now absorbs junior tasks.</p></div>
      <div class="why-card"><span class="why-num">3&times;</span><p>the rate AI-related postings are growing at, vs. the UK average job category.</p></div>
      <div class="why-card"><span class="why-num">17%</span><p>of employers expect to shrink headcount via AI within 12 months (CIPD).</p></div>
      <div class="why-card"><span class="why-num">62%</span><p>of those say clerical, junior and admin roles are most exposed.</p></div>
    </div>
    <p class="demo-source fine" style="margin-top:14px;">Source: CompTIA, UK Tech Workforce 2026 &middot; CIPD Labour Market Outlook, 2026</p>
  </div>
</section>

<section class="band band-alt" id="layoffs">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">04 &mdash; Refilling the pool</span>
      <h2>Layoffs are back.</h2>
      <p>Global tech layoffs reversed 2025's brief calm &mdash; and every laid-off engineer competes in the same pool as new graduates.</p>
    </div>
    <div class="dashboard-panel">
      <div class="dash-stats">
        <div class="stat-tile"><span class="stat-label">Global tech layoffs, Q1 2026</span><span class="stat-value">70,474</span><span class="stat-delta down">&#9650; 136% YoY</span></div>
        <div class="stat-tile"><span class="stat-label">Share attributed to AI/automation</span><span class="stat-value">~50%</span><span class="stat-delta neutral">of all 2026 cuts</span></div>
        <div class="stat-tile"><span class="stat-label">Share that were US-based</span><span class="stat-value">~75%</span><span class="stat-delta neutral">UK arms not spared</span></div>
      </div>
      <div class="dash-charts single">
        <div class="chart-card"><div class="chart-head"><h3>Global tech layoffs, Q1 by year</h3><span class="chart-sub">Layoffs.fyi</span></div><div id="chart-layoffs"></div></div>
      </div>
      <p class="demo-source">Source: Layoffs.fyi tracker &middot; Nikkei Asia corroborating estimate, ~78,000&ndash;80,000 for Q1 2026</p>
    </div>
  </div>
</section>

<section class="band" id="salaries">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">05 &mdash; The salary landscape</span>
      <h2>Pay climbs steeply &mdash; for people who already made it.</h2>
      <p>Rotate the landscape: the entry-level plateau is wide and low, the senior peaks keep rising.</p>
    </div>
    <div class="dashboard-panel">
      <div class="toggle-row" role="group" aria-label="3D chart view">
        <button class="toggle-btn active" id="btn-salary" onclick="setSalaryView('salary')">Median salary (£)</button>
        <button class="toggle-btn" id="btn-multiple" onclick="setSalaryView('multiple')">&times; entry-level pay</button>
      </div>
      <span class="hint">drag to rotate &middot; scroll to zoom</span>
      <div class="chart-card" style="padding:8px;">
        <div id="chart-salary3d" style="height:480px;"></div>
      </div>
      <div class="dash-table-wrap">
        <table class="dash-table">
          <thead><tr><th>Specialism</th><th>Entry</th><th>Senior</th><th>Multiple</th></tr></thead>
          <tbody>
            <tr><td>Software Development</td><td class="mono">&pound;33,000</td><td class="mono">&pound;82,500</td><td class="hot">2.5&times;</td></tr>
            <tr><td>Cloud Engineering</td><td class="mono">&pound;47,500</td><td class="mono">&pound;95,000</td><td class="hot">2.0&times;</td></tr>
            <tr><td>Cybersecurity</td><td class="mono">&pound;38,500</td><td class="mono">&pound;80,000</td><td class="hot">2.1&times;</td></tr>
            <tr><td>Data &amp; AI</td><td class="mono">&pound;45,000</td><td class="mono">&pound;95,000</td><td class="hot">2.1&times;</td></tr>
            <tr><td>DevOps &amp; SRE</td><td class="mono">&pound;44,000</td><td class="mono">&pound;92,500</td><td class="hot">2.1&times;</td></tr>
          </tbody>
        </table>
      </div>
      <p class="demo-source">Cybersecurity vacancies &#9650; 12% YoY, 70%+ orgs report a skills shortage &middot; Software Dev postings &#9650; 71% YoY, only 366 live roles nationwide &middot; Source: IT Job Board Salary Guide 2026, IT Jobs Watch</p>
    </div>
  </div>
</section>

<section class="band band-alt" id="visa">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">06 &mdash; Borders tightening</span>
      <h2>The side door narrowed too.</h2>
      <p>Even the specialist tier that is hiring has a harder route in for international talent.</p>
    </div>
    <div class="process-list">
      <div class="process-step"><span class="process-num">01</span><span class="pv">&pound;41,700</span><p>new salary floor to sponsor a Skilled Worker visa</p></div>
      <div class="process-step"><span class="process-num">02</span><span class="pv">111 roles cut</span><p>occupations removed from the eligible list</p></div>
      <div class="process-step"><span class="process-num">03</span><span class="pv">B1 &rarr; B2</span><p>English proficiency requirement raised</p></div>
      <div class="process-step"><span class="process-num">04</span><span class="pv">5 &rarr; 10 yrs</span><p>standard path to settlement, roughly doubled</p></div>
      <div class="process-step"><span class="process-num">05</span><span class="pv">~2,000</span><p>sponsor licences revoked in 2025 alone</p></div>
    </div>
    <p class="demo-source fine" style="margin-top:18px;">Source: UK Home Office rule changes, 2025&ndash;26, via Centuro Global &amp; IAS Services</p>
  </div>
</section>

<section class="band" id="regional">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">07 &mdash; Beyond London</span>
      <h2>The M25 isn't the only map anymore.</h2>
      <p>London still pays a premium, but the South West and secondary hubs are where growth is happening.</p>
    </div>
    <div class="dashboard-panel">
      <div class="dash-stats">
        <div class="stat-tile"><span class="stat-label">South West, tech jobs projected</span><span class="stat-value">+125,000</span><span class="stat-delta up">&#9650; new cluster growth</span></div>
        <div class="stat-tile"><span class="stat-label">Secondary hubs scaling</span><span class="stat-value">5 cities</span><span class="stat-delta neutral">Manchester, Birmingham, Edinburgh, Bristol, Leeds</span></div>
        <div class="stat-tile"><span class="stat-label">London salary premium</span><span class="stat-value">+21%</span><span class="stat-delta up">YoY for software developers</span></div>
      </div>
      <div class="dash-charts single">
        <div class="chart-card"><div class="chart-head"><h3>Software developer median salary</h3><span class="chart-sub">IT Jobs Watch</span></div><div id="chart-regional"></div></div>
      </div>
      <p class="demo-source">Source: IT Jobs Watch, UK Software Developer salary data, 6 months to Sep 2026 &middot; itjobboard.co.uk regional cluster projections</p>
    </div>
  </div>
</section>

<section class="band band-alt" id="verdict">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">08 &mdash; The verdict</span>
      <h2>It isn't a shortage. It's a mismatch.</h2>
    </div>
    <div class="about-card">
      <div class="paradox">
        <div class="side"><span class="num down">71%</span><span class="lbl">of employers can't fill vacancies</span></div>
        <div class="side"><span class="num" style="color:var(--gold);">2.5</span><span class="lbl">jobseekers per open vacancy</span></div>
      </div>
      <p class="verdict-text">A narrow band of <b>specialist, senior-leaning skills</b> employers actually need &mdash; cloud, cybersecurity, applied AI, 3+ years' experience &mdash; against a much larger pool of junior and generalist candidates chasing a shrinking number of entry doors. Time-to-hire is up 10&ndash;20%+ because employers are pickier, not because nobody is applying.</p>
      <div class="chip-row">
        <span class="chip">&rarr; Specialise early</span>
        <span class="chip">&rarr; Widen your map beyond London</span>
        <span class="chip">&rarr; Expect 40&ndash;50+ applications as normal</span>
        <span class="chip">&rarr; Weight experience over credentials</span>
      </div>
    </div>
  </div>
</section>

<section class="band" id="sources">
  <div class="wrap">
    <details class="faq-item">
      <summary>Where this data comes from</summary>
      <div class="src-grid">
        <a href="https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/bulletins/jobsandvacanciesintheuk/june2026" target="_blank" rel="noopener">ONS &middot; Vacancies &amp; Jobs, June 2026</a>
        <a href="https://www.itjobboard.co.uk/blog/353/state-of-uk-it-jobs-market-2026-full-report/" target="_blank" rel="noopener">IT Job Board &middot; State of UK IT Jobs 2026</a>
        <a href="https://www.freshminds.co.uk/blog/2026/05/how-difficult-is-the-uk-job-market" target="_blank" rel="noopener">Freshminds &middot; UK Job Market Difficulty</a>
        <a href="https://careermetrics.co.uk/blog/uk-graduate-vacancies-crash-record-low-2026/" target="_blank" rel="noopener">CareerMetrics &middot; Graduate Vacancies</a>
        <a href="https://www.efinancialcareers.com/news/unemployment-uk-graduates" target="_blank" rel="noopener">eFinancialCareers &middot; CS Grad Unemployment</a>
        <a href="https://employernews.co.uk/news/applications-per-job-up-286-yoy-as-uk-job-market-faces-ongoing-challenges/" target="_blank" rel="noopener">Tribepad &middot; Applications +286%</a>
        <a href="https://www.onrec.com/news/news-archive/the-uks-most-applied-for-jobs-in-2026-it-and-administration-top-list" target="_blank" rel="noopener">CV-Library &middot; Most Applied-For Jobs</a>
        <a href="https://gulfnews.com/business/tech-layoffs-top-30000-in-2026-worst-hit-countries-revealed-1.500441093" target="_blank" rel="noopener">Layoffs.fyi &middot; 2026 Tech Layoffs</a>
        <a href="https://techradar.com/pro/nearly-80-000-tech-workers-have-already-lost-their-jobs-in-2026-and-ai-impact-means-more-could-be-to-come" target="_blank" rel="noopener">TechRadar Pro &middot; Q1 2026 Layoffs</a>
        <a href="https://www.peoplemanagement.co.uk/article/1939164/one-six-employers-expect-job-losses-ai-cipd-finds" target="_blank" rel="noopener">People Management &middot; CIPD AI Survey</a>
        <a href="https://www.comptia.org/en-gb/blog/the-uk-tech-workforce-in-2026/" target="_blank" rel="noopener">CompTIA &middot; UK Tech Workforce 2026</a>
        <a href="https://www.itjobswatch.co.uk/jobs/uk/software%20developer.do" target="_blank" rel="noopener">IT Jobs Watch &middot; Software Developer</a>
        <a href="https://www.itjobboard.co.uk/blog/203/it-&-tech-job-salaries-in-the-uk-(2026)-%E2%80%94-complete-pay-guide-by-role/" target="_blank" rel="noopener">IT Job Board &middot; Salary Guide 2026</a>
        <a href="https://www.centuroglobal.com/articles/uk-immigration-2026-changes/" target="_blank" rel="noopener">Centuro Global &middot; Immigration Changes</a>
      </div>
      <p class="fine methodology">Figures are drawn from official statistics (ONS, UK Home Office) and industry trackers (Adzuna, Layoffs.fyi, IT Jobs Watch, CV-Library, Tribepad, CIPD) published between late 2025 and September 2026. Where an exact time series wasn't publicly available, two known anchor points are shown as an indexed comparison rather than an invented trend line. Vacancy and application figures use different underlying methodologies (survey-based vs. platform-based) and are presented as directional evidence, not one unified series.</p>
    </details>
  </div>
</section>

<footer>
  <div class="wrap footer-row">
    <span class="brand">The Saturation Point</span>
    <span class="fine">Independent UK tech labour-market analysis &middot; September 2026</span>
  </div>
</footer>

<script>
const CHART_DATA = $CHART_DATA_JSON;
const cfg = {displayModeBar:false, responsive:true};

Plotly.newPlot('chart-hero', CHART_DATA.grad_index.data, CHART_DATA.grad_index.layout, cfg);
Plotly.newPlot('chart-vacancies', CHART_DATA.vacancies.data, CHART_DATA.vacancies.layout, cfg);
Plotly.newPlot('chart-grad-index', CHART_DATA.grad_index.data, CHART_DATA.grad_index.layout, cfg);
Plotly.newPlot('chart-applications', CHART_DATA.applications.data, CHART_DATA.applications.layout, cfg);
Plotly.newPlot('chart-grad-subjects', CHART_DATA.grad_subjects.data, CHART_DATA.grad_subjects.layout, cfg);
Plotly.newPlot('chart-layoffs', CHART_DATA.layoffs.data, CHART_DATA.layoffs.layout, cfg);
Plotly.newPlot('chart-regional', CHART_DATA.regional.data, CHART_DATA.regional.layout, cfg);
Plotly.newPlot('chart-salary3d', CHART_DATA.salary3d.data, CHART_DATA.salary3d.layout, cfg);

function setSalaryView(mode){
  const extra = CHART_DATA.salary3d_extra;
  const btnSalary = document.getElementById('btn-salary');
  const btnMultiple = document.getElementById('btn-multiple');
  if(mode === 'salary'){
    Plotly.restyle('chart-salary3d', {
      z: [extra.salary_z],
      intensity: [extra.salary_intensity],
      customdata: [extra.salary_customdata],
      'colorbar.title.text': '£ / yr',
      'colorbar.tickformat': ','
    });
    btnSalary.classList.add('active');
    btnMultiple.classList.remove('active');
  } else {
    Plotly.restyle('chart-salary3d', {
      z: [extra.multiple_z],
      intensity: [extra.multiple_intensity],
      customdata: [extra.multiple_customdata],
      'colorbar.title.text': '× entry',
      'colorbar.tickformat': '.1f'
    });
    btnMultiple.classList.add('active');
    btnSalary.classList.remove('active');
  }
}
</script>
</body>
</html>
"""

tpl = string.Template(TEMPLATE)
html = tpl.substitute(CHART_DATA_JSON=CHART_JSON)
(OUT_DIR / "dashboard.html").write_text(html)
print("Wrote", OUT_DIR / "dashboard.html", "-", len(html), "bytes")
