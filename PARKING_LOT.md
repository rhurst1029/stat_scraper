# PARKING_LOT.md
Ideas, bugs, tangents, future work. Capture everything. Nothing gets lost here.

---

## Logged Items

- **`get_games` + `get_play_by_play` decoupling** — `get_games` still passes `driver` to `get_play_by_play` but the new signature takes `url`. Needs a URL-extraction step before the call. Not urgent while direct URL mode is active.

- **Playwright import unused** — `6_8_scraper.py` imports `playwright` at the top but never uses it. Can be removed when cleaning up.

- **OT/Shootout handling** — current quarter loop only handles Q1–Q4. No handling for overtime periods. Low priority unless a scraped game goes to OT.

- **TWP scraper status** — `twp_scraper.py` and `twp_constructor.py` haven't been touched in recent sessions. Unknown if they still work against current site structure.

- **AWS/Redshift schema compatibility** — added `Game` column to export. Confirm downstream Redshift table schema still matches.

- **`parseRoles` comma-in-label edge case** — the Python list literal parser splits on all commas, so a role name containing a comma (e.g., `'Transition, Counter'`) would break silently. Current data has no such roles, but worth hardening with a proper parser if role names ever change.

- **`eventIndex` naming in `computeScoreTimeline`** — `eventIndex` is the sequential position within the filtered scoring-events result, not a reference into the original `rawEvents` array. If a future chart needs to look up the source event by index, this won't work. Rename to `pointIndex` or store a reference to the source event if cross-referencing is needed.

- **`AppData` flat shape forces repeated filter logic** — all five arrays in `AppData` are mixed across games and teams. Every component filters in place. If performance becomes a concern (unlikely for 553 events), consider pre-indexing by game at parse time.

- **`score` string field in `RawEvent`** — kept as a display string (`"1-0"`, `"0 - 0"`) alongside structured `score_a`/`score_b`. If it's unused by components, remove it from the type and parser in a cleanup pass.

- **`get_games` full re-enable** — once `get_play_by_play` is validated in direct URL mode, re-wire `get_games` and test the full schedule-scraping flow.
