import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'
import { computeScoreTimeline } from '../../lib/computeScoreTimeline'
import type { LiveGame } from '../../lib/gamesFromData'
import { UCLA_TEAM } from '../../types'

interface Props {
  game: LiveGame
}

export default function GameCard({ game }: Props) {
  const navigate = useNavigate()
  const data = useAppStore(s => s.data)
  const { gameId, title, uclaScore, oppScore, oppTeam, isLive } = game
  const win = uclaScore > oppScore
  const resultClass = isLive ? 'text-sky-400' : win ? 'text-green-400' : 'text-red-400'
  const badgeClass = isLive
    ? 'bg-sky-900/40 text-sky-300 border-sky-900'
    : win
      ? 'bg-green-900/20 text-green-400 border-green-900'
      : 'bg-red-900/20 text-red-400 border-red-900'
  const badgeLabel = isLive ? 'LIVE' : win ? 'W' : 'L'

  const timeline = data ? computeScoreTimeline(data.rawEvents, game) : []

  const W = 200
  const H = 32
  const mid = H / 2
  const maxAbs = Math.max(1, ...timeline.map(p => Math.abs(p.scoreDiff)))
  const points = timeline.length
    ? timeline
        .map((p, i) => {
          const x = timeline.length > 1 ? (i / (timeline.length - 1)) * W : W / 2
          const y = mid - (p.scoreDiff / maxAbs) * (mid - 4)
          return `${x.toFixed(1)},${y.toFixed(1)}`
        })
        .join(' ')
    : `0,${mid} ${W},${mid}`

  const gameEvents = data?.rawEvents.filter(e => e.game === title) ?? []
  const uclaEvents = gameEvents.filter(e => e.team === UCLA_TEAM)
  const goals = uclaEvents.filter(e => e.event_type === 'goal' || e.event_type === 'goal_penalty').length
  const steals = uclaEvents.filter(e => e.event_type === 'steal').length
  const shots = uclaEvents.filter(e =>
    ['goal', 'goal_penalty', 'miss', 'miss_penalty'].includes(e.event_type)
  ).length
  const shotPct = shots > 0 ? ((goals / shots) * 100).toFixed(1) + '%' : '—'

  const strokeColor = isLive ? '#38bdf8' : win ? '#4ade80' : '#f87171'

  return (
    <div
      onClick={() => navigate(`/game/${gameId}`)}
      className="bg-dark-bg border border-border rounded-xl p-3 cursor-pointer hover:border-ucla-blue transition-colors group"
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <div className="text-xs font-bold text-muted">vs {oppTeam}</div>
          <div className={`text-xl font-extrabold ${resultClass}`}>
            {uclaScore} – {oppScore}
          </div>
        </div>
        <span className={`text-xs font-bold px-2 py-0.5 rounded border ${badgeClass}`}>
          {badgeLabel}
        </span>
      </div>

      <div className="rounded overflow-hidden mb-2">
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="h-8">
          <rect width={W} height={H} fill="#0f172a" />
          <line x1={0} y1={mid} x2={W} y2={mid} stroke="#334155" strokeWidth={1} />
          {[0, 1, 2, 3].map(i => (
            <line
              key={i}
              x1={((i + 1) * W) / 4}
              y1={0}
              x2={((i + 1) * W) / 4}
              y2={H}
              stroke="#1e293b"
              strokeWidth={1}
            />
          ))}
          <polyline
            points={points}
            fill="none"
            stroke={strokeColor}
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      <div className="flex gap-2 text-center">
        {[
          { v: shotPct, l: 'Shot %' },
          { v: steals, l: 'Steals' },
        ].map(({ v, l }) => (
          <div key={l} className="flex-1">
            <div className="text-xs font-bold text-gold">{v}</div>
            <div className="text-[9px] text-slate-500">{l}</div>
          </div>
        ))}
      </div>

      <div className="text-[9px] text-center text-slate-600 mt-2 group-hover:text-ucla-blue transition-colors">
        Click to view game →
      </div>
    </div>
  )
}
