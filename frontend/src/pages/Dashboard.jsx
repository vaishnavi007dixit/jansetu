import { useEffect, useState } from 'react'
import Heatmap from '../components/Heatmap.jsx'
import RankedList from '../components/RankedList.jsx'
import CategoryCharts from '../components/CategoryCharts.jsx'
import { getHotspots, usingMocks } from '../api.js'

const CATEGORIES = ['water', 'road', 'electricity', 'sanitation', 'health', 'education', 'other']

export default function Dashboard() {
  const [hotspots, setHotspots] = useState([])
  const [generatedAt, setGeneratedAt] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [category, setCategory] = useState('')
  const [district, setDistrict] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError('')

    getHotspots({ category: category || undefined, district: district || undefined })
      .then((data) => {
        if (cancelled) return
        setHotspots(data.hotspots)
        setGeneratedAt(data.generated_at)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Could not load hotspots')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [category, district])

  const districts = [...new Set(hotspots.map((h) => h.district))]
  const totalReports = hotspots.reduce((sum, h) => sum + h.request_count, 0)
  const avgScore = hotspots.length
    ? (hotspots.reduce((sum, h) => sum + h.priority_score, 0) / hotspots.length).toFixed(1)
    : '—'
  const topCategory = (() => {
    const counts = {}
    hotspots.forEach((h) => { counts[h.category] = (counts[h.category] || 0) + h.request_count })
    const entries = Object.entries(counts)
    if (!entries.length) return '—'
    return entries.sort((a, b) => b[1] - a[1])[0][0]
  })()

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <span className="intake-eyebrow">Policymaker view</span>
          <h1>Priority hotspots</h1>
          <p>Ranked and explained — not a raw complaint feed.</p>
        </div>
        <div className="dashboard-meta">
          {usingMocks && <span className="mono-tag mono-tag--warn">Using mock data</span>}
          {generatedAt && <span className="mono-tag">Updated {new Date(generatedAt).toLocaleString()}</span>}
        </div>
      </div>

      {!loading && !error && (
        <div className="stat-row">
          <div className="stat-card">
            <span className="stat-value">{hotspots.length}</span>
            <span className="stat-label">Active hotspots</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{totalReports}</span>
            <span className="stat-label">Reports clustered</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{avgScore}</span>
            <span className="stat-label">Avg. priority score</span>
          </div>
          <div className="stat-card stat-card--accent">
            <span className="stat-value stat-value--tag">{topCategory}</span>
            <span className="stat-label">Top category</span>
          </div>
        </div>
      )}

      <div className="filter-row">
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">All categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        <select value={district} onChange={(e) => setDistrict(e.target.value)}>
          <option value="">All districts</option>
          {districts.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      {error && <p className="intake-error">{error}</p>}
      {loading && <p className="loading-note">Loading hotspots…</p>}

      {!loading && !error && (
        <>
          <Heatmap hotspots={hotspots} />

          <div className="dashboard-grid">
            <div>
              <h2 className="section-heading">Ranked by priority</h2>
              <RankedList hotspots={hotspots} />
            </div>
            <div>
              <CategoryCharts hotspots={hotspots} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
