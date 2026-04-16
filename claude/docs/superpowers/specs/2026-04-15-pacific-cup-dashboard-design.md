# Design Doc: UCLA Pacific Cup Interactive Dashboard

**Date:** 2026-04-15
**Status:** Approved — ready for implementation
**Source spec:** `../../../PACIFIC_CUP_UI_DESIGN_SPEC.md` (full detail)

---

## 1. Project Summary

A coach-grade analytics dashboard for the UCLA Water Polo team's 3-game Pacific Cup tournament. Visualizes play-by-play data, player impact scores, efficiency trends, and situational splits. Built to be shared with coaching staff via a URL.

**Games:** vs UC Davis (W), vs SJSU (W), vs Stanford (L)

---

## 2. Decisions Made in Brainstorm

| Decision | Choice | Rationale |
|---|---|---|
| Deployment | GitHub Pages (static) | Free, shareable URL, no server required |
| Data loading | Client-side xlsx parsing via SheetJS | No preprocessing step; xlsx files served from `public/` |
| Opponent stats visibility | Game View: shown · Tournament Overview: hidden | Tournament view is UCLA-focused |
| Goalie rotation | Both Tovani & Tauscher treated as "Goalie Anchor" | Keep simple now; GK rotation logic is a parking lot item |
| Implementation strategy | Page-by-page (Tournament Overview → Game View → Player Profile → PBP Explorer) | Atomic, completable units; each page is shippable |

---

## 3. Tech Stack

```
Framework:   Vite + React 18 + TypeScript
Charts:      Recharts (bar, line, radar, area, scatter) + D3 for custom viz
Styling:     Tailwind CSS v3 — dark theme default
Data:        SheetJS (xlsx) — client-side parsing of PERFORMANCE_REPORT.xlsx from public/
State:       Zustand
Routing:     React Router v6
Deployment:  GitHub Pages via gh-pages CLI or GitHub Actions
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

All files go in `public/data/`:
- `PERFORMANCE_REPORT.xlsx` — original spec references 7 sheets; 6 are named and parsed (see below). Verify actual sheet count on first load — the 7th sheet, if present, is ignored.
- Per-game xlsx files (optional fallback)

**Sheets parsed:**
1. `Raw Play-by-Play` — all event-level data, 553 rows
2. `Player Summary` — tournament-aggregate player stats
3. `Team Metrics` — one row per team
4. `Quarter Splits` — goals/shots/steals by quarter
5. `Score State Splits` — same, grouped by Leading/Tied/Trailing
6. `Player Roles` — player summary + roles array

**Computed on the fly from Raw PBP:**
- Per-game player stats (filter by `game` column)
- Win probability / score diff timeline (event sequence index as X-axis — time column is `--:--`)
- Momentum index (rolling 5-event window)

---

## 5. App Shell

### Navigation
- Top nav bar: UCLA Water Polo branding | tabs: Overview · Game View · Players · Play-by-Play
- Global game filter pills in top-right: All · vs UC Davis · vs SJSU · vs Stanford
- Hero stats bar below nav: Record (2-1) · Goals · Shot% · Steals · Net Impact
- Dark mode default; light mode toggle optional

### Routing
```
/                      → TournamentOverview
/game/:gameId          → GameView (ucdavis | sjsu | stanford)
/players               → PlayerIndex (grid of UCLA players — nav tab landing page)
/player/:name          → PlayerProfile (drilled into from PlayerIndex or leaderboard)
/play-by-play          → PlayByPlayExplorer
```

---

## 6. Page-by-Page Scope

### Phase 1 — Tournament Overview (highest value, ships first)
- Hero bar
- Impact Leaderboard (ranked table with percentile bars + role badges)
- Team Shot Efficiency chart (horizontal grouped bar)
- Quarter Momentum area chart
- Game Score Timeline mini-charts (3-column, score diff over event index)
- Advanced Analytics panel: Possession Efficiency, Special Teams, IPS Scatter, Momentum Index, Clutch Performer Radar

### Phase 2 — Game View
- Game Header (score, shot%, steals, special teams)
- Full-width Win Probability Timeline (interactive scrubber)
- Quarter Performance Grid (4 cards, color-coded W/L/T per quarter)
- Score State Performance Table (Leading/Tied/Trailing)
- Per-Game Player Impact (computed from PBP filtered to game)
- Key Sequences Panel (auto-detect runs and exclusion→goal patterns)

### Phase 3 — Player Profile
- Player header (name, cap, role badges, Impact Score)
- Radar chart (6 axes, player vs team average)
- Event feed (all events across tournament, grouped by game)
- Situational splits table (by quarter + by score state)
- Per-game comparison bar (3 segments, one per opponent)

### Phase 4 — Play-by-Play Explorer
- Filter sidebar (game, team, event type, quarter, score state, player, clutch toggle)
- Virtual-scrolled event table (553 rows)
- CSV export

---

## 7. Impact Score Formulas

```
Offense = goals×3 + goal_penalty×1 + earned_excl×1.3 + earned_pen×1.6
          − miss×2.5 − miss_pen×0.9 − offensive×2

Defense = steals×2 + field_blocks×2 + saves×1
          − excluded×1 − pen_committed×1.3

Impact  = pre-computed in Player Summary sheet (use as-is)
```

---

## 8. Radar Chart Axes (Player Profile)

```
1. Shooting Efficiency   non_pen_pct, 0–1 normalized
2. Shot Volume           shots / max_shots_on_team
3. Defensive Disruption  (steals + field_blocks) / max
4. Leverage Creation     (earned_excl + earned_pen) / max
5. Discipline            1 − (excluded + pen_committed) / max
6. Clutch                clutch_goals / max_clutch_on_team
```

Two polygons: player (UCLA blue fill) + team average (gold dashed).

---

## 9. Parking Lot

- **GK rotation toggle** — Tovani and Tauscher both logged saves; future feature to surface "GK minutes" split once we know how to determine who was in net each quarter
- `get_games` re-wiring in the scraper pipeline (separate project)

---

## 10. Definition of Done

The dashboard is complete when:
- [ ] All 4 pages render with real data from `PERFORMANCE_REPORT.xlsx`
- [ ] GitHub Pages deployment works via `npm run deploy`
- [ ] Coaching staff can open the URL and navigate all 4 views
- [ ] Charts are interactive (hover tooltips, click-to-drill where specified)
- [ ] CSV export works on the Play-by-Play page
