# Design Spec: UCLA Pacific Cup Interactive Tournament Dashboard

**For:** Agent implementation (human review before build)
**Data source:** `PERFORMANCE_REPORT.xlsx` (7 sheets) + raw play-by-play
**Games covered:**
- Game 1: UC Davis Aggies vs UCLA Bruins
- Game 2: UCLA Bruins vs SJSU Spartans
- Game 3: UCLA Bruins vs Stanford Cardinal

---

## 1. Goals & Philosophy

This dashboard is a **coach-grade analytics tool**, not a fan stats page. It answers:
1. **Who drove the win?** (Impact Score leaderboard, role profiles)
2. **How did we play across the tournament?** (efficiency trends, quarter splits)
3. **Where are the patterns?** (score-state performance, clutch moments)
4. **Who do we deploy in what situation?** (role profiles + situational splits)

Design philosophy:
- **Dunks & Threes pattern**: single composite metric (Impact Score) prominently displayed with offensive/defensive splits below it — percentile bars on every metric.
- **BBall-Index pattern**: radar/spider charts for multi-dimensional player profiles, tabs for different analytical lenses.
- **Soccer analytics pattern**: possession/transition efficiency, pressing metrics (steals + field blocks as a "press success" analog).

---

## 2. Tech Stack

```
Frontend:  React 18 + TypeScript
Charts:    Recharts (bar, line, radar, scatter, area) + D3 for custom viz
Styling:   Tailwind CSS (dark theme, UCLA blue/gold palette)
Data:      xlsx.js to parse PERFORMANCE_REPORT.xlsx client-side
           OR: Python preprocessing script that emits a single data.json
State:     Zustand (lightweight, no Redux overhead)
```

UCLA palette:
```
--ucla-blue:  #2774AE
--gold:       #FFD100
--dark-bg:    #0f172a
--card-bg:    #1e293b
--text-muted: #94a3b8
```

---

## 3. Data Model

The agent must parse the following sheets from `PERFORMANCE_REPORT.xlsx`:

### 3.1 Raw Play-by-Play (`Raw Play-by-Play` sheet)
Columns: `time, team, cap_number, player_name, action_detail, score, quarter, game,
          score_a, score_b, score_diff_raw, score_diff_pre, score_state, is_clutch,
          event_type, is_penalty_attempt`

### 3.2 Player Summary (`Player Summary` sheet)
Columns: `team, player_name, impact, goals, goals_pen, shots, shot_pct,
          non_pen_goals, non_pen_shots, non_pen_pct, steals, field_blocks,
          saves, earned_excl, excluded, earned_pen, pen_committed,
          clutch_goals, shots_per_goal`

Filter to `team == "UCLA Bruins"` for UCLA-only views.

### 3.3 Team Metrics (`Team Metrics` sheet)
One row per team across all games combined.

### 3.4 Quarter Splits (`Quarter Splits` sheet)
Columns: `team, quarter, goals, shots, shot_pct, steals, saves, field_blocks,
          earned_excl, earned_pen, clutch_goals`

### 3.5 Score State Splits (`Score State Splits` sheet)
Same columns as quarter splits, grouped by `Leading / Trailing / Tied`.

### 3.6 Player Roles (`Player Roles` sheet)
Same as Player Summary + `roles` column (array of role strings).

### 3.7 Computed on the fly (from Raw Play-by-Play):
- Per-game player stats (filter by `game` column)
- Win probability timeline (running score_diff → normalized sigmoid curve)
- Momentum chart (rolling 5-event goal rate per team)

---

## 4. App Structure

```
/
├── TournamentOverview    ← default landing
├── GameView/:gameId      ← deep dive per game
├── PlayerProfile/:name   ← individual player page
└── PlayByPlay            ← raw event explorer
```

---

## 5. Section Specifications

---

### 5.1 Tournament Overview (Landing Page)

#### Hero Bar
- UCLA record: `W-L-T` across the 3 tournament games
- Total goals scored / allowed
- Overall shot%: `40.9%` (label it vs tournament average)
- Net Impact: sum of all UCLA player impact scores

#### 5.1.1 Impact Leaderboard (Primary Panel)
Inspired by Dunks & Threes EPM leaderboard.

**Layout:** Ranked table with percentile bars

| Rank | Player | Impact | Offense | Defense | Shot% | Clutch | Role Badges |
|------|--------|--------|---------|---------|-------|--------|-------------|

- **Impact** = sum of weighted event scores (already computed)
- **Offense** = goals×3 + goal_penalty×1 + earned_excl×1.3 + earned_pen×1.6 − miss×2.5 − miss_pen×0.9 − offensive×2
- **Defense** = steals×2 + field_blocks×2 + saves×1 − excluded×1 − pen_committed×1.3
- **Percentile bars**: thin horizontal bars (0–100) next to each metric, colored UCLA blue → gold at extremes
- **Role badges**: pill chips (e.g. "Primary Finisher", "Disruptor") pulled from Player Roles sheet
- Click a row → navigate to `PlayerProfile/:name`

#### 5.1.2 Team Shot Efficiency Panel
Horizontal grouped bar chart (Recharts `BarChart`, horizontal layout):
- X-axis: Shot% values
- Y-axis: Teams (UCLA, UC Davis, SJSU, Stanford)
- Two bars per team: Overall Shot% (dark blue) and Non-Penalty Shot% (gold)
- Annotate UCLA bar with actual values

#### 5.1.3 UCLA Quarter-by-Quarter Momentum
Recharts `AreaChart` — single UCLA line:
- X: Q1, Q2, Q3, Q4
- Y: Shot% per quarter
- Second line (dashed): Opponent combined shot% per quarter
- Shaded area between = efficiency gap
- Data from `Quarter Splits` filtered to `team = UCLA`

#### 5.1.4 Game Score Timeline (Win Probability)
For each of the 3 games, a mini `LineChart`:
- X: sequential event index
- Y: score_diff (UCLA − opponent)
- Color: green above 0, red below 0
- Markers: goal events (dot), exclusion windows (translucent band)
- Hover: shows event detail (who scored, what type)
- Aligned in a 3-column row for quick comparison

---

### 5.2 Game View (`/game/:gameId`)

One page per game. Toggle between games via tab strip at top.
`gameId` values: `ucdavis`, `sjsu`, `stanford`

#### 5.2.1 Game Header
- Score: `UCLA 13 — UC Davis 7`
- Shot stats: UCLA shot% vs opponent shot%
- Possession proxy: UCLA steals vs opponent steals
- Special teams: UCLA earned exclusions converted / total

#### 5.2.2 Win Probability Timeline (full-width)
Same as landing page mini charts but full-width and interactive:
- Draggable scrubber on X-axis — scrubbing shows "what the game looked like at this moment"
- Highlight clutch window (Q4, score ≤ ±2) with gold overlay band
- Click any event marker → shows popup with full event detail

#### 5.2.3 Quarter Performance Grid
4-column grid (Q1, Q2, Q3, Q4), each column is a card showing:
- UCLA goals / shots / shot%
- Opponent goals / shots / shot%
- UCLA steals + blocks (disruption score)
- Color-coded: green if UCLA won the quarter, red if lost, yellow if tied

#### 5.2.4 Score State Performance Table
3-row table (Leading / Tied / Trailing) for this game:
- UCLA goals, shot%, steals per state
- Opponent goals, shot%, steals per state
- Insight callout: "UCLA shot 52% when leading, 28% when trailing"

#### 5.2.5 Per-Game Player Impact (this game only)
Same layout as tournament leaderboard but filtered to this game's events.
This requires computing impact from Raw Play-by-Play filtered to `game == gameId`.

#### 5.2.6 Key Sequences Panel
Auto-detect and surface:
- **Runs**: 3+ consecutive UCLA events that are goals/steals/blocks (momentum run)
- **Exclusion sequences**: earned_exclusion → goal_6on5 patterns
- Display as a compact event feed with timestamps and player names

---

### 5.3 Player Profile (`/player/:name`)

UCLA players from the data (filtered to team = UCLA):
`ben larsen, Max Matthews, Nick Tovani, Nate Tauscher, Harper Gardner,
Harry Tucker, ANDREW SPENCER, Marcell Szecsi, Wade Sherlock, Jackson Harlan,
Vinnie Merk, Hayden O'Hare`

#### 5.3.1 Player Header
- Name, cap number
- Role badges (from Player Roles sheet)
- Tournament Impact Score (large, primary number — styled like EPM on Dunks & Threes)
- Offensive impact / Defensive impact side by side below it

#### 5.3.2 Radar Chart (Spider Chart)
6-axis radar built with Recharts `RadarChart`:
```
Axes:
  1. Shooting Efficiency   (non_pen_pct, 0–1 normalized)
  2. Shot Volume           (shots / max_shots_on_team, normalized)
  3. Defensive Disruption  ((steals + field_blocks) / max, normalized)
  4. Leverage Creation     ((earned_excl + earned_pen) / max, normalized)
  5. Discipline            (1 − (excluded + pen_committed) / max, normalized)
  6. Clutch                (clutch_goals / max_clutch_on_team, normalized)
```
- Two overlapping polygons: this player (UCLA blue fill) + team average (gold dashed line)
- This is the "role fingerprint" — analogous to BBall-Index's Player Skills tool

#### 5.3.3 Event Feed (this player's events across tournament)
Chronological list of all events for this player across all 3 games:
- Game | Quarter | Score State | Action | Score at Time
- Color-coded by event type (green = positive, red = negative, gray = neutral)
- Grouped by game with collapsible sections

#### 5.3.4 Situational Splits (mini table)
From Raw Play-by-Play, compute this player's stats broken by:
- By Quarter: Q1 / Q2 / Q3 / Q4
- By Score State: Leading / Tied / Trailing
- Show: goals, shot%, impact contribution

#### 5.3.5 Per-Game Comparison Bar
Horizontal stacked bar showing Impact contribution per game:
- 3 segments (one per game), color-coded by opponent
- Tooltip: full game stats for that segment

---

### 5.4 Play-by-Play Explorer (`/play-by-play`)

Full raw event viewer, filterable:

#### Filters (sidebar or top bar)
- Game selector (All / Game 1 / Game 2 / Game 3)
- Team (All / UCLA / Opponent)
- Event Type (multi-select pill filter)
- Quarter (Q1–Q4)
- Score State (Leading / Tied / Trailing)
- Player name (search/typeahead)
- Clutch only toggle

#### Event Table
Columns: `Game | Quarter | Score | Score State | Clutch? | Team | Player | Event | Impact Weight`

- Highlight UCLA rows in light blue, opponent rows neutral
- Positive impact events green-tinted, negative red-tinted
- Sticky header, virtual scroll for performance (553 rows)
- Export to CSV button

---

## 6. Advanced Analytics Panel (within Tournament Overview)

These are the "EPM-adjacent" analytics borrowed from basketball/soccer:

### 6.1 Possession Efficiency Proxy
Water polo doesn't log possessions explicitly, but we can approximate:
```
UCLA Possessions ≈ goals + misses + turnovers + earned_excl_against_them
```
Compute:
- UCLA Points per Possession
- UCLA Defensive Stops per Possession (steals + field_blocks) / opponent_possessions
Display as: `Off Eff: 1.2 pts/poss | Def Eff: 0.34 stops/poss`

### 6.2 Special Teams Efficiency
Power play (man-up) stats:
- Exclusions drawn → conversion rate (goals_on_power_play / earned_exclusions)
- Man-down defense: times excluded → goals conceded while down (from raw data proximity)
- Display as: "Special Teams Net: +X" (power play goals − penalty goals allowed)

### 6.3 Impact Per Shot (IPS)
```
IPS = (goals × 3 − misses × 2.5) / shots
```
This is analogous to xG-above-expected in soccer — measures shot quality/selection.
Show as a scatter plot:
- X: shots (volume)
- Y: IPS (efficiency)
- Bubble: sized by total impact
- Quadrants labeled: "Efficient Scorer", "High Volume", "Needs Selection", "Low Usage"

### 6.4 Momentum Index
Rolling 5-event window across the game:
```
momentum[i] = sum(impact_weights[i-4:i+1]) for UCLA events only
```
Display as a line chart colored UCLA blue. Spikes = runs. Troughs = opponent runs.
Companion line: opponent momentum. Crossover points are circled.

### 6.5 Clutch Performer Index
```
CPI = (clutch_goals × 3 + clutch_steals × 2) / clutch_events_total
```
Radar of top 5 UCLA players by CPI — who do you want on the ball in Q4 down 1?

---

## 7. Interactivity Requirements

| Feature | Behavior |
|---------|----------|
| Game filter | Global filter — all charts update when game is selected |
| Player hover | Highlights that player's events across all visible charts simultaneously |
| Chart click | Drills down (e.g. clicking a quarter bar → shows that quarter's events) |
| Export | Every table has a CSV export button |
| Responsive | Works on 13" laptop screen minimum (1280px); not mobile-required |
| Dark mode | Default dark (coach film-room aesthetic); toggle to light |

---

## 8. Data Processing Requirements

The implementing agent must write a preprocessing step that:

1. Reads `PERFORMANCE_REPORT.xlsx` using `xlsx` (Node) or `openpyxl` (Python)
2. Parses the 7 sheets into typed objects
3. Computes **per-game** player stats from the Raw Play-by-Play sheet (since Player Summary is tournament-aggregate)
4. Computes offensive/defensive impact splits
5. Computes normalized percentile ranks for all player metrics (0–100 within UCLA players)
6. Computes IPS, momentum index, and possession efficiency proxy
7. Outputs a single `data.json` that the React app imports as a static asset

Recommended preprocessing: Python script `preprocess.py` → `public/data.json`

---

## 9. Component Tree (High Level)

```
App
├── NavBar (game filter tabs, UCLA logo)
├── TournamentOverview
│   ├── HeroBar
│   ├── ImpactLeaderboard
│   ├── TeamShotEfficiencyChart
│   ├── QuarterMomentumChart
│   ├── GameTimelineGrid (3 mini charts)
│   └── AdvancedAnalyticsPanel
│       ├── PossessionEfficiencyCard
│       ├── SpecialTeamsCard
│       ├── IPSScatterPlot
│       ├── MomentumIndexChart
│       └── ClutchPerformerRadar
├── GameView
│   ├── GameHeader
│   ├── WinProbabilityTimeline
│   ├── QuarterPerformanceGrid
│   ├── ScoreStateSplitsTable
│   ├── PerGamePlayerImpact
│   └── KeySequencesPanel
├── PlayerProfile
│   ├── PlayerHeader (impact + role badges)
│   ├── RadarChart
│   ├── EventFeed
│   ├── SituationalSplitsTable
│   └── PerGameComparisonBar
└── PlayByPlayExplorer
    ├── FilterSidebar
    └── EventTable (virtual scrolled)
```

---

## 10. Sample Data Snapshot (for agent reference)

UCLA key players from the data:
```
ben larsen:    impact=32.0, goals=9, shot%=64%, steals=7, earned_excl=5  → Primary Finisher + Disruptor
Max Matthews:  impact=16.5, goals=7, shot%=58%, steals=3                 → Primary Finisher
Nick Tovani:   impact=13.5, saves=10                                     → Goalie Anchor
Nate Tauscher: impact=13.3, saves=10                                     → Goalie Anchor
Harper Gardner:impact=9.0,  saves=5                                      → Goalie Anchor
Harry Tucker:  impact=6.3,  goals=2, shot%=100%, steals=2               → Clutch Contributor
```

UCLA tournament aggregates:
```
Goals: 36  |  Shots: 88  |  Shot%: 40.9%
Steals: 31  |  Field Blocks: 11  |  Earned Exclusions: 21
```

Games (score estimates from data):
```
Game 1 vs UC Davis:  UCLA win (final score visible from raw data)
Game 2 vs SJSU:      UCLA win
Game 3 vs Stanford:  UCLA loss (final: UCLA 12 - Stanford 13, trailing in Q4 data)
```

---

## 11. Open Questions for Builder

1. **Static vs live**: Is this a one-time static site (Vite/React → GitHub Pages) or does it need a server? Recommend static — data doesn't change.
2. **Per-game player stats**: Not pre-computed in the xlsx — must be derived from Raw Play-by-Play by filtering `game` column.
3. **Time column**: Most rows show `--:--` rather than actual timestamps, so true clock-based timelines are not possible. Use event sequence index as X-axis proxy.
4. **Goalie rotation**: Nick Tovani and Nate Tauscher both show saves — may be a rotation. Consider a "GK minutes" toggle if save data supports it.
5. **Opponent comparisons**: Include or hide opponent player stats? Recommend: shown on Game View, hidden on Tournament Overview (UCLA-focused).
