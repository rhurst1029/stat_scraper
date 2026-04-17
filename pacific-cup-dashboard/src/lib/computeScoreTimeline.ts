import type { RawEvent, GameId } from '../types'
import { GAME_NAMES, UCLA_IS_SCORE_A } from '../types'

export interface TimelinePoint {
  eventIndex: number
  scoreDiff: number  // positive = UCLA leading
}

export function computeScoreTimeline(events: RawEvent[], gameId: GameId): TimelinePoint[] {
  const gameName = GAME_NAMES[gameId]
  const uclaIsA = UCLA_IS_SCORE_A[gameId]
  const SCORING_TYPES = new Set(['goal', 'goal_penalty'])

  const scoringEvents = events.filter(
    e => e.game === gameName && SCORING_TYPES.has(e.event_type)
  )

  const points: TimelinePoint[] = [{ eventIndex: 0, scoreDiff: 0 }]

  scoringEvents.forEach((e, i) => {
    points.push({
      eventIndex: i + 1,
      scoreDiff: uclaIsA ? e.score_a - e.score_b : e.score_b - e.score_a,
    })
  })

  return points
}
