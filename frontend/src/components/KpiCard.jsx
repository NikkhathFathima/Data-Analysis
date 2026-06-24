export function KpiCard({ label, value, icon, color = 'blue' }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className={`kpi-icon ${color}`}>{icon}</div>
      <div>
        <div className="kpi-value">{value}</div>
        <div className="kpi-label">{label}</div>
      </div>
    </div>
  )
}

export function Loading({ text = 'Loading...' }) {
  return (
    <div className="loading">
      <div className="loading-spinner" />
      <span>{text}</span>
    </div>
  )
}

export function EmptyState({ icon = '📭', message = 'No data available' }) {
  return (
    <div className="empty-state">
      <div className="icon">{icon}</div>
      <p>{message}</p>
    </div>
  )
}

export function fmt(n) {
  if (n === undefined || n === null) return '—'
  if (Math.abs(n) >= 1000000) return `$${(n/1000000).toFixed(1)}M`
  if (Math.abs(n) >= 1000) return `$${(n/1000).toFixed(1)}K`
  return `$${n.toFixed(2)}`
}
