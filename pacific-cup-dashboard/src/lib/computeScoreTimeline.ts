import type { RawEvent, GameId } from '../types'
import { GAME_NAMES, UCLA_IS_SCORE_A } from '../types'

export interface TimelinePoint {
  eventIndex: number
  scoreDiff: number  // positive = UCLA leading
}

export function computeScoreTimeline(events: RawEvent[], gameId: GameId): TimelinePoint[] {
  const gameName = GAME_NAMES[gameId]
  const uclaIsA = UCLA_IS_SCORE_A[gameId]

  return events
    .filter(e => e.game === gameName && e.score_diff_pre != null)
    .map((e, i) => ({
      eventIndex: i,
      scoreDiff: uclaIsA ? e.score_a - e.score_b : e.score_b - e.score_a,
    }))
}
