import { describe, it, expect } from 'vitest'
import { parseWorkbook } from '../../src/lib/parseWorkbook'
import * as XLSX from 'xlsx'

function makeWorkbook(sheets: Record<string, unknown[]>): XLSX.WorkBook {
  const wb = XLSX.utils.book_new()
  for (const [name, data] of Object.entries(sheets)) {
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), name)
  }
  return wb
}

const EMPTY_SHEETS = {
  'Team Metrics': [],
  'Quarter Splits': [],
  'Score State Splits': [],
  'Raw Play-by-Play': [],
}

describe('parseWorkbook', () => {
  it('parses Player Roles into PlayerSummary with roles array', () => {
    const wb = makeWorkbook({
      'Player Roles': [{
        team: ' UCLA Bruins ',
        player_name: 'ben larsen',
        impact: 32,
        goals: 9, goals_pen: 0, shots: 14, shot_pct: 0.643,
        non_pen_goals: 9, non_pen_shots: 14, non_pen_pct: 0.643,
        steals: 7, field_blocks: 2, saves: 0,
        earned_excl: 5, excluded: 3, earned_pen: 0, pen_committed: 0,
        clutch_goals: 0, shots_per_goal: 1.55,
        roles: "['Primary Finisher', 'Disruptor (Defense/Transition)']",
      }],
      ...EMPTY_SHEETS,
    })

    const data = parseWorkbook(wb)
    expect(data.playerSummaries).toHaveLength(1)
    const p = data.playerSummaries[0]
    expect(p.team).toBe('UCLA Bruins')
    expect(p.player_name).toBe('ben larsen')
    expect(p.impact).toBe(32)
    expect(p.roles).toEqual(['Primary Finisher', 'Disruptor (Defense/Transition)'])
  })

  it('trims whitespace from team names', () => {
    const wb = makeWorkbook({
      'Player Roles': [{ team: '  UCLA Bruins  ', player_name: 'test', impact: 0, goals: 0, goals_pen: 0, shots: 0, shot_pct: 0, non_pen_goals: 0, non_pen_shots: 0, non_pen_pct: 0, steals: 0, field_blocks: 0, saves: 0, earned_excl: 0, excluded: 0, earned_pen: 0, pen_committed: 0, clutch_goals: 0, shots_per_goal: null, roles: null }],
      ...EMPTY_SHEETS,
    })
    expect(parseWorkbook(wb).playerSummaries[0].team).toBe('UCLA Bruins')
  })

  it('handles missing roles gracefully', () => {
    const wb = makeWorkbook({
      'Player Roles': [{ team: ' UCLA Bruins ', player_name: 'Test Player', impact: 0, goals: 0, goals_pen: 0, shots: 0, shot_pct: 0, non_pen_goals: 0, non_pen_shots: 0, non_pen_pct: 0, steals: 0, field_blocks: 0, saves: 0, earned_excl: 0, excluded: 0, earned_pen: 0, pen_committed: 0, clutch_goals: 0, shots_per_goal: null, roles: null }],
      ...EMPTY_SHEETS,
    })
    expect(parseWorkbook(wb).playerSummaries[0].roles).toEqual([])
  })

  it('sets shots_per_goal to null when not present', () => {
    const wb = makeWorkbook({
      'Player Roles': [{ team: ' UCLA Bruins ', player_name: 'GK', impact: 10, goals: 0, goals_pen: 0, shots: 0, shot_pct: 0, non_pen_goals: 0, non_pen_shots: 0, non_pen_pct: 0, steals: 0, field_blocks: 0, saves: 10, earned_excl: 0, excluded: 0, earned_pen: 0, pen_committed: 0, clutch_goals: 0, shots_per_goal: null, roles: null }],
      ...EMPTY_SHEETS,
    })
    expect(parseWorkbook(wb).playerSummaries[0].shots_per_goal).toBeNull()
  })

  it('throws if a required sheet is missing', () => {
    const wb = XLSX.utils.book_new()
    expect(() => parseWorkbook(wb)).toThrow('Sheet "Player Roles" not found')
  })

  it('parses Raw Play-by-Play events with score_diff_pre null preserved', () => {
    const wb = makeWorkbook({
      'Player Roles': [],
      'Team Metrics': [],
      'Quarter Splits': [],
      'Score State Splits': [],
      'Raw Play-by-Play': [
        { time: '--:--', team: ' UCLA Bruins ', cap_number: ' 6 ', player_name: 'ben larsen', action_detail: 'Sprint (winner)', score: '0 - 0', quarter: 'Q1', game: 'UCLA Bruins VS SJSU Spartans', score_a: 0, score_b: 0, score_diff_raw: 0, score_diff_pre: null, score_state: 'Unknown', is_clutch: false, event_type: 'sprint_won', is_penalty_attempt: false },
        { time: '6:12', team: ' UCLA Bruins ', cap_number: ' 11 ', player_name: "Hayden O'Hare", action_detail: 'Goal - Counter', score: '0-1', quarter: 'Q1', game: 'UCLA Bruins VS SJSU Spartans', score_a: 1, score_b: 0, score_diff_raw: 1, score_diff_pre: 0, score_state: 'Tied', is_clutch: false, event_type: 'goal', is_penalty_attempt: false },
      ],
    })
    const data = parseWorkbook(wb)
    expect(data.rawEvents).toHaveLength(2)
    expect(data.rawEvents[0].score_diff_pre).toBeNull()
    expect(data.rawEvents[1].score_diff_pre).toBe(0)
    expect(data.rawEvents[0].team).toBe('UCLA Bruins') // trimmed
  })
})
