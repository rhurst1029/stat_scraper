import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'
import ImpactLeaderboard from '../components/leaderboard/ImpactLeaderboard'
import ShotEfficiencyChart from '../components/charts/ShotEfficiencyChart'
import QuarterMomentumChart from '../components/charts/QuarterMomentumChart'
import GameCard from '../components/charts/GameCard'
import { GAME_IDS } from '../types'

export default function TournamentOverview() {
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
          <div className="grid grid-cols-3 gap-4">
            {GAME_IDS.map(id => (
              <GameCard key={id} gameId={id} />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
