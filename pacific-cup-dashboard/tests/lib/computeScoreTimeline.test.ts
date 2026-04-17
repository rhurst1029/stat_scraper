import { describe, it, expect } from 'vitest'
import { computeScoreTimeline } from '../../src/lib/computeScoreTimeline'
import type { RawEvent } from '../../src/types'

function makeEvent(overrides: Partial<RawEvent>): RawEvent {
  return {
    time: '--:--', team: 'UCLA Bruins', cap_number: '6',
    player_name: 'test', action_detail: 'Goal',
    score: '1-0', quarter: 'Q1',
    game: 'UCLA Bruins VS SJSU Spartans',
    score_a: 1, score_b: 0,
    score_diff_raw: 1, score_diff_pre: 0,
    score_state: 'Tied', is_clutch: false,
    event_type: 'goal', is_penalty_attempt: false,
    ...overrides,
  }
}

describe('computeScoreTimeline', () => {
  it('returns UCLA score diff as score_a - score_b for sjsu (UCLA is score_a)', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 0, score_b: 0, score_diff_pre: 0 }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 1, score_b: 0, score_diff_pre: 0 }),
    ]
    const result = computeScoreTimeline(events, 'sjsu')
    expect(result).toHaveLength(2)
    expect(result[0].scoreDiff).toBe(0)
    expect(result[1].scoreDiff).toBe(1)
  })

  it('returns UCLA score diff as score_b - score_a for ucdavis (UCLA is score_b)', () => {
    const events: RawEvent[] = [
      makeEvent({
        game: 'UC Davis Aggies VS UCLA Bruins',
        score_a: 1, score_b: 0, score_diff_pre: 0,
      }),
    ]
    const result = computeScoreTimeline(events, 'ucdavis')
    expect(result[0].scoreDiff).toBe(-1) // UCLA (score_b=0) minus UC Davis (score_a=1) = -1
  })

  it('filters out events with null score_diff_pre', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_diff_pre: null }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_diff_pre: 0 }),
    ]
    expect(computeScoreTimeline(events, 'sjsu')).toHaveLength(1)
  })

  it('filters to the requested game only', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_diff_pre: 0 }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_diff_pre: 0 }),
    ]
    expect(computeScoreTimeline(events, 'sjsu')).toHaveLength(1)
  })

  it('returns empty array when no matching events exist', () => {
    expect(computeScoreTimeline([], 'stanford')).toEqual([])
  })

  it('assigns sequential eventIndex values', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_diff_pre: 0 }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_diff_pre: 1 }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_diff_pre: 0 }),
    ]
    const result = computeScoreTimeline(events, 'stanford')
    expect(result.map(p => p.eventIndex)).toEqual([0, 1, 2])
  })
})
