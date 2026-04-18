import { useAppStore } from '../../store/useAppStore'
import { FOCAL_TEAM, FOCAL_TEAM_SHORT } from '../../types'
import { extractGames } from '../../lib/gamesFromData'

export default function HeroBar() {
  const data = useAppStore(s => s.data)
  const focal = data?.teamMetrics.find(t => t.team === FOCAL_TEAM)
  const games = data ? extractGames(data.rawEvents) : []

  const finalGames = games.filter(g => !g.isLive)
  const wins = finalGames.filter(g => g.focalScore > g.oppScore).length
  const losses = finalGames.length - wins
  const record = finalGames.length ? `${wins}-${losses}` : '—'

  const stats = [
    { val: record, lbl: 'Record' },
    { val: focal?.goals_total ?? '—', lbl: `${FOCAL_TEAM_SHORT} Goals` },
    { val: focal ? `${(focal.shot_pct * 100).toFixed(1)}%` : '—', lbl: 'Shot %' },
    { val: focal?.steals ?? '—', lbl: 'Steals' },
    { val: focal?.saves ?? '—', lbl: 'Saves' },
    { val: focal?.earned_exclusions ?? '—', lbl: 'Earned Excl.' },
  ]

  return (
    <div className="bg-gradient-to-r from-[#1e3a5f] to-card-bg px-6 py-4 flex items-center gap-8 border-b border-border flex-wrap">
      {stats.map(({ val, lbl }) => (
        <div key={lbl} className="text-center">
          <div className="text-2xl font-extrabold text-gold leading-none">{val}</div>
          <div className="text-[10px] text-muted uppercase tracking-wide mt-1">{lbl}</div>
        </div>
      ))}
      {games.length > 0 && <div className="h-9 w-px bg-border mx-2" />}
      <div className="flex gap-3">
        {games.map(g => {
          const win = g.focalScore > g.oppScore
          const prefix = g.isLive ? 'LIVE' : win ? 'W' : 'L'
          const score = `${prefix} ${g.focalScore}–${g.oppScore}`
          const cls = g.isLive
            ? 'bg-sky-900/40 text-sky-300'
            : win
              ? 'bg-green-900/40 text-green-400'
              : 'bg-red-900/40 text-red-400'
          return (
            <div key={g.gameId} className="text-center">
              <div className={`text-xs font-bold px-2 py-0.5 rounded ${cls}`}>{score}</div>
              <div className="text-[9px] text-slate-500 mt-1">vs {g.oppTeam}</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
