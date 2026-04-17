import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'
import ImpactLeaderboard from '../components/leaderboard/ImpactLeaderboard'
import ShotEfficiencyChart from '../components/charts/ShotEfficiencyChart'
import QuarterMomentumChart from '../components/charts/QuarterMomentumChart'

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
      </div>
    </div>
  )
}
