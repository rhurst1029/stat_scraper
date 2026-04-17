import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'

const OPP_ORDER = ['UC Davis Aggies', 'SJSU Spartans', 'Stanford Cardinal']

export default function ShotEfficiencyChart() {
  const data = useAppStore(s => s.data)
  const teams = data?.teamMetrics ?? []

  const ucla = teams.find(t => t.team === UCLA_TEAM)
  const opponents = OPP_ORDER.map(name => teams.find(t => t.team === name)).filter(Boolean)
  const allTeams = [
    { team: 'UCLA Bruins', shot_pct: ucla?.shot_pct ?? 0, isUcla: true },
    ...opponents.map(t => ({ team: t!.team, shot_pct: t!.shot_pct, isUcla: false })),
  ]

  const maxPct = Math.max(...allTeams.map(t => t.shot_pct))

  return (
    <div className="bg-card-bg border border-border rounded-xl p-4">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Shot Efficiency
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>
      <div className="flex flex-col gap-3">
        {allTeams.map(({ team, shot_pct, isUcla }) => (
          <div key={team}>
            <div className="flex justify-between items-baseline mb-1">
              <span className={`text-xs font-semibold ${isUcla ? 'text-sky-300' : 'text-muted'}`}>
                {team}
              </span>
              <span className={`text-sm font-bold ${isUcla ? 'text-gold' : 'text-slate-400'}`}>
                {(shot_pct * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-2.5 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  isUcla
                    ? 'bg-gradient-to-r from-ucla-blue to-sky-400'
                    : shot_pct > (ucla?.shot_pct ?? 0)
                    ? 'bg-red-800'
                    : 'bg-slate-600'
                }`}
                style={{ width: `${maxPct > 0 ? (shot_pct / maxPct) * 100 : 0}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
