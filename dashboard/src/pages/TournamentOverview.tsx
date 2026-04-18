import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'
import ImpactLeaderboard from '../components/leaderboard/ImpactLeaderboard'
import ShotEfficiencyChart from '../components/charts/ShotEfficiencyChart'
import QuarterMomentumChart from '../components/charts/QuarterMomentumChart'
import GameCard from '../components/charts/GameCard'
import { useAppStore } from '../store/useAppStore'
import { extractGames } from '../lib/gamesFromData'

export default function TournamentOverview() {
  const data = useAppStore(s => s.data)
  const games = data ? extractGames(data.rawEvents) : []
  const gridCols = games.length === 1 ? 'grid-cols-1' : games.length === 2 ? 'grid-cols-2' : 'grid-cols-3'

  return (
    <div className="min-h-screen bg-dark-bg">
      <NavBar />
      <FilterPills />
      <HeroBar />
      <div className="max-w-5xl mx-auto p-6 flex flex-col gap-5">
        <ImpactLeaderboard />
        <div className="grid grid-cols-2 gap-5">
          <ShotEfficiencyChart />
          <QuarterMomentumChart />
        </div>

        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
              Game Score Timelines
            </span>
            <div className="flex-1 h-px bg-border" />
            <span className="text-[10px] text-slate-600">Click a card to view game →</span>
          </div>
          <div className={`grid ${gridCols} gap-4`}>
            {games.map(g => (
              <GameCard key={g.gameId} game={g} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
