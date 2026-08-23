// Signature element: rank badges styled like Indian roadside distance-marker
// posts (rounded top, bold number, small label). Fitting metaphor for
// "how urgently does this need fixing" — and it's the one place we spend
// visual boldness in this dashboard.
//
// Order is exactly as given by the backend — never re-sorted client-side,
// per contract (scoring logic stays single-sourced on the backend).

const CATEGORY_LABELS = {
  water: 'Water supply',
  road: 'Road condition',
  electricity: 'Electricity',
  sanitation: 'Sanitation',
  health: 'Health access',
  education: 'Education',
  other: 'Other',
}

const CATEGORY_DOT = {
  water: 'var(--petrol)',
  road: 'var(--marigold)',
  electricity: 'var(--rust)',
  sanitation: 'var(--ink-soft)',
  health: 'var(--rust)',
  education: 'var(--petrol)',
  other: 'var(--ink-soft)',
}

export default function RankedList({ hotspots }) {
  if (hotspots.length === 0) {
    return (
      <div className="empty-state">
        <p>No hotspots computed yet. Once enough reports come in, priority clusters will appear here.</p>
      </div>
    )
  }

  return (
    <ol className="ranked-list">
      {hotspots.map((h) => (
        <li key={h.cluster_id} className="ranked-item">
          <div className="marker-post">
            <span className="marker-number">{h.rank}</span>
          </div>
          <div className="ranked-content">
            <div className="ranked-heading">
              <span className="category-dot" style={{ background: CATEGORY_DOT[h.category] || 'var(--ink-soft)' }} />
              <span className="mono-tag">{CATEGORY_LABELS[h.category] || h.category}</span>
              <span className="ranked-district">{h.district}</span>
              <span className="ranked-score">{h.priority_score.toFixed(1)}</span>
            </div>
            <div className="score-bar">
              <div className="score-bar-fill" style={{ width: `${Math.min(h.priority_score, 100)}%` }} />
            </div>
            <p className="ranked-explain">{h.explainability_text}</p>
            <p className="ranked-meta">{h.request_count} reports clustered</p>
          </div>
        </li>
      ))}
    </ol>
  )
}
