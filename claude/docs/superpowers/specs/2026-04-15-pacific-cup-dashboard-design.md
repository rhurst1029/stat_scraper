# Design Doc: UCLA Pacific Cup Interactive Dashboard

**Date:** 2026-04-15
**Updated:** 2026-04-16
**Status:** Approved — implementation plan ready
**Source spec:** `../../../PACIFIC_CUP_UI_DESIGN_SPEC.md` (full detail)

---

## 1. Project Summary

A coach-grade analytics dashboard for the UCLA Water Polo team's 3-game Pacific Cup tournament. Visualizes play-by-play data, player impact scores, efficiency trends, and situational splits. Built to be shared with coaching staff via a URL.

**Games:** vs UC Davis (W 14–7), vs SJSU (W 11–10), vs Stanford (L 11–12)

---

## 2. Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Deployment | GitHub Pages (static) | Free, shareable URL, no server required |
| Data loading | Client-side xlsx parsing via SheetJS | No preprocessing step; xlsx file served from `public/data/` |
| Opponent stats visibility | Game View: shown · Tournament Overview: hidden | Tournament view is UCLA-focused |
| Goalie rotation | Both Tovani & Tauscher treated as "Goalie Anchor" | Keep simple now; GK rotation logic is a parking lot item |
| Implementation strategy | Page-by-page (Tournament Overview first) | Atomic, completable units; each page is shippable |
| **Overview layout** | **Single-column scroll (Command Center)** | Coaching staff want all data visible without clicking tabs; natural reading flow |
| **Drill-down style** | **Everything is clickable** | Player names, game cards, chart bars all navigate somewhere — rich, explorable |
| **Context on drill-down** | **Always tournament-wide** | Consistent entry point; filter pills let coach narrow down after landing |

---

## 3. Tech Stack

```
Framework:   Vite + React 18 + TypeScript
Charts:      Recharts (bar, line, radar, area) + inline SVG for score timelines
Styling:     Tailwind CSS v3 — dark theme default
Data:        SheetJS (xlsx) — client-side parsing of PERFORMANCE_REPORT.xlsx from public/data/
State:       Zustand
Routing:     React Router v6
Deployment:  GitHub Pages via gh-pages CLI
```

**UCLA Palette:**
```
--ucla-blue:  #2774AE
--gold:       #FFD100
--dark-bg:    #0f172a
--card-bg:    #1e293b
--border:     #334155
--text-muted: #94a3b8
```

---

## 4. Data Sources

`public/data/PERFORMANCE_REPORT.xlsx` — 7 sheets (Definitions sheet ignored at runtime):

| Sheet | Used for |
|---|---|
| `Raw Play-by-Play` | Score timelines, PBP Explorer, per-game player stats computed on the fly |
| `Player Summary` | Leaderboard stats, Player Profile base stats |
| `Player Roles` | Role badges in leaderboard + Player Profile header |
| `Team Metrics` | Shot efficiency chart |
| `Quarter Splits` | Quarter momentum chart |
| `Score State Splits` | Score state table in Game View |

**Computed on the fly from Raw PBP:**
- Per-game player stats (filter by `game` column)
- Score diff timeline per game (event sequence index as X-axis)
- Score state classification is pre-computed in the sheet (`score_state` column)

---

## 5. App Shell

### Navigation
- **Top nav bar:** `UCLA WATER POLO · Pacific Cup 2026` branding | tabs: Overview · Games · Players · Play-by-Play
- **Global game filter pills** below nav: `All Games` · `vs UC Davis` · `vs SJSU` · `vs Stanford` — active pill is UCLA blue, inactive is bordered muted
- **Hero stats bar** below filter pills: Record (2-1) · UCLA Goals · Shot% · Steals · Saves · Earned Excl. · mini game result badges
- Dark mode only (no toggle needed for v1)

### Routing
```
/                      → TournamentOverview
/game/:gameId          → GameView (ucdavis | sjsu | stanford)
/players               → PlayerIndex (grid of UCLA players)
/player/:name          → PlayerProfile (drilled into from leaderboard or PlayerIndex)
/play-by-play          → PlayByPlayExplorer
```

---

## 6. Drill-Down Navigation Map

Every clickable element navigates to a specific destination. No hidden or arbitrary hotspots — every element that looks interactive IS interactive.

```
Tournament Overview
├── Leaderboard row (player name)     → /player/:name  (tournament-wide profile)
├── Game card (score timelines)       → /game/:gameId
├── Shot efficiency bar (team label)  → /game/:gameId  (for opponent rows)
├── Quarter momentum bar (Q label)    → /play-by-play?quarter=Q3  (pre-filtered)
└── Top nav tabs                      → any page directly

Game View (/game/:gameId)
├── Player name in per-game table     → /player/:name  (tournament-wide profile)
├── Key sequence event                → /play-by-play?game=X&event=Y  (pre-filtered)
└── Top nav / back breadcrumb         → Overview or Games list

Player Profile (/player/:name)
├── "Game: vs Stanford" segment bar   → /game/stanford
├── Event in event feed               → /play-by-play?player=X&game=Y  (pre-filtered)
└── Top nav / back breadcrumb         → Overview or Players list

Play-by-Play Explorer (/play-by-play)
└── Player name in event row          → /player/:name
```

**Context rule:** All drill-downs land on the **tournament-wide** view of the destination. The global game filter pills are always visible and let the coach narrow context after landing. No state is implicitly passed through navigation — the URL is the only state.

### Breadcrumbs
Each page below Overview shows a one-level breadcrumb:
```
Overview → Game: vs Stanford
Overview → ben larsen
Overview → Play-by-Play
```
Clicking the `Overview` segment navigates back. No multi-level breadcrumbs needed for v1.

---

## 7. Page-by-Page Scope

### Phase 1 — Tournament Overview ✅ Design approved
Single-column scroll. Sections in order:

1. **Hero bar** — Record, Goals, Shot%, Steals, Saves, Earned Excl., game result badges
2. **Impact Leaderboard** — ranked table, percentile gradient bars, role badges, clickable player names
3. **Shot Efficiency** + **Quarter Momentum** — side-by-side in a 2-column row
4. **Game Score Timelines** — 3-column grid of game cards with inline SVG score-diff lines, key stats, clickable to Game View

### Phase 2 — Game View
- Game Header (score, shot%, steals, special teams)
- Full-width Win Probability / Score Diff Timeline (interactive scrubber via event index)
- Quarter Performance Grid (4 cards, color-coded W/L/T per quarter)
- Score State Performance Table (Leading/Tied/Trailing)
- Per-Game Player Impact (computed from Raw PBP filtered to game)
- Key Sequences Panel (runs: 3+ consecutive scoring events by same team)

### Phase 3 — Player Profile
- Player header (name, cap, role badges, IPS score)
- Radar chart (6 axes: Shooting Efficiency, Shot Volume, Defensive Disruption, Leverage Creation, Discipline, Clutch) — player vs team average
- Per-game comparison bar (3 segments, one per opponent, goals + IPS)
- Event feed (all events across tournament, grouped by game)
- Situational splits table (by quarter + by score state)

### Phase 4 — Play-by-Play Explorer
- Filter sidebar: game, team, event type, quarter, score state, player, clutch toggle
- Virtual-scrolled event table (553 rows)
- CSV export

---

## 8. Impact Score Formulas

Pre-computed in `Player Summary` sheet — use as-is. Formula documented here for reference:

```
Offense = goals×3 + goal_penalty×1 + earned_excl×1.3 + earned_pen×1.6
          − miss×2.5 − miss_pen×0.9 − offensive×2

Defense = steals×2 + field_blocks×2 + saves×1
          − excluded×1 − pen_committed×1.3

Impact  = Offense + Defense
```

---

## 9. Radar Chart Axes (Player Profile)

```
1. Shooting Efficiency   non_pen_pct, 0–1 normalized to team max
2. Shot Volume           shots / max_shots_on_team
3. Defensive Disruption  (steals + field_blocks) / max
4. Leverage Creation     (earned_excl + earned_pen) / max
5. Discipline            1 − (excluded + pen_committed) / max
6. Clutch                clutch_goals / max_clutch_on_team
```

Two polygons: player (UCLA blue fill, 40% opacity) + team average (gold dashed outline).

---

## 10. Role Badge Definitions

Derived from `Player Roles` sheet — `roles` column is a Python list string, parsed client-side:

| Role string | Badge label | Badge color |
|---|---|---|
| `Primary Finisher` | Finisher | Blue |
| `Leverage Creator (Draws Calls)` | Leverage Creator | Purple |
| `Disruptor (Defense/Transition)` | Disruptor | Green |
| `Goalie Anchor` | Goalie Anchor | Amber |
| `Special Teams` | Special Teams | Gray |

---

## 11. Parking Lot

- **GK rotation toggle** — Tovani and Tauscher both logged saves; future feature to surface "GK minutes" split
- **Playwright import unused** in `6_8_scraper.py` — remove on next scraper pass
- **OT/Shootout handling** — quarter loop only handles Q1–Q4; no OT support yet
- **`get_games` re-wiring** — currently bypassed in scraper; re-enable after dashboard ships
- **Light mode toggle** — deferred to v2
- **Advanced Analytics panel** (IPS Scatter, Clutch Radar, Possession Efficiency, Special Teams deep-dive) — deferred to v2

---

## 12. Definition of Done

The dashboard is complete when:
- [ ] All 4 pages render with real data from `PERFORMANCE_REPORT.xlsx`
- [ ] GitHub Pages deployment works via `npm run deploy`
- [ ] Coaching staff can open the URL and navigate all 4 views
- [ ] All drill-down links in the navigation map (§6) work correctly
- [ ] Charts have hover tooltips
- [ ] CSV export works on the Play-by-Play page
- [ ] Game cards, leaderboard rows, and chart labels are all clickable as specified
