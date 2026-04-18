import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import * as XLSX from 'xlsx'
import { parseWorkbook } from './lib/parseWorkbook'
import { useAppStore } from './store/useAppStore'
import LoadingScreen from './components/LoadingScreen'

const DATA_URL = '/stat_scraper/data/PERFORMANCE_REPORT.xlsx'
const REFRESH_INTERVAL_MS = 5000

async function fetchAndParse(): Promise<ReturnType<typeof parseWorkbook>> {
  const res = await fetch(`${DATA_URL}?ts=${Date.now()}`)
  if (!res.ok) throw new Error(`Failed to fetch data file: ${res.status}`)
  const buf = await res.arrayBuffer()
  const wb = XLSX.read(buf, { type: 'array' })
  return parseWorkbook(wb)
}

export default function App() {
  const loading = useAppStore(s => s.loading)
  const error = useAppStore(s => s.error)
  const setData = useAppStore(s => s.setData)
  const refreshData = useAppStore(s => s.refreshData)
  const setError = useAppStore(s => s.setError)

  useEffect(() => {
    let cancelled = false

    fetchAndParse()
      .then(data => { if (!cancelled) setData(data) })
      .catch(err => { if (!cancelled) setError(String(err)) })

    const id = setInterval(() => {
      fetchAndParse()
        .then(data => { if (!cancelled) refreshData(data) })
        // transient fetch failures don't flip the UI to error — next tick heals.
        .catch(err => console.warn('refresh failed:', err))
    }, REFRESH_INTERVAL_MS)

    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [setData, refreshData, setError])

  if (loading || error) return <LoadingScreen error={error} />
  return <Outlet />
}
