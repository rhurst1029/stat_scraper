# Live Dashboard — Orchestration Plan

> **This is the master spec. Read it first.** It describes how the 4 task specs
> (01–04) combine into a working live view, who does what, branching strategy,
> and the cross-cutting rules every implementing agent must follow.

---

## Goal

Deliver §12 of `CLAUDE_DESIGN_LIVE_DASHBOARD_PROMPT.md` — a working `/live`
route with polling, staleness detection, `LiveHero`, `EventFeed`, and
`rollingMomentum()` (with test) — running against the simulated poller:

```bash
python live_poller.py --simulate ucla_bruins_vs_sjsu_spartans_20260415.xlsx --interval 5
```

The coach-grade user story: open `http://localhost:5173/stat_scraper/live`,
watch score + quarter + most-recent-3 events + staleness badge, see new events
animate into the feed every 5 s. That's the whole first-session acceptance test.

---

## Dependency Graph

```
  main (baseline commit: uncommitted work + push)
    │
    ├── feat/live-01-polling-infra   (Task 1 — polling + /live route)
    │        │
    ├── feat/live-02-metrics         (Task 2 — liveMetrics.ts + tests)
    │        │
    │   [01 and 02 merge to main — phase A complete]
    │        │
    ├── feat/live-03-hero            (Task 3 — LiveHero.tsx)  [from main after 01+02 merged]
    └── feat/live-04-event-feed      (Task 4 — EventFeed.tsx) [from main after 01+02 merged]
             │
       [03 and 04 merge to main — phase B complete]
```

**Phase A (parallel):** Task 1 + Task 2. Zero file overlap.
**Phase B (parallel):** Task 3 + Task 4. Both depend on A being merged.

---

## Agent assignments

| Task | Implementer | Reviewer | Consultant (when needed) |
|---|---|---|---|
| 01 Polling + route | `frontend-developer` agent | `superpowers:code-reviewer` | `claude-code-guide` (Vite/Vitest specifics) |
| 02 liveMetrics lib | `frontend-developer` agent | `superpowers:code-reviewer` | `claude-code-guide` (TDD patterns) |
| 03 LiveHero | `frontend-developer` agent | `superpowers:code-reviewer` | `claude-code-guide` (React animation) |
| 04 EventFeed | `frontend-developer` agent | `superpowers:code-reviewer` | `claude-code-guide` (React list animation / virtualization) |

The orchestrator (me) spawns each implementer agent with that task's `.md` file
as the prompt, waits for completion, spawns the code-reviewer on that branch,
fixes any blocking findings, then opens the PR.

---

## Branching + merge contract

Every implementer agent MUST:

1. Start on a clean working tree — branch from `main` (after baseline commit).
2. Branch name: exactly as specified in the task file (`feat/live-0N-...`).
3. Commit atomically — one commit per logical change, conventional commit
   messages (`feat:`, `test:`, `refactor:`, `docs:`).
4. **Do not merge the branch.** Stop after the last commit and report back.
5. **Do not push.** The orchestrator pushes after code review passes.
6. **Do not modify files outside the task's stated scope** — log any needed
   side changes to `PARKING_LOT.md` instead (repo convention, `CLAUDE.md`
   line 193).

Every code-reviewer invocation:

- Input: the branch name, the task's `.md` file, and the PR template.
- Output: either ✅ APPROVED or a list of blocking findings tagged BLOCKING or
  SUGGESTION. Only BLOCKING findings prevent push.
- If findings are BLOCKING, the orchestrator loops back to the implementer
  with the review text as the next task input.

Every PR:

- Target: `main` on `origin` (confirm origin is pushed first).
- Title: `feat(live): <one-line summary>`.
- Body: uses the PR template in §7 of the task file.
- One PR per branch. Squash-merge (preserves linear history).

---

## Cross-cutting rules (every task must follow)

From `dashboard/CLAUDE.md` §11 — these are canonical:

1. **Selector-based Zustand access.** `useAppStore(s => s.data)`, never
   `const { data } = useAppStore()`.
2. **Derive from canonical sources.** Don't hardcode UCLA-specific strings —
   use `UCLA_TEAM`, `UCLA_IS_SCORE_A` from `src/types/index.ts`. The live
   view does **not** rely on `GAME_IDS` / `GAME_SCORES` / `GAME_NAMES`
   because those are tournament-completed constants; in live mode the
   opponent is discovered from the data.
3. **Divide-by-zero guards everywhere.** `Math.max(1, x)` or `Math.max(0.0001, x)`
   on any width / ratio math.
4. **TDD for `src/lib/*.ts`.** Every exported function needs a Vitest test
   in `tests/lib/`. Chart/UI components do not require unit tests.
5. **Dark-theme Tailwind tokens only.** Use `bg-dark-bg`, `bg-card-bg`,
   `border-border`, `text-muted`, `text-ucla-blue`, `text-gold`. No inline
   hex outside Recharts. Recharts hex values go in
   `src/theme/colors.ts` (Task 1 creates this if absent).
6. **No new top-level dependencies** without logging rationale in
   `DECISIONS.md`. `framer-motion` is pre-approved if animation requires it;
   `react-window` pre-approved for event feed virtualization.

From repo root `CLAUDE.md`:

7. **Evidence-first completion.** Each task must cite actual output — test
   run, screenshot, or `npm run build` result — before reporting done.
8. **Parking-lot discipline.** If a task surfaces a side issue, append it to
   `PARKING_LOT.md`, do not chase it.

---

## Prerequisites (BLOCKS all tasks until done)

These are the orchestrator's responsibility before any agent is spawned:

1. **Baseline commit on main.** Current working tree has ~15 modifications
   and ~7 untracked files (scraper refactors, `gamesFromData.ts`,
   `build_performance_report.py`, etc.). Either:
   - Commit them as a `chore: baseline for live dashboard work` commit, OR
   - Split into logical commits (preferred — scraper refactor is its own
     concern from dashboard untracked).
2. **Push `main` to `origin`.** Currently 17 commits ahead. PRs need a remote
   target.
3. **Start dev server.** `npm run dev` in `dashboard/`, leave running — each
   task verifies against the same live server.
4. **Start simulated poller.** `python live_poller.py --simulate
   ucla_bruins_vs_sjsu_spartans_20260415.xlsx --interval 5` in another
   terminal, leave running.

---

## Done when

- All 4 branches merged to `origin/main`.
- `PROGRESS.md` has a new session entry describing what shipped.
- `TASKS.md` marks the first-session scope complete.
- `PARKING_LOT.md` has any surfaced tangents logged.
- `http://localhost:5173/stat_scraper/live` shows a working live dashboard
  against the simulated poller, with score, quarter, polyline, staleness
  badge, momentum card, and an animated event feed.
- Bundle size is within budget (≤ +40 kB gzipped over Phase 1's 310 kB).
