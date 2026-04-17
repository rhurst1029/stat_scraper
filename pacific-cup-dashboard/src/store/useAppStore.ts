import { create } from 'zustand'
import type { AppData, GameFilter } from '../types'

interface AppStore {
  data: AppData | null
  loading: boolean
  error: string | null
  gameFilter: GameFilter
  setData: (data: AppData) => void
  setLoading: (loading: boolean) => void
  setError: (error: string) => void
  setGameFilter: (filter: GameFilter) => void
}

export const useAppStore = create<AppStore>(set => ({
  data: null,
  loading: true,
  error: null,
  gameFilter: 'all',
  setData: data => set({ data, loading: false, error: null }),
  setLoading: loading => set({ loading }),
  setError: error => set({ error, loading: false }),
  setGameFilter: gameFilter => set({ gameFilter }),
}))
