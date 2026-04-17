# PROGRESS.md
Append-only session log. Never delete entries.

---

## Session: 2026-04-15

### What got done
- Refactored `6_8_scraper.py`: `get_play_by_play()` now takes a `url` directly and spins up its own driver internally (decoupled from `get_games`)
- Added popup dismissal logic (close-dialog-btn)
- Fixed quarter button detection: now filters `ng-star-inserted` elements by text (`1st Quarter`, etc.) instead of using the old `arrow-down` class
- Added team name parsing from raw innerHTML span tags
- Added `Game` column to exported DataFrame
- Export filename now lowercase, no index
- Added retry logic (3x) in `get_games` for resilience
- `__main__` now calls `get_play_by_play` directly with individual game URLs (bypassing `get_games` for now)

### State of codebase
Working and committable. Uncommitted changes exist in `6_8_scraper.py`. `get_games` is commented out in `__main__` — direct URL mode is the active path.

### Next step
Next: verify `get_play_by_play` runs end-to-end against the 3 URLs in `lst` and exports valid `.xlsx` files.

### Parking lot review
- `get_games` flow (schedule page → click dates → click games) is not currently tested with the new decoupled `get_play_by_play` signature — will need wiring update before re-enabling
- TWP scraper (`twp_scraper.py`) and constructor (`twp_constructor.py`) status unknown — not touched this session

### Emotional check-in
Not recorded.

---

## Session: 2026-04-16

### What got done
Shipped Phase 1 of the Pacific Cup Dashboard — Tournament Overview page deployed to GitHub Pages at https://rhurst1029.github.io/stat_scraper/. Eight-task plan executed via subagent-driven development with two-stage review (spec compliance → code quality) on each task.

- **Task 1**: Vite + React + TS scaffold with Tailwind, Recharts, Zustand, React Router, Vitest, SheetJS
- **Task 2**: TypeScript types + `parseWorkbook` (SheetJS → typed AppData) + `computeScoreTimeline` + 14 passing unit tests
- **Task 3**: Zustand store, React Router with basename `/stat_scraper`, App shell with xlsx fetch, LoadingScreen, page stubs
- **Task 4**: NavBar + FilterPills + HeroBar layout chrome (plus refactor to selector-based store access and derived HeroBar stats)
- **Task 5**: Impact Leaderboard with role badges, percentile bars, click-to-profile (plus negative/zero-impact bar math fix)
- **Task 6**: Shot Efficiency (Tailwind) + Quarter Momentum (Recharts) charts (plus refactor to derive opponent count from data + new `OPP_TEAMS` constant)
- **Task 7**: GameCards with inline SVG score-diff timelines and click-to-game navigation
- **Task 8**: Production build clean, preview verified locally, deployed to GitHub Pages via `npm run deploy`

Commits: `1d5bfd0` → `3c0a711` (17 ahead of origin/main).

### State of codebase
Working and deployed. Build is clean (tsc + Vite, 604 modules, 980 kB bundle / 310 kB gzip — dominated by SheetJS). 14/14 tests pass. `main` is 17 commits ahead of `origin/main` — not pushed to remote yet. `gh-pages` branch is published. `PARKING_LOT.md` has ~15 items surfaced during code reviews.

### Next step
Next: push `main` to `origin` so the source is on GitHub, then decide whether to start Phase 2 (Game View page) or work through the parking-lot polish pass (a11y, color tokens, aria-sort).

### Parking lot review
All items are in `PARKING_LOT.md`. Top candidates for a polish-pass session:
- Clickable-surface a11y (GameCard + ImpactLeaderboard row both use `<div/tr onClick>`)
- Shared `src/theme/colors.ts` for Recharts color constants
- `OPP_TEAMS` is now in types — could propagate to other places that still name teams inline

Scraper TODOs from prior session (verify `get_play_by_play` end-to-end, re-wire `get_games`) are still open and should be picked up in a dedicated scraper session.

### Emotional check-in
Not recorded.

---
