import { NavLink } from 'react-router-dom'

const TABS = [
  { label: 'Overview', to: '/' },
  { label: 'Games', to: '/game/ucdavis' },
  { label: 'Players', to: '/players' },
  { label: 'Play-by-Play', to: '/play-by-play' },
]

export default function NavBar() {
  return (
    <nav className="bg-ucla-blue h-12 flex items-center justify-between px-6 sticky top-0 z-50">
      <span className="text-gold font-extrabold text-sm tracking-wide">
        UCLA WATER POLO · Pacific Cup 2026
      </span>
      <div className="flex gap-1">
        {TABS.map(({ label, to }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `px-3 py-1.5 rounded text-xs font-semibold transition-colors ${
                isActive
                  ? 'bg-white/20 text-white'
                  : 'text-white/70 hover:bg-white/10 hover:text-white'
              }`
            }
          >
            {label}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
