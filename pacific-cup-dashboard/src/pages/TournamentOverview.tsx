import NavBar from '../components/layout/NavBar'
import FilterPills from '../components/layout/FilterPills'
import HeroBar from '../components/layout/HeroBar'

export default function TournamentOverview() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <NavBar />
      <FilterPills />
      <HeroBar />
      <div className="max-w-5xl mx-auto p-6 text-muted">
        Leaderboard coming next...
      </div>
    </div>
  )
}
