# Live Game Analytics Dashboard — Design Brief for Claude Design

> **Hand this file to Claude Design. It is self-contained.** Everything needed —
> repo map, data contract, metric formulas, user stories, reuse inventory, and
> acceptance criteria — is below. No external links required.
>
> **Project repo:** `/Users/ryanhurst/Desktop/wp_scraper` (local path; the repo is a
> private water-polo analytics pipeline authored by Ryan Hurst).
>
> **Existing dashboard to extend:** `dashboard/` — Vite + React 19 + TS + Tailwind
> + Zustand + Recharts + SheetJS. A tournament-wide view (Phase 1) is already
> deployed to GitHub Pages. The goal of this brief is a new **live single-game
> view** that sits alongside the shipped Tournament Overview.
>
> **Why now:** the scraper pipeline already polls a live 6-8 Sports game every
> 15 seconds and rewrites `PERFORMANCE_REPORT.xlsx` atomically
> (`live_poller.py` + `scraper_core.py`). The data surface is live-ready today;
> what's missing is a UI designed for **in-game** consumption — a coach on the
> pool deck glancing at a phone/tablet between quarters.
>
> **Terminology:** `Team1` is the focal team the dashboard is built around.
> `Team2` is the current opponent in a single-game context. The dashboard is
> currently configured for one specific focal team; team values live in
> `src/types/index.ts` and can be swapped to retarget.

---

## 1 · The Product in One Sentence

A **coach-grade, live-updating, single-game analytics view** that sits on top of
the existing tournament dashboard — reads the same `PERFORMANCE_REPORT.xlsx`
file (which the scraper rewrites every ~15s during a live game), and surfaces
**who's driving the game right now**, **what's working / what's breaking**, and
**what just happened** without the user ever clicking a tab.

It is not a fan scoreboard. It is a decision-support tool for the focal team's
bench.

---

## 2 · Who It's For — User Stories

### Primary: Head Coach (on the pool deck, between quarters)

> "I have 90 seconds. Tell me the three things I need to know before I huddle
> the team."

- Glances at one screen on a tablet. Sees: current score, current quarter, time
  since last data update, three most-impactful players *in the last 5 minutes*,
  and a momentum indicator.
- Needs to know **immediately** if Team1 has gone cold on offense (shot% last Q
  vs game average), or if the opponent is winning the press (steals-against
  trend line).
- Needs to know who is in foul trouble (excluded count, penalties committed).
- **Must not have to scroll or click** for the top-of-mind answer.

### Secondary: Assistant Coach / Analyst (courtside laptop)

> "I'm logging decisions and looking for patterns the head coach won't see."

- Watches the live event feed — every new row that arrives from the scraper
  should animate in.
- Can open a player card mid-game to see that player's per-quarter impact,
  clutch events, role-fit trends.
- Compares Team1's score-state splits (leading / tied / trailing) in *this* game
  against Team1's tournament baseline. "We're shooting 28% when trailing
  tonight — tournament average is 41%."
- Can export a snapshot of the current state (CSV of last 20 events) to share
  in Slack at halftime.

### Tertiary: Post-Game Review (within an hour of final whistle)

> "The game just ended. Walk me through what happened."

- The live view freezes on final — but the same screen is now readable as a
  post-game recap.
- Scrubbing back through the score timeline should reconstruct any moment:
  "what did the floor look like when we went down 6-8 in Q3?"
- Key-sequence detection should surface automatically: runs (3+ consecutive
  positive events), exclusion conversions (earned → goal within 2 events),
  momentum flips.

### Non-goal: Fans, broadcasters, public viewers

This dashboard is an internal coaching tool. No "fan engagement" features
(social sharing, polls, GIF reactions). No marketing surface.

---

## 3 · Repo Map — Files Claude Design Must Be Aware Of

All paths below are relative to `/Users/ryanhurst/Desktop/wp_scraper/`.

### 3.1 Data pipeline (Python — the source of the xlsx Claude Design will consume)

| File | Role | Why it matters |
|---|---|---|
| `live_poller.py` | Polling loop — calls the scraper every 15 s and writes `dashboard/public/data/PERFORMANCE_REPORT.xlsx` atomically. Has `--simulate` mode that replays a completed-game xlsx. | Sets the refresh cadence (**15 s** target interval) and guarantees the dashboard sees a consistent file (uses `.tmp` + `os.replace`). |
| `scraper_core.py` | The browser-automation core (Selenium, Chrome, fake-useragent). Exports `launch_driver()` and `scrape_play_by_play(driver, url) → pd.DataFrame`. | Produces the raw event log that feeds `build_report`. |
| `build_performance_report.py` | Transforms raw scraper DataFrame into the **7-sheet** `PERFORMANCE_REPORT.xlsx`. Canonical source of event taxonomy, impact weights, role rules, and score-state logic. | **Read this file end-to-end.** The metric definitions the dashboard renders are defined here. |
| `6_8_scraper.py` / `twp_scraper.py` | Per-source scrapers for 6-8 Sports and Total Water Polo. | Background only — Claude Design does not need to touch these. |

### 3.2 Existing dashboard (TypeScript — the codebase to extend)

| File | Role |
|---|---|
| `dashboard/public/data/PERFORMANCE_REPORT.xlsx` | **The one and only data source.** Fetched client-side at app load. During a live game this file is rewritten every ~15 s by `live_poller.py`. |
| `dashboard/src/types/index.ts` | All shared TS types + tournament-specific constants. **Live view must not assume `GAME_IDS`, `GAME_SCORES`, or `OPP_TEAMS` are populated** — in live mode the opponent is whoever shows up in the raw events. |
| `dashboard/src/lib/parseWorkbook.ts` | `SheetJS WorkBook → AppData`. Already handles all 7 sheets. Live view can reuse verbatim. |
| `dashboard/src/lib/computeScoreTimeline.ts` | Per-game score-diff timeline. Already takes a `LiveGame` object (not a hardcoded gameId). **Already live-compatible.** |
| `dashboard/src/lib/gamesFromData.ts` | Derives `LiveGame[]` from the raw events — **this is the pattern the live view should extend**. An `isLive: true` flag is already plumbed through. |
| `dashboard/src/store/useAppStore.ts` | Zustand store — `{ data, loading, error, gameFilter }`. Live view will add polling state (`lastUpdated`, `staleness`, `pollError`). |
| `dashboard/src/App.tsx` | Root — fetches the xlsx once on mount. **Live view needs this to poll instead.** See §6.2 for the pattern. |
| `dashboard/src/components/charts/GameCard.tsx` | Existing inline-SVG score-diff polyline + W/L badge. The `isLive: true` path already renders a blue `LIVE` badge. **This is the seed for the live hero element.** |
| `dashboard/src/components/layout/HeroBar.tsx` | Current record/goals/shot%/steals/saves header. Live view needs a *different* hero — see §5. |
| `dashboard/src/components/leaderboard/ImpactLeaderboard.tsx` | Tournament-wide player ranking. Live view reuses the row layout but filters to the current live game and adds a "last 5 min" lens. |
| `dashboard/src/components/charts/ShotEfficiencyChart.tsx`, `QuarterMomentumChart.tsx` | Existing chart vocabulary. Reuse the visual language (Tailwind horizontal bars for one-shot stats, Recharts grouped bars for categorical splits). |
| `dashboard/src/pages/TournamentOverview.tsx` | The shipped Phase 1 page. **Match its visual density and section rhythm.** |
| `dashboard/src/pages/GameView.tsx` | Phase 2 stub — currently empty. The **live view may take this route over**, or land at a new `/live` route. See §6.1. |
| `dashboard/CLAUDE.md` | Full design spec, tech-stack rationale, patterns, gotchas. **Read this in full.** It is the canonical dashboard doc. |

### 3.3 Session protocol (read before writing any code)

| File | Role |
|---|---|
| `CLAUDE.md` (repo root) | ADHD-aware development protocol — three-phase flow (plan → build → close-out), 45-minute checkpoints, evidence-first completion, parking-lot rule. **Non-negotiable.** |
| `PROGRESS.md` | Append-only session log. Ship every session with a new entry. |
| `TASKS.md` | Active priority list. Update on completion. |
| `PARKING_LOT.md` | Capture tangents here, don't silently chase them. |

### 3.4 Reference data (inspect to understand the shape)

| File | Notes |
|---|---|
| `dashboard/public/data/PERFORMANCE_REPORT.xlsx` | 7 sheets, 553 raw events across 3 completed games. Sheet names: `Definitions`, `Team Metrics`, `Quarter Splits`, `Score State Splits`, `Player Summary`, `Player Roles`, `Raw Play-by-Play`. |
| A raw tournament CSV at the repo root | Raw scraper output covering the shipped tournament's games. Useful for understanding the pre-transform shape. |
| Per-game scraper `.xlsx` files at the repo root | Per-game scraper output (before aggregation). Shape matches what the live scrape produces mid-game. |

---

## 4 · The Data Contract — What Claude Design Can Count On

The dashboard reads **one file**: `dashboard/public/data/PERFORMANCE_REPORT.xlsx`.
During a live game, `live_poller.py` rewrites this file every ~15 s using an
atomic `os.replace()` — **partial reads are impossible**.

### 4.1 Canonical event taxonomy

From `build_performance_report.py`:

```
event_type  ∈  { goal, goal_penalty, miss, miss_penalty,
                 steal, field_block, save,
                 earned_exclusion, earned_penalty,
                 excluded, penalty_committed,
                 offensive, turnover, assist,
                 sprint_won, other }
```

### 4.2 Impact weights (live view uses these directly)

```
goal              +3.0      miss              −2.5
goal_penalty      +1.0      miss_penalty      −0.9
steal             +2.0      excluded          −1.0
field_block       +2.0      penalty_committed −1.3
save              +1.0      offensive         −2.0
earned_exclusion  +1.3
earned_penalty    +1.6
```

`impact` for a player = weighted sum across all their events. **Can be
negative.** Bar-width math must clamp to `Math.max(0, impact)` for visuals but
display the signed value in text.

### 4.3 Score-state logic

```
score_diff_pre > 0  →  Leading
score_diff_pre < 0  →  Trailing
score_diff_pre = 0  →  Tied
NaN                  →  Unknown
```

Note: `score_diff_pre` is the diff *before* the event fired. That's the correct
"state when the play started" value — use this, not `score_diff_raw`.

### 4.4 Clutch rule

`is_clutch = (quarter == 'Q4') && |score_diff_pre| <= 1`

Applies to any event type, not just goals. In a live game, the clutch window
**opens automatically** the moment Q4 starts with a one-possession game — the
UI should respond (e.g. a thin gold rail at the top of the page).

### 4.5 Roles (pre-tagged in `Player Roles` sheet)

```
Primary Finisher                  goals ≥ 5   AND non_pen_pct ≥ 40%
Volume Shooter (Needs Selection)  shots ≥ 14  AND shot_pct   < 35%
Leverage Creator (Draws Calls)    earned_excl + earned_pen ≥ 2
Disruptor (Defense/Transition)    steals + field_blocks    ≥ 6
Clutch Contributor                clutch_goals ≥ 1
Goalie Anchor                     saves       ≥ 3
Role Player                       (none of the above)
```

In a live game these thresholds are still computed against the **running
aggregate** — a player can earn a role mid-game. The UI should animate the
badge arrival when it first appears.

### 4.6 Sheet shapes (exact columns)

- **`Raw Play-by-Play`** (553 rows in sample):
  `time, team, cap_number, player_name, action_detail, score, quarter, game,
   score_a, score_b, score_diff_raw, score_diff_pre, score_state, is_clutch,
   event_type, is_penalty_attempt`
- **`Player Summary`**: `team, player_name, impact, goals, goals_pen, shots,
   shot_pct, non_pen_goals, non_pen_shots, non_pen_pct, steals, field_blocks,
   saves, earned_excl, excluded, earned_pen, pen_committed, clutch_goals,
   shots_per_goal`
- **`Player Roles`**: Player Summary + `roles: string[]` (parsed from Python
   list literal).
- **`Team Metrics`**: `team, goals_total, shots_total, shot_pct, non_pen_goals,
   non_pen_shots, non_pen_shot_pct, steals, saves, field_blocks,
   earned_exclusions, earned_penalties, penalty_attempts_detected,
   penalty_goals, penalty_pct, pp_goals_tagged`
- **`Quarter Splits`** / **`Score State Splits`**: `team, quarter|score_state,
   goals, shots, shot_pct, steals, saves, field_blocks, earned_excl,
   earned_pen, clutch_goals`

### 4.7 Data gotchas (from `dashboard/CLAUDE.md`)

1. **`time` column is sparse.** Most rows show `--:--`. Use **sequential event
   index** as the X-axis proxy, never clock time.
2. **The focal team may be `score_a` or `score_b`** depending on which team is
   listed first in `game`. In the live view, use `gamesFromData.ts`'s
   `focalIsScoreA` flag.
3. **Roles are parsed from Python list literal strings** in the xlsx. The
   existing `parseRoles` helper is brittle on role names containing commas —
   don't invent new role names with commas.
4. **Impact can be negative.** Guard width math.
5. **Divide-by-zero everywhere.** Shots-per-goal, shot%, and percentile bars
   all need `max(1, x)` or `max(0.0001, x)` guards.
6. **OT / shootout not modeled.** Quarter is Q1–Q4 only. If the game goes to
   OT, the live view should display `OT` as a fifth bucket and surface the
   fact that no OT stats are aggregated yet (graceful degradation, not a
   crash).

---

## 5 · What the Live View Shows — Screen Inventory

**Layout target:** 1280 px wide landscape tablet in a hand on the pool deck, *and*
a 1920 px coaching-desk monitor. Single-column scroll, no tabs within the page.
Dark theme (matches shipped dashboard).

### 5.1 LIVE HERO (pinned top, never scrolls out)

The single element a coach sees at a glance. **If they can only see one thing,
it's this.**

```
┌────────────────────────────────────────────────────────────┐
│  🔴 LIVE  ·  Q3  4:12 remaining                            │
│                                                            │
│   Team1  9  —  8  Team2                                    │
│                                                            │
│   [score-diff polyline, full width, last 60 s highlighted] │
│                                                            │
│   Updated 7 s ago  ·  next refresh in 8 s                  │
└────────────────────────────────────────────────────────────┘
```

- Big score. Period + remaining time (if available; else "Q3").
- Full-width score-diff polyline (reuse `GameCard.tsx` SVG pattern, scaled up).
  Zero line in slate-500. Team1-leading region tinted primary blue at 8% opacity,
  trailing region tinted red at 8% opacity.
- **Most recent 3 events** as a ribbon of colored pills below the line (green
  goal, red miss, blue steal, amber exclusion). Each pill: player last name +
  event glyph.
- **Freshness indicator.** "Updated 7 s ago" in muted, flips yellow at 30 s,
  red at 60 s, and the whole hero gets a yellow/red border if the poller
  stalled. This is non-negotiable — a coach must **never** make a decision off
  stale data without knowing it's stale.
- **Clutch rail.** When `is_clutch` is true for the current score state (Q4,
  |diff| ≤ 1), a 3 px gold bar sits across the top edge of the hero.

### 5.2 RIGHT-NOW PANEL (below hero, 2-column on desktop)

**Left column: "What's Working"** — three cards:

1. **Momentum** — rolling 5-event impact window for Team1. Number (e.g. `+7.5`),
   trend glyph (↗ / ↘ / →), sparkline of the last 10 windows. Color-coded:
   green ≥ +3, red ≤ −3, else slate.
2. **Hot Players (last 5 min)** — top 3 players by impact computed over the
   last 5 minutes of wall clock *or* last ~20 events (whichever is smaller —
   time is unreliable). Small row: cap # · name · +Δimpact · event icons.
3. **Press Rate** — `(steals + field_blocks) / Team1_possessions_estimate`
   expressed as a percent. Live-game version of the "defensive disruption"
   metric. Delta vs tournament baseline.

**Right column: "What's Breaking"** — three cards:

1. **Cold Shooting** — Last-5-min Team1 shot% vs game-average shot%. Red if
   delta ≥ −15 pts. Shows who's missing ("player name 0/3 last 2 min").
2. **Foul Trouble** — any Team1 player at ≥ 2 exclusions or ≥ 1 penalty
   committed. Cap #, name, incident list. Empty state: "Clean." in muted.
3. **Opponent Surge** — last 3 opponent events. If 2 of the last 3 are
   positive-impact opponent events, flag as "Surge" in red.

### 5.3 LIVE EVENT FEED (below Right-Now, scrollable, 400 px tall)

- Reverse-chronological. **New events animate in from the top.**
- Each row: time (or event #) · quarter · team pill (Team1 primary blue / opponent
  neutral) · cap # · player · event glyph + label · score after · impact
  delta.
- Clutch events have a gold left border. Clicking a row *in the live view* does
  nothing (no navigation during a live game — stay on this page). In post-game
  mode, rows become clickable.
- Sticky "jump to newest" button if the user has scrolled down.

### 5.4 PLAYER IMPACT GRID (below event feed)

Same shape as the shipped `ImpactLeaderboard` but with one addition: **dual
bar**. Each row shows the player's *game-total impact* as the primary bar, and
a second, thinner "last 5 min" bar in gold on top. Coaches instantly see:
"Player X has been quietly massive all game but is cold right now."

- Columns: rank · cap # · name · role badges · impact (big number) · offense
  breakdown (goals · shots · shot%) · defense breakdown (steals · blocks ·
  saves) · exclusion line (earned · drawn-against).
- Sorted by running impact desc by default. Secondary sort by last-5-min impact.
- Negative-impact rows get a subtle red left border.

### 5.5 QUARTER TRACE (bottom, full-width)

Horizontal band, 4 (or 5 w/ OT) columns. Each column shows Q-by-Q:

```
Q1   Team1 3/5 (60%)    Team2 2/4 (50%)    Δ +1
Q2   Team1 2/6 (33%)    Team2 3/4 (75%)    Δ −1
Q3   Team1 4/5 (80%) ●  Team2 3/5 (60%)    Δ +1  ← current (live pulse)
Q4   —                  —                   —
```

Current quarter gets a soft primary-blue pulse animation. Completed quarters that
Team1 won get a green tick, lost get a red cross. Hover on any completed
quarter → tooltip with earned exclusions, steals, field blocks for that Q.

### 5.6 SCORE-STATE SPLITS (collapsed by default, expandable)

The tournament-view style table, but for this game only: `Leading | Tied |
Trailing` × Team1 stats. One-line insight callout auto-generated:

> "Team1 is shooting 55% when leading, 20% when trailing tonight
>  — tournament baseline is 48%/35%."

The insight updates live. If trailing data is empty ("we've led the whole
game"), show "Never trailed tonight — no data to compare."

### 5.7 OPTIONAL: KEY SEQUENCES (auto-detected, shows only when triggered)

Surfaces only when a pattern fires:

- **Run**: 3+ consecutive Team1 positive-impact events with no opponent
  positive in between.
- **Exclusion conversion**: `earned_exclusion` → Team1 `goal` within 2 events.
- **Defensive stand**: 3+ consecutive opponent events with no goals.
- **Momentum flip**: rolling impact crosses from negative to positive (or vice
  versa) for the first time since the last flip.

One-line toast at the top of the event feed ("🔥 Team1 RUN — 3 impact events,
+8.0 momentum") that lingers for 30 s before fading.

---

## 6 · Technical Constraints & Integration

### 6.1 Routing

The live view needs a **stable, bookmarkable URL**:

```
/live                     ← reads current state of PERFORMANCE_REPORT.xlsx
/live/:gameId             ← optional scoped form for multi-game future
```

Recommendation: take over the `/game/:gameId` stub if no tournament data is
present and `isLive` is true, **or** add a `/live` route. Do **not** modify the
`basename: '/stat_scraper'` setting or break the existing `/` Tournament
Overview route.

### 6.2 Polling pattern (replaces the one-shot fetch in `App.tsx`)

The current `App.tsx` fetches `PERFORMANCE_REPORT.xlsx` once on mount. Replace
(for the live route only) with:

```ts
// Conceptual — Claude Design implements the concrete shape.
useEffect(() => {
  let cancelled = false
  async function tick() {
    const buf = await fetch('/stat_scraper/data/PERFORMANCE_REPORT.xlsx',
                           { cache: 'no-store' }).then(r => r.arrayBuffer())
    if (cancelled) return
    const wb = XLSX.read(buf, { type: 'array' })
    setData(parseWorkbook(wb))
    setLastUpdated(Date.now())
  }
  tick()
  const id = setInterval(tick, 15_000)
  return () => { cancelled = true; clearInterval(id) }
}, [])
```

- Cadence: **15 s** matches `TARGET_INTERVAL_S` in `live_poller.py`.
- `cache: 'no-store'` is required — GitHub Pages will otherwise cache aggressively.
- Track `lastUpdated`, compute staleness (`Date.now() - lastUpdated`), and
  render it in the hero. Yellow at > 30 s, red at > 60 s.
- Poll errors keep the last-good data on screen — never blank the UI on
  transient fetch failures.
- Respect `document.visibilityState` — pause polling when the tab is hidden.

### 6.3 State management

Extend the existing Zustand store (`useAppStore.ts`), do not create a new one:

```ts
interface AppState {
  data: AppData | null
  loading: boolean
  error: string | null
  gameFilter: GameFilter
  // NEW (live only):
  lastUpdated: number | null    // epoch ms
  stalenessMs: number           // derived, recomputed every second
  pollError: string | null
  isPolling: boolean
}
```

Use **selector-based access** (`useAppStore(s => s.lastUpdated)`) — this is
the canonical pattern in the existing codebase. Do not destructure the store.

### 6.4 Static hosting still works

GitHub Pages only serves static files. Live mode works because the `.xlsx` at
`/stat_scraper/data/PERFORMANCE_REPORT.xlsx` is *written to by the scraper on
whatever machine is running `live_poller.py`*. For the live flow, the host
needs to be a writable target (local dev server, or a VPS — out of scope for
this design brief). Claude Design should **assume** the xlsx is being rewritten
behind the scenes and design the client to be robust to that.

### 6.5 Reuse vs build-new

**Reuse verbatim:**
- `parseWorkbook.ts`
- `computeScoreTimeline.ts`
- `gamesFromData.ts` (the `isLive` flag is already there)
- `RoleBadge.tsx`
- Tailwind theme tokens (primary blue, `gold`, `dark-bg`, `card-bg`, etc.)
- Impact leaderboard row layout

**Extend:**
- `App.tsx` — add polling for the live route only
- `useAppStore.ts` — add live fields
- `NavBar.tsx` — add a `Live` tab that appears only when live data is present
- `types/index.ts` — add `LiveGameState`, `MomentumWindow`, etc.

**Build new:**
- `pages/LiveGame.tsx` — the page this brief specifies
- `components/live/LiveHero.tsx`
- `components/live/RightNowPanel.tsx` (with `MomentumCard`, `HotPlayersCard`,
  `PressRateCard`, `ColdShootingCard`, `FoulTroubleCard`, `OpponentSurgeCard`)
- `components/live/EventFeed.tsx`
- `components/live/LiveImpactGrid.tsx`
- `components/live/QuarterTrace.tsx`
- `components/live/StalenessBadge.tsx`
- `components/live/KeySequenceToast.tsx`
- `lib/liveMetrics.ts` — momentum window, hot players, press rate,
  run detection. **Each function gets a Vitest test in `tests/lib/`** — this
  matches the repo convention (see `dashboard/CLAUDE.md` §11).

---

## 7 · Live Metrics — Formulas Claude Design Must Implement

These are new, live-specific derivations (the static tournament view doesn't
have them). All operate on the filtered subset of `rawEvents` where
`event.game === currentLiveGame.title`.

### 7.1 Rolling Momentum Window

```
momentum(k) = Σ (impact_weight(event_i)  for i in window)
             where window = last 5 Team1 events
```

Recompute every new event. Keep a 10-wide history for the sparkline in the
Momentum card.

### 7.2 Hot Players (last 5 min / last N events)

```
horizon = min(20 events, events in last 5 min by event index)
hot[player] = Σ impact_weight(event) for event in horizon where event.player == player
top3 = sort(hot desc)[:3]
```

If fewer than 10 events have occurred in the game, show "Too early to call" —
do not render a stale top-3.

### 7.3 Live Press Rate

```
Team1_possessions_estimate = goals + misses + turnovers + opponent_earned_excl
press_rate                = (steals + field_blocks) / max(1, Team1_possessions_estimate)
press_rate_delta          = press_rate − tournament_avg_press_rate
```

### 7.4 Run Detection

```
run_length(t) = length of longest suffix ending at t in the Team1-filtered stream
                where every event has impact_weight > 0
run_threshold = 3
```

Fire toast when `run_length(t) == 3` crossing from 2.

### 7.5 Exclusion Conversion

```
For each event `e` of type `earned_exclusion` by Team1:
  look at next 2 Team1 events
  if any is `goal` or `goal_penalty`: converted = True
```

Display as a "Power-play %" badge in Right-Now when ≥ 2 exclusions have occurred.

### 7.6 Momentum Flip

```
flip(t) = sign(momentum(t)) != sign(momentum(t - 1))
          AND |momentum(t)| ≥ 3
```

### 7.7 Score-State Dwell Time

```
for each row in raw events:
  count the event index range in each score_state
dwell[state] = count / total_events
```

Useful as a one-line callout: "Team1 has led for 68% of the game."

---

## 8 · Design Language — What It Should Feel Like

Inspiration (cited verbatim from `dashboard/CLAUDE.md` §1):

- **Dunks & Threes (EPM)** — single composite metric prominently displayed;
  percentile bars on every metric.
- **BBall-Index** — multi-dimensional profiles (we use role badges + radar).
- **Soccer analytics** — possession/transition efficiency; pressing metrics.

Live-specific additions:

- **Freshness is a first-class UI element.** Don't hide the "updated N s ago"
  line in a footer. It lives in the hero.
- **Motion is meaningful.** New events animate in (slide-from-top + fade).
  Quarter pulses while active. Clutch rail fades in when clutch fires.
  Everything else is static — no decorative motion.
- **Red and green are reserved.** Don't use them for decoration. Red means
  "Team1 is in trouble" — cold shooting, opponent surge, foul trouble, stale
  data. Green means "Team1 is winning this moment" — run fire, momentum up,
  quarter won. Primary blue is the neutral accent.
- **Gold is for clutch + peak.** Clutch rail, best quarter, hot player top-line.
  Use sparingly — it loses meaning if it's on every row.
- **Dark theme only.** `bg-dark-bg` (`#0f172a`) page, `bg-card-bg` (`#1e293b`)
  cards, `border-border` (`#334155`) edges. No light mode for v1.

---

## 9 · Edge Cases & Graceful Degradation

1. **No live data yet** (first 30 seconds of a game): show a skeleton state
   with "Waiting for first event…" — not a spinner.
2. **Poll stalls > 60 s**: full-page yellow banner — "Data is stale (last
   update 2 min 14 s ago). Check the scraper." Last-good data stays visible
   below.
3. **Scraper returns empty**: `live_poller.py` preserves the previous file, so
   this is indistinguishable from "no new events" — handle via the staleness
   indicator only.
4. **OT reached**: quarter trace grows a 5th column labeled `OT`. Stats aggregate
   normally (the 4-quarter ceiling is a scraper gap, not a UI one — flag it in
   `PARKING_LOT.md`).
5. **Opponent goalie shutout us for a whole quarter**: no Team1 goals means
   score timeline has a long flat segment — ensure the polyline still renders
   a visible flat line, not a blank panel.
6. **Tournament data is missing** (someone opens `/live` without any xlsx on
   the server): render a clear empty state, not a crash.
7. **Focal team not a participant** (someone reuses this view for a different
   team): current view hardcodes the focal team via the `FOCAL_TEAM` constant
   and `FOCAL_IS_SCORE_A` helper. Don't over-engineer for team-agnosticism in
   v1 — but leave a comment at the one place it's hardcoded so a future
   team-picker has an obvious landing spot.

---

## 10 · Definition of Done (Acceptance Criteria)

A coach running the simulated live poller
(`python live_poller.py --simulate <per_game_xlsx> --interval 5`) and opening
`/live` on a 13" laptop should be able to:

- [ ] See score, quarter, and staleness within 2 s of the page loading.
- [ ] Watch new events animate into the feed at the configured cadence.
- [ ] See the Momentum card flip color when a run starts or ends.
- [ ] See their top-3 hot players update as the game progresses.
- [ ] See the Clutch rail appear automatically when Q4 hits with a
      one-possession game.
- [ ] Know, without asking, that the data is live vs stale.
- [ ] Never see a spinner or a blank screen after the initial load —
      last-good data stays visible on any poll error.
- [ ] Jump to any historical quarter's stats by hovering the Quarter Trace.
- [ ] Read the full-screen banner within 1 s if the poller has stalled.

**Technical acceptance:**

- [ ] `npm run build` — clean tsc + Vite build, no new warnings.
- [ ] `npm test` — all existing Vitest tests still pass; new tests exist in
      `tests/lib/` for every function added to `lib/liveMetrics.ts`.
- [ ] Bundle size impact: ≤ +40 kB gzipped over the Phase 1 baseline
      (310 kB gzip). Lazy-load `react-window` if the event feed virtualizes.
- [ ] No new inline magic colors — all Recharts hex comes from a shared
      `src/theme/colors.ts` (this also closes a parking-lot polish item —
      see root `PARKING_LOT.md`).
- [ ] Polling pauses on `document.hidden` (verified by toggling tab focus).
- [ ] No modification to `GAME_IDS`, `GAME_SCORES`, `OPP_TEAMS`, or the
      shipped Tournament Overview route.
- [ ] Session-end artifacts: a new entry in `PROGRESS.md` with what shipped,
      state of codebase, and one concrete next step; any surfaced tangents
      logged in `PARKING_LOT.md`, not silently chased.

---

## 11 · Out of Scope (For This Brief)

- Fan / spectator features (sharing, reactions, broadcast graphics).
- Team-agnostic support (generic "focal team picker"). A single focal team
  is fine for v1.
- OT / shootout full handling — render OT in the Quarter Trace when present,
  but deep OT-specific analytics are v2.
- Multi-game live mode (two games simultaneously).
- Authentication, user accounts, personalization.
- Historical multi-tournament archive. The live view is about *this* game.
- Backend / API layer. File-based xlsx pipeline stays.
- Mobile portrait optimization. 1280 px landscape is the target.
- Push notifications / alerts outside the tab.

---

## 12 · First-Session Deliverable (What to Ship Today)

Scoped for a **single 3-hour session** (the repo enforces 45-min checkpoints):

1. `/live` route wired up, taking over an empty `GameView.tsx` or added fresh.
2. Polling in place in `App.tsx` with staleness computation.
3. `LiveHero.tsx` — score, quarter, polyline, staleness, most-recent-3 ribbon.
4. `EventFeed.tsx` — reverse-chronological, animated arrival.
5. `lib/liveMetrics.ts` with `rollingMomentum()` + Vitest test.
6. `StalenessBadge.tsx` as a standalone component for reuse.

Everything else (Hot Players, Press Rate, Run Detection, Quarter Trace) goes
into the next session. Plan it on the spot with the user before starting.

---

## Appendix A — Exact File Paths to Read First

Before writing a single line, open these in order:

1. `CLAUDE.md` (repo root) — session protocol
2. `dashboard/CLAUDE.md` — dashboard design doc (full read)
3. `build_performance_report.py` — canonical metric definitions
4. `live_poller.py` — polling cadence + atomic write guarantee
5. `dashboard/src/types/index.ts` — shared types
6. `dashboard/src/lib/parseWorkbook.ts` — the parser the live view reuses
7. `dashboard/src/lib/gamesFromData.ts` — `isLive` plumbing
8. `dashboard/src/components/charts/GameCard.tsx` — the seed of the LiveHero
9. `dashboard/src/pages/TournamentOverview.tsx` — the visual rhythm to match
10. `PROGRESS.md`, `TASKS.md`, `PARKING_LOT.md` — current project state

## Appendix B — One-Line Description of Each Canonical Metric

```
impact            Weighted sum of event weights for a player. Primary ranking stat. Can be negative.
goals             Field goals + penalty goals.
goals_pen         Penalty goals only.
shots             Goals + misses (field + penalty).
shot_pct          goals / shots. Overall shooting efficiency.
non_pen_goals     Field goals only.
non_pen_shots     Field attempts only.
non_pen_pct       Field-only shooting %. True finishing efficiency.
steals            Stolen possessions — turnovers won.
field_blocks      Shots blocked in open play.
saves             Goalkeeper saves.
earned_excl       Opponent exclusions drawn — power-play creation.
excluded          Times this player was excluded.
earned_pen        Penalties drawn.
pen_committed     Penalties conceded.
clutch_goals      Goals in Q4 with |score_diff| ≤ 1.
shots_per_goal    shots / goals. Lower = more efficient.
score_state       Leading / Tied / Trailing / Unknown — at the moment the event fired.
is_clutch         Q4 AND |score_diff_pre| ≤ 1.
is_penalty_attempt  Flag — includes made + missed penalties.
```

## Appendix C — Focal-Team Palette (reuse from `tailwind.config.js`)

```
primary-blue: #2774AE   ← primary accent, Team1-leading band, live pulse
gold:         #FFD100   ← clutch, hot, peak callouts
dark-bg:      #0f172a   ← page background
card-bg:      #1e293b   ← card surface
border:       #334155   ← card edges
muted:        #94a3b8   ← secondary copy
slate-500:    #64748b   ← zero lines, tertiary copy

Signal colors (use sparingly):
green-400:    #4ade80   ← Team1 win state, momentum-up, run
red-400:      #f87171   ← opponent surge, cold shooting, stale data, foul trouble
sky-400:      #38bdf8   ← LIVE badge, active quarter pulse
```

---

*End of brief. Hand this file to Claude Design along with read access to the
repo. The design should land `/live` end-to-end, tested, inside one 3-hour
session, with `PROGRESS.md` + `PARKING_LOT.md` updated on close-out per the
repo's session protocol.*
