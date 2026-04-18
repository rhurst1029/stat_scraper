import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { useAppStore } from '../../store/useAppStore'
import { FOCAL_TEAM, FOCAL_TEAM_SHORT } from '../../types'


const QUARTERS = ['Q1', 'Q2', 'Q3', 'Q4']

export default function QuarterMomentumChart() {
  const data = useAppStore(s => s.data)
  const splits = data?.quarterSplits ?? []

  const focalByQ = Object.fromEntries(
    QUARTERS.map(q => {
      const row = splits.find(r => r.team === FOCAL_TEAM && r.quarter === q)
      return [q, row?.goals ?? 0]
    }),
  )

  const oppTeams = new Set(splits.filter(r => r.team !== FOCAL_TEAM).map(r => r.team))
  const oppDivisor = Math.max(1, oppTeams.size)

  const oppByQ = Object.fromEntries(
    QUARTERS.map(q => {
      const oppRows = splits.filter(r => r.team !== FOCAL_TEAM && r.quarter === q)
      const total = oppRows.reduce((sum, r) => sum + r.goals, 0)
      return [q, Math.round((total / oppDivisor) * 10) / 10]
    }),
  )

  const chartData = QUARTERS.map(q => ({
    quarter: q,
    Focal: focalByQ[q],
    Opponents: oppByQ[q],
  }))

  const maxGoals = Math.max(1, ...chartData.flatMap(d => [d.Focal, d.Opponents]))
  const bestQ = chartData.reduce((best, d) => (d.Focal > best.Focal ? d : best), chartData[0])

  return (
    <div className="bg-card-bg border border-border rounded-xl p-4">
      <div className="flex items-center gap-3 mb-4">
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-500">
          Quarter Momentum · {FOCAL_TEAM_SHORT} Goals
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={chartData} barCategoryGap="30%" barGap={2}>
          <XAxis
            dataKey="quarter"
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, maxGoals + 1]}
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={24}
          />
          <Tooltip
            contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 6 }}
            labelStyle={{ color: '#94a3b8', fontSize: 11 }}
            itemStyle={{ fontSize: 11 }}
          />
          <Legend
            iconType="rect"
            iconSize={8}
            wrapperStyle={{ fontSize: 10, color: '#94a3b8' }}
          />
          <Bar dataKey="Focal" name={FOCAL_TEAM_SHORT} radius={[3, 3, 0, 0]}>
            {chartData.map(entry => (
              <Cell
                key={entry.quarter}
                fill={entry.quarter === bestQ.quarter ? '#FFD100' : '#2774AE'}
              />
            ))}
          </Bar>
          <Bar dataKey="Opponents" name="Opp. Avg" fill="#475569" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
