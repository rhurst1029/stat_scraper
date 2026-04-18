# Task 02 — `liveMetrics.ts` + Tests

> Implementer: `frontend-developer` agent.
> Reviewer: `superpowers:code-reviewer` agent.
> Branch: **`feat/live-02-metrics`** (from `main`).
> Depends on: nothing (Phase A, runs parallel to Task 01).

---

## 1 · Goal

Pure-function analytics library with Vitest coverage. Every live-specific
metric Tasks 03 and 04 need derives from this module. No UI, no store, no
React — just data in, data out.

This is the single most important task for correctness — if these formulas
are wrong, everything downstream is lying to the coach.

---

## 2 · Context files to read before writing

**Required:**

1. `CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md` §7 (live metric formulas — the
   authoritative spec for this task).
2. `specs/live-dashboard/00-orchestration.md` (cross-cutting rules).
3. `build_performance_report.py` lines 16–46 (impact weights + event taxonomy)
   and lines 33–46 (`IMPACT_WEIGHTS` dict — mirror exactly).
4. `dashboard/src/types/index.ts` (RawEvent shape + constants).
5. `dashboard/src/lib/computeScoreTimeline.ts` (existing lib-module style).
6. `dashboard/src/lib/gamesFromData.ts` (LiveGame shape).
7. `dashboard/tests/lib/computeScoreTimeline.test.ts` (test style).

---

## 3 · Deliverables

### 3.1 New files

```
dashboard/src/lib/liveMetrics.ts
dashboard/tests/lib/liveMetrics.test.ts
```

### 3.2 Files to edit

None. This task is additive only. If a type needs to live in
`src/types/index.ts`, that's fine — but log it in the PR body.

---

## 4 · Implementation contract

### 4.1 Constants (mirror `build_performance_report.py`)

```ts
// dashboard/src/lib/liveMetrics.ts
export const IMPACT_WEIGHTS: Readonly<Record<string, number>> = {
  goal: 3.0,
  goal_penalty: 1.0,
  miss: -2.5,
  miss_penalty: -0.9,
  steal: 2.0,
  field_block: 2.0,
  save: 1.0,
  earned_exclusion: 1.3,
  earned_penalty: 1.6,
  excluded: -1.0,
  penalty_committed: -1.3,
  offensive: -2.0,
} as const

export function impactWeight(eventType: string): number {
  return IMPACT_WEIGHTS[eventType] ?? 0
}
```

Any drift between this file and the Python weights must be caught by a
snapshot-style test (§5.1).

### 4.2 Public functions

```ts
export function currentLiveGame(
  rawEvents: RawEvent[],
): LiveGame | null

export function eventsForLiveGame(
  rawEvents: RawEvent[],
  liveGame: LiveGame,
): RawEvent[]

export interface MomentumWindow {
  windowEnd: number        // event index in the filtered stream (0-based)
  value: number            // sum of impact weights in the window
  contributingEvents: number   // 1..windowSize
}

export function rollingMomentum(
  uclaEvents: RawEvent[],
  windowSize?: number,     // default 5
): MomentumWindow[]

export interface HotPlayer {
  player_name: string
  cap_number: string
  impactDelta: number
  eventCount: number
  eventTypes: string[]     // ordered, most-recent-last
}

export function hotPlayers(
  uclaEvents: RawEvent[],
  horizon?: number,        // default 20 events
  topN?: number,           // default 3
): HotPlayer[]

export interface CurrentQuarter {
  quarter: string          // 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'OT' | 'Unknown'
  eventCount: number
}

export function currentQuarter(
  rawEvents: RawEvent[],
  liveGame: LiveGame,
): CurrentQuarter

export interface Run {
  startIndex: number
  endIndex: number
  length: number
  totalImpact: number
}

export function detectRun(
  uclaEvents: RawEvent[],
  minLength?: number,      // default 3
): Run | null   // current ongoing run, or null
```

### 4.3 Behavior — exact rules

**`currentLiveGame(rawEvents)`:**

- Delegates to `extractGames(rawEvents)` (reuse — do not duplicate).
- Returns the first `LiveGame` with `isLive === true`, else `null`.
- Does NOT mutate inputs.

**`eventsForLiveGame(rawEvents, liveGame)`:**

- Returns `rawEvents.filter(e => e.game === liveGame.title)`.
- One-liner, but wrapped so Tasks 03 and 04 don't re-invent it.

**`rollingMomentum(uclaEvents, windowSize = 5)`:**

- Input: UCLA-only, chronologically-ordered events.
- Output: one `MomentumWindow` per event index. For the first `windowSize-1`
  events, `value` is the partial sum (not zero) and `contributingEvents` < windowSize.
- `value` = sum of `impactWeight(e.event_type)` for the last N events.
- Empty input → `[]`.
- Never throws.

**`hotPlayers(uclaEvents, horizon = 20, topN = 3)`:**

- Input: UCLA-only events.
- Takes the last `min(horizon, uclaEvents.length)` events.
- Groups by `player_name`, sums `impactWeight`, counts events.
- Returns top `topN` by `impactDelta` descending, ties broken by `eventCount`.
- **If the full game has < 10 events total (not just in horizon), return `[]`.**
  (Too early to rank — §7.2 of the design brief.)
- `cap_number` taken from the most recent event by that player in the horizon.
- `eventTypes` in chronological order, most recent last.

**`currentQuarter(rawEvents, liveGame)`:**

- Take the last event in `eventsForLiveGame(...)`. Return its `quarter` and
  the number of events in that quarter.
- Empty game → `{ quarter: 'Unknown', eventCount: 0 }`.

**`detectRun(uclaEvents, minLength = 3)`:**

- Walk from the end of `uclaEvents` back while `impactWeight > 0`.
- If the suffix length `>= minLength`, return a `Run` with that suffix's
  bounds and summed impact.
- Otherwise return `null`.

### 4.4 Style constraints

- No default exports — named exports only.
- No `let` for accumulators when `reduce` is natural.
- No inline magic numbers — constants at the top of the file.
- JSDoc on every exported function describing input + output + edge cases.

---

## 5 · Tests required (Vitest)

### 5.1 Weight-drift snapshot

```ts
test('IMPACT_WEIGHTS matches build_performance_report.py', () => {
  expect(IMPACT_WEIGHTS).toEqual({
    goal: 3.0, goal_penalty: 1.0, miss: -2.5, miss_penalty: -0.9,
    steal: 2.0, field_block: 2.0, save: 1.0, earned_exclusion: 1.3,
    earned_penalty: 1.6, excluded: -1.0, penalty_committed: -1.3,
    offensive: -2.0,
  })
})
```

If the Python weights change, this test breaks — prompting a conscious
migration rather than silent drift.

### 5.2 `rollingMomentum`

- Empty input → `[]`.
- 1 event goal → `[{ value: 3.0, contributingEvents: 1, windowEnd: 0 }]`.
- 6 events: goal, goal, miss, steal, miss, goal → windows assert per position.
- Unknown event type contributes 0.
- Default `windowSize === 5`.
- Custom `windowSize === 3` works.

### 5.3 `hotPlayers`

- `< 10 events total` → `[]`.
- 20-event synthetic stream with 3 players → correct top 3 by impact.
- Tie on impact → broken by eventCount desc.
- `horizon` shorter than stream → only last `horizon` events considered.
- `topN === 1` → one result.

### 5.4 `currentLiveGame`

- Empty events → `null`.
- Events from a single game with `isLive === true` → that game.
- Events from multiple games, only one live → the live one.

### 5.5 `eventsForLiveGame`

- Filters by exact `e.game === liveGame.title` match.
- Preserves order.

### 5.6 `currentQuarter`

- Empty → `{ quarter: 'Unknown', eventCount: 0 }`.
- Mix of Q1/Q2/Q3 events, last in Q3 with 5 Q3 events → `{ quarter: 'Q3', eventCount: 5 }`.

### 5.7 `detectRun`

- Fewer than `minLength` positive tail → `null`.
- Exactly `minLength` positive tail → returns Run.
- Negative event in the middle breaks the run.
- Positive run followed by a 0-weight event (e.g. `sprint_won`) — clarify in
  JSDoc: `sprint_won` has weight 0, breaks the run. Test this explicitly.

### 5.8 Fixtures

Use a shared `makeEvent(partial)` helper to keep tests readable.

---

## 6 · Acceptance criteria

- [ ] `npm test` — new tests all green; existing 14 still pass.
- [ ] `npm run build` clean.
- [ ] No new dependencies added.
- [ ] JSDoc on every exported function.
- [ ] Weight-drift test present and green.
- [ ] File sizes: `liveMetrics.ts` under 200 lines, test under 400 lines.

---

## 7 · PR template

```
Title: feat(live): liveMetrics lib — momentum, hot players, run detection

## Summary
- New `src/lib/liveMetrics.ts` with pure functions for all live-specific derivations
- Mirrors Python `IMPACT_WEIGHTS` — weight-drift snapshot test prevents silent divergence
- Exports: impactWeight, currentLiveGame, eventsForLiveGame, rollingMomentum,
  hotPlayers, currentQuarter, detectRun

## Test plan
- [x] `npm test` — N new tests, 14 existing still green
- [x] `npm run build` clean
- [x] Weight-drift snapshot matches build_performance_report.py
- [x] Edge cases: empty, <10 events, unknown event_type, OT

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 8 · Review checklist (for `superpowers:code-reviewer`)

Flag as BLOCKING if any:

- `IMPACT_WEIGHTS` differs from `build_performance_report.py` lines 33–46.
- Any exported function mutates its inputs.
- Any function throws on empty input (must return empty array / null).
- Divide-by-zero math anywhere.
- Default exports used.
- Missing JSDoc on an exported function.
- React/DOM imports present — this file must be UI-free.
- Weight-drift test missing.
- Test coverage below: every exported function has ≥ 3 cases (happy path,
  empty input, edge case).

Flag as SUGGESTION: unclear variable names, test names that don't describe
behavior.
