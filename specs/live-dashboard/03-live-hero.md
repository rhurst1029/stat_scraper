# Task 03 — `LiveHero` Component

> Implementer: `frontend-developer` agent.
> Reviewer: `superpowers:code-reviewer` agent.
> Branch: **`feat/live-03-hero`** (from `main`, **after** Tasks 01 + 02 merged).
> Depends on: Task 01 (polling + route) and Task 02 (liveMetrics).

---

## 1 · Goal

Ship the pinned LIVE HERO from §5.1 of
`CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md`. This is the first thing a coach
sees. **If they can only read one element, it's this.**

Specified:

- Big score (UCLA N — M Opponent).
- Period + remaining time (if available; else just `Q3`).
- Full-width score-diff polyline with UCLA-leading area tinted UCLA blue,
  trailing area tinted red, at 8% opacity.
- Three most-recent events as colored pills.
- Staleness badge in the corner.
- Clutch rail (3 px gold bar across the top) appears automatically when Q4
  hits with |score_diff| ≤ 1.

---

## 2 · Context files to read before writing

**Required:**

1. `CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md` §5.1 (LIVE HERO spec) and §8
   (design language).
2. `specs/live-dashboard/00-orchestration.md` (cross-cutting rules).
3. `specs/live-dashboard/01-polling-infrastructure.md` (what's already shipped
   — store shape, `StalenessBadge`, `LiveGame` page stub).
4. `specs/live-dashboard/02-live-metrics.md` (functions available —
   `currentLiveGame`, `eventsForLiveGame`, `currentQuarter`).
5. `dashboard/src/components/charts/GameCard.tsx` — the seed pattern. The
   LiveHero is a scaled-up, live variant of its inline-SVG polyline. Reuse
   the polyline math pattern (lines 30–38).
6. `dashboard/src/lib/computeScoreTimeline.ts` — drives the polyline.

**Reference:**

- `dashboard/src/pages/TournamentOverview.tsx` (visual rhythm to match).

---

## 3 · Deliverables

### 3.1 New files

```
dashboard/src/components/live/LiveHero.tsx
dashboard/src/components/live/RecentEventsRibbon.tsx   ← 3-event ribbon, own file for reuse
dashboard/src/components/live/ClutchRail.tsx           ← 3px gold bar when clutch
dashboard/tests/components/LiveHero.test.tsx           ← snapshot + clutch trigger + stale border
```

### 3.2 Files to edit

| File | Change |
|---|---|
| `dashboard/src/pages/LiveGame.tsx` | Replace the `<pre>` JSON stub from Task 01 with `<LiveHero game={liveGame} />`. Retain the StalenessBadge somewhere inside LiveHero. |

No other files.

---

## 4 · Implementation contract

### 4.1 `LiveHero` props

```tsx
export interface LiveHeroProps {
  game: LiveGame     // from gamesFromData
}
```

Internally pulls: `data`, `lastUpdated`, `stalenessMs` from the store (selector
access). Computes `events = eventsForLiveGame(data.rawEvents, game)` and
`quarter = currentQuarter(data.rawEvents, game)`.

### 4.2 Visual layout (Tailwind only)

```
┌────────────────────────────────────────────────────────────┐   ← optional gold clutch rail (3px)
│  🔴 LIVE  ·  Q3  ·  12 events         [StalenessBadge]     │
│                                                            │
│          UCLA   9   —   8   STANFORD                       │
│                                                            │
│  [full-width SVG polyline, 120px tall]                     │
│                                                            │
│  [pill: T.Goal S.Jones] [pill: Steal M.Matthews] ...       │
└────────────────────────────────────────────────────────────┘
```

- Container: `bg-card-bg border border-border rounded-2xl p-6 relative overflow-hidden`.
- `ClutchRail` absolutely positioned at top `0` with `h-1 bg-gold` when `clutch === true`.
- Score: `text-6xl font-extrabold` for each team's numeral. Team name labels
  below in `text-muted text-xs uppercase tracking-wider`. Winning side (higher
  score) gets `text-ucla-blue` / `text-red-400` based on `uclaLeading`.
- Quarter strip: `text-sm text-muted` with a small red pulsing dot to the
  left of "LIVE" when `data` has updated in the last 3 seconds (reuse the
  staleness timing logic).
- StalenessBadge in the top-right corner (`absolute top-4 right-4`).

### 4.3 Polyline specifics

Reuse the pattern from `GameCard.tsx:30-38` but scaled: `W = 1200` (let the
SVG be responsive via `viewBox`), `H = 120`, `mid = H/2`. Differences from
GameCard:

- Background: `<rect fill={colors.darkBg} />`.
- Zero line: `<line stroke={colors.slate500} strokeOpacity={0.4} />`.
- Quarter gridlines: 3 lines at 25%, 50%, 75% in `colors.border` (faint).
- **Two filled areas (new vs GameCard):** a path above the zero line filled
  `colors.uclaBlue` at 8% opacity, below filled `colors.red400` at 8% opacity.
  Compose with a second polyline `points` including `${W},${mid}` and `0,${mid}`
  to close the shape.
- Polyline itself: `stroke={colors.sky400}` (live blue), `strokeWidth={2.5}`.
- If `timeline.length === 0`, render a flat dashed line at `mid` with
  "Awaiting first score" muted label — never a blank panel (§9.5 of the
  design brief).

### 4.4 `RecentEventsRibbon`

```tsx
export interface RecentEventsRibbonProps {
  events: RawEvent[]    // already filtered to the live game, chronological
  max?: number          // default 3
}
```

Takes the last `max` events, renders right-to-left (most recent on the
right). Each pill:

- Event glyph (emoji or unicode is fine: 🎯 goal, 🧱 field_block, 🛡 save, ⛔ excluded, ⚔ steal, ⚠ earned_exclusion, etc. — define the full map at the top of the file).
- Player last name (split `player_name` on space, take the last chunk).
- Background color by event sign:
  - Positive (goal, steal, save, field_block, earned_*) → `bg-green-900/30 text-green-300 border-green-900`.
  - Negative (miss, excluded, penalty_committed, offensive) → `bg-red-900/30 text-red-300 border-red-900`.
  - Neutral (sprint_won, other) → `bg-slate-700 text-slate-300 border-slate-600`.
- UCLA events get a left border stripe in `colors.uclaBlue`, opponent events in `colors.red400`.

If `events.length === 0`, render "— awaiting events —" in muted.

### 4.5 `ClutchRail`

```tsx
export interface ClutchRailProps {
  active: boolean
}
```

- `active === false` → `null`.
- `active === true` → `<div className="absolute top-0 left-0 right-0 h-1 bg-gold" />`
  with a subtle pulse class.

Clutch logic lives inside `LiveHero`:

```ts
const clutch =
  quarter.quarter === 'Q4' &&
  Math.abs(game.uclaScore - game.oppScore) <= 1
```

### 4.6 Animation discipline

From §8 of the design brief: **"Motion is meaningful."**

- Score numbers cross-fade when they change (compare previous render's
  score). 200 ms.
- Polyline re-renders smoothly (SVG handles this via React's key-stable
  diff). No explicit animation.
- Pills slide-from-right + fade when a new one arrives. 250 ms. Use CSS
  `@keyframes` in `index.css` or a small inline style — no `framer-motion`
  unless absolutely necessary (log in `DECISIONS.md` if added).
- ClutchRail fades in over 400 ms when `active` flips from `false` to `true`.

Nothing else animates. No decorative motion.

---

## 5 · Tests required (Vitest + RTL)

### 5.1 `LiveHero.test.tsx`

- Renders score from the provided `LiveGame`.
- Renders the quarter label from `currentQuarter(...)`.
- Clutch rail NOT rendered when Q3 and |diff| ≤ 1.
- Clutch rail rendered when Q4 and |diff| ≤ 1.
- Clutch rail NOT rendered when Q4 and |diff| === 2.
- Renders StalenessBadge (verify by role/text — don't duplicate its own tests).
- Empty `rawEvents` → renders the "awaiting events" fallback, not a crash.

Use a fixture helper that builds a `LiveGame` + a small `RawEvent[]`. Keep
fixtures co-located at the top of the test file.

---

## 6 · Acceptance criteria

- [ ] `npm run build` clean.
- [ ] `npm test` — new tests green, all prior tests (from Tasks 01 + 02) green.
- [ ] Manual: `npm run dev` + simulated poller → `/stat_scraper/live` renders
      score, polyline, ribbon, staleness. Stop the poller → staleness goes
      amber → red. Restart → goes green.
- [ ] Resize to 1024 px → polyline scales (viewBox handles it), no layout
      break.
- [ ] Clutch rail visually verified by hacking the sample data to Q4 + 1-point
      lead (paste a fake last event, screenshot, revert).
- [ ] Bundle size reported in PR (should be ≤ +15 kB gzip added).

---

## 7 · PR template

```
Title: feat(live): LiveHero — score, polyline, ribbon, staleness, clutch rail

## Summary
- Pinned live hero with big score, Q-label, full-width polyline
- UCLA-leading area tinted blue, trailing tinted red (8% opacity)
- Last-3 events pill ribbon with slide-in animation
- ClutchRail appears automatically when Q4 + |diff| ≤ 1
- Reuses StalenessBadge from Task 01

## Test plan
- [x] `npm test` — LiveHero tests green (X new, Y existing)
- [x] `npm run build` — clean
- [x] Manual: simulated poller + `/live` — see attached screenshot
- [x] Clutch rail verified with injected Q4 close-game data

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 8 · Review checklist (for `superpowers:code-reviewer`)

Flag as BLOCKING if any:

- Score displayed with wrong side (`uclaIsScoreA` not honored).
- Clutch rail triggered outside Q4 or with |diff| > 1.
- Polyline crashes on empty `timeline`.
- Inline hex anywhere — must import from `src/theme/colors.ts`.
- `useAppStore` destructured.
- `framer-motion` or other animation library added without entry in
  `DECISIONS.md`.
- Animation on elements other than score, pills, ClutchRail.
- Pill color mapping omits an event type used in the sample data.
- StalenessBadge not visible in the hero.

Flag as SUGGESTION: opportunities to extract sub-components, naming nits.
