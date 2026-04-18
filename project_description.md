# Project description — wp_scraper (water polo stat pipeline)

> Drafted from repo evidence during a brownfield retrofit (Step B3 of
> `RETROFIT.md`). Claims carry an `(inferred)` tag where they were derived
> from indirect signals; unconfirmed items repeat at the bottom under
> *Assumptions needing confirmation*. Correct or confirm each item before
> the retrofit proceeds to `design-doc.md`.

## What the product does

A single-maintainer data pipeline that scrapes water polo play-by-play events
from two public platforms — **Total Water Polo** (TWP) and **6-8 Sports** —
normalizes the events into per-game Excel workbooks, aggregates them into a
tournament-level `PERFORMANCE_REPORT.xlsx`, and renders the aggregate in a
React + Vite dashboard published to GitHub Pages
(`https://rhurst1029.github.io/stat_scraper`). A Jupyter notebook
(`water_polo_post_game_report_template.ipynb`) produces ad-hoc per-game
post-game reports from the CSV exports.

Evidence:
- `README.md` lines 1–3 (pipeline overview)
- `6_8_scraper.py` (339 lines — 6-8 Sports scraper, current)
- `twp_scraper.py` (361 lines — TWP scraper, current)
- `twp_constructor.py` (142 lines — TWP link discovery via Playwright)
- `get_pbp_links.py` (70 lines — diagnostic DOM inspector, one-off)
- `dashboard/package.json` (React 19.2.4 + Vite 8.0.4 + Tailwind 3.4.19
  + Zustand 5.0.12 + Recharts 3.8.1 + Vitest 4.1.4)
- `PERFORMANCE_REPORT.xlsx` at `dashboard/public/data/`
- Legal positioning in `README.md` line 5 (hiQ Labs v. LinkedIn cited)

## Primary users / customer

- **Ryan Hurst** (`rhurst1029@gmail.com`), the sole author and maintainer.
  Confirmed via `git log`; every commit on `main` is his.
- **Water polo coaches and analysts who follow the dashboard link**
  *(inferred)*. The dashboard is public, the output is domain-specific
  (team abbreviations, cap numbers, shot efficiency, momentum), and
  `README.md` references Tableau dashboards, which implies an audience
  beyond the author.
- **No external paying customers** *(inferred)*. Nothing in the repo
  suggests billing, auth, accounts, or a go-to-market motion.

## Tech stack constraints

- **Python** 3.9.6 for all scraping and data work. Dependencies pinned in
  `requirements.txt`:
  - `selenium==4.15.2` (primary browser automation for both scrapers)
  - `playwright==1.41.2` (used only in `twp_constructor.py` for link
    discovery; imported but unused in `6_8_scraper.py` — see
    `PARKING_LOT.md`)
  - `pandas==2.0.3`, `openpyxl==3.1.2` (DataFrame + Excel export)
  - `beautifulsoup4==4.12.2` (HTML parsing)
  - `fake-useragent==1.4.0`, `webdriver-manager==4.0.1` (anti-bot + driver
    management)
- **TypeScript + React** for the dashboard. `dashboard/package.json`:
  - React 19.2.4, React Router 7.14.1
  - Vite 8.0.4, TypeScript ~6.0.2
  - Tailwind CSS 3.4.19, Recharts 3.8.1
  - Zustand 5.0.12 (state), SheetJS `xlsx` 0.18.5 (in-browser parsing of
    the aggregate workbook)
  - Vitest 4.1.4 (14 unit tests, all passing per `PROGRESS.md` 2026-04-16)
- **No backend, no database, no API.** Data flows file → file:
  scraper → `<game>.xlsx` → aggregated `PERFORMANCE_REPORT.xlsx` →
  browser-side SheetJS in the dashboard.
- **No cloud infrastructure.** Deploy target is GitHub Pages via
  `scripts/deploy.sh` and the `gh-pages` npm package. Branch: `main` →
  published at `gh-pages` orphan branch.
- **Forbidden / absent:** No Node/Deno runtime outside `dashboard/`; no
  Docker; no Terraform; no CI (GitHub Actions not yet configured — see
  `TASKS.md`).

## Compliance / regulatory constraints

- **None known.** No PII, no payments, no auth, no health or financial
  data. The only user identifiers in the data are public roster items
  (team abbreviations, cap numbers, player names) scraped from
  publicly-viewable pages. `README.md` cites *hiQ Labs v. LinkedIn* as the
  legal framing for scraping public data.
- **GDPR / CCPA:** not applicable *(inferred)* — no user accounts exist
  and no personally-identifying user data is collected. Scraped player
  names are public-record sports rosters.
- **No security review or secret management needed** *(inferred)* — the
  `.gitignore` blocks `.env*`, but no `.env` files exist in the repo and
  the scrapers do not authenticate against either target site.

## Anticipated scale

- **Solo hobby project** *(inferred from commit patterns)*. All commits on
  `main` are by one author; recent activity (2026-04-15 through 2026-04-17)
  focuses on dashboard Phase 1 shipping and scraper refactors.
- **Data volume:** small. A sample play-by-play CSV
  holds 553 events; per-game workbooks are 11–13 KB each; the aggregated
  `PERFORMANCE_REPORT.xlsx` is 54 KB. Single tournament's worth of data at a
  time.
- **Traffic:** single-digit viewers on the GitHub Pages dashboard
  *(inferred)* — no analytics, no CDN, no rate-limit concerns documented.
- **No uptime SLO.** Deploys are manual via `npm run deploy`. Scrapers are
  invoked by hand from the command line with hardcoded URLs in
  `__main__` blocks.

## Anything else worth knowing

- **Binding project protocol in `CLAUDE.md` Part 2.** This is the most
  important constraint in the repo. Any agent operating here must honor:
  - Planning phase explicit and complete **before** any code is written
    (`CLAUDE.md` line 117 onward).
  - **45-minute checkpoints** during the Building phase
    (`CLAUDE.md` lines 158, 275, 321).
  - **Evidence-first completion** — every "done" claim cites a file, test,
    or command output (`CLAUDE.md` line 212).
  - **Scope drift is logged** to `PARKING_LOT.md`, not silently actioned
    (`CLAUDE.md` line 193).
  - `PROGRESS.md` is the append-only session log;
    `TASKS.md` is the active priority list
    (`CLAUDE.md` lines 371–427).
- **Tracking files already exist** and are in active use — `PROGRESS.md`
  (session log), `TASKS.md` (priorities), `PARKING_LOT.md` (unresolved
  items, 15 entries as of 2026-04-16). Agent role files must append to
  these rather than creating parallel trackers.
- **Known unresolved issues** from `PARKING_LOT.md` that the agent team
  will inherit as open backlog:
  - OT / shootout periods are not handled by either scraper.
  - `get_games` wire-up is pending.
  - Playwright imported but unused in `6_8_scraper.py`.
  - TWP scraper last-verified status is unknown (not run since
    2026-04-15).
  - Dashboard needs an a11y pass (WCAG AA).
  - Color-token drift across dashboard components.
- **Test gap:** 14 Vitest tests for the dashboard, **zero** Python tests
  for the scrapers. The QA role's first deliverable should close this gap.
- **`main` is 17 commits ahead of `origin`** as of the survey date. Top
  `[MUST]` in `TASKS.md` is to push. The DevOps/SRE role should address
  this before any further deploys.
