# Dashboard — Water Polo Tournament Analytics

A coach-grade water polo analytics dashboard for a single tournament (N games of a focal team vs opponents). Static single-page React app, deployed to GitHub Pages, loading `PERFORMANCE_REPORT.xlsx` client-side via SheetJS. This file is the single source of truth for design, implementation, and ops.

> **Terminology used in this doc:** prose refers to the focal team generically ("Team1") and to opponents as "Team2/Team3/Team4". Code is team-agnostic by convention — identifiers use `FOCAL_*` prefixes (e.g. `FOCAL_TEAM`, `FOCAL_IS_SCORE_A`, `focalScore`, `focal-blue`) and the current tournament's real team names live only as _values_ in `src/types/index.ts` (`FOCAL_TEAM = 'UCLA Bruins'`, `TOURNAMENT_NAME = 'Pacific Cup 2026'`, etc.) and as color hex values in `tailwind.config.js`. To retarget to a different tournament, edit only those values.

---

## 1. Goals & Philosophy

This is a **coach-grade tool, not a fan stats page**. It answers four questions:

1. **Who drove the win?** (Impact Score leaderboard, role profiles)
2. **How did we play across the tournament?** (efficiency trends, quarter splits)
3. **Where are the patterns?** (score-state performance, clutch moments)
4. **Who do we deploy in what situation?** (role profiles + situational splits)

Design influences:

- **Dunks & Threes (EPM)** — single composite metric prominently displayed with offensive/defensive splits; percentile bars on every metric.
- **BBall-Index** — radar/spider charts for multi-dimensional player profiles; tabs for different analytical lenses.
- **Soccer analytics** — possession/transition efficiency; pressing metrics (steals + field blocks as a "press success" analog).

Coaching staff want everything visible without clicking tabs — so the Tournament Overview is a single-column scroll ("Command Center") where every clickable element drills somewhere concrete.

---

## 2. Current Status

| Phase | Scope | Status |
|-------|-------|--------|
| **Phase 1** | Tournament Overview (landing) — HeroBar, Impact Leaderboard with percentile bars + role badges, Shot Efficiency chart, Quarter Momentum chart, GameCards with inline SVG score timelines | ✅ **Shipped + live** |
| **Phase 2** | Game View (`/game/:gameId`) — full-width score timeline with scrubber, quarter performance grid, score state splits table, per-game player impact, key sequences panel | Pending |
| **Phase 3** | Player Profile (`/player/:name`) — 6-axis role fingerprint radar, per-game comparison bar, chronological event feed, situational splits | Pending |
| **Phase 4** | Play-by-Play Explorer (`/play-by-play`) — virtualized filter table (553 rows), multi-filter sidebar, CSV export | Pending |
| **Polish** | ~15 parking-lot items: clickable-surface a11y, shared `src/theme/colors.ts`, `aria-sort`/`aria-pressed`, token consistency (see root `PARKING_LOT.md`) | Pending |

Live URL: <https://rhurst1029.github.io/stat_scraper/>

---

## 3. Tech Stack

```
Framework:   Vite + React 19 + TypeScript
Charts:      Recharts (bar, line, radar, area) + inline SVG for custom viz
Styling:     Tailwind CSS v3 — dark theme default
Data:        SheetJS (xlsx) — client-side parsing of PERFORMANCE_REPORT.xlsx
State:       Zustand
Routing:     React Router v7 (basename '/stat_scraper')
Testing:     Vitest + React Testing Library + jsdom
Deployment:  Custom scripts/deploy.sh — clean orphan branch force-push to gh-pages
```

Palette (defined in `tailwind.config.js`):

```
focal-blue:  #2774AE   ← focal-team accent (currently UCLA blue; change the hex to retarget)
gold:        #FFD100
dark-bg:     #0f172a
card-bg:     #1e293b
border:      #334155
muted:       #94a3b8
```

---

## 4. Codebase Layout

Location: `/Users/ryanhurst/Desktop/wp_scraper/dashboard/`

```
dashboard/
  public/
    data/PERFORMANCE_REPORT.xlsx    ← copied from parent repo root
  scripts/
    deploy.sh                        ← clean orphan → gh-pages
  src/
    types/
      index.ts                       ← all shared TS types + tournament constants (GAME_IDS, GAME_SCORES, OPP_TEAMS, FOCAL_TEAM, etc.)
    lib/
      parseWorkbook.ts               ← SheetJS WorkBook → typed AppData
      computeScoreTimeline.ts        ← per-game score-diff array from Raw PBP
    store/
      useAppStore.ts                 ← Zustand: { data, loading, error, gameFilter }
    components/
      LoadingScreen.tsx
      layout/
        NavBar.tsx                   ← sticky nav + tabs
        FilterPills.tsx              ← All / vs UC Davis / vs SJSU / vs Stanford
        HeroBar.tsx                  ← Record, Goals, Shot%, Steals, Saves, Earned Excl.
      leaderboard/
        RoleBadge.tsx
        ImpactLeaderboard.tsx
      charts/
        ShotEfficiencyChart.tsx      ← Tailwind horizontal bars
        QuarterMomentumChart.tsx     ← Recharts grouped bars
        GameCard.tsx                 ← inline SVG score timeline + click-to-game
    pages/
      TournamentOverview.tsx         ← Phase 1 ✅
      GameView.tsx                   ← Phase 2 stub
      PlayerIndex.tsx                ← Phase 3 stub (grid of players)
      PlayerProfile.tsx              ← Phase 3 stub
      PlayByPlayExplorer.tsx         ← Phase 4 stub
    router.tsx                       ← React Router v7 routes
    App.tsx                          ← root: fetches xlsx, renders Outlet
    main.tsx                         ← ReactDOM.createRoot
  tests/
    lib/
      parseWorkbook.test.ts
      computeScoreTimeline.test.ts
  index.html
  vite.config.ts
  tailwind.config.js
  postcss.config.js
  tsconfig.json
  tsconfig.app.json
  tsconfig.node.json
  package.json
```

Prefer small, focused files. Charts, leaderboard, and layout are separated so each component can be read and modified independently.

---

## 5. Data Model

`public/data/PERFORMANCE_REPORT.xlsx` has 7 sheets. Parsed once at app load by `parseWorkbook(wb)` into a single `AppData` object stored in Zustand.

| Sheet | Used for |
|---|---|
| `Raw Play-by-Play` | Score timelines, PBP Explorer, per-game player stats computed on the fly |
| `Player Summary` | Leaderboard base stats, Player Profile base stats |
| `Player Roles` | Role badges in leaderboard + Player Profile header |
| `Team Metrics` | Shot efficiency chart, HeroBar |
| `Quarter Splits` | Quarter momentum chart |
| `Score State Splits` | Score state table in Game View |
| `Definitions` | Ignored at runtime (docs only) |

Full type definitions live in `src/types/index.ts` — that file is authoritative. Key shapes:

```typescript
interface PlayerSummary {
  team: string; player_name: string; impact: number;
  goals: number; goals_pen: number; shots: number; shot_pct: number;
  non_pen_goals: number; non_pen_shots: number; non_pen_pct: number;
  steals: number; field_blocks: number; saves: number;
  earned_excl: number; excluded: number; earned_pen: number; pen_committed: number;
  clutch_goals: number; shots_per_goal: number | null;
  roles: string[];
}

interface RawEvent {
  time: string; team: string; cap_number: string; player_name: string;
  action_detail: string; score: string; quarter: string; game: string;
  score_a: number; score_b: number;
  score_diff_raw: number; score_diff_pre: number | null;
  score_state: string; is_clutch: boolean;
  event_type: string; is_penalty_attempt: boolean;
}

interface AppData {
  playerSummaries: PlayerSummary[];
  teamMetrics: TeamMetrics[];
  quarterSplits: QuarterSplit[];
  scoreStateSplits: ScoreStateSplit[];
  rawEvents: RawEvent[];
}

type GameId = 'ucdavis' | 'sjsu' | 'stanford';   // one slug per game in the tournament
```

Canonical tournament-config constants (also in `src/types/index.ts`):

```typescript
GAME_IDS:   ['ucdavis', 'sjsu', 'stanford']
GAME_NAMES: { ucdavis: 'UC Davis Aggies VS UCLA Bruins',
              sjsu: 'UCLA Bruins VS SJSU Spartans',
              stanford: 'UCLA Bruins VS Stanford Cardinal' }
GAME_LABELS: { ucdavis: 'vs UC Davis', sjsu: 'vs SJSU', stanford: 'vs Stanford' }
FOCAL_IS_SCORE_A: { ucdavis: false, sjsu: true, stanford: true }
GAME_SCORES: { ucdavis: { focalScore: 14, oppScore: 7,  win: true  },
               sjsu:    { focalScore: 11, oppScore: 10, win: true  },
               stanford:{ focalScore: 11, oppScore: 12, win: false } }
OPP_TEAMS:   { ucdavis: 'UC Davis Aggies', sjsu: 'SJSU Spartans',
               stanford: 'Stanford Cardinal' }
FOCAL_TEAM:          'UCLA Bruins'
FOCAL_TEAM_SHORT:    'UCLA'            // used in chart labels ("UCLA Goals", etc.)
FOCAL_TEAM_HEADER:   'UCLA WATER POLO' // used in NavBar branding + LoadingScreen
TOURNAMENT_NAME:     'Pacific Cup 2026'
```

### Derived data

Some values are computed at render time, not pre-stored:

- **Per-game player stats** — filter `rawEvents` by `game` column + `event_type` (no per-game summary in the xlsx).
- **Score diff timeline per game** — `computeScoreTimeline(rawEvents, gameId)` returns `{ eventIndex, scoreDiff }[]`, with `scoreDiff > 0` meaning Team1 leading.
- **Tournament record** — derived from `GAME_SCORES` (`wins-losses`), not hardcoded.

### Data gotchas

- **Time column is sparse** — most rows show `--:--`. Charts use **sequential event index** as the X-axis proxy, not clock time.
- **The focal team may be `score_a` or `score_b`** — depending on which team is listed first in the raw data's `game` column. Use `FOCAL_IS_SCORE_A` to disambiguate.
- **Roles are parsed from Python list literal strings** — `"['Primary Finisher', 'Disruptor']"` → `['Primary Finisher', 'Disruptor']`. Current parser splits on commas; a role name containing a comma would break silently (no such roles today).

---

## 6. App Structure & Routing

### Routes

```
/                      → TournamentOverview (Phase 1 ✅)
/game/:gameId          → GameView (Phase 2)
/players               → PlayerIndex (Phase 3)
/player/:name          → PlayerProfile (Phase 3)
/play-by-play          → PlayByPlayExplorer (Phase 4)
```

Routes use React Router v7 with `basename: '/stat_scraper'` (the GitHub Pages repo path).

### Persistent chrome

Every page renders the same top stack:

- **NavBar** — branding (focal team + tournament) + tabs (Overview · Games · Players · Play-by-Play). Sticky top.
- **FilterPills** — `All Games · vs Team2 · vs Team3 · vs Team4`. Global game filter in Zustand (`gameFilter`).
- **HeroBar** — Record (e.g. 2-1) · Team1 Goals · Shot% · Steals · Saves · Earned Excl. + one game result badge per game.

### Drill-down navigation map

Every clickable element navigates to a specific destination. No hidden hotspots.

```
Tournament Overview
├── Leaderboard row (player name)    → /player/:name   (tournament-wide profile)
├── Game card (score timelines)      → /game/:gameId
├── Shot efficiency bar (team label) → /game/:gameId   (opponent rows only)
├── Quarter momentum bar (Q label)   → /play-by-play?quarter=Q3   (pre-filtered)
└── Top nav tabs                     → any page directly

Game View (/game/:gameId)
├── Player name in per-game table    → /player/:name   (tournament-wide profile)
├── Key sequence event               → /play-by-play?game=X&event=Y
└── Top nav / breadcrumb             → Overview or Games list

Player Profile (/player/:name)
├── "Game: vs Team4" segment bar     → /game/stanford
├── Event in event feed              → /play-by-play?player=X&game=Y
└── Top nav / breadcrumb             → Overview or Players list

Play-by-Play Explorer (/play-by-play)
└── Player name in event row         → /player/:name
```

**Context rule:** all drill-downs land on the **tournament-wide** view of the destination. The global game filter pills are always visible so the coach can narrow after landing. No state is passed implicitly through navigation — the URL is the only state.

### Breadcrumbs

Each page below Overview shows a one-level breadcrumb (e.g. `Overview → Game: vs Team4`, `Overview → player name`). Clicking the `Overview` segment navigates back. No multi-level breadcrumbs for v1.

---

## 7. Page Specs

### 7.1 Tournament Overview (Phase 1 — implemented)

Single-column scroll. Sections in order:

1. **Hero bar** — Record, Goals, Shot%, Steals, Saves, Earned Excl., game result badges (e.g. Team2 W 14–7, Team3 W 11–10, Team4 L 11–12).
2. **Impact Leaderboard** — ranked table, percentile gradient bars, role badges, clickable player names. Sort by `impact` desc.
3. **Shot Efficiency + Quarter Momentum** — side-by-side in a 2-column row.
   - Shot Efficiency: plain Tailwind bars, Team1 first, then opponents in tournament order (derived from `GAME_IDS.map(id => OPP_TEAMS[id])`). Opponents that out-shot Team1 rendered red.
   - Quarter Momentum: Recharts grouped bars — Team1 goals per quarter vs opponent average (count of distinct opponent teams, not hardcoded). Best quarter highlighted gold.
4. **Game Score Timelines** — N-column grid of game cards with inline SVG score-diff polylines, key stats (shot%, steals), clickable to Game View.

### 7.2 Game View (Phase 2)

One page per game. Tab strip at top. `gameId` slugs come from `GAME_IDS` (currently `ucdavis | sjsu | stanford`).

- **Game Header** — `Team1 13 — Team2 7` score, shot% Team1 vs opponent, steals (possession proxy), earned exclusions converted.
- **Win Probability Timeline (full-width)** — Recharts `LineChart` of running `score_diff`, normalized. Features:
  - Draggable scrubber on X-axis → shows "what the game looked like at this moment."
  - Gold overlay band on Q4 clutch window (`score ≤ ±2`).
  - Clickable event markers → popup with full event detail.
- **Quarter Performance Grid** — 4-column card grid (Q1–Q4). Each card: Team1 goals/shots/shot%, opponent goals/shots/shot%, Team1 disruption score (steals + blocks). Color-coded green/red/yellow for quarter winner.
- **Score State Performance Table** — 3 rows (Leading / Tied / Trailing), Team1 vs opponent stats per state. Auto-generated insight callout ("Team1 shot 52% when leading, 28% when trailing").
- **Per-Game Player Impact** — same layout as tournament leaderboard, filtered to this game's raw events.
- **Key Sequences Panel** — auto-detect runs (3+ consecutive positive Team1 events) and exclusion sequences (`earned_exclusion` → `goal_6on5` within N events). Compact event feed with timestamps + player names.

### 7.3 Player Profile (Phase 3)

Focal-team roster is derived from data, filtering `rawEvents` where `team == FOCAL_TEAM`.

- **Player Header** — name, cap number (from raw events, not summary), role badges, large Impact Score, offense/defense split side by side.
- **Radar Chart** — 6 axes, player polygon (focal-blue, 40% opacity) vs team average (gold dashed outline):
  1. Shooting Efficiency — `non_pen_pct / max_non_pen_pct`
  2. Shot Volume — `shots / max_shots`
  3. Defensive Disruption — `(steals + field_blocks) / max`
  4. Leverage Creation — `(earned_excl + earned_pen) / max`
  5. Discipline — `1 − (excluded + pen_committed) / max`
  6. Clutch — `clutch_goals / max_clutch`
- **Event Feed** — chronological list of all events for this player across all games. Columns: Game | Quarter | Score State | Action | Score at Time. Color-coded by event sign. Grouped by game, collapsible.
- **Situational Splits** — mini table: stats by quarter (Q1–Q4) and by score state (Leading / Tied / Trailing). Shows goals, shot%, impact contribution.
- **Per-Game Comparison Bar** — horizontal stacked bar showing Impact contribution per game. N segments color-coded by opponent. Tooltip shows full game stats.

### 7.4 Play-by-Play Explorer (Phase 4)

- **Filter Sidebar** — game selector, team (All / Team1 / Opponent), event type (multi-select pills), quarter, score state, player search, clutch toggle.
- **Event Table** — columns: `Game | Quarter | Score | Score State | Clutch? | Team | Player | Event | Impact Weight`.
  - Team1 rows in light blue, opponent rows neutral.
  - Positive impact events green-tinted, negative red-tinted.
  - Sticky header, virtual scroll (use `react-window` `FixedSizeList` for ~500 rows).
- **CSV export** button on the table (use `papaparse`).

---

## 8. Impact Score Formulas

Pre-computed in the `Player Summary` sheet — use `p.impact` directly in components. The formulas are documented here for reference:

```
Offense = goals×3 + goal_penalty×1 + earned_excl×1.3 + earned_pen×1.6
          − miss×2.5 − miss_pen×0.9 − offensive×2

Defense = steals×2 + field_blocks×2 + saves×1
          − excluded×1 − pen_committed×1.3

Impact  = Offense + Defense
```

Note: `impact` can be **negative** (a player with only misses/exclusions). Percentile-bar math must guard against `maxImpact === 0` and clamp `impact < 0` to 0 for the bar visual (keep the numeric value as-is in the cell). Pattern in `ImpactLeaderboard.tsx`:

```tsx
const maxImpact = Math.max(players[0]?.impact ?? 1, 0.0001)
// inside map:
width: `${(Math.max(0, p.impact) / maxImpact) * 100}%`
```

---

## 9. Role Badges

Parsed from the `Player Roles` sheet. `roles` column is a Python list literal string. Display mapping:

| Role string | Badge label | Badge color |
|---|---|---|
| `Primary Finisher` | Finisher | Blue (`bg-blue-900/40 text-sky-300`) |
| `Leverage Creator (Draws Calls)` | Leverage Creator | Purple |
| `Disruptor (Defense/Transition)` | Disruptor | Green |
| `Goalie Anchor` | Goalie Anchor | Amber |
| Unknown | *raw string* | Slate (fallback) |

`RoleBadge.tsx` holds both the style map and the label map. Keep them in sync; a future refactor should consolidate to a single `{ [role]: { label, style } }` object (see `PARKING_LOT.md`).

---

## 10. Advanced Analytics (Deferred to v2)

These are "EPM-adjacent" analytics worth implementing after Phase 4 ships.

### 10.1 Possession Efficiency Proxy

Water polo doesn't log possessions explicitly, but we can approximate:

```
Team1 Possessions ≈ goals + misses + turnovers + earned_excl_against_them
Off Eff = Team1 goals / Team1 possessions           (points-per-possession)
Def Eff = (steals + field_blocks) / opp_possessions (stops-per-possession)
```

Display: `Off Eff: 1.2 pts/poss | Def Eff: 0.34 stops/poss`.

### 10.2 Special Teams Efficiency

Power play (man-up) stats:

- Conversion rate: `goals_on_power_play / earned_exclusions`
- Man-down defense: goals conceded while down (from raw data proximity).

Display: `Special Teams Net: +X` (power-play goals − penalty goals allowed).

### 10.3 Impact Per Shot (IPS)

```
IPS = (goals × 3 − misses × 2.5) / shots
```

Analogous to xG-above-expected in soccer. Display as a scatter plot: X = shots (volume), Y = IPS (efficiency), bubble size = total impact. Quadrants: "Efficient Scorer", "High Volume", "Needs Selection", "Low Usage".

### 10.4 Momentum Index

Rolling 5-event window across a game:

```
momentum[i] = sum(impact_weights[i-4:i+1])  for Team1 events only
```

Line chart, focal-blue. Companion line for opponent momentum. Crossover points circled.

### 10.5 Clutch Performer Index

```
CPI = (clutch_goals × 3 + clutch_steals × 2) / clutch_events_total
```

Radar of top 5 Team1 players by CPI — "who do you want on the ball in Q4 down 1?"

---

## 11. Implementation Patterns (Learned During Phase 1)

These patterns are canonical. New code should match them; deviations should be justified.

### Store access

**Always use selectors**, never destructure the whole store:

```tsx
// ✅ Correct
const data = useAppStore(s => s.data)
const gameFilter = useAppStore(s => s.gameFilter)

// ❌ Wrong — re-renders on every store change
const { data, gameFilter } = useAppStore()
```

### Derive from canonical sources

Never hardcode tournament-specific values (game count, team order, scores, record). Derive from `GAME_IDS`, `GAME_SCORES`, `OPP_TEAMS` in `src/types/index.ts`. Example:

```tsx
// ✅ Game-count-agnostic
const oppTeams = new Set(splits.filter(r => r.team !== FOCAL_TEAM).map(r => r.team))
const oppDivisor = Math.max(1, oppTeams.size)

// ❌ Silently wrong if games change
const avg = total / 3
```

### Divide-by-zero + NaN guards

Every width/size computation needs a guard:

```tsx
// ✅
const maxImpact = Math.max(players[0]?.impact ?? 1, 0.0001)
width: `${(Math.max(0, p.impact) / maxImpact) * 100}%`

// ✅
const points = timeline.length > 1
  ? timeline.map((p, i) => `${(i / (timeline.length - 1)) * W},${y}`).join(' ')
  : `0,${mid} ${W},${mid}`
```

### Recharts color constants

Recharts can't read Tailwind tokens. Inline hex values (`#FFD100`, `#2774AE`, `#475569`) match the Tailwind theme but are duplicated. The right cleanup is a shared `src/theme/colors.ts` imported by both `tailwind.config.js` and Recharts call sites. Parked as a polish item.

### TDD for data logic

Every `src/lib/*.ts` module has a Vitest test in `tests/lib/`. UI components don't require unit tests — they're verified via `npm run build` (tsc clean) and visual inspection of `npm run dev`.

---

## 12. Testing

```bash
cd dashboard
npm test          # Vitest run — currently 14/14 pass (parseWorkbook + computeScoreTimeline)
npm run build     # tsc + Vite production build
npm run dev       # Vite dev server on localhost:5173/stat_scraper/
npm run preview   # Preview production build on localhost:4173/stat_scraper/
```

Test philosophy:

- **Test data logic, not UI.** `parseWorkbook` and `computeScoreTimeline` have deterministic input/output — test them. Chart components don't — rely on type checks + visual verification.
- **No mocking of internal modules.** Use real data shapes in test fixtures.
- **Phase 2+ should maintain test coverage for new data derivations** (per-game stat computation, radar normalization, etc.).

---

## 13. DevOps / Deployment

### Deploy pipeline

```bash
npm run deploy
```

This runs `npm run build && ./scripts/deploy.sh`. The script:

1. Copies `dist/` into a fresh `mktemp` directory.
2. Adds a `.nojekyll` file.
3. `git init`s a new repo on branch `gh-pages`.
4. Commits and force-pushes to `origin/gh-pages`.

### Why not the `gh-pages` CLI?

`gh-pages@6.3.0` clones the default branch (`main`) as a working tree before copying `dist/` and committing. Two problems that silently broke deploys:

1. **Main-branch files leaked onto gh-pages.** `.claude/settings.json`, `claude/.superpowers/`, nested `.gitignore`s — all published to the live site.
2. **`.gitignore` filtering dropped the data file.** The root `.gitignore`'s `*.xlsx` rule caused `git add -A` to silently skip `dist/data/PERFORMANCE_REPORT.xlsx`, so the live dashboard 404'd on the data fetch and rendered the error screen.

The manual `scripts/deploy.sh` sidesteps both by initializing a fresh repo in `mktemp` — no parent state bleeds in, no `.gitignore` filtering applies.

### GitHub Pages URL

The site is served at `https://rhurst1029.github.io/stat_scraper/` — the `stat_scraper` path comes from the **repo name**, not the dashboard directory. Vite's `base` is `/stat_scraper/` and React Router's `basename` is `/stat_scraper`. Renaming the `dashboard/` directory does NOT affect the live URL.

### Local dev vs preview

- `npm run dev` — Vite dev server with HMR, live at `http://localhost:5173/stat_scraper/`.
- `npm run preview` — serves the built `dist/` at `http://localhost:4173/stat_scraper/`. Use this to verify production behavior (bundle size, asset paths) before deploying.

---

## 14. Constraints & Gotchas

1. **Static site only** — no server, no API. All data is parsed from xlsx at load time.
2. **Responsive target is 13" laptop (1280px).** Mobile is not a v1 requirement.
3. **Dark mode only** for v1. Light-mode toggle is parked.
4. **Goalie rotation is simplified.** Multiple goalies on the same team tagged `Goalie Anchor` — a GK-minutes split is a parking-lot item.
5. **Phase 1 patterns are canonical.** New phases should match existing conventions (selector-based store access, derive-from-canonical, guarded math, TDD for lib modules).
6. **Per-game player stats must be derived** — the xlsx only has tournament-aggregate player stats. Per-game requires filtering `rawEvents` by `game` + `event_type`.
7. **Time data is sparse** — most rows show `--:--`. Charts use event-index as X-axis, not clock time.
8. **Routing basename** — `/stat_scraper`. Game IDs are slugs drawn from `GAME_IDS` (currently `ucdavis`, `sjsu`, `stanford`).
9. **gh-pages is force-pushed on every deploy** — don't store anything there that needs to survive.

---

## 15. Relevant External Files

| File | Purpose |
|------|---------|
| `../PARKING_LOT.md` | ~15 polish items (a11y, color tokens, aria attributes, etc.) |
| `../PROGRESS.md` | Session log — Phase 1 build details, decisions, deploy fixes |
| `../TASKS.md` | Cross-project task list (dashboard + scraper work) |
| `../CLAUDE.md` | Parent-dir session protocol (ADHD-aware partner, three-phase flow) |
| `public/data/PERFORMANCE_REPORT.xlsx` | The one and only data source |

---

## 16. Open Questions (Answer Before Starting a New Phase)

1. **Static vs live data** — confirmed static for the shipped build. Tournament is complete; data doesn't change. (A live-polling variant is specified separately.)
2. **Per-game player stats** — must be derived from Raw PBP (not pre-computed in xlsx).
3. **Time column** — use event sequence index as X-axis proxy, not clock.
4. **Goalie rotation** — treat all tagged goalies as "Goalie Anchor" for now; GK-minutes toggle is v2.
5. **Opponent player comparisons** — shown on Game View, hidden on Tournament Overview (focal-team-focused).
