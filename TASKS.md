# TASKS.md
Current task list. Updated each session.

---

## Active Tasks

| Priority | Task | Notes |
|---|---|---|
| `[MUST]` | Push `main` to `origin` | 17 commits ahead of remote — Phase 1 work is local only on `main` (but `gh-pages` branch is live) |
| `[SHOULD]` | Phase 2: Game View page (`/game/:gameId`) | Score diff timeline, quarter grid, score state table, per-game player impact — see plan Task 9 stub |
| `[SHOULD]` | Polish pass: clickable-surface a11y | `GameCard` + `ImpactLeaderboard` row-click need keyboard support |
| `[SHOULD]` | Test `get_play_by_play` end-to-end against the 3 URLs in `lst` | Verify `.xlsx` exports are valid and columns are correct |
| `[SHOULD]` | Re-wire `get_games` to pass URL to new `get_play_by_play(url, date)` signature | Currently broken — `get_games` passes `driver` (old signature) |
| `[NICE]` | Phase 3: Player Profile page (`/player/:name`) | Radar chart, per-game bar, event feed |
| `[NICE]` | Phase 4: Play-by-Play Explorer | Virtualized filter table + CSV export |
| `[NICE]` | Extract `src/theme/colors.ts` for Recharts constants | See parking lot |
| `[NICE]` | Audit `twp_scraper.py` and `twp_constructor.py` — confirm still working | Not touched in recent sessions |
| `[NICE]` | Test full pipeline end-to-end: scrape → `.xlsx` → Tableau | Confirm Redshift/AWS downstream still compatible |
| `[NICE]` | Clean up duplicate `bun` entries in `~/.zshrc` | Minor, unrelated to project |

---

## Completed Tasks

- **Pacific Cup Dashboard Phase 1 (Tournament Overview) — deployed to GitHub Pages** — 2026-04-16
- Refactored `get_play_by_play` to be self-contained (own driver, own URL) — 2026-04-15
- Fixed quarter button detection — 2026-04-15
- Added popup dismissal, team name parsing, `Game` column, retry logic — 2026-04-15
