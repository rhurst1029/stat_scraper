# Pacific Cup Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static Vite + React + TypeScript coach-grade analytics dashboard for the UCLA Water Polo Pacific Cup 2026 tournament, deployed to GitHub Pages, loading all data client-side from `PERFORMANCE_REPORT.xlsx` via SheetJS.

**Architecture:** Single-page app with React Router v6. Data is loaded once at startup via SheetJS, parsed into typed objects, and stored in a Zustand store. All pages read from the store. Phase 1 (Tournament Overview) is the full deliverable for this session; Phases 2–4 are stubbed pages.

**Tech Stack:** Vite 5, React 18, TypeScript, Tailwind CSS v3, Recharts, SheetJS (xlsx), Zustand, React Router v6, Vitest, gh-pages

---

## File Map

```
wp_scraper/pacific-cup-dashboard/
  public/
    data/
      PERFORMANCE_REPORT.xlsx        ← copied from parent dir
  src/
    types/
      index.ts                       ← all shared TS interfaces + constants
    lib/
      parseWorkbook.ts               ← SheetJS → typed AppData
      computeScoreTimeline.ts        ← score diff array from Raw PBP per game
    store/
      useAppStore.ts                 ← Zustand: AppData + gameFilter
    hooks/
      useWorkbook.ts                 ← fetch + parse xlsx, expose loading/error
    components/
      LoadingScreen.tsx              ← full-page loading/error state
      layout/
        NavBar.tsx                   ← sticky top nav + tabs
        FilterPills.tsx              ← All / vs UC Davis / vs SJSU / vs Stanford
        HeroBar.tsx                  ← Record, Goals, Shot%, Steals, Saves, Earned Excl.
      leaderboard/
        RoleBadge.tsx                ← colored badge chip for a single role string
        ImpactLeaderboard.tsx        ← ranked table with percentile bars + badges
      charts/
        ShotEfficiencyChart.tsx      ← horizontal bar chart (Recharts)
        QuarterMomentumChart.tsx     ← grouped bar chart by quarter (Recharts)
        GameCard.tsx                 ← game result card with inline SVG timeline
    pages/
      TournamentOverview.tsx         ← Phase 1: full page assembly
      GameView.tsx                   ← Phase 2 stub
      PlayerIndex.tsx                ← Phase 3 stub
      PlayerProfile.tsx              ← Phase 3 stub
      PlayByPlayExplorer.tsx         ← Phase 4 stub
    router.tsx                       ← React Router v6 routes
    App.tsx                          ← root: loads data, renders router
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
  tsconfig.node.json
  package.json
```

---

## Task 1: Scaffold Project + Install Dependencies

**Files:**
- Create: `pacific-cup-dashboard/` (entire project)

- [ ] **Step 1: Scaffold Vite project**

Run from `/Users/ryanhurst/Desktop/wp_scraper/`:
```bash
npm create vite@latest pacific-cup-dashboard -- --template react-ts
cd pacific-cup-dashboard
```

- [ ] **Step 2: Install runtime dependencies**

```bash
npm install recharts xlsx zustand react-router-dom
```

- [ ] **Step 3: Install dev dependencies**

```bash
npm install -D tailwindcss postcss autoprefixer vitest @vitejs/plugin-react @testing-library/react jsdom gh-pages
```

- [ ] **Step 4: Initialize Tailwind**

```bash
npx tailwindcss init -p
```

- [ ] **Step 5: Write `tailwind.config.js`**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'ucla-blue': '#2774AE',
        gold: '#FFD100',
        'dark-bg': '#0f172a',
        'card-bg': '#1e293b',
        border: '#334155',
        muted: '#94a3b8',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 6: Write `src/index.css`** (replace generated content)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  background-color: #0f172a;
  color: #e2e8f0;
}
```

- [ ] **Step 7: Configure Vite for GitHub Pages**

Write `vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/stat_scraper/',
  test: {
    environment: 'jsdom',
    globals: true,
  },
})
```

- [ ] **Step 8: Configure package.json scripts**

Add to `package.json` (merge with existing scripts):
```json
{
  "homepage": "https://rhurst1029.github.io/stat_scraper",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "deploy": "npm run build && gh-pages -d dist"
  }
}
```

- [ ] **Step 9: Copy data file**

```bash
cp /Users/ryanhurst/Desktop/wp_scraper/PERFORMANCE_REPORT.xlsx public/data/PERFORMANCE_REPORT.xlsx
```

- [ ] **Step 10: Verify dev server starts**

```bash
npm run dev
```
Expected: Vite server running at `http://localhost:5173/stat_scraper/`

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "feat: scaffold Vite + React + TS project with Tailwind and deps"
```

---

## Task 2: TypeScript Types + Data Parsing Library

**Files:**
- Create: `src/types/index.ts`
- Create: `src/lib/parseWorkbook.ts`
- Create: `src/lib/computeScoreTimeline.ts`
- Create: `tests/lib/parseWorkbook.test.ts`
- Create: `tests/lib/computeScoreTimeline.test.ts`

- [ ] **Step 1: Write `src/types/index.ts`**

```typescript
export interface PlayerSummary {
  team: string
  player_name: string
  impact: number
  goals: number
  goals_pen: number
  shots: number
  shot_pct: number
  non_pen_goals: number
  non_pen_shots: number
  non_pen_pct: number
  steals: number
  field_blocks: number
  saves: number
  earned_excl: number
  excluded: number
  earned_pen: number
  pen_committed: number
  clutch_goals: number
  shots_per_goal: number | null
  roles: string[]
}

export interface TeamMetrics {
  team: string
  goals_total: number
  shots_total: number
  shot_pct: number
  steals: number
  saves: number
  field_blocks: number
  earned_exclusions: number
  earned_penalties: number
  penalty_goals: number
  penalty_pct: number
  pp_goals_tagged: number
}

export interface QuarterSplit {
  team: string
  quarter: string
  goals: number
  shots: number
  shot_pct: number
  steals: number
  saves: number
  field_blocks: number
  earned_excl: number
  earned_pen: number
  clutch_goals: number
}

export interface ScoreStateSplit {
  team: string
  score_state: string
  goals: number
  shots: number
  shot_pct: number
  steals: number
  saves: number
  field_blocks: number
  earned_excl: number
  earned_pen: number
  clutch_goals: number
}

export interface RawEvent {
  time: string
  team: string
  cap_number: string
  player_name: string
  action_detail: string
  score: string
  quarter: string
  game: string
  score_a: number
  score_b: number
  score_diff_raw: number
  score_diff_pre: number | null
  score_state: string
  is_clutch: boolean
  event_type: string
  is_penalty_attempt: boolean
}

export interface AppData {
  playerSummaries: PlayerSummary[]
  teamMetrics: TeamMetrics[]
  quarterSplits: QuarterSplit[]
  scoreStateSplits: ScoreStateSplit[]
  rawEvents: RawEvent[]
}

export type GameId = 'ucdavis' | 'sjsu' | 'stanford'
export type GameFilter = 'all' | GameId

// Exact game name strings as they appear in the `game` column of Raw PBP
export const GAME_NAMES: Record<GameId, string> = {
  ucdavis: 'UC Davis Aggies VS UCLA Bruins',
  sjsu: 'UCLA Bruins VS SJSU Spartans',
  stanford: 'UCLA Bruins VS Stanford Cardinal',
}

export const GAME_LABELS: Record<GameId, string> = {
  ucdavis: 'vs UC Davis',
  sjsu: 'vs SJSU',
  stanford: 'vs Stanford',
}

// UCLA is score_b for ucdavis (they're listed second); score_a for the others
export const UCLA_IS_SCORE_A: Record<GameId, boolean> = {
  ucdavis: false,
  sjsu: true,
  stanford: true,
}

export const GAME_SCORES: Record<GameId, { uclaScore: number; oppScore: number; win: boolean }> = {
  ucdavis: { uclaScore: 14, oppScore: 7, win: true },
  sjsu: { uclaScore: 11, oppScore: 10, win: true },
  stanford: { uclaScore: 11, oppScore: 12, win: false },
}

export const UCLA_TEAM = 'UCLA Bruins'
export const GAME_IDS: GameId[] = ['ucdavis', 'sjsu', 'stanford']
```

- [ ] **Step 2: Write `src/lib/parseWorkbook.ts`**

```typescript
import * as XLSX from 'xlsx'
import type {
  AppData, PlayerSummary, TeamMetrics,
  QuarterSplit, ScoreStateSplit, RawEvent,
} from '../types'

function sheetToRows<T extends Record<string, unknown>>(
  wb: XLSX.WorkBook,
  sheetName: string,
): T[] {
  const ws = wb.Sheets[sheetName]
  if (!ws) throw new Error(`Sheet "${sheetName}" not found in workbook`)
  return XLSX.utils.sheet_to_json<T>(ws, { defval: null })
}

function parseRoles(raw: unknown): string[] {
  if (typeof raw !== 'string' || !raw) return []
  // Python list literal: "['Primary Finisher', 'Disruptor']"
  return raw
    .replace(/^\[|\]$/g, '')
    .split(',')
    .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean)
}

export function parseWorkbook(wb: XLSX.WorkBook): AppData {
  const roleRows = sheetToRows(wb, 'Player Roles')
  const playerSummaries: PlayerSummary[] = roleRows.map(row => ({
    team: String(row.team ?? '').trim(),
    player_name: String(row.player_name ?? '').trim(),
    impact: Number(row.impact ?? 0),
    goals: Number(row.goals ?? 0),
    goals_pen: Number(row.goals_pen ?? 0),
    shots: Number(row.shots ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    non_pen_goals: Number(row.non_pen_goals ?? 0),
    non_pen_shots: Number(row.non_pen_shots ?? 0),
    non_pen_pct: Number(row.non_pen_pct ?? 0),
    steals: Number(row.steals ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    saves: Number(row.saves ?? 0),
    earned_excl: Number(row.earned_excl ?? 0),
    excluded: Number(row.excluded ?? 0),
    earned_pen: Number(row.earned_pen ?? 0),
    pen_committed: Number(row.pen_committed ?? 0),
    clutch_goals: Number(row.clutch_goals ?? 0),
    shots_per_goal: row.shots_per_goal != null ? Number(row.shots_per_goal) : null,
    roles: parseRoles(row.roles),
  }))

  const teamRows = sheetToRows(wb, 'Team Metrics')
  const teamMetrics: TeamMetrics[] = teamRows.map(row => ({
    team: String(row.team ?? '').trim(),
    goals_total: Number(row.goals_total ?? 0),
    shots_total: Number(row.shots_total ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    steals: Number(row.steals ?? 0),
    saves: Number(row.saves ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    earned_exclusions: Number(row.earned_exclusions ?? 0),
    earned_penalties: Number(row.earned_penalties ?? 0),
    penalty_goals: Number(row.penalty_goals ?? 0),
    penalty_pct: Number(row.penalty_pct ?? 0),
    pp_goals_tagged: Number(row.pp_goals_tagged ?? 0),
  }))

  const qRows = sheetToRows(wb, 'Quarter Splits')
  const quarterSplits: QuarterSplit[] = qRows.map(row => ({
    team: String(row.team ?? '').trim(),
    quarter: String(row.quarter ?? ''),
    goals: Number(row.goals ?? 0),
    shots: Number(row.shots ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    steals: Number(row.steals ?? 0),
    saves: Number(row.saves ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    earned_excl: Number(row.earned_excl ?? 0),
    earned_pen: Number(row.earned_pen ?? 0),
    clutch_goals: Number(row.clutch_goals ?? 0),
  }))

  const ssRows = sheetToRows(wb, 'Score State Splits')
  const scoreStateSplits: ScoreStateSplit[] = ssRows.map(row => ({
    team: String(row.team ?? '').trim(),
    score_state: String(row.score_state ?? ''),
    goals: Number(row.goals ?? 0),
    shots: Number(row.shots ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    steals: Number(row.steals ?? 0),
    saves: Number(row.saves ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    earned_excl: Number(row.earned_excl ?? 0),
    earned_pen: Number(row.earned_pen ?? 0),
    clutch_goals: Number(row.clutch_goals ?? 0),
  }))

  const pbpRows = sheetToRows(wb, 'Raw Play-by-Play')
  const rawEvents: RawEvent[] = pbpRows.map(row => ({
    time: String(row.time ?? ''),
    team: String(row.team ?? '').trim(),
    cap_number: String(row.cap_number ?? '').trim(),
    player_name: String(row.player_name ?? '').trim(),
    action_detail: String(row.action_detail ?? ''),
    score: String(row.score ?? ''),
    quarter: String(row.quarter ?? ''),
    game: String(row.game ?? ''),
    score_a: Number(row.score_a ?? 0),
    score_b: Number(row.score_b ?? 0),
    score_diff_raw: Number(row.score_diff_raw ?? 0),
    score_diff_pre: row.score_diff_pre != null ? Number(row.score_diff_pre) : null,
    score_state: String(row.score_state ?? ''),
    is_clutch: Boolean(row.is_clutch),
    event_type: String(row.event_type ?? ''),
    is_penalty_attempt: Boolean(row.is_penalty_attempt),
  }))

  return { playerSummaries, teamMetrics, quarterSplits, scoreStateSplits, rawEvents }
}
```

- [ ] **Step 3: Write `src/lib/computeScoreTimeline.ts`**

```typescript
import type { RawEvent, GameId } from '../types'
import { GAME_NAMES, UCLA_IS_SCORE_A } from '../types'

export interface TimelinePoint {
  eventIndex: number
  scoreDiff: number  // positive = UCLA leading
}

export function computeScoreTimeline(events: RawEvent[], gameId: GameId): TimelinePoint[] {
  const gameName = GAME_NAMES[gameId]
  const uclaIsA = UCLA_IS_SCORE_A[gameId]

  return events
    .filter(e => e.game === gameName && e.score_diff_pre != null)
    .map((e, i) => ({
      eventIndex: i,
      scoreDiff: uclaIsA ? e.score_a - e.score_b : e.score_b - e.score_a,
    }))
}
```

- [ ] **Step 4: Write `tests/lib/parseWorkbook.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'
import { parseWorkbook } from '../../src/lib/parseWorkbook'
import * as XLSX from 'xlsx'

function makeWorkbook(sheets: Record<string, unknown[]>): XLSX.WorkBook {
  const wb = XLSX.utils.book_new()
  for (const [name, data] of Object.entries(sheets)) {
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), name)
  }
  return wb
}

describe('parseWorkbook', () => {
  it('parses Player Roles into PlayerSummary with roles array', () => {
    const wb = makeWorkbook({
      'Player Roles': [{
        team: ' UCLA Bruins ',
        player_name: 'ben larsen',
        impact: 32,
        goals: 9, goals_pen: 0, shots: 14, shot_pct: 0.643,
        non_pen_goals: 9, non_pen_shots: 14, non_pen_pct: 0.643,
        steals: 7, field_blocks: 2, saves: 0,
        earned_excl: 5, excluded: 3, earned_pen: 0, pen_committed: 0,
        clutch_goals: 0, shots_per_goal: 1.55,
        roles: "['Primary Finisher', 'Disruptor (Defense/Transition)']",
      }],
      'Team Metrics': [],
      'Quarter Splits': [],
      'Score State Splits': [],
      'Raw Play-by-Play': [],
    })

    const data = parseWorkbook(wb)
    expect(data.playerSummaries).toHaveLength(1)
    const p = data.playerSummaries[0]
    expect(p.team).toBe('UCLA Bruins')
    expect(p.player_name).toBe('ben larsen')
    expect(p.impact).toBe(32)
    expect(p.roles).toEqual(['Primary Finisher', 'Disruptor (Defense/Transition)'])
  })

  it('handles missing roles gracefully', () => {
    const wb = makeWorkbook({
      'Player Roles': [{
        team: ' UCLA Bruins ', player_name: 'Test Player',
        impact: 0, goals: 0, goals_pen: 0, shots: 0, shot_pct: 0,
        non_pen_goals: 0, non_pen_shots: 0, non_pen_pct: 0,
        steals: 0, field_blocks: 0, saves: 0,
        earned_excl: 0, excluded: 0, earned_pen: 0, pen_committed: 0,
        clutch_goals: 0, shots_per_goal: null, roles: null,
      }],
      'Team Metrics': [],
      'Quarter Splits': [],
      'Score State Splits': [],
      'Raw Play-by-Play': [],
    })
    const data = parseWorkbook(wb)
    expect(data.playerSummaries[0].roles).toEqual([])
  })

  it('throws if a required sheet is missing', () => {
    const wb = XLSX.utils.book_new()
    expect(() => parseWorkbook(wb)).toThrow('Sheet "Player Roles" not found')
  })
})
```

- [ ] **Step 5: Write `tests/lib/computeScoreTimeline.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'
import { computeScoreTimeline } from '../../src/lib/computeScoreTimeline'
import type { RawEvent } from '../../src/types'

function makeEvent(overrides: Partial<RawEvent>): RawEvent {
  return {
    time: '--:--', team: 'UCLA Bruins', cap_number: '6',
    player_name: 'test', action_detail: 'Goal',
    score: '1-0', quarter: 'Q1',
    game: 'UCLA Bruins VS SJSU Spartans',
    score_a: 1, score_b: 0,
    score_diff_raw: 1, score_diff_pre: 0,
    score_state: 'Tied', is_clutch: false,
    event_type: 'goal', is_penalty_attempt: false,
    ...overrides,
  }
}

describe('computeScoreTimeline', () => {
  it('returns UCLA score diff (score_a - score_b) for sjsu', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 0, score_b: 0, score_diff_pre: 0 }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 1, score_b: 0, score_diff_pre: 0 }),
    ]
    const result = computeScoreTimeline(events, 'sjsu')
    expect(result).toHaveLength(2)
    expect(result[0].scoreDiff).toBe(0)
    expect(result[1].scoreDiff).toBe(1)
  })

  it('returns UCLA score diff (score_b - score_a) for ucdavis', () => {
    const events: RawEvent[] = [
      makeEvent({
        game: 'UC Davis Aggies VS UCLA Bruins',
        score_a: 1, score_b: 0, score_diff_pre: 0,
      }),
    ]
    const result = computeScoreTimeline(events, 'ucdavis')
    expect(result[0].scoreDiff).toBe(-1) // UCLA is losing
  })

  it('filters out events with null score_diff_pre', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_diff_pre: null }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_diff_pre: 0 }),
    ]
    expect(computeScoreTimeline(events, 'sjsu')).toHaveLength(1)
  })

  it('filters to the requested game only', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_diff_pre: 0 }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_diff_pre: 0 }),
    ]
    expect(computeScoreTimeline(events, 'sjsu')).toHaveLength(1)
  })
})
```

- [ ] **Step 6: Run tests**

```bash
npm test
```
Expected: 7 tests pass, 0 fail.

- [ ] **Step 7: Commit**

```bash
git add src/types src/lib tests
git commit -m "feat: add TypeScript types, data parsers, and unit tests"
```

---

## Task 3: Zustand Store + Router + Page Stubs

**Files:**
- Create: `src/store/useAppStore.ts`
- Create: `src/router.tsx`
- Create: `src/App.tsx`
- Create: `src/main.tsx`
- Create: `src/pages/TournamentOverview.tsx` (stub)
- Create: `src/pages/GameView.tsx` (stub)
- Create: `src/pages/PlayerIndex.tsx` (stub)
- Create: `src/pages/PlayerProfile.tsx` (stub)
- Create: `src/pages/PlayByPlayExplorer.tsx` (stub)

- [ ] **Step 1: Write `src/store/useAppStore.ts`**

```typescript
import { create } from 'zustand'
import type { AppData, GameFilter } from '../types'

interface AppStore {
  data: AppData | null
  loading: boolean
  error: string | null
  gameFilter: GameFilter
  setData: (data: AppData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string) => void
  setGameFilter: (filter: GameFilter) => void
}

export const useAppStore = create<AppStore>(set => ({
  data: null,
  loading: true,
  error: null,
  gameFilter: 'all',
  setData: data => set({ data, loading: false, error: null }),
  setLoading: loading => set({ loading }),
  setError: error => set({ error, loading: false }),
  setGameFilter: gameFilter => set({ gameFilter }),
}))
```

- [ ] **Step 2: Write page stubs** (one file each)

`src/pages/GameView.tsx`:
```typescript
export default function GameView() {
  return <div className="p-8 text-muted">Game View — coming soon</div>
}
```

`src/pages/PlayerIndex.tsx`:
```typescript
export default function PlayerIndex() {
  return <div className="p-8 text-muted">Players — coming soon</div>
}
```

`src/pages/PlayerProfile.tsx`:
```typescript
export default function PlayerProfile() {
  return <div className="p-8 text-muted">Player Profile — coming soon</div>
}
```

`src/pages/PlayByPlayExplorer.tsx`:
```typescript
export default function PlayByPlayExplorer() {
  return <div className="p-8 text-muted">Play-by-Play Explorer — coming soon</div>
}
```

`src/pages/TournamentOverview.tsx`:
```typescript
export default function TournamentOverview() {
  return <div className="p-8 text-muted">Tournament Overview — in progress</div>
}
```

- [ ] **Step 3: Write `src/router.tsx`**

```typescript
import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import TournamentOverview from './pages/TournamentOverview'
import GameView from './pages/GameView'
import PlayerIndex from './pages/PlayerIndex'
import PlayerProfile from './pages/PlayerProfile'
import PlayByPlayExplorer from './pages/PlayByPlayExplorer'

export const router = createBrowserRouter(
  [
    {
      path: '/',
      element: <App />,
      children: [
        { index: true, element: <TournamentOverview /> },
        { path: 'game/:gameId', element: <GameView /> },
        { path: 'players', element: <PlayerIndex /> },
        { path: 'player/:name', element: <PlayerProfile /> },
        { path: 'play-by-play', element: <PlayByPlayExplorer /> },
      ],
    },
  ],
  { basename: '/stat_scraper' },
)
```

- [ ] **Step 4: Write `src/App.tsx`**

```typescript
import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import * as XLSX from 'xlsx'
import { parseWorkbook } from './lib/parseWorkbook'
import { useAppStore } from './store/useAppStore'
import LoadingScreen from './components/LoadingScreen'

export default function App() {
  const { loading, error, setData, setError } = useAppStore()

  useEffect(() => {
    fetch('/stat_scraper/data/PERFORMANCE_REPORT.xlsx')
      .then(res => {
        if (!res.ok) throw new Error(`Failed to fetch data file: ${res.status}`)
        return res.arrayBuffer()
      })
      .then(buf => {
        const wb = XLSX.read(buf, { type: 'array' })
        setData(parseWorkbook(wb))
      })
      .catch(err => setError(String(err)))
  }, [setData, setError])

  if (loading || error) return <LoadingScreen error={error} />
  return <Outlet />
}
```

- [ ] **Step 5: Write `src/components/LoadingScreen.tsx`**

```typescript
interface Props {
  error: string | null
}

export default function LoadingScreen({ error }: Props) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-bg">
      {error ? (
        <div className="text-center">
          <p className="text-red-400 font-bold mb-2">Failed to load data</p>
          <p className="text-muted text-sm">{error}</p>
        </div>
      ) : (
        <div className="text-center">
          <div className="text-gold text-xl font-bold mb-2">UCLA Water Polo</div>
          <p className="text-muted text-sm">Loading tournament data...</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6: Write `src/main.tsx`**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
```

- [ ] **Step 7: Delete generated boilerplate**

```bash
rm -f src/App.css src/assets/react.svg public/vite.svg
```

- [ ] **Step 8: Verify app loads without errors**

```bash
npm run dev
```
Open `http://localhost:5173/stat_scraper/`. Expected: loading spinner briefly, then "Tournament Overview — in progress" text. No console errors.

- [ ] **Step 9: Commit**

```bash
git add src
git commit -m "feat: add Zustand store, React Router, App shell, page stubs"
```

---

## Task 4: NavBar + FilterPills + HeroBar

**Files:**
- Create: `src/components/layout/NavBar.tsx`
- Create: `src/components/layout/FilterPills.tsx`
- Create: `src/components/layout/HeroBar.tsx`
- Modify: `src/pages/TournamentOverview.tsx`

- [ ] **Step 1: Write `src/components/layout/NavBar.tsx`**

```typescript
import { NavLink } from 'react-router-dom'

const TABS = [
  { label: 'Overview', to: '/' },
  { label: 'Games', to: '/game/ucdavis' },
  { label: 'Players', to: '/players' },
  { label: 'Play-by-Play', to: '/play-by-play' },
]

export default function NavBar() {
  return (
    <nav className="bg-ucla-blue h-12 flex items-center justify-between px-6 sticky top-0 z-50">
      <span className="text-gold font-extrabold text-sm tracking-wide">
        UCLA WATER POLO · Pacific Cup 2026
      </span>
      <div className="flex gap-1">
        {TABS.map(({ label, to }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                isActive
                  ? 'bg-white/20 text-white'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
```

- [ ] **Step 2: Write `src/components/layout/FilterPills.tsx`**

```typescript
import { useAppStore } from '../../store/useAppStore'
import type { GameFilter } from '../../types'

const PILLS: { label: string; value: GameFilter }[] = [
  { label: 'All Games', value: 'all' },
  { label: 'vs UC Davis', value: 'ucdavis' },
  { label: 'vs SJSU', value: 'sjsu' },
  { label: 'vs Stanford', value: 'stanford' },
]

export default function FilterPills() {
  const { gameFilter, setGameFilter } = useAppStore()

  return (
    <div className="bg-card-bg border-b border-border px-6 py-2 flex items-center gap-2">
      <span className="text-xs text-slate-500 uppercase tracking-wide mr-1">Filter</span>
      {PILLS.map(({ label, value }) => (
        <button
          key={value}
          onClick={() => setGameFilter(value)}
          className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${
            gameFilter === value
              ? 'bg-ucla-blue text-white border-ucla-blue'
              : 'bg-transparent text-muted border-border hover:border-ucla-blue hover:text-sky-300'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Write `src/components/layout/HeroBar.tsx`**

```typescript
import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'

const GAME_RESULTS = [
  { opp: 'UC Davis', score: 'W 14–7', win: true },
  { opp: 'SJSU', score: 'W 11–10', win: true },
  { opp: 'Stanford', score: 'L 11–12', win: false },
]

export default function HeroBar() {
  const data = useAppStore(s => s.data)
  const ucla = data?.teamMetrics.find(t => t.team === UCLA_TEAM)

  const stats = [
    { val: '2-1', lbl: 'Record' },
    { val: ucla?.goals_total ?? '—', lbl: 'UCLA Goals' },
    { val: ucla ? `${(ucla.shot_pct * 100).toFixed(1)}%` : '—', lbl: 'Shot %' },
    { val: ucla?.steals ?? '—', lbl: 'Steals' },
    { val: ucla?.saves ?? '—', lbl: 'Saves' },
    { val: ucla?.earned_exclusions ?? '—', lbl: 'Earned Excl.' },
  ]

  return (
    <div className="bg-gradient-to-r from-[#1e3a5f] to-card-bg px-6 py-4 flex items-center gap-8 border-b border-border flex-wrap">
      {stats.map(({ val, lbl }) => (
        <div key={lbl} className="text-center">
          <div className="text-2xl font-extrabold text-gold leading-none">{val}</div>
          <div className="text-[10px] text-muted uppercase tracking-wide mt-1">{lbl}</div>
        </div>
      ))}
      <div className="h-9 w-px bg-border mx-2" />
      <div className="flex gap-3">
        {GAME_RESULTS.map(({ opp, score, win }) => (
          <div key={opp} className="text-center">
            <div
              className={`text-xs font-bold px-2 py-0.5 rounded ${
                win ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'
              }`}
            >
              {score}
            </div>
            <div className="text-[9px] text-slate-500 mt-1">{opp}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Wire layout into TournamentOverview stub**

```typescript
import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'

export default function TournamentOverview() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <NavBar />
      <FilterPills />
      <HeroBar />
      <div className="max-w-5xl mx-auto p-6 text-muted">
        Leaderboard coming next...
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Visual check**

```bash
npm run dev
```
Open `http://localhost:5173/stat_scraper/`. Expected: blue nav bar, filter pills row, hero bar with real stats (36 goals, 40.9%, 31 steals, 25 saves, 21 earned excl). Clicking nav tabs navigates to stub pages.

- [ ] **Step 6: Commit**

```bash
git add src
git commit -m "feat: add NavBar, FilterPills, and HeroBar layout components"
```

---

## Task 5: Impact Leaderboard

**Files:**
- Create: `src/components/leaderboard/RoleBadge.tsx`
- Create: `src/components/leaderboard/ImpactLeaderboard.tsx`
- Modify: `src/pages/TournamentOverview.tsx`

- [ ] **Step 1: Write `src/components/leaderboard/RoleBadge.tsx`**

```typescript
const ROLE_STYLES: Record<string, string> = {
  'Primary Finisher': 'bg-blue-900/40 text-sky-300',
  'Leverage Creator (Draws Calls)': 'bg-purple-900/40 text-purple-300',
  'Disruptor (Defense/Transition)': 'bg-green-900/40 text-green-300',
  'Goalie Anchor': 'bg-amber-900/40 text-amber-300',
}
const DEFAULT_STYLE = 'bg-slate-800 text-slate-400'

const ROLE_LABELS: Record<string, string> = {
  'Primary Finisher': 'Finisher',
  'Leverage Creator (Draws Calls)': 'Leverage Creator',
  'Disruptor (Defense/Transition)': 'Disruptor',
  'Goalie Anchor': 'Goalie Anchor',
}

interface Props {
  role: string
}

export default function RoleBadge({ role }: Props) {
  const style = ROLE_STYLES[role] ?? DEFAULT_STYLE
  const label = ROLE_LABELS[role] ?? role
  return (
    <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${style}`}>
      {label}
    </span>
  )
}
```

- [ ] **Step 2: Write `src/components/leaderboard/ImpactLeaderboard.tsx`**

```typescript
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'
import RoleBadge from './RoleBadge'

export default function ImpactLeaderboard() {
  const data = useAppStore(s => s.data)
  const navigate = useNavigate()

  const players = (data?.playerSummaries ?? [])
    .filter(p => p.team === UCLA_TEAM)
    .sort((a, b) => b.impact - a.impact)

  const maxImpact = players[0]?.impact ?? 1

  return (
    <div className="bg-card-bg border border-border rounded-xl p-4">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Impact Leaderboard
        </span>
        <div className="flex-1 h-px bg-border" />
        <span className="text-[10px] text-slate-600">Click a player to view profile →</span>
      </div>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-border">
            {['#', 'Player', 'Impact', 'Percentile', 'Goals', 'Steals', 'Shot %'].map(h => (
              <th
                key={h}
                className={`text-[10px] font-semibold uppercase tracking-wide text-slate-500 pb-2 ${
                  h === 'Player' || h === '#' ? 'text-left' : 'text-right'
                }`}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {players.map((p, i) => (
            <tr
              key={p.player_name}
              onClick={() => navigate(`/player/${encodeURIComponent(p.player_name)}`)}
              className="cursor-pointer group hover:bg-slate-700/40 rounded transition-colors"
            >
              <td className="py-2 px-1 text-slate-500 text-xs font-bold text-center w-8">
                {i + 1}
              </td>
              <td className="py-2 px-2">
                <div className="text-sm font-semibold group-hover:text-sky-300 transition-colors">
                  {p.player_name}
                  <span className="text-slate-500 text-xs ml-1 font-normal">
                    #{p.cap_number ?? '—'}
                  </span>
                </div>
                <div className="flex gap-1 flex-wrap mt-1">
                  {p.roles.map(r => <RoleBadge key={r} role={r} />)}
                </div>
              </td>
              <td className="py-2 px-2 text-right text-lg font-extrabold text-gold w-16">
                {p.impact.toFixed(1)}
              </td>
              <td className="py-2 px-2 w-36">
                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-ucla-blue to-gold"
                    style={{ width: `${(p.impact / maxImpact) * 100}%` }}
                  />
                </div>
              </td>
              <td className="py-2 px-2 text-right text-xs text-slate-300 w-12">
                {p.goals || '—'}
              </td>
              <td className="py-2 px-2 text-right text-xs text-slate-300 w-12">
                {p.steals || '—'}
              </td>
              <td className="py-2 px-2 text-right text-xs text-slate-300 w-16">
                {p.shots > 0 ? `${(p.shot_pct * 100).toFixed(1)}%` : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

Note: `p.cap_number` doesn't exist on `PlayerSummary` — the cap number is in the Raw PBP, not the summary sheet. Replace the cap number display with `''` for now; it can be back-filled in a future pass by joining on player_name from rawEvents.

- [ ] **Step 3: Fix cap number — update the `<td>` for player name in ImpactLeaderboard.tsx**

Cap number isn't in the Player Roles sheet. Remove it from the display:
```typescript
// Replace this line:
<span className="text-slate-500 text-xs ml-1 font-normal">#{p.cap_number ?? '—'}</span>
// With nothing — just show the name
```

- [ ] **Step 4: Add leaderboard to TournamentOverview**

```typescript
import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'
import ImpactLeaderboard from '../components/leaderboard/ImpactLeaderboard'

export default function TournamentOverview() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <NavBar />
      <FilterPills />
      <HeroBar />
      <div className="max-w-5xl mx-auto p-6 flex flex-col gap-5">
        <ImpactLeaderboard />
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Visual check**

Open `http://localhost:5173/stat_scraper/`. Expected: leaderboard shows UCLA players ranked by impact score with gradient percentile bars and role badges. Hovering a row highlights it. Clicking navigates to `/player/ben%20larsen` (stub page).

- [ ] **Step 6: Commit**

```bash
git add src
git commit -m "feat: add Impact Leaderboard with role badges and percentile bars"
```

---

## Task 6: Shot Efficiency + Quarter Momentum Charts

**Files:**
- Create: `src/components/charts/ShotEfficiencyChart.tsx`
- Create: `src/components/charts/QuarterMomentumChart.tsx`
- Modify: `src/pages/TournamentOverview.tsx`

- [ ] **Step 1: Write `src/components/charts/ShotEfficiencyChart.tsx`**

```typescript
import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'

const OPP_ORDER = ['UC Davis Aggies', 'SJSU Spartans', 'Stanford Cardinal']

export default function ShotEfficiencyChart() {
  const data = useAppStore(s => s.data)
  const teams = data?.teamMetrics ?? []

  const ucla = teams.find(t => t.team === UCLA_TEAM)
  const opponents = OPP_ORDER.map(name => teams.find(t => t.team === name)).filter(Boolean)
  const allTeams = [
    { team: 'UCLA Bruins', shot_pct: ucla?.shot_pct ?? 0, isUcla: true },
    ...opponents.map(t => ({ team: t!.team, shot_pct: t!.shot_pct, isUcla: false })),
  ]

  const maxPct = Math.max(...allTeams.map(t => t.shot_pct))

  return (
    <div className="bg-card-bg border border-border rounded-xl p-4">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Shot Efficiency
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>
      <div className="flex flex-col gap-3">
        {allTeams.map(({ team, shot_pct, isUcla }) => (
          <div key={team}>
            <div className="flex justify-between items-baseline mb-1">
              <span className={`text-xs font-semibold ${isUcla ? 'text-sky-300' : 'text-muted'}`}>
                {team}
              </span>
              <span className={`text-sm font-bold ${isUcla ? 'text-gold' : 'text-slate-400'}`}>
                {(shot_pct * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2.5 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  isUcla
                    ? 'bg-gradient-to-r from-ucla-blue to-sky-400'
                    : shot_pct > (ucla?.shot_pct ?? 0)
                    ? 'bg-red-800'
                    : 'bg-slate-600'
                }`}
                style={{ width: `${(shot_pct / maxPct) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write `src/components/charts/QuarterMomentumChart.tsx`**

```typescript
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'

const QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']

export default function QuarterMomentumChart() {
  const data = useAppStore(s => s.data)
  const splits = data?.quarterSplits ?? []

  const uclaByQ = Object.fromEntries(
    QUARTERS.map(q => {
      const row = splits.find(r => r.team === UCLA_TEAM && r.quarter === q)
      return [q, row?.goals ?? 0]
    }),
  )

  // Average opponent goals per quarter (sum across all opp teams / 3 games)
  const oppByQ = Object.fromEntries(
    QUARTERS.map(q => {
      const oppRows = splits.filter(r => r.team !== UCLA_TEAM && r.quarter === q)
      const total = oppRows.reduce((sum, r) => sum + r.goals, 0)
      return [q, Math.round((total / 3) * 10) / 10]
    }),
  )

  const chartData = QUARTERS.map(q => ({
    quarter: q,
    UCLA: uclaByQ[q],
    Opponents: oppByQ[q],
  }))

  const maxGoals = Math.max(...chartData.flatMap(d => [d.UCLA, d.Opponents]))
  const bestQ = chartData.reduce((best, d) => (d.UCLA > best.UCLA ? d : best), chartData[0])

  return (
    <div className="bg-card-bg border border-border rounded-xl p-4">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Quarter Momentum · UCLA Goals
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={chartData} barCategoryGap="30%" barGap={2}>
          <XAxis
            dataKey="quarter"
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, maxGoals + 1]}
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={24}
          />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 6 }}
            labelStyle={{ color: '#94a3b8', fontSize: 11 }}
            itemStyle={{ fontSize: 11 }}
          />
          <Legend
            iconType="rect"
            iconSize={8}
            wrapperStyle={{ fontSize: 10, color: '#94a3b8' }}
          />
          <Bar dataKey="UCLA" name="UCLA" radius={[3, 3, 0, 0]}>
            {chartData.map(entry => (
              <Cell
                key={entry.quarter}
                fill={entry.quarter === bestQ.quarter ? '#FFD100' : '#2774AE'}
              />
            ))}
          </Bar>
          <Bar dataKey="Opponents" name="Opp. Avg" fill="#475569" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```

- [ ] **Step 3: Add both charts to TournamentOverview in a 2-column row**

```typescript
import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'
import ImpactLeaderboard from '../components/leaderboard/ImpactLeaderboard'
import ShotEfficiencyChart from '../components/charts/ShotEfficiencyChart'
import QuarterMomentumChart from '../components/charts/QuarterMomentumChart'

export default function TournamentOverview() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <NavBar />
      <FilterPills />
      <HeroBar />
      <div className="max-w-5xl mx-auto p-6 flex flex-col gap-5">
        <ImpactLeaderboard />
        <div className="grid grid-cols-2 gap-5">
          <ShotEfficiencyChart />
          <QuarterMomentumChart />
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Visual check**

Open `http://localhost:5173/stat_scraper/`. Expected: shot efficiency bars (UCLA highest in blue/sky, SJSU highlighted red since they out-shot UCLA, others gray). Quarter momentum grouped bar chart with Q3 gold-highlighted for UCLA.

- [ ] **Step 5: Commit**

```bash
git add src
git commit -m "feat: add Shot Efficiency and Quarter Momentum charts"
```

---

## Task 7: Game Cards + Score Timelines

**Files:**
- Create: `src/components/charts/GameCard.tsx`
- Modify: `src/pages/TournamentOverview.tsx`

- [ ] **Step 1: Write `src/components/charts/GameCard.tsx`**

```typescript
import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'
import { computeScoreTimeline } from '../../lib/computeScoreTimeline'
import type { GameId } from '../../types'
import { GAME_LABELS, GAME_NAMES, GAME_SCORES, UCLA_TEAM } from '../../types'

interface Props {
  gameId: GameId
}

export default function GameCard({ gameId }: Props) {
  const navigate = useNavigate()
  const data = useAppStore(s => s.data)
  const { uclaScore, oppScore, win } = GAME_SCORES[gameId]

  const timeline = data ? computeScoreTimeline(data.rawEvents, gameId) : []

  // Build SVG polyline points from score diff
  const W = 200
  const H = 32
  const mid = H / 2
  const maxAbs = Math.max(1, ...timeline.map(p => Math.abs(p.scoreDiff)))
  const points = timeline.length
    ? timeline
        .map((p, i) => {
          const x = (i / (timeline.length - 1)) * W
          const y = mid - (p.scoreDiff / maxAbs) * (mid - 4)
          return `${x.toFixed(1)},${y.toFixed(1)}`
        })
        .join(' ')
    : `0,${mid} ${W},${mid}`

  // Per-game UCLA stats from rawEvents — use GAME_NAMES for exact match
  const gameEvents = data?.rawEvents.filter(e => e.game === GAME_NAMES[gameId]) ?? []
  const uclaEvents = gameEvents.filter(e => e.team === UCLA_TEAM)
  const goals = uclaEvents.filter(e => e.event_type === 'goal' || e.event_type === 'goal_penalty').length
  const steals = uclaEvents.filter(e => e.event_type === 'steal').length
  const shots = uclaEvents.filter(e =>
    ['goal', 'goal_penalty', 'miss', 'miss_penalty'].includes(e.event_type)
  ).length
  const shotPct = shots > 0 ? ((goals / shots) * 100).toFixed(1) + '%' : '—'

  return (
    <div
      onClick={() => navigate(`/game/${gameId}`)}
      className="bg-dark-bg border border-border rounded-xl p-3 cursor-pointer hover:border-ucla-blue transition-colors group"
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="text-xs font-bold text-muted">{GAME_LABELS[gameId]}</div>
          <div className={`text-xl font-extrabold ${win ? 'text-green-400' : 'text-red-400'}`}>
            {uclaScore} – {oppScore}
          </div>
        </div>
        <span
          className={`text-xs font-bold px-2 py-0.5 rounded border ${
            win
              ? 'bg-green-900/20 text-green-400 border-green-900'
              : 'bg-red-900/20 text-red-400 border-red-900'
          }`}
        >
          {win ? 'W' : 'L'}
        </span>
      </div>

      {/* Score diff timeline */}
      <div className="rounded overflow-hidden mb-2">
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="h-8">
          <rect width={W} height={H} fill="#0f172a" />
          <line x1={0} y1={mid} x2={W} y2={mid} stroke="#334155" strokeWidth={1} />
          {['Q1', 'Q2', 'Q3', 'Q4'].map((_, i) => (
            <line
              key={i}
              x1={((i + 1) * W) / 4}
              y1={0}
              x2={((i + 1) * W) / 4}
              y2={H}
              stroke="#1e293b"
              strokeWidth={1}
            />
          ))}
          <polyline
            points={points}
            fill="none"
            stroke={win ? '#4ade80' : '#f87171'}
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Key stats */}
      <div className="flex gap-2 text-center">
        {[
          { v: shotPct, l: 'Shot %' },
          { v: steals, l: 'Steals' },
        ].map(({ v, l }) => (
          <div key={l} className="flex-1">
            <div className="text-xs font-bold text-gold">{v}</div>
            <div className="text-[9px] text-slate-500">{l}</div>
          </div>
        ))}
      </div>

      <div className="text-[9px] text-center text-slate-600 mt-2 group-hover:text-ucla-blue transition-colors">
        Click to view game →
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Add game cards section to TournamentOverview**

```typescript
import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'
import ImpactLeaderboard from '../components/leaderboard/ImpactLeaderboard'
import ShotEfficiencyChart from '../components/charts/ShotEfficiencyChart'
import QuarterMomentumChart from '../components/charts/QuarterMomentumChart'
import GameCard from '../components/charts/GameCard'
import type { GameId } from '../types'

export default function TournamentOverview() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <NavBar />
      <FilterPills />
      <HeroBar />
      <div className="max-w-5xl mx-auto p-6 flex flex-col gap-5">
        <ImpactLeaderboard />
        <div className="grid grid-cols-2 gap-5">
          <ShotEfficiencyChart />
          <QuarterMomentumChart />
        </div>

        {/* Game Score Timelines */}
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
              Game Score Timelines
            </span>
            <div className="flex-1 h-px bg-border" />
            <span className="text-[10px] text-slate-600">Click a card to view game →</span>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {(['ucdavis', 'sjsu', 'stanford'] as GameId[]).map(id => (
              <GameCard key={id} gameId={id} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Visual check**

Open `http://localhost:5173/stat_scraper/`. Expected: three game cards with inline SVG score diff lines (green for wins, red for Stanford loss), per-game shot% and steals stats, hover border effect. Clicking navigates to `/game/ucdavis` etc.

- [ ] **Step 4: Commit**

```bash
git add src
git commit -m "feat: add GameCard with SVG score timeline — Tournament Overview complete"
```

---

## Task 8: Deploy to GitHub Pages

**Files:**
- Modify: `.gitignore` (ensure `dist/` is excluded from main tracking)

- [ ] **Step 1: Verify production build succeeds**

```bash
npm run build
```
Expected: `dist/` created, no TypeScript errors, no Vite build errors.

- [ ] **Step 2: Preview build locally**

```bash
npm run preview
```
Open `http://localhost:4173/stat_scraper/`. Verify all sections render, data loads from xlsx, all navigation works.

- [ ] **Step 3: Deploy to GitHub Pages**

```bash
npm run deploy
```
Expected: `gh-pages` branch created/updated, terminal shows `Published`.

- [ ] **Step 4: Verify live URL**

Open `https://rhurst1029.github.io/stat_scraper/` in browser. Expected: full dashboard loads with real data.

- [ ] **Step 5: Commit anything uncommitted**

```bash
git add -A
git commit -m "feat: Pacific Cup Tournament Overview — Phase 1 complete and deployed"
```

---

## Phase 2–4 Stubs (Future Sessions)

These tasks are not part of today's session. They are documented here so the next session starts with a clear next step.

### Task 9 (Future): Game View Page
- Game Header (score, quarter W/L grid, shot%)
- Full-width Score Diff Timeline with Recharts `LineChart` + `ReferenceArea` for quarters
- Quarter Performance Grid (4 cards)
- Score State Table from `scoreStateSplits` filtered to game + opponent
- Per-Game Player Table computed from `rawEvents` filtered to game + UCLA

### Task 10 (Future): Player Profile Page
- Player header (name, roles, IPS) from `playerSummaries`
- Radar chart (6 axes) using Recharts `RadarChart`
- Per-game bar from `rawEvents` grouped by game
- Event feed from `rawEvents` filtered to player, grouped by game

### Task 11 (Future): Play-by-Play Explorer
- Filter sidebar (game/team/type/quarter/score state/player/clutch)
- Virtualized table with `react-window` `FixedSizeList`
- CSV export via `papaparse`

---

## Definition of Done (Phase 1)

- [ ] `npm run dev` shows full Tournament Overview with real data
- [ ] Hero bar stats match: 36 goals, 40.9%, 31 steals, 25 saves, 21 earned excl.
- [ ] Leaderboard shows ben larsen #1 (32.0), role badges visible
- [ ] Q3 bar is gold in Quarter Momentum chart
- [ ] Stanford game card shows red timeline + "L"
- [ ] Clicking a player row navigates to `/player/:name`
- [ ] Clicking a game card navigates to `/game/:gameId`
- [ ] `npm run deploy` publishes to `https://rhurst1029.github.io/stat_scraper/`
- [ ] Live URL loads and all sections visible
