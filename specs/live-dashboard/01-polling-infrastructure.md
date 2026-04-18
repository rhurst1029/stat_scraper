# Task 01 — Polling Infrastructure + `/live` Route

> Implementer: `frontend-developer` agent.
> Reviewer: `superpowers:code-reviewer` agent.
> Branch: **`feat/live-01-polling-infra`** (from `main`).
> Depends on: nothing (Phase A, runs parallel to Task 02).

---

## 1 · Goal

Turn the dashboard from "fetch xlsx once on load" into "poll every 15 s and
expose freshness state." Create the `/live` route and a minimal page stub so
Tasks 03 and 04 have somewhere to mount.

**No visual polish in this task** — the page can render `<StalenessBadge />`
plus raw JSON of the current live game. Beauty lands in Task 03.

---

## 2 · Context files to read before writing

**Required (in order):**

1. `CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md` §6 (technical constraints).
2. `specs/live-dashboard/00-orchestration.md` (cross-cutting rules).
3. `dashboard/CLAUDE.md` §3, §6, §11 (tech stack, routing, patterns).
4. `dashboard/src/App.tsx` (current one-shot fetch — replace pattern).
5. `dashboard/src/store/useAppStore.ts` (extend).
6. `dashboard/src/router.tsx` (add route).
7. `dashboard/src/lib/parseWorkbook.ts` (reuse verbatim).
8. `dashboard/src/lib/gamesFromData.ts` (live game detection — already has `isLive`).
9. `live_poller.py` (cadence reference — `TARGET_INTERVAL_S = 15`).

**Reference (skim for patterns):**

- `dashboard/src/components/layout/HeroBar.tsx` (token usage).
- `dashboard/tests/lib/computeScoreTimeline.test.ts` (Vitest pattern).

---

## 3 · Deliverables

### 3.1 New files

```
dashboard/src/theme/colors.ts               ← single source of truth for Recharts + component hex
dashboard/src/components/live/StalenessBadge.tsx
dashboard/src/pages/LiveGame.tsx            ← minimal stub page
dashboard/src/hooks/usePolling.ts           ← encapsulates the polling effect
dashboard/tests/hooks/usePolling.test.ts    ← test timer + visibility pause (fake timers)
dashboard/tests/components/StalenessBadge.test.tsx  ← test yellow/red thresholds
```

### 3.2 Files to edit

| File | Change |
|---|---|
| `dashboard/src/router.tsx` | Add `{ path: 'live', element: <LiveGame /> }` to the children array. |
| `dashboard/src/store/useAppStore.ts` | Extend state with `lastUpdated`, `stalenessMs`, `pollError`, `isPolling`. Add actions `setData`, `setLastUpdated`, `setPollError`, `tickStaleness`. |
| `dashboard/src/App.tsx` | Replace the current `useEffect(..., [])` single-shot fetch with a call to `usePolling({ url, intervalMs: 15_000 })`. Keep the LoadingScreen flow for the first load. |
| `dashboard/src/components/layout/NavBar.tsx` | Add a "🔴 LIVE" tab that renders only when `data && extractGames(data.rawEvents).some(g => g.isLive)`. Link to `/live`. |
| `dashboard/src/types/index.ts` | Add `LivePollState` interface + export. |
| `dashboard/tailwind.config.js` | If `src/theme/colors.ts` defines tokens used here, import them (optional; parking-lot if not done). |

### 3.3 Nothing modified outside the list above.

Any need to touch other files → append a bullet to `PARKING_LOT.md` and stop.

---

## 4 · Implementation contract

### 4.1 `usePolling` hook signature

```ts
// dashboard/src/hooks/usePolling.ts
export interface UsePollingOpts {
  url: string
  intervalMs: number
  onTick: (wb: XLSX.WorkBook) => void
  onError?: (err: Error) => void
}

export function usePolling(opts: UsePollingOpts): void
```

Behavior (test all of this):

- Fetches `url` with `cache: 'no-store'` on mount, then every `intervalMs`.
- On success, decodes to `XLSX.WorkBook` and calls `onTick`.
- On error, calls `onError` with the thrown error. Does **not** clear last-good
  data — the caller decides.
- **Pauses when `document.hidden === true`.** Listens for `visibilitychange`
  and resumes on re-show. Fires an immediate tick on resume.
- Cleans up the interval + listener on unmount.

### 4.2 Store extensions

```ts
// additions to AppState
interface AppState {
  // ... existing fields ...
  lastUpdated: number | null   // epoch ms of last successful parse
  stalenessMs: number          // Date.now() - lastUpdated, recomputed every 1s
  pollError: string | null
  isPolling: boolean

  setData: (d: AppData) => void
  setLastUpdated: (t: number) => void
  setPollError: (e: string | null) => void
  tickStaleness: () => void    // called by a 1s interval
  setIsPolling: (b: boolean) => void
}
```

`tickStaleness` is called from a 1 s `setInterval` inside `App.tsx` so the
badge counts up smoothly even between polls.

### 4.3 `StalenessBadge` component

```tsx
// dashboard/src/components/live/StalenessBadge.tsx
export interface StalenessBadgeProps {
  lastUpdated: number | null
  stalenessMs: number
  intervalMs: number   // e.g. 15_000
}
```

Rules (test each):

- `lastUpdated === null` → "Waiting for first update…" in muted.
- `stalenessMs < 30_000` → "Updated 7s ago · next in 8s" in muted. Text green
  when `< 3_000`.
- `30_000 ≤ stalenessMs < 60_000` → amber badge, "Updated 45s ago".
- `stalenessMs ≥ 60_000` → red badge with a pulsing dot, "Data stale — 1m 14s".
- Countdown text (`next in Ns`) always rounds to the nearest second.

Implementation: single flex div, Tailwind only, no Recharts. Respect
`src/theme/colors.ts` if you export staleness colors there (optional —
parking-lot if not clean).

### 4.4 `/live` page stub

```tsx
// dashboard/src/pages/LiveGame.tsx — minimal, Task 03 replaces the body
export default function LiveGame() {
  const data = useAppStore(s => s.data)
  const lastUpdated = useAppStore(s => s.lastUpdated)
  const stalenessMs = useAppStore(s => s.stalenessMs)
  const pollError = useAppStore(s => s.pollError)

  const liveGame = useMemo(
    () => data ? extractGames(data.rawEvents).find(g => g.isLive) ?? null : null,
    [data],
  )

  if (!data) return <div className="p-8 text-muted">Loading live data…</div>
  if (!liveGame) return <div className="p-8 text-muted">No live game detected.</div>

  return (
    <div className="p-6 space-y-4">
      <StalenessBadge
        lastUpdated={lastUpdated}
        stalenessMs={stalenessMs}
        intervalMs={15_000}
      />
      {pollError && (
        <div className="text-red-400 text-sm">Poll error: {pollError} (showing last good)</div>
      )}
      {/* Task 03 replaces below this line */}
      <pre className="text-xs text-muted overflow-auto bg-card-bg p-4 rounded">
        {JSON.stringify(liveGame, null, 2)}
      </pre>
    </div>
  )
}
```

### 4.5 `src/theme/colors.ts` contents

```ts
// Single source of truth. Matches tailwind.config.js tokens.
export const colors = {
  uclaBlue: '#2774AE',
  gold:     '#FFD100',
  darkBg:   '#0f172a',
  cardBg:   '#1e293b',
  border:   '#334155',
  muted:    '#94a3b8',
  slate500: '#64748b',
  green400: '#4ade80',
  red400:   '#f87171',
  sky400:   '#38bdf8',
  amber400: '#fbbf24',
} as const

export type ColorToken = keyof typeof colors
```

Also migrate any existing inline hex in `QuarterMomentumChart.tsx` to import
from here — but **only if it touches files already edited**. Otherwise log to
`PARKING_LOT.md`.

### 4.6 NavBar "🔴 LIVE" tab

- Visible only when `extractGames(rawEvents).some(g => g.isLive)`.
- Pulse animation on the red dot: `animate-pulse` Tailwind class on the dot
  span, rest of tab static.
- Uses the same `NavLink` pattern as existing tabs.

---

## 5 · Tests required (Vitest)

### 5.1 `tests/hooks/usePolling.test.ts`

- Calls `onTick` on mount.
- Calls `onTick` again after `intervalMs` (fake timers).
- Does NOT tick while `document.hidden === true` (mock `Object.defineProperty`
  on `document`).
- Ticks immediately on `visibilitychange` → visible.
- Unmounting clears the interval (advance timers past 2× interval, assert no
  new calls).
- Error in fetch → `onError` called, `onTick` not called.

### 5.2 `tests/components/StalenessBadge.test.tsx`

- Renders "Waiting…" when `lastUpdated === null`.
- Renders muted text when `stalenessMs < 30_000`.
- Renders amber variant at `stalenessMs === 30_000`.
- Renders red variant at `stalenessMs === 60_000`.
- Countdown text is correct (`next in Ns` matches `(intervalMs - stalenessMs)/1000`).

Use `@testing-library/react` — already in `devDependencies` (verify in
`package.json`; if absent, add it in the same commit and log in `DECISIONS.md`).

Target: all tests green, no new warnings. Existing 14 tests must still pass.

---

## 6 · Acceptance criteria

- [ ] `npm run build` clean (tsc + Vite, no new warnings).
- [ ] `npm test` — all new tests green, existing 14 still pass.
- [ ] `npm run dev` → open `/stat_scraper/live` → page renders (stub is fine).
- [ ] With the simulated poller running, `lastUpdated` and `stalenessMs`
      update in the store (verify via React DevTools or a temporary
      `console.log` you remove before commit).
- [ ] Switching tabs pauses polling (verify `document.hidden = true` stops
      the tick).
- [ ] NavBar shows the 🔴 LIVE tab when sample xlsx has live games.
- [ ] No inline hex outside `src/theme/colors.ts` and Recharts call sites.
- [ ] Bundle size impact reported in PR body (`npm run build` stdout).

---

## 7 · PR template

```
Title: feat(live): polling infrastructure + /live route

## Summary
- Adds 15s xlsx polling via new `usePolling` hook, pause-on-hidden
- Extends Zustand store with freshness state (lastUpdated, stalenessMs, pollError)
- Adds `/live` route with minimal `LiveGame` page stub (Task 03 replaces body)
- Adds `StalenessBadge` component with green/amber/red thresholds
- Introduces `src/theme/colors.ts` as the single source for Recharts/component hex
- NavBar grows a 🔴 LIVE tab when a live game is detected

## Test plan
- [x] `npm test` — all tests pass (X new, 14 existing)
- [x] `npm run build` — clean tsc + Vite
- [x] Manual: simulated poller + `/stat_scraper/live` shows freshness countdown
- [x] Manual: tab backgrounded → polling pauses; refocused → immediate tick
- [x] Bundle size: 310 → X kB gzip (Δ +Y kB)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## 8 · Review checklist (for `superpowers:code-reviewer`)

Flag as BLOCKING if any:

- `useAppStore` destructured anywhere (must be selector-based — `dashboard/CLAUDE.md` §11).
- Magic hex codes outside `src/theme/colors.ts` in newly-added code.
- `document.hidden` check missing from `usePolling`.
- Polling keeps running after `unmount` (verify cleanup in the hook).
- `cache: 'no-store'` missing on the `fetch` call — GitHub Pages will cache.
- No divide-by-zero guards on derived staleness values.
- Hardcoded UCLA-specific strings outside `src/types/index.ts`.
- Any file modified outside §3.2 list (unless logged in `PARKING_LOT.md`).

Flag as SUGGESTION (non-blocking): inline-style Tailwind class soup, unclear
variable names, missing JSDoc on exported interfaces.

Return ✅ APPROVED when every BLOCKING item is clean.
