import type { RawEvent } from '../types'
import { FOCAL_TEAM } from '../types'

export interface LiveGame {
  gameId: string
  title: string
  focalIsScoreA: boolean
  isLive: boolean
  focalScore: number
  oppScore: number
  oppTeam: string
}

const CANONICAL_SLUGS = ['ucdavis', 'sjsu', 'stanford'] as const

function slugify(oppTeam: string): string {
  const compact = oppTeam.toLowerCase().replaceAll(' ', '')
  for (const slug of CANONICAL_SLUGS) {
    if (compact.startsWith(slug)) return slug
  }
  return oppTeam.toLowerCase().replace(/[^a-z0-9]/g, '')
}

export function extractGames(rawEvents: RawEvent[]): LiveGame[] {
  const titles: string[] = []
  const eventsByTitle = new Map<string, RawEvent[]>()

  for (const e of rawEvents) {
    if (!eventsByTitle.has(e.game)) {
      titles.push(e.game)
      eventsByTitle.set(e.game, [])
    }
    eventsByTitle.get(e.game)!.push(e)
  }

  return titles.map(title => {
    const focalIsScoreA = title.startsWith(FOCAL_TEAM)
    const [firstHalf, secondHalf] = title.split(' VS ')
    const oppTeam = (focalIsScoreA ? secondHalf : firstHalf).trim()
    const gameId = slugify(oppTeam)

    const events = eventsByTitle.get(title)!
    let lastA = 0
    let lastB = 0
    for (let i = events.length - 1; i >= 0; i--) {
      const ev = events[i]
      if (!Number.isNaN(ev.score_a) && !Number.isNaN(ev.score_b)) {
        lastA = ev.score_a
        lastB = ev.score_b
        break
      }
    }

    return {
      gameId,
      title,
      focalIsScoreA,
      // TODO: detect end-of-game (Q4 + no events for N seconds) to flip isLive=false; out of scope for v1.
      isLive: true,
      focalScore: focalIsScoreA ? lastA : lastB,
      oppScore: focalIsScoreA ? lastB : lastA,
      oppTeam,
    }
  })
}
