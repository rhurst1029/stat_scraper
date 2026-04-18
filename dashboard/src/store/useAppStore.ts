import { create } from 'zustand'
import type { AppData, GameFilter } from '../types'

interface AppStore {
  data: AppData | null
  loading: boolean
  error: string | null
  gameFilter: GameFilter
  lastRefreshAt: number | null
  setData: (data: AppData) => void
  refreshData: (data: AppData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string) => void
  setGameFilter: (filter: GameFilter) => void
}

export const useAppStore = create<AppStore>(set => ({
  data: null,
  loading: true,
  error: null,
  gameFilter: 'all',
  lastRefreshAt: null,
  setData: data => set({ data, loading: false, error: null, lastRefreshAt: Date.now() }),
  // refreshData never toggles `loading` — preserves scroll, hover, filter state on each poll.
  refreshData: data => set({ data, error: null, lastRefreshAt: Date.now() }),
  setLoading: loading => set({ loading }),
  setError: error => set({ error, loading: false }),
  setGameFilter: gameFilter => set({ gameFilter }),
}))
