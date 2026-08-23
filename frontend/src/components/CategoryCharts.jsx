import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const COLORS = {
  water: '#1f6f78',
  road: '#e2a32d',
  electricity: '#b4472a',
  sanitation: '#3a4a41',
}
const FALLBACK_COLOR = '#8a8a7a'

export default function CategoryCharts({ hotspots }) {
  const byCategory = {}
  hotspots.forEach((h) => {
    byCategory[h.category] = (byCategory[h.category] || 0) + h.request_count
  })
  const data = Object.entries(byCategory).map(([category, count]) => ({ category, count }))

  if (data.length === 0) return null

  return (
    <div className="chart-card">
      <h3>Reports by category</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--line)" vertical={false} />
          <XAxis dataKey="category" tick={{ fontFamily: 'var(--font-mono)', fontSize: 12 }} axisLine={{ stroke: 'var(--line)' }} tickLine={false} />
          <YAxis tick={{ fontFamily: 'var(--font-mono)', fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ fontFamily: 'var(--font-body)', borderRadius: 8, border: '1px solid var(--line)' }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.category} fill={COLORS[entry.category] || FALLBACK_COLOR} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
