import { useAppStore } from '../../store/useAppStore'
import { extractGames } from '../../lib/gamesFromData'

export default function FilterPills() {
  const gameFilter = useAppStore(s => s.gameFilter)
  const setGameFilter = useAppStore(s => s.setGameFilter)
  const data = useAppStore(s => s.data)

  const games = data ? extractGames(data.rawEvents) : []
  const pills: { label: string; value: string }[] = [
    { label: 'All Games', value: 'all' },
    ...games.map(g => ({ label: `vs ${g.oppTeam}`, value: g.gameId })),
  ]

  return (
    <div className="bg-card-bg border-b border-border px-6 py-2 flex items-center gap-2">
      <span className="text-xs text-slate-500 uppercase tracking-wide mr-1">Filter</span>
      {pills.map(({ label, value }) => (
        <button
          key={value}
          onClick={() => setGameFilter(value)}
          className={`px-3 py-1 rounded-full text-xs font-semibold border transition-colors ${
            gameFilter === value
              ? 'bg-ucla-blue text-white border-ucla-blue'
              : 'bg-transparent text-muted border-border hover:border-ucla-blue hover:text-sky-300'
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
