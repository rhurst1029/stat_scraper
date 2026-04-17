import { useNavigate } from 'react-router-dom'
import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'
import RoleBadge from './RoleBadge'

export default function ImpactLeaderboard() {
  const data = useAppStore(s => s.data)
  const navigate = useNavigate()

  const players = (data?.playerSummaries ?? [])
    .filter(p => p.team === UCLA_TEAM)
    .sort((a, b) => b.impact - a.impact)

  const maxImpact = Math.max(players[0]?.impact ?? 1, 0.0001)

  return (
    <div className="bg-card-bg border border-border rounded-xl p-4">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Impact Leaderboard
        </span>
        <div className="flex-1 h-px bg-border" />
        <span className="text-[10px] text-slate-600">Click a player to view profile →</span>
      </div>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-border">
            {['#', 'Player', 'Impact', 'Percentile', 'Goals', 'Steals', 'Shot %'].map(h => (
              <th
                key={h}
                className={`text-[10px] font-semibold uppercase tracking-wide text-slate-500 pb-2 ${
                  h === 'Player' || h === '#' ? 'text-left' : 'text-right'
                }`}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {players.map((p, i) => (
            <tr
              key={p.player_name}
              onClick={() => navigate(`/player/${encodeURIComponent(p.player_name)}`)}
              className="cursor-pointer group hover:bg-slate-700/40 rounded transition-colors"
            >
              <td className="py-2 px-1 text-slate-500 text-xs font-bold text-center w-8">
                {i + 1}
              </td>
              <td className="py-2 px-2">
                <div className="text-sm font-semibold group-hover:text-sky-300 transition-colors">
                  {p.player_name}
                </div>
                <div className="flex gap-1 flex-wrap mt-1">
                  {p.roles.map(r => <RoleBadge key={r} role={r} />)}
                </div>
              </td>
              <td className="py-2 px-2 text-right text-lg font-extrabold text-gold w-16">
                {p.impact.toFixed(1)}
              </td>
              <td className="py-2 px-2 w-36">
                <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-ucla-blue to-gold"
                    style={{ width: `${Math.max(0, p.impact) / maxImpact * 100}%` }}
                  />
                </div>
              </td>
              <td className="py-2 px-2 text-right text-xs text-slate-300 w-12">
                {p.goals || '—'}
              </td>
              <td className="py-2 px-2 text-right text-xs text-slate-300 w-12">
                {p.steals || '—'}
              </td>
              <td className="py-2 px-2 text-right text-xs text-slate-300 w-16">
                {p.shots > 0 ? `${(p.shot_pct * 100).toFixed(1)}%` : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
