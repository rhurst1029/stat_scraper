# Task 04 — `EventFeed` Component

> Implementer: `frontend-developer` agent.
> Reviewer: `superpowers:code-reviewer` agent.
> Branch: **`feat/live-04-event-feed`** (from `main`, **after** Tasks 01 + 02 merged).
> Depends on: Task 01 (polling + route) and Task 02 (liveMetrics).

---

## 1 · Goal

Ship the live event feed from §5.3 of
`CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md`. The assistant coach's primary tool
— every new event arrives from the scraper animates into this feed.

Specified:

- Reverse-chronological. Newest on top.
- Each row: event #, quarter, team pill, cap #, player, event glyph + label,
  score after, impact delta.
- New events slide in from the top + fade. 250 ms.
- Clutch events get a gold left border.
- Sticky "jump to newest" button if scrolled down.
- Container height 400 px, scrollable within.
- Reverse-chrono means newest-first — the arrival animation happens on row
  index 0 each poll.

---

## 2 · Context files to read before writing

**Required:**

1. `CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md` §5.3 (EventFeed spec).
2. `specs/live-dashboard/00-orchestration.md` (cross-cutting rules).
3. `specs/live-dashboard/01-polling-infrastructure.md` (store shape — use
   `data`, `lastUpdated` to key animations).
4. `specs/live-dashboard/02-live-metrics.md` (`eventsForLiveGame` helper).
5. `dashboard/src/components/charts/GameCard.tsx` — reference for event
   filtering patterns.
6. `dashboard/src/types/index.ts` — `RawEvent`.

---

## 3 · Deliverables

### 3.1 New files

```
dashboard/src/components/live/EventFeed.tsx
dashboard/src/components/live/EventRow.tsx          ← single row, own file for test
dashboard/src/components/live/JumpToNewestButton.tsx
dashboard/src/lib/eventGlyphs.ts                    ← event_type → { glyph, label, signClass }
dashboard/tests/lib/eventGlyphs.test.ts             ← mapping completeness
dashboard/tests/components/EventFeed.test.tsx      ← arrival animation trigger, clutch border, empty state
```

### 3.2 Files to edit

| File | Change |
|---|---|
| `dashboard/src/pages/LiveGame.tsx` | Mount `<EventFeed game={liveGame} />` below `<LiveHero />`. |

No other files.

---

## 4 · Implementation contract

### 4.1 `eventGlyphs.ts` — shared mapping

```ts
export interface EventGlyph {
  glyph: string        // unicode symbol or emoji — prefer unicode for consistency
  label: string        // short human label, e.g. "Goal", "Earned Excl."
  sign: 'pos' | 'neg' | 'neutral'
}

export const EVENT_GLYPHS: Record<string, EventGlyph> = {
  goal:              { glyph: '⚽', label: 'Goal',          sign: 'pos' },
  goal_penalty:      { glyph: '🎯', label: 'Pen. Goal',     sign: 'pos' },
  miss:              { glyph: '✕',  label: 'Miss',          sign: 'neg' },
  miss_penalty:      { glyph: '✕',  label: 'Pen. Miss',     sign: 'neg' },
  steal:             { glyph: '⚡', label: 'Steal',         sign: 'pos' },
  field_block:       { glyph: '🧱', label: 'Block',         sign: 'pos' },
  save:              { glyph: '🛡', label: 'Save',          sign: 'pos' },
  earned_exclusion:  { glyph: '▲',  label: 'Earned Excl.',  sign: 'pos' },
  earned_penalty:    { glyph: '△',  label: 'Earned Pen.',   sign: 'pos' },
  excluded:          { glyph: '⛔', label: 'Excluded',      sign: 'neg' },
  penalty_committed: { glyph: '⚠',  label: 'Pen. Committed', sign: 'neg' },
  offensive:         { glyph: '↩',  label: 'Offensive',     sign: 'neg' },
  sprint_won:        { glyph: '🏁', label: 'Sprint Won',    sign: 'neutral' },
  turnover:          { glyph: '↔',  label: 'Turnover',      sign: 'neutral' },
  assist:            { glyph: '+1', label: 'Assist',        sign: 'pos' },
  other:             { glyph: '·',  label: 'Other',         sign: 'neutral' },
}

export function glyphFor(eventType: string): EventGlyph {
  return EVENT_GLYPHS[eventType] ?? EVENT_GLYPHS.other
}
```

Coordinate with Task 03's `RecentEventsRibbon` — if Task 03 defined an
internal map, **Task 04 migrates it to this shared file** (and the ribbon
imports from here). Log the migration in `PARKING_LOT.md` if it touches
Task 03's code path.

### 4.2 `EventRow` props

```tsx
export interface EventRowProps {
  event: RawEvent
  eventIndex: number           // position in the game-filtered stream
  impactDelta: number          // precomputed (impactWeight(event.event_type))
  isNew?: boolean              // true means "render the slide-in animation"
}
```

Row layout (grid, not flex — easier to align):

```
| # | Q | [team pill] | cap | player | glyph label | score | +Δ |
```

- `#`: `text-xs text-slate-500`.
- `Q`: `text-xs text-muted`.
- Team pill: focal team → `bg-focal-blue/20 text-sky-300`; opponent → `bg-slate-700 text-slate-300`.
- `cap`: `font-mono text-xs bg-card-bg border border-border rounded px-1`.
- `player`: `text-sm`.
- `glyph label`: glyph + space + label; sign class:
  - `sign === 'pos'` → `text-green-400`.
  - `sign === 'neg'` → `text-red-400`.
  - `sign === 'neutral'` → `text-slate-400`.
- `score`: `text-xs font-mono text-muted`.
- `impactDelta`: right-aligned, `text-xs font-bold`, same sign color as glyph.
- **Clutch rows** (`event.is_clutch === true`): `border-l-2 border-gold pl-2`.
- **New rows** (`isNew === true`): slide-in + fade animation (keyframes in
  `index.css` under `@keyframes eventRowIn`).

### 4.3 `EventFeed` props + behavior

```tsx
export interface EventFeedProps {
  game: LiveGame
  maxHeight?: number   // default 400 (px)
  animate?: boolean    // default true; Task tests pass false to simplify
}
```

Behavior:

- Pulls `data` and `lastUpdated` from the store (selectors).
- Computes `events = eventsForLiveGame(data.rawEvents, game)` with `useMemo`
  keyed on `data.rawEvents` and `game.title`.
- Renders **reverse-chronological** (`events.slice().reverse()`) — newest on
  top, original chronological event index preserved for display.
- Tracks "last seen event count" in a ref. On each render, if the count has
  grown, pass `isNew={true}` to rows at positions 0..(newCount - lastCount).
  After animation duration (250 ms), update the ref.
- Scrolls to top on `lastUpdated` change if the user was already at the top
  (scrollTop < 50). Otherwise holds position and shows `JumpToNewestButton`.
- Container: `max-h-{maxHeight}px overflow-y-auto bg-card-bg border border-border rounded-xl`.
- Sticky header at the top with column labels (non-scrolling).
- **No virtualization for v1.** 553 rows is the sample cap. If performance
  regresses (measure with DevTools Profiler), `react-window` is pre-approved
  per `00-orchestration.md` §cross-cutting rule 6.

### 4.4 `JumpToNewestButton`

- Absolutely positioned, `bottom-4 right-4 z-10`, inside the EventFeed container.
- Visible only when `scrollTop > 50`.
- Label: `↑ N new` (N = events since last view).
- Click: scrolls the container to `top: 0, behavior: 'smooth'`.
- Uses `bg-focal-blue text-white shadow-lg`.

### 4.5 Empty state

- `events.length === 0` → "No events yet — waiting for first play." in
  muted, centered vertically.

### 4.6 Performance notes

- The feed re-renders every 15 s. Memoize `events`, the reversed array, and
  the mapped impactDelta per row.
- Use `useRef` for `lastSeenCount` — it doesn't need to trigger renders.

---

## 5 · Tests required (Vitest + RTL)

### 5.1 `tests/lib/eventGlyphs.test.ts`

- `glyphFor('goal')` returns pos.
- `glyphFor('unknown_event')` returns `EVENT_GLYPHS.other`.
- Every event type in the `IMPACT_WEIGHTS` map (from Task 02) has an entry
  in `EVENT_GLYPHS` — enforce with a static check loop.

### 5.2 `tests/components/EventFeed.test.tsx`

- Renders empty state when no events.
- Renders one row per event in the live game's stream (filtered correctly).
- New events rendered with `isNew` when events are added between renders
  (use rerender + count increase).
- Clutch event → row has gold left-border class applied.
- JumpToNewestButton only appears when scroll > 50 (use `Object.defineProperty(container, 'scrollTop', { get: () => 100 })` or fire scroll event).

Pass `animate={false}` to the component in tests to make assertions deterministic.

---

## 6 · Acceptance criteria

- [ ] `npm run build` clean.
- [ ] `npm test` — new tests green, all prior tests green.
- [ ] Manual: simulated poller + `/stat_scraper/live` → feed populates, new
      events slide in each tick.
- [ ] Manual: scroll down in the feed, new event arrives → JumpToNewestButton
      appears. Click → scrolls to top.
- [ ] Clutch event visually verified (inject a fake `is_clutch: true` row or
      use a natural Q4 event).
- [ ] No CLS / layout jank on arrival — measure with DevTools Performance.
- [ ] Bundle size reported in PR (should be ≤ +10 kB gzip).

---

## 7 · PR template

```
Title: feat(live): EventFeed with animated arrivals + clutch borders

## Summary
- Live event feed, reverse-chrono, newest on top
- Slide-in + fade animation for new rows (CSS keyframe)
- Clutch events get gold left border
- `JumpToNewestButton` for when the user has scrolled away
- Shared `eventGlyphs.ts` — Task 03's ribbon can now import from here
- No virtualization in v1 (parked for future if 553-row perf regresses)

## Test plan
- [x] `npm test` — N new tests green
- [x] `npm run build` clean
- [x] Manual against simulated poller — rows animate in every 5s
- [x] JumpToNewestButton verified via scroll

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 8 · Review checklist (for `superpowers:code-reviewer`)

Flag as BLOCKING if any:

- Event ordering not reverse-chronological.
- Clutch rows missing the gold left border.
- Glyph map missing any event type that appears in the sample data.
- `useAppStore` destructured (must be selectors).
- Inline hex outside `src/theme/colors.ts`.
- Animation always-on without a way to disable for tests (`animate` prop
  must exist).
- Scroll-jump disrupts user when they're mid-scroll (must only auto-scroll
  if scrollTop < 50).
- Filtering logic duplicated instead of using `eventsForLiveGame` from
  Task 02.
- `react-window` added without `DECISIONS.md` entry (not needed for v1 —
  should be absent).

Flag as SUGGESTION: row key strategy (event index is fine; composite is
nicer), memoization quality.
