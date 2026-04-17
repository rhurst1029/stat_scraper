import { useAppStore } from '../../store/useAppStore'
import type { GameFilter } from '../../types'

const PILLS: { label: string; value: GameFilter }[] = [
  { label: 'All Games', value: 'all' },
  { label: 'vs UC Davis', value: 'ucdavis' },
  { label: 'vs SJSU', value: 'sjsu' },
  { label: 'vs Stanford', value: 'stanford' },
]

export default function FilterPills() {
  const { gameFilter, setGameFilter } = useAppStore()

  return (
    <div className="bg-card-bg border-b border-border px-6 py-2 flex items-center gap-2">
      <span className="text-xs text-slate-500 uppercase tracking-wide mr-1">Filter</span>
      {PILLS.map(({ label, value }) => (
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
