import { createBrowserRouter } from 'react-router-dom'
import App from './App'
import TournamentOverview from './pages/TournamentOverview'
import GameView from './pages/GameView'
import PlayerIndex from './pages/PlayerIndex'
import PlayerProfile from './pages/PlayerProfile'
import PlayByPlayExplorer from './pages/PlayByPlayExplorer'

export const router = createBrowserRouter(
  [
    {
      path: '/',
      element: <App />,
      children: [
        { index: true, element: <TournamentOverview /> },
        { path: 'game/:gameId', element: <GameView /> },
        { path: 'players', element: <PlayerIndex /> },
        { path: 'player/:name', element: <PlayerProfile /> },
        { path: 'play-by-play', element: <PlayByPlayExplorer /> },
      ],
    },
  ],
  { basename: '/stat_scraper' },
)
