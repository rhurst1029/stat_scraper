# TASKS.md
Current task list. Updated each session.

---

## Active Tasks

| Priority | Task | Notes |
|---|---|---|
| `[MUST]` | Test `get_play_by_play` end-to-end against the 3 URLs in `lst` | Verify `.xlsx` exports are valid and columns are correct |
| `[MUST]` | Re-wire `get_games` to pass URL to new `get_play_by_play(url, date)` signature | Currently broken — `get_games` passes `driver` (old signature) |
| `[SHOULD]` | Audit `twp_scraper.py` and `twp_constructor.py` — confirm still working | Not touched in recent sessions |
| `[SHOULD]` | Test full pipeline end-to-end: scrape → `.xlsx` → Tableau | Confirm Redshift/AWS downstream still compatible |
| `[NICE]` | Clean up duplicate `bun` entries in `~/.zshrc` | Minor, unrelated to project |

---

## Completed Tasks

- Refactored `get_play_by_play` to be self-contained (own driver, own URL) — 2026-04-15
- Fixed quarter button detection — 2026-04-15
- Added popup dismissal, team name parsing, `Game` column, retry logic — 2026-04-15
