import time

import numpy as np
import pandas as pd
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


COLS = ['Time', 'Team', 'Cap Number', 'Player Name', 'Action Detail', 'Score', 'Quarter']
QUARTER_LABELS = ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter']


def launch_driver():
    options = Options()
    ua = UserAgent()
    options.add_argument(f'user-agent={ua.random}')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def _dismiss_popup(driver) -> None:
    try:
        wait = WebDriverWait(driver, 2)
        popup = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'close-dialog-btn')))
        driver.execute_script('arguments[0].click();', popup)
        time.sleep(2)
    except Exception:
        pass


def _click_play_by_play_tab(driver) -> None:
    wait = WebDriverWait(driver, 10)
    tab = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Play-by-Play')))
    driver.execute_script('arguments[0].click();', tab)
    time.sleep(2)


def _parse_team_html(raw: str) -> str:
    return raw.split('="">')[-1].split('</span')[0]


def _build_game_name(teams) -> str:
    parts = [t.replace(' NL ', '').replace('/', '_').strip().split(' ') for t in teams]
    return '_VS_'.join(['_'.join(p) for p in parts]).replace('_', ' ')


def scrape_play_by_play(driver, url: str) -> pd.DataFrame:
    driver.get(url)
    time.sleep(3)
    _dismiss_popup(driver)
    _click_play_by_play_tab(driver)

    wait = WebDriverWait(driver, 10)
    buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'ng-star-inserted')))
    buttons = [b for b in buttons if b.text in QUARTER_LABELS]

    meta = pd.DataFrame(columns=COLS)

    for quarter, button in enumerate(buttons, start=1):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.5)
            driver.execute_script('arguments[0].click();', button)
            time.sleep(0.5)
        except Exception as e:
            print(f'Error opening quarter {quarter}: {str(e).split("Stacktrace:")[0]}')
            continue

        try:
            table = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[contains(@class, 'table acc-table ng-star-inserted')]")
            ))
        except Exception as e:
            print(f'Error finding table for quarter {quarter}: {str(e).split("Stacktrace:")[0]}')
            continue

        rows = []
        for tr in table.find_elements(By.TAG_NAME, 'tr'):
            rows.append([td.get_attribute('innerHTML') for td in tr.find_elements(By.TAG_NAME, 'td')])

        current = pd.DataFrame(rows, columns=COLS[:-1])
        current.dropna(axis=0, how='all', inplace=True)
        current.loc[:, 'Quarter'] = f'Q{quarter}'
        current.loc[:, 'Score'] = current.loc[:, 'Score'].replace('', np.nan)
        meta = pd.concat([meta, current], ignore_index=True)

    if meta.empty:
        return meta

    meta = meta[
        (~meta['Time'].astype(str).str.contains('finished</', na=False))
        & (~meta['Time'].astype(str).str.contains('started</', na=False))
    ]
    meta = meta.ffill()
    meta['Score'] = meta['Score'].fillna('0 - 0')
    meta.dropna(axis=0, how='any', inplace=True)
    meta['Team'] = [_parse_team_html(v) for v in meta['Team'].values]

    teams = meta['Team'].unique()
    if len(teams) > 0:
        meta['Game'] = _build_game_name(teams)

    return meta
