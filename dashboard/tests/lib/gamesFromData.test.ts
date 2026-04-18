import { describe, it, expect } from 'vitest'
import { extractGames } from '../../src/lib/gamesFromData'
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

describe('extractGames', () => {
  it('returns empty array for empty input', () => {
    expect(extractGames([])).toEqual([])
  })

  it('parses UCLA-first title (SJSU format)', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans' }),
    ]
    const result = extractGames(events)
    expect(result).toHaveLength(1)
    expect(result[0]).toMatchObject({
      title: 'UCLA Bruins VS SJSU Spartans',
      uclaIsScoreA: true,
      oppTeam: 'SJSU Spartans',
      gameId: 'sjsu',
      isLive: true,
    })
  })

  it('parses opp-first title (UC Davis format)', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UC Davis Aggies VS UCLA Bruins' }),
    ]
    const result = extractGames(events)
    expect(result[0]).toMatchObject({
      uclaIsScoreA: false,
      oppTeam: 'UC Davis Aggies',
      gameId: 'ucdavis',
    })
  })

  it('derives scores from the last event with valid score values', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 1, score_b: 0 }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 5, score_b: 4 }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans', score_a: 11, score_b: 10 }),
    ]
    const result = extractGames(events)
    expect(result[0].uclaScore).toBe(11)
    expect(result[0].oppScore).toBe(10)
  })

  it('handles multiple games in stable first-seen order', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UC Davis Aggies VS UCLA Bruins' }),
      makeEvent({ game: 'UCLA Bruins VS SJSU Spartans' }),
      makeEvent({ game: 'UC Davis Aggies VS UCLA Bruins' }),
      makeEvent({ game: 'UCLA Bruins VS Stanford Cardinal' }),
    ]
    const result = extractGames(events)
    expect(result.map(g => g.gameId)).toEqual(['ucdavis', 'sjsu', 'stanford'])
  })

  it('slugifies a novel opponent team when no canonical slug matches', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UCLA Bruins VS Cal Poly SLO' }),
    ]
    const result = extractGames(events)
    expect(result[0].gameId).toBe('calpolyslo')
    expect(result[0].oppTeam).toBe('Cal Poly SLO')
  })

  it('uclaScore assignment respects uclaIsScoreA', () => {
    const events: RawEvent[] = [
      makeEvent({ game: 'UC Davis Aggies VS UCLA Bruins', score_a: 7, score_b: 14 }),
    ]
    const result = extractGames(events)
    expect(result[0].uclaIsScoreA).toBe(false)
    expect(result[0].uclaScore).toBe(14)
    expect(result[0].oppScore).toBe(7)
  })
})