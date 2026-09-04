# The Saturation Point — UK Tech Job Market 2026

An interactive data project on the state of the UK tech job market in 2026: is it actually as saturated as it feels, or is that just noise? I pulled real labour-market data from ONS, Adzuna, CIPD, IT Jobs Watch, Layoffs.fyi, CV-Library and the UK Home Office, built the charts in Python/Plotly, and put it together as a single self-contained interactive dashboard.

**Live dashboard:** add your hosted link here (GitHub Pages instructions below)

![Dashboard preview](assets/preview.png)

## What's in it

- Vacancy trends and the graduate postings collapse
- The application flood (applications per vacancy, YoY)
- Where AI is actually cutting entry-level hiring, and by how much
- Global tech layoffs, Q1 by year
- A 3D salary chart: median pay and pay multiple by role and seniority — junior, mid, senior, across five specialisms
- The UK visa/sponsorship changes making things tighter for international candidates
- Regional pay gap (London vs. the rest of the UK)

## Why the salary chart is bars, not a smooth surface

Early version of this used a `go.Surface` mesh across the role/seniority grid. That's wrong for this data: a surface interpolates continuously between grid points, so it implies pay values for something like "junior-and-a-half" that doesn't exist. The current version renders each role/seniority combination as its own discrete 3D bar (built with `go.Mesh3d`), so you're only ever looking at the 15 real numbers, not an invented gradient between them.

## Stack

Python · Plotly · Pillow (PIL) · Playwright · HTML/CSS/JS · no backend, no build step

## Running it locally

```bash
pip install -r requirements.txt
python generate.py     # computes stats + builds all Plotly figures -> chart_data.json, stats.json
python assemble.py     # assembles the self-contained dashboard.html
python build_carousel.py   # builds the 10-slide LinkedIn carousel (slide_*.png + carousel.pdf)
```

`dashboard.html` is fully self-contained (all chart data inlined, fonts and Plotly loaded from CDN) — open it directly in a browser, no server needed.

## Rendering a walkthrough video

```bash
playwright install chromium   # one-time browser download
python render_walkthrough.py  # -> dashboard_walkthrough.mp4
```

This doesn't screen-record the browser in real time. A real-time recording only captures a new frame when the browser repaints, and repaints don't land at even intervals — stretch that into a fixed frame rate and you get stutter. Instead, `render_walkthrough.py` drives the scroll position and the 3D chart's camera angle itself, one exact step at a time, screenshots each step, and hands ffmpeg the frame sequence with an explicit duration per frame. Every frame is deterministic, so playback can't stutter. Needs `ffmpeg` on `PATH`.

## Hosting it on GitHub Pages

The `docs/index.html` file is a copy of the built dashboard. To make it public:

1. Repo Settings → Pages → Source: deploy from branch → branch `main`, folder `/docs`
2. Save. GitHub gives you a `https://<username>.github.io/<repo>/` URL a minute or two later.

If you rebuild the dashboard, copy the new `dashboard.html` over `docs/index.html` before pushing.

## Data notes

Vacancy and application figures come from different methodologies (survey-based vs. platform-based) and are shown as directional evidence, not a single unified series. Where an exact time series wasn't publicly available, two known anchor points are shown as an indexed comparison instead of an invented trend line. Full source list is in the dashboard's "Sources" section at the bottom of the page.

## Also in this repo

- `assets/carousel.pdf` — the 10-slide LinkedIn document-carousel version of this project
- `assets/carousel/` — a few of those slides as PNGs
