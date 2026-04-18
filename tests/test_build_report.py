import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from build_performance_report import (
    ACTION_PATTERNS,
    IMPACT_WEIGHTS,
    build_report,
    build_report_from_scraper_xlsx,
)


FIXTURE = ROOT / 'ucla_bruins_vs_sjsu_spartans_20260415.xlsx'


EXPECTED_SHEETS = {
    'Definitions', 'Team Metrics', 'Quarter Splits', 'Score State Splits',
    'Player Summary', 'Player Roles', 'Raw Play-by-Play',
}


def _synth_row(**overrides):
    base = {
        'Time': '--:--',
        'Team': ' UCLA Bruins ',
        'Cap Number': '6',
        'Player Name': 'test',
        'Action Detail': 'Goal',
        'Score': '0 - 0',
        'Quarter': 'Q1',
        'Game': 'UCLA Bruins VS SJSU Spartans',
    }
    base.update(overrides)
    return base


def test_report_has_all_7_sheets():
    report = build_report_from_scraper_xlsx(FIXTURE)
    assert set(report.keys()) == EXPECTED_SHEETS


def test_score_diff_pre_shifted_correctly():
    report = build_report_from_scraper_xlsx(FIXTURE)
    raw = report['Raw Play-by-Play']
    scored = raw[raw['score_diff_raw'].notna()].reset_index(drop=True)
    assert pd.isna(scored.loc[0, 'score_diff_pre'])
    assert scored.loc[1, 'score_diff_pre'] == scored.loc[0, 'score_diff_raw']


def test_ucla_is_score_a_auto_detect():
    report = build_report_from_scraper_xlsx(FIXTURE)
    raw = report['Raw Play-by-Play']
    assert raw['game'].iloc[0] == 'UCLA Bruins VS SJSU Spartans'
    scored = raw[raw['score_a'].notna() & raw['score_b'].notna()]
    row = scored.iloc[0]
    expected = row['score_a'] - row['score_b']
    assert row['score_diff_raw'] == expected


def test_is_clutch_only_q4_within_margin():
    rows = [
        _synth_row(Quarter='Q4', Score='1 - 0'),
        _synth_row(Quarter='Q4', Score='2 - 0'),
        _synth_row(Quarter='Q4', Score='2 - 1'),
        _synth_row(Quarter='Q3', Score='1 - 1'),
    ]
    df = pd.DataFrame(rows)
    report = build_report(df)
    raw = report['Raw Play-by-Play']
    # row 0: score_diff_pre NaN → not clutch
    assert raw.iloc[0]['is_clutch'] == False
    # row 1: score_diff_pre = 1 (from row 0), Q4 → clutch
    assert raw.iloc[1]['is_clutch'] == True
    # row 2: score_diff_pre = 2, Q4, |2| > 1 → not clutch
    assert raw.iloc[2]['is_clutch'] == False
    # row 3: Q3 → not clutch regardless
    assert raw.iloc[3]['is_clutch'] == False


def test_miss_penalty_rewrite():
    rows = [
        _synth_row(**{'Action Detail': 'Earned Penalty'}),
        _synth_row(**{'Action Detail': 'Missed Shot'}),
    ]
    df = pd.DataFrame(rows)
    report = build_report(df)
    raw = report['Raw Play-by-Play']
    assert raw.iloc[0]['event_type'] == 'earned_penalty'
    assert raw.iloc[1]['event_type'] == 'miss_penalty'
    assert raw.iloc[1]['is_penalty_attempt'] == True


@pytest.mark.parametrize('action_detail,expected_type', [
    ('Goal', 'goal'),
    ('Goal - Penalty', 'goal_penalty'),
    ('Missed Shot', 'miss'),
    ('Steal', 'steal'),
    ('Save', 'save'),
    ('Field Block', 'field_block'),
    ('Earned Exclusion', 'earned_exclusion'),
    ('Exclusion', 'excluded'),
    ('Earned Penalty', 'earned_penalty'),
    ('Penalty', 'penalty_committed'),
    ('Turnover', 'turnover'),
    ('Offensive Foul', 'offensive'),
    ('Sprint Won', 'sprint_won'),
    ('Assist', 'assist'),
])
def test_event_type_patterns(action_detail, expected_type):
    df = pd.DataFrame([_synth_row(**{'Action Detail': action_detail})])
    report = build_report(df)
    raw = report['Raw Play-by-Play']
    assert raw.iloc[0]['event_type'] == expected_type


def test_player_impact_sum_matches_formula():
    # one UCLA player: 2 goals, 1 miss, 1 steal
    # expected impact = 2*3.0 + 1*(-2.5) + 1*2.0 = 6 - 2.5 + 2 = 5.5
    rows = [
        _synth_row(**{'Player Name': 'ace', 'Action Detail': 'Goal'}),
        _synth_row(**{'Player Name': 'ace', 'Action Detail': 'Goal'}),
        _synth_row(**{'Player Name': 'ace', 'Action Detail': 'Missed Shot'}),
        _synth_row(**{'Player Name': 'ace', 'Action Detail': 'Steal'}),
    ]
    df = pd.DataFrame(rows)
    report = build_report(df)
    ps = report['Player Summary']
    ace = ps[ps['player_name'] == 'ace'].iloc[0]
    expected = 2 * IMPACT_WEIGHTS['goal'] + IMPACT_WEIGHTS['miss'] + IMPACT_WEIGHTS['steal']
    assert ace['impact'] == pytest.approx(expected)


def test_team_metrics_present_for_all_unique_teams():
    report = build_report_from_scraper_xlsx(FIXTURE)
    tm = report['Team Metrics']
    raw = report['Raw Play-by-Play']
    unique_teams = set(raw['team'].dropna().unique())
    assert set(tm['team']) == unique_teams
