import argparse
import sys
import time
from pathlib import Path

import pandas as pd

from build_performance_report import build_report, write_report_atomic


LIVE_URL = 'https://scores.6-8sports.com/scoreboard/games/20272dfe-423d-43c4-85bb-7079f40cbc26/play-by-play'
OUT_PATH = Path('dashboard/public/data/PERFORMANCE_REPORT.xlsx')
TARGET_INTERVAL_S = 15
OUR_TEAM = ' UCLA Bruins '


def _read_scraper_xlsx(path: Path) -> pd.DataFrame:
    import re as _re
    xls = pd.ExcelFile(path)
    preferred = [s for s in xls.sheet_names if _re.search(r'raw|play|log|data', s, _re.I)]
    sheet = preferred[0] if preferred else xls.sheet_names[0]
    return pd.read_excel(path, sheet_name=sheet)


def run_simulated(source_xlsx: Path, out_path: Path, interval_s: float) -> None:
    print(f'[simulate] source: {source_xlsx}')
    print(f'[simulate] output: {out_path}')
    print(f'[simulate] interval: {interval_s}s')
    poll = 0
    while True:
        poll += 1
        t0 = time.perf_counter()
        try:
            df_raw = _read_scraper_xlsx(source_xlsx)
            sheets = build_report(df_raw, our_team=OUR_TEAM)
            write_report_atomic(sheets, out_path)
            elapsed = time.perf_counter() - t0
            print(f'[poll {poll}] wrote {out_path} in {elapsed:.2f}s ({len(df_raw)} events)')
        except Exception as e:
            print(f'[poll {poll}] WARN: {e} — last-good preserved')
        time.sleep(max(0, interval_s - (time.perf_counter() - t0)))


def run_live(url: str, out_path: Path, interval_s: float) -> None:
    from scraper_core import launch_driver, scrape_play_by_play

    print(f'[live] url: {url}')
    print(f'[live] output: {out_path}')
    print(f'[live] target interval: {interval_s}s')

    driver = launch_driver()
    poll = 0
    try:
        while True:
            poll += 1
            t0 = time.perf_counter()
            try:
                df_raw = scrape_play_by_play(driver, url)
                if df_raw.empty:
                    print(f'[poll {poll}] WARN: empty scrape — last-good preserved')
                else:
                    sheets = build_report(df_raw, our_team=OUR_TEAM)
                    write_report_atomic(sheets, out_path)
                    elapsed = time.perf_counter() - t0
                    print(f'[poll {poll}] wrote {out_path} in {elapsed:.2f}s ({len(df_raw)} events)')
            except Exception as e:
                print(f'[poll {poll}] WARN: {e} — last-good preserved')
            time.sleep(max(0, interval_s - (time.perf_counter() - t0)))
    finally:
        print('[live] shutting down driver')
        driver.quit()


def main() -> None:
    ap = argparse.ArgumentParser(description='Live-polling pipeline for one water polo game.')
    ap.add_argument('--simulate', type=Path, default=None,
                    help='Path to a completed-game scraper xlsx. Skips Selenium; loops over the file.')
    ap.add_argument('--url', type=str, default=LIVE_URL, help='Live game URL.')
    ap.add_argument('--out', type=Path, default=OUT_PATH, help='Output xlsx path.')
    ap.add_argument('--interval', type=float, default=TARGET_INTERVAL_S, help='Target seconds between polls.')
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    try:
        if args.simulate:
            run_simulated(args.simulate, args.out, args.interval)
        else:
            run_live(args.url, args.out, args.interval)
    except KeyboardInterrupt:
        print('\n[exit] interrupted')
        sys.exit(0)


if __name__ == '__main__':
    main()
