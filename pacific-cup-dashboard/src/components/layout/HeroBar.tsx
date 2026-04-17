import { useAppStore } from '../../store/useAppStore'
import { UCLA_TEAM } from '../../types'

const GAME_RESULTS = [
  { opp: 'UC Davis', score: 'W 14–7', win: true },
  { opp: 'SJSU', score: 'W 11–10', win: true },
  { opp: 'Stanford', score: 'L 11–12', win: false },
]

export default function HeroBar() {
  const data = useAppStore(s => s.data)
  const ucla = data?.teamMetrics.find(t => t.team === UCLA_TEAM)

  const stats = [
    { val: '2-1', lbl: 'Record' },
    { val: ucla?.goals_total ?? '—', lbl: 'UCLA Goals' },
    { val: ucla ? `${(ucla.shot_pct * 100).toFixed(1)}%` : '—', lbl: 'Shot %' },
    { val: ucla?.steals ?? '—', lbl: 'Steals' },
    { val: ucla?.saves ?? '—', lbl: 'Saves' },
    { val: ucla?.earned_exclusions ?? '—', lbl: 'Earned Excl.' },
  ]

  return (
    <div className="bg-gradient-to-r from-[#1e3a5f] to-card-bg px-6 py-4 flex items-center gap-8 border-b border-border flex-wrap">
      {stats.map(({ val, lbl }) => (
        <div key={lbl} className="text-center">
          <div className="text-2xl font-extrabold text-gold leading-none">{val}</div>
          <div className="text-[10px] text-muted uppercase tracking-wide mt-1">{lbl}</div>
        </div>
      ))}
      <div className="h-9 w-px bg-border mx-2" />
      <div className="flex gap-3">
        {GAME_RESULTS.map(({ opp, score, win }) => (
          <div key={opp} className="text-center">
            <div
              className={`text-xs font-bold px-2 py-0.5 rounded ${
                win ? 'bg-green-900/40 text-green-400' : 'bg-red-900/40 text-red-400'
              }`}
            >
              {score}
            </div>
            <div className="text-[9px] text-slate-500 mt-1">{opp}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
