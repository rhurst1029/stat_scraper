export interface PlayerSummary {
  team: string
  player_name: string
  impact: number
  goals: number
  goals_pen: number
  shots: number
  shot_pct: number
  non_pen_goals: number
  non_pen_shots: number
  non_pen_pct: number
  steals: number
  field_blocks: number
  saves: number
  earned_excl: number
  excluded: number
  earned_pen: number
  pen_committed: number
  clutch_goals: number
  shots_per_goal: number | null
  roles: string[]
}

export interface TeamMetrics {
  team: string
  goals_total: number
  shots_total: number
  shot_pct: number
  steals: number
  saves: number
  field_blocks: number
  earned_exclusions: number
  earned_penalties: number
  penalty_goals: number
  penalty_pct: number
  pp_goals_tagged: number
}

export interface QuarterSplit {
  team: string
  quarter: string
  goals: number
  shots: number
  shot_pct: number
  steals: number
  saves: number
  field_blocks: number
  earned_excl: number
  earned_pen: number
  clutch_goals: number
}

export interface ScoreStateSplit {
  team: string
  score_state: string
  goals: number
  shots: number
  shot_pct: number
  steals: number
  saves: number
  field_blocks: number
  earned_excl: number
  earned_pen: number
  clutch_goals: number
}

export interface RawEvent {
  time: string
  team: string
  cap_number: string
  player_name: string
  action_detail: string
  score: string
  quarter: string
  game: string
  score_a: number
  score_b: number
  score_diff_raw: number
  score_diff_pre: number | null
  score_state: string
  is_clutch: boolean
  event_type: string
  is_penalty_attempt: boolean
}

export interface AppData {
  playerSummaries: PlayerSummary[]
  teamMetrics: TeamMetrics[]
  quarterSplits: QuarterSplit[]
  scoreStateSplits: ScoreStateSplit[]
  rawEvents: RawEvent[]
}

export type GameId = 'ucdavis' | 'sjsu' | 'stanford'
export type GameFilter = 'all' | GameId

// Exact game name strings as they appear in the `game` column of Raw PBP
export const GAME_NAMES: Record<GameId, string> = {
  ucdavis: 'UC Davis Aggies VS UCLA Bruins',
  sjsu: 'UCLA Bruins VS SJSU Spartans',
  stanford: 'UCLA Bruins VS Stanford Cardinal',
}

export const GAME_LABELS: Record<GameId, string> = {
  ucdavis: 'vs UC Davis',
  sjsu: 'vs SJSU',
  stanford: 'vs Stanford',
}

// UCLA is score_b for ucdavis (listed second); score_a for the others
export const UCLA_IS_SCORE_A: Record<GameId, boolean> = {
  ucdavis: false,
  sjsu: true,
  stanford: true,
}

export const GAME_SCORES: Record<GameId, { uclaScore: number; oppScore: number; win: boolean }> = {
  ucdavis: { uclaScore: 14, oppScore: 7, win: true },
  sjsu: { uclaScore: 11, oppScore: 10, win: true },
  stanford: { uclaScore: 11, oppScore: 12, win: false },
}

export const OPP_TEAMS: Record<GameId, string> = {
  ucdavis: 'UC Davis Aggies',
  sjsu: 'SJSU Spartans',
  stanford: 'Stanford Cardinal',
}

export const UCLA_TEAM = 'UCLA Bruins'
export const GAME_IDS: GameId[] = ['ucdavis', 'sjsu', 'stanford']
