import os
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


SCORE_IS_POST_EVENT = True
OUR_TEAM = ' UCLA Bruins '
CLUTCH_QUARTERS = {'Q4'}
CLUTCH_MARGIN = 1
PENALTY_WINDOW_EVENTS = 2

ACTION_PATTERNS = {
    'goal_penalty': [r'^goal\s*-\s*penalty$'],
    'goal': [r'^goal(?!ie)'],
    'assist': [r'^assist'],
    'offensive': [r'^offensive'],
    'turnover': [r'^turnover$'],
    'miss': [r'^missed\s*shot$'],
    'save': [r'^save$'],
    'steal': [r'^steal$'],
    'field_block': [r'^field\s*block$'],
    'earned_exclusion': [r'^earned\s*exclusion$'],
    'excluded': [r'^exclusion$'],
    'earned_penalty': [r'^earned\s*penalty$'],
    'penalty_committed': [r'^penalty$'],
    'sprint_won': [r'^[Ss]print\s'],
}

IMPACT_WEIGHTS = {
    'goal': 3.0,
    'goal_penalty': 1,
    'miss': -2.5,
    'miss_penalty': -0.9,
    'steal': 2.0,
    'field_block': 2,
    'save': 1,
    'earned_exclusion': 1.3,
    'earned_penalty': 1.6,
    'excluded': -1.0,
    'penalty_committed': -1.3,
    'offensive': -2,
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {c: str(c).strip().lower() for c in df.columns}
    df = df.rename(columns=col_map).copy()
    df = df.rename(columns={
        'cap number': 'cap_number',
        'player name': 'player_name',
        'action detail': 'action_detail',
    })
    return df


def _parse_score(s):
    if pd.isna(s):
        return (np.nan, np.nan)
    m = re.search(r'(\d+)\s*[-:]\s*(\d+)', str(s))
    if not m:
        return (np.nan, np.nan)
    return (int(m.group(1)), int(m.group(2)))


def _canon_event(action) -> str:
    if pd.isna(action):
        return 'other'
    a = str(action).strip().lower()
    for k, pats in ACTION_PATTERNS.items():
        for p in pats:
            if re.search(p, a):
                return k
    return 'other'


def _score_state(d) -> str:
    if pd.isna(d):
        return 'Unknown'
    if d > 0:
        return 'Leading'
    if d < 0:
        return 'Trailing'
    return 'Tied'


def _team_metrics(df: pd.DataFrame, team: str) -> dict:
    d = df[df['team'] == team].copy() if 'team' in df.columns else df.copy()
    goals = d['event_type'].isin(['goal', 'goal_penalty']).sum()
    goals_pen = (d['event_type'] == 'goal_penalty').sum()
    shots = d['event_type'].isin(['goal', 'goal_penalty', 'miss', 'miss_penalty']).sum()
    non_pen_goals = (d['event_type'] == 'goal').sum()
    non_pen_shots = d['event_type'].isin(['goal', 'miss']).sum()
    steals = (d['event_type'] == 'steal').sum()
    saves = (d['event_type'] == 'save').sum()
    field_blocks = (d['event_type'] == 'field_block').sum()
    earned_excl = (d['event_type'] == 'earned_exclusion').sum()
    earned_pen = (d['event_type'] == 'earned_penalty').sum()
    pen_att = d['event_type'].isin(['goal_penalty', 'miss_penalty']).sum()
    pp_goals = d['action_detail'].astype(str).str.contains(r'6v5|7v6', case=False, na=False).sum()
    return {
        'team': team,
        'goals_total': int(goals),
        'shots_total': int(shots),
        'shot_pct': float(goals / shots) if shots else np.nan,
        'non_pen_goals': int(non_pen_goals),
        'non_pen_shots': int(non_pen_shots),
        'non_pen_shot_pct': float(non_pen_goals / non_pen_shots) if non_pen_shots else np.nan,
        'steals': int(steals),
        'saves': int(saves),
        'field_blocks': int(field_blocks),
        'earned_exclusions': int(earned_excl),
        'earned_penalties': int(earned_pen),
        'penalty_attempts_detected': int(pen_att),
        'penalty_goals': int(goals_pen),
        'penalty_pct': float(goals_pen / pen_att) if pen_att else np.nan,
        'pp_goals_tagged': int(pp_goals),
    }


def _split_summary(df: pd.DataFrame, by_cols: list) -> pd.DataFrame:
    g = df.groupby(by_cols, dropna=False)
    out = g.apply(lambda d: pd.Series({
        'goals': d['event_type'].isin(['goal', 'goal_penalty']).sum(),
        'shots': d['event_type'].isin(['goal', 'goal_penalty', 'miss', 'miss_penalty']).sum(),
        'shot_pct': (d['event_type'].isin(['goal', 'goal_penalty']).sum() /
                     max(1, d['event_type'].isin(['goal', 'goal_penalty', 'miss', 'miss_penalty']).sum())),
        'steals': (d['event_type'] == 'steal').sum(),
        'saves': (d['event_type'] == 'save').sum(),
        'field_blocks': (d['event_type'] == 'field_block').sum(),
        'earned_excl': (d['event_type'] == 'earned_exclusion').sum(),
        'earned_pen': (d['event_type'] == 'earned_penalty').sum(),
        'clutch_goals': (d['is_clutch'] & d['event_type'].isin(['goal', 'goal_penalty'])).sum(),
    }))
    return out.reset_index()


def _player_summary(df: pd.DataFrame) -> pd.DataFrame:
    if 'player_name' not in df.columns:
        return pd.DataFrame()
    d = df.copy()
    d['w'] = d['event_type'].map(IMPACT_WEIGHTS).fillna(0.0)
    g = d.groupby(['team', 'player_name'], dropna=False)
    out = g.apply(lambda x: pd.Series({
        'impact': x['w'].sum(),
        'goals': x['event_type'].isin(['goal', 'goal_penalty']).sum(),
        'goals_pen': (x['event_type'] == 'goal_penalty').sum(),
        'shots': x['event_type'].isin(['goal', 'goal_penalty', 'miss', 'miss_penalty']).sum(),
        'shot_pct': (x['event_type'].isin(['goal', 'goal_penalty']).sum() /
                     max(1, x['event_type'].isin(['goal', 'goal_penalty', 'miss', 'miss_penalty']).sum())),
        'non_pen_goals': (x['event_type'] == 'goal').sum(),
        'non_pen_shots': x['event_type'].isin(['goal', 'miss']).sum(),
        'non_pen_pct': ((x['event_type'] == 'goal').sum() /
                        max(1, x['event_type'].isin(['goal', 'miss']).sum())),
        'steals': (x['event_type'] == 'steal').sum(),
        'field_blocks': (x['event_type'] == 'field_block').sum(),
        'saves': (x['event_type'] == 'save').sum(),
        'earned_excl': (x['event_type'] == 'earned_exclusion').sum(),
        'excluded': (x['event_type'] == 'excluded').sum(),
        'earned_pen': (x['event_type'] == 'earned_penalty').sum(),
        'pen_committed': (x['event_type'] == 'penalty_committed').sum(),
        'clutch_goals': (x['is_clutch'] & x['event_type'].isin(['goal', 'goal_penalty'])).sum(),
    }))
    out = out.reset_index()
    out['shots_per_goal'] = out['shots'] / out['goals'].replace(0, np.nan)
    return out.sort_values(['team', 'impact'], ascending=[True, False])


def _assign_roles(row) -> list:
    roles = []
    if row['goals'] >= 5 and row['non_pen_pct'] >= 0.4:
        roles.append('Primary Finisher')
    if row['shots'] >= 14 and row['shot_pct'] < 0.35:
        roles.append('Volume Shooter (Needs Selection)')
    if row['earned_excl'] + row['earned_pen'] >= 2:
        roles.append('Leverage Creator (Draws Calls)')
    if row['steals'] + row['field_blocks'] >= 6:
        roles.append('Disruptor (Defense/Transition)')
    if row['clutch_goals'] >= 1:
        roles.append('Clutch Contributor')
    if row['saves'] >= 3:
        roles.append('Goalie Anchor')
    if not roles:
        roles.append('Role Player')
    return roles


def _definitions_df() -> pd.DataFrame:
    return pd.DataFrame([
        ('IMPACT WEIGHTS', '', ''),
        ('goal', '+3.0', 'Field goal (non-penalty). Highest-value positive event.'),
        ('goal_penalty', '+1.0', 'Penalty goal. Scored from the 5m spot. Counted separately.'),
        ('miss', '-2.5', 'Non-penalty shot that did not result in a goal.'),
        ('miss_penalty', '-0.9', 'Penalty attempt that missed. Lighter penalty than a field miss.'),
        ('steal', '+2.0', 'Won the ball from an opponent. Positive transition event.'),
        ('field_block', '+2.0', 'Blocked an opponent shot in open play.'),
        ('save', '+1.0', 'Goalkeeper save. Prevents a goal.'),
        ('earned_exclusion', '+1.3', 'Drew a 20-second exclusion against an opponent.'),
        ('earned_penalty', '+1.6', 'Drew a penalty (5m shot) against an opponent.'),
        ('excluded', '-1.0', 'Committed a foul resulting in your own 20-second exclusion.'),
        ('penalty_committed', '-1.3', 'Committed a foul resulting in a 5m penalty shot against you.'),
        ('offensive', '-2.0', 'Offensive foul / turnover. Surrenders possession.'),
        ('', '', ''),
        ('PLAYER SUMMARY COLUMNS', '', ''),
        ('team', '—', 'Team name as recorded in the play-by-play log.'),
        ('player_name', '—', 'Player name as recorded in the log.'),
        ('impact', 'weighted sum', 'Sum of all event weights for this player. Primary ranking metric.'),
        ('goals', 'count', 'Total goals (field + penalty).'),
        ('goals_pen', 'count', 'Penalty goals only.'),
        ('shots', 'count', 'Total shots attempted (goals + misses, field + penalty).'),
        ('shot_pct', '%', 'Goals ÷ total shots. Overall shooting efficiency.'),
        ('non_pen_goals', 'count', 'Field goals only (excludes penalty goals).'),
        ('non_pen_shots', 'count', 'Field shot attempts only (excludes penalty attempts).'),
        ('non_pen_pct', '%', 'Non-penalty goals ÷ non-penalty shots. True field shooting %.'),
        ('steals', 'count', 'Steals recorded.'),
        ('field_blocks', 'count', 'Field blocks recorded.'),
        ('saves', 'count', 'Goalkeeper saves.'),
        ('earned_excl', 'count', 'Exclusions drawn (opponent was excluded).'),
        ('excluded', 'count', 'Times the player was excluded (20-sec penalty).'),
        ('earned_pen', 'count', 'Penalties drawn (opponent commits 5m foul).'),
        ('pen_committed', 'count', 'Penalties committed (player caused 5m foul on self team).'),
        ('clutch_goals', 'count', 'Goals scored in clutch moments (Q4 or later, score within ±2).'),
        ('shots_per_goal', 'ratio', 'Shots needed per goal. Lower = more efficient.'),
        ('', '', ''),
        ('ROLE PROFILE DEFINITIONS', '', ''),
        ('Primary Finisher', 'goals ≥ 5 AND non_pen_pct ≥ 40%', 'High-volume, high-efficiency scorer.'),
        ('Volume Shooter (Needs Selection)', 'shots ≥ 14 AND shot_pct < 35%', 'Takes many shots but converts poorly — consider shot selection.'),
        ('Leverage Creator (Draws Calls)', 'earned_excl + earned_pen ≥ 2', 'Regularly earns power-play and penalty opportunities for the team.'),
        ('Disruptor (Defense/Transition)', 'steals + field_blocks ≥ 6', 'High defensive impact; generates transition opportunities.'),
        ('Clutch Contributor', 'clutch_goals ≥ 1', 'Scores when the game is on the line.'),
        ('Goalie Anchor', 'saves ≥ 3', 'Goalkeeper with meaningful save volume.'),
        ('Role Player', '(none of the above)', 'Contributes but does not meet a specialist threshold.'),
        ('', '', ''),
        ('TEAM / SPLIT COLUMNS', '', ''),
        ('goals_total', 'count', 'Total goals scored by the team.'),
        ('shots_total', 'count', 'Total shots attempted.'),
        ('shot_pct', '%', 'Overall team shooting %.'),
        ('non_pen_goals', 'count', 'Field goals (no penalties).'),
        ('non_pen_shots', 'count', 'Field shots (no penalties).'),
        ('non_pen_shot_pct', '%', 'Non-penalty team shooting %.'),
        ('steals', 'count', 'Total steals.'),
        ('saves', 'count', 'Total saves (goalie).'),
        ('field_blocks', 'count', 'Total field blocks.'),
        ('earned_exclusions', 'count', 'Total exclusions drawn.'),
        ('earned_penalties', 'count', 'Total penalties drawn.'),
        ('penalty_attempts_detected', 'count', 'Penalty attempts detected (goal + miss_penalty).'),
        ('penalty_goals', 'count', 'Penalty goals scored.'),
        ('penalty_pct', '%', 'Penalty conversion rate.'),
        ('pp_goals_tagged', 'count', 'Power-play goals heuristically tagged (6v5 / 7v6 in log).'),
        ('score_state', 'category', 'Team score state at event time: Leading / Trailing / Tied / Unknown.'),
        ('clutch_goals', 'count', 'Goals scored in clutch situations (Q4, score ≤ ±2).'),
    ], columns=['Term', 'Value / Unit', 'Description'])


def build_report(
    df_raw: pd.DataFrame,
    our_team: str = OUR_TEAM,
    our_team_is_score_a: Optional[bool] = None,
) -> dict:
    df = _normalize_columns(df_raw)

    if our_team_is_score_a is None:
        first_game = df['game'].iloc[0] if 'game' in df.columns and len(df) else ''
        our_team_is_score_a = str(first_game).startswith(our_team.strip())

    score_parsed = df.get('score', pd.Series([np.nan] * len(df))).apply(_parse_score)
    df['score_a'] = score_parsed.apply(lambda x: x[0])
    df['score_b'] = score_parsed.apply(lambda x: x[1])

    def _score_diff_row(row):
        a, b = row['score_a'], row['score_b']
        if pd.isna(a) or pd.isna(b):
            return np.nan
        diff = a - b
        return diff if our_team_is_score_a else -diff

    df['score_diff_raw'] = df.apply(_score_diff_row, axis=1)
    df['score_diff_pre'] = df['score_diff_raw'].shift(1) if SCORE_IS_POST_EVENT else df['score_diff_raw']
    df['score_state'] = df['score_diff_pre'].apply(_score_state)
    df['is_clutch'] = (
        df.get('quarter', pd.Series([np.nan] * len(df))).apply(lambda q: q in CLUTCH_QUARTERS)
        & df['score_diff_pre'].abs().le(CLUTCH_MARGIN)
    )

    df['event_type'] = df.get('action_detail', pd.Series([np.nan] * len(df))).apply(_canon_event)

    df['is_penalty_attempt'] = False
    df.loc[df['event_type'] == 'goal_penalty', 'is_penalty_attempt'] = True
    earned_pen_idx = df.index[df['event_type'] == 'earned_penalty'].tolist()
    for i in earned_pen_idx:
        team_i = df.at[i, 'team'] if 'team' in df.columns else None
        q_i = df.at[i, 'quarter'] if 'quarter' in df.columns else None
        for j in range(i + 1, min(i + 1 + PENALTY_WINDOW_EVENTS, len(df))):
            if q_i is not None and 'quarter' in df.columns and df.at[j, 'quarter'] != q_i:
                break
            if team_i is not None and 'team' in df.columns and df.at[j, 'team'] != team_i:
                continue
            if df.at[j, 'event_type'] == 'miss':
                df.at[j, 'is_penalty_attempt'] = True
                df.at[j, 'event_type'] = 'miss_penalty'
                break

    teams = list(df.get('team', pd.Series(dtype='object')).dropna().astype(str).unique()) if 'team' in df.columns else []
    team_list = teams if teams else [our_team]
    tm = pd.DataFrame([_team_metrics(df, t) for t in team_list])

    quarter_splits = (_split_summary(df, ['team', 'quarter'])
                      if 'team' in df.columns and 'quarter' in df.columns else pd.DataFrame())
    scorestate_splits = (_split_summary(df, ['team', 'score_state'])
                         if 'team' in df.columns else pd.DataFrame())

    ps = _player_summary(df)
    ps = ps[ps['team'] == our_team].copy() if not ps.empty else ps

    if not ps.empty:
        roles_df = ps.copy()
        roles_df['roles'] = roles_df.apply(_assign_roles, axis=1)
    else:
        roles_df = pd.DataFrame()

    raw_export_cols = [c for c in df.columns if c not in ('__sheet__', 'w')]
    raw_pbp = df[raw_export_cols].copy()

    return {
        'Definitions': _definitions_df(),
        'Team Metrics': tm,
        'Quarter Splits': quarter_splits,
        'Score State Splits': scorestate_splits,
        'Player Summary': ps,
        'Player Roles': roles_df,
        'Raw Play-by-Play': raw_pbp,
    }


def build_report_from_scraper_xlsx(
    path: Path,
    our_team: str = OUR_TEAM,
) -> dict:
    xls = pd.ExcelFile(path)
    preferred = [s for s in xls.sheet_names if re.search(r'raw|play|log|data', s, re.I)]
    sheet = preferred[0] if preferred else xls.sheet_names[0]
    df_raw = pd.read_excel(path, sheet_name=sheet)
    return build_report(df_raw, our_team=our_team)


def write_report_atomic(sheets: dict, out_path: Path) -> Path:
    out_path = Path(out_path)
    tmp_path = out_path.with_suffix(out_path.suffix + '.tmp')
    with pd.ExcelWriter(tmp_path, engine='openpyxl') as writer:
        for name, df in sheets.items():
            if df is None or df.empty:
                continue
            df.to_excel(writer, sheet_name=name, index=False)
    os.replace(tmp_path, out_path)
    return out_path
