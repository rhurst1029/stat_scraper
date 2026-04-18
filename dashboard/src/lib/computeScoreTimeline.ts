import type { RawEvent } from '../types'
import type { LiveGame } from './gamesFromData'

export interface TimelinePoint {
  eventIndex: number
  scoreDiff: number  // positive = UCLA leading
}

export function computeScoreTimeline(events: RawEvent[], game: LiveGame): TimelinePoint[] {
  const SCORING_TYPES = new Set(['goal', 'goal_penalty'])

  const scoringEvents = events.filter(
    e => e.game === game.title && SCORING_TYPES.has(e.event_type)
  )

  const points: TimelinePoint[] = [{ eventIndex: 0, scoreDiff: 0 }]

  scoringEvents.forEach((e, i) => {
    points.push({
      eventIndex: i + 1,
      scoreDiff: game.uclaIsScoreA ? e.score_a - e.score_b : e.score_b - e.score_a,
    })
  })

  return points
}
