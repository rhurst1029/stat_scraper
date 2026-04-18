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

- **Clickable-surface a11y (recurring)** — `ImpactLeaderboard` rows and `GameCard`s use `onClick` on non-interactive elements (`<tr>`, `<div>`). Not keyboard-reachable, not screen-reader announced, blocks middle-click/cmd-click "open in new tab." Polish pass: extract a shared `<ClickableCard>` wrapper with `role="button"`, `tabIndex={0}`, and Enter/Space key handlers — or wrap the primary label inside each in a React Router `<Link>`.

- **Duplicate `player_name` row key risk** — `ImpactLeaderboard` uses `p.player_name` as the React key. If the roster ever has two players with the same name, React will warn and row state could mix. Use composite key (e.g. `${team}-${name}-${i}`) if it ever matters.

- **`RoleBadge` two-maps drift risk** — `ROLE_STYLES` and `ROLE_LABELS` are separate objects. If they drift out of sync, unknown roles silently render verbose strings. Consider consolidating to `{ [role]: { label, style } }`.

- **`aria-sort` on Impact column header** — the leaderboard table is always sorted by Impact desc. Adding `aria-sort="descending"` on that header is a one-line a11y win for a polish pass.

- **NavBar Games tab target hardcoded** — `Games` tab always navigates to `/game/ucdavis` regardless of the current `gameFilter`. Could derive the target from `gameFilter` (or route to a `/games` index page) so clicking "Games" when SJSU is filtered lands on the SJSU game instead.

- **`FilterPills` aria-pressed** — toggle buttons lack `aria-pressed`, so screen-reader users can't tell which filter is active from color alone. Add `aria-pressed={gameFilter === value}` or promote to `role="radiogroup"` + `role="radio"`.

- **HeroBar gradient magic hex** — `from-[#1e3a5f]` is an inline arbitrary color while everything else uses theme tokens. Add a `focal-blue-dark` token in `tailwind.config.js` or swap for an existing token.

- **FilterPills hover token drift** — `hover:text-sky-300` uses the raw Tailwind palette while the rest of the file uses theme tokens. Minor inconsistency; consider a named token.

- **Recharts color constants duplication** — `QuarterMomentumChart` inlines hex values (`#FFD100`, `#2774AE`, `#475569`, `#334155`, etc.) because Recharts can't read Tailwind tokens. These overlap with `tailwind.config.js` colors. Extract to a `src/theme/colors.ts` module and import in both Tailwind config and Recharts call sites for a single source of truth.
