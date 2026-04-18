import { FOCAL_TEAM_HEADER } from '../types'

interface Props {
  error: string | null
}

export default function LoadingScreen({ error }: Props) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-bg">
      {error ? (
        <div className="text-center">
          <p className="text-red-400 font-bold mb-2">Failed to load data</p>
          <p className="text-muted text-sm">{error}</p>
        </div>
      ) : (
        <div className="text-center">
          <div className="text-gold text-xl font-bold mb-2">{FOCAL_TEAM_HEADER}</div>
          <p className="text-muted text-sm">Loading tournament data...</p>
        </div>
      )}
    </div>
  )
}
