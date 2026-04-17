import * as XLSX from 'xlsx'
import type {
  AppData, PlayerSummary, TeamMetrics,
  QuarterSplit, ScoreStateSplit, RawEvent,
} from '../types'

function sheetToRows<T extends Record<string, unknown>>(
  wb: XLSX.WorkBook,
  sheetName: string,
): T[] {
  const ws = wb.Sheets[sheetName]
  if (!ws) throw new Error(`Sheet "${sheetName}" not found in workbook`)
  return XLSX.utils.sheet_to_json<T>(ws, { defval: null })
}

function parseRoles(raw: unknown): string[] {
  if (typeof raw !== 'string' || !raw) return []
  // Python list literal: "['Primary Finisher', 'Disruptor']"
  return raw
    .replace(/^\[|\]$/g, '')
    .split(',')
    .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
    .filter(Boolean)
}

export function parseWorkbook(wb: XLSX.WorkBook): AppData {
  const roleRows = sheetToRows(wb, 'Player Roles')
  const playerSummaries: PlayerSummary[] = roleRows.map(row => ({
    team: String(row.team ?? '').trim(),
    player_name: String(row.player_name ?? '').trim(),
    impact: Number(row.impact ?? 0),
    goals: Number(row.goals ?? 0),
    goals_pen: Number(row.goals_pen ?? 0),
    shots: Number(row.shots ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    non_pen_goals: Number(row.non_pen_goals ?? 0),
    non_pen_shots: Number(row.non_pen_shots ?? 0),
    non_pen_pct: Number(row.non_pen_pct ?? 0),
    steals: Number(row.steals ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    saves: Number(row.saves ?? 0),
    earned_excl: Number(row.earned_excl ?? 0),
    excluded: Number(row.excluded ?? 0),
    earned_pen: Number(row.earned_pen ?? 0),
    pen_committed: Number(row.pen_committed ?? 0),
    clutch_goals: Number(row.clutch_goals ?? 0),
    shots_per_goal: row.shots_per_goal != null ? Number(row.shots_per_goal) : null,
    roles: parseRoles(row.roles),
  }))

  const teamRows = sheetToRows(wb, 'Team Metrics')
  const teamMetrics: TeamMetrics[] = teamRows.map(row => ({
    team: String(row.team ?? '').trim(),
    goals_total: Number(row.goals_total ?? 0),
    shots_total: Number(row.shots_total ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    steals: Number(row.steals ?? 0),
    saves: Number(row.saves ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    earned_exclusions: Number(row.earned_exclusions ?? 0),
    earned_penalties: Number(row.earned_penalties ?? 0),
    penalty_goals: Number(row.penalty_goals ?? 0),
    penalty_pct: Number(row.penalty_pct ?? 0),
    pp_goals_tagged: Number(row.pp_goals_tagged ?? 0),
  }))

  const qRows = sheetToRows(wb, 'Quarter Splits')
  const quarterSplits: QuarterSplit[] = qRows.map(row => ({
    team: String(row.team ?? '').trim(),
    quarter: String(row.quarter ?? ''),
    goals: Number(row.goals ?? 0),
    shots: Number(row.shots ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    steals: Number(row.steals ?? 0),
    saves: Number(row.saves ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    earned_excl: Number(row.earned_excl ?? 0),
    earned_pen: Number(row.earned_pen ?? 0),
    clutch_goals: Number(row.clutch_goals ?? 0),
  }))

  const ssRows = sheetToRows(wb, 'Score State Splits')
  const scoreStateSplits: ScoreStateSplit[] = ssRows.map(row => ({
    team: String(row.team ?? '').trim(),
    score_state: String(row.score_state ?? ''),
    goals: Number(row.goals ?? 0),
    shots: Number(row.shots ?? 0),
    shot_pct: Number(row.shot_pct ?? 0),
    steals: Number(row.steals ?? 0),
    saves: Number(row.saves ?? 0),
    field_blocks: Number(row.field_blocks ?? 0),
    earned_excl: Number(row.earned_excl ?? 0),
    earned_pen: Number(row.earned_pen ?? 0),
    clutch_goals: Number(row.clutch_goals ?? 0),
  }))

  const pbpRows = sheetToRows(wb, 'Raw Play-by-Play')
  const rawEvents: RawEvent[] = pbpRows.map(row => ({
    time: String(row.time ?? ''),
    team: String(row.team ?? '').trim(),
    cap_number: String(row.cap_number ?? '').trim(),
    player_name: String(row.player_name ?? '').trim(),
    action_detail: String(row.action_detail ?? ''),
    score: String(row.score ?? ''),
    quarter: String(row.quarter ?? ''),
    game: String(row.game ?? ''),
    score_a: Number(row.score_a ?? 0),
    score_b: Number(row.score_b ?? 0),
    score_diff_raw: Number(row.score_diff_raw ?? 0),
    score_diff_pre: row.score_diff_pre != null ? Number(row.score_diff_pre) : null,
    score_state: String(row.score_state ?? ''),
    is_clutch: row.is_clutch === true || row.is_clutch === 1 || row.is_clutch === 'TRUE',
    event_type: String(row.event_type ?? ''),
    is_penalty_attempt: row.is_penalty_attempt === true || row.is_penalty_attempt === 1 || row.is_penalty_attempt === 'TRUE',
  }))

  return { playerSummaries, teamMetrics, quarterSplits, scoreStateSplits, rawEvents }
}
