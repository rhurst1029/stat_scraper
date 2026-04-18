import { describe, it, expect } from 'vitest'
import { computeScoreTimeline } from '../../src/lib/computeScoreTimeline'
import type { LiveGame } from '../../src/lib/gamesFromData'
import type { RawEvent } from '../../src/types'

function makeEvent(overrides: Partial<RawEvent>): RawEvent {
  return {
    time: '--:--', team: 'UCLA Bruins', cap_number: '6',
    player_name: 'test', action_detail: 'Goal - Natural',
    score: '1-0', quarter: 'Q1',
    game: 'UCLA Bruins VS SJSU Spartans',
    score_a: 1, score_b: 0,
    score_diff_raw: 1, score_diff_pre: 0,
    score_state: 'Leading', is_clutch: false,
    event_type: 'goal', is_penalty_attempt: false,
    ...overrides,
  }
}

function makeGame(overrides: Partial<LiveGame>): LiveGame {
  return {
    gameId: 'sjsu',
    title: 'UCLA Bruins VS SJSU Spartans',
    uclaIsScoreA: true,
    isLive: false,
    uclaScore: 0,
    oppScore: 0,
    oppTeam: 'SJSU Spartans',
    ...overrides,
  }
}

describe('computeScoreTimeline', () => {
  it('always starts with an opening 0-0 point', () => {
    const result = computeScoreTimeline([], makeGame({}))
    expect(result).toHaveLength(1)
    expect(result[0]).toEqual({ eventIndex: 0, scoreDiff: 0 })
  })

  it('computes scoreDiff as score_a - score_b when UCLA is score_a (SJSU)', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 1, score_b: 0 }),
    ]
    const result = computeScoreTimeline(events, makeGame({}))
    expect(result).toHaveLength(2)
    expect(result[1].scoreDiff).toBe(1)
  })

  it('computes scoreDiff as score_b - score_a when UCLA is score_b (UC Davis)', () => {
    const game = makeGame({
      gameId: 'ucdavis',
      title: 'UC Davis Aggies VS UCLA Bruins',
      uclaIsScoreA: false,
      oppTeam: 'UC Davis Aggies',
    })
    const events: RawEvent[] = [
      makeEvent({
        game: 'UC Davis Aggies VS UCLA Bruins',
        score_a: 1, score_b: 2,
        event_type: 'goal',
      }),
    ]
    const result = computeScoreTimeline(events, game)
    expect(result[1].scoreDiff).toBe(1) // UCLA (score_b=2) - UC Davis (score_a=1) = 1
  })

  it('computes negative scoreDiff when UCLA is trailing', () => {
    const game = makeGame({
      gameId: 'stanford',
      title: 'UCLA Bruins VS Stanford Cardinal',
      oppTeam: 'Stanford Cardinal',
    })
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_a: 0, score_b: 1, event_type: 'goal' }),
    ]
    const result = computeScoreTimeline(events, game)
    expect(result[1].scoreDiff).toBe(-1)
  })

  it('filters out non-scoring events (steals, exclusions, sprints)', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', event_type: 'steal' }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', event_type: 'goal', score_a: 1, score_b: 0 }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', event_type: 'sprint_won' }),
    ]
    const result = computeScoreTimeline(events, makeGame({}))
    expect(result).toHaveLength(2)
    expect(result[1].scoreDiff).toBe(1)
  })

  it('includes goal_penalty events', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', event_type: 'goal_penalty', score_a: 1, score_b: 0 }),
    ]
    const result = computeScoreTimeline(events, makeGame({}))
    expect(result).toHaveLength(2)
  })

  it('filters to the requested game only', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 1, score_b: 0 }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_a: 0, score_b: 1, event_type: 'goal' }),
    ]
    const stanfordGame = makeGame({
      gameId: 'stanford',
      title: 'UCLA Bruins VS Stanford Cardinal',
      oppTeam: 'Stanford Cardinal',
    })
    expect(computeScoreTimeline(events, makeGame({}))).toHaveLength(2)
    expect(computeScoreTimeline(events, stanfordGame)).toHaveLength(2)
  })

  it('assigns sequential eventIndex values starting at 0', () => {
    const game = makeGame({
      gameId: 'stanford',
      title: 'UCLA Bruins VS Stanford Cardinal',
      oppTeam: 'Stanford Cardinal',
    })
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_a: 1, score_b: 0, event_type: 'goal' }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal', score_a: 2, score_b: 0, event_type: 'goal' }),
    ]
    const result = computeScoreTimeline(events, game)
    expect(result.map(p => p.eventIndex)).toEqual([0, 1, 2])
  })
})
