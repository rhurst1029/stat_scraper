# PARKING_LOT.md
Ideas, bugs, tangents, future work. Capture everything. Nothing gets lost here.

---

## Logged Items

- **`get_games` + `get_play_by_play` decoupling** — `get_games` still passes `driver` to `get_play_by_play` but the new signature takes `url`. Needs a URL-extraction step before the call. Not urgent while direct URL mode is active.

- **Playwright import unused** — `6_8_scraper.py` imports `playwright` at the top but never uses it. Can be removed when cleaning up.

- **OT/Shootout handling** — current quarter loop only handles Q1–Q4. No handling for overtime periods. Low priority unless a scraped game goes to OT.

- **TWP scraper status** — `twp_scraper.py` and `twp_constructor.py` haven't been touched in recent sessions. Unknown if they still work against current site structure.

- **AWS/Redshift schema compatibility** — added `Game` column to export. Confirm downstream Redshift table schema still matches.

- **`get_games` full re-enable** — once `get_play_by_play` is validated in direct URL mode, re-wire `get_games` and test the full schedule-scraping flow.
