import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import * as XLSX from 'xlsx'
import { parseWorkbook } from './lib/parseWorkbook'
import { useAppStore } from './store/useAppStore'
import LoadingScreen from './components/LoadingScreen'

export default function App() {
  const { loading, error, setData, setError } = useAppStore()

  useEffect(() => {
    fetch('/stat_scraper/data/PERFORMANCE_REPORT.xlsx')
      .then(res => {
        if (!res.ok) throw new Error(`Failed to fetch data file: ${res.status}`)
        return res.arrayBuffer()
      })
      .then(buf => {
        const wb = XLSX.read(buf, { type: 'array' })
        setData(parseWorkbook(wb))
      })
      .catch(err => setError(String(err)))
  }, [setData, setError])

  if (loading || error) return <LoadingScreen error={error} />
  return <Outlet />
}
