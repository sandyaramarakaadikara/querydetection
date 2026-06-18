import { BarChart3, AlertCircle } from 'lucide-react'

const CAT_LABELS = {
  'Sederhana': 'Sederhana',
  'Sedang': 'Sedang',
  'Kompleks': 'Kompleks',
  'Sangat Kompleks': 'Sangat Kompleks',
}

export default function ComplexityScore({ complexity }) {
  if (!complexity) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><BarChart3 size={16}/> Kompleksitas</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Belum ada analisis</p></div></div>
      </div>
    )
  }

  const { score, category, metrics } = complexity
  const ringClass = score <= 20 ? 'simple' : score <= 40 ? 'medium-complex' : score <= 65 ? 'complex' : 'very-complex'

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><BarChart3 size={16}/> Kompleksitas Query</span>
        <span className={`badge badge-${ringClass === 'simple' ? 'valid' : ringClass === 'medium-complex' ? 'medium' : ringClass === 'complex' ? 'high' : 'critical'}`}>
          {category}
        </span>
      </div>
      <div className="card-body">
        <div className="complexity-container">
          <div className={`score-ring ${ringClass}`}>{score}</div>
          <div className="score-label">Query {category}</div>
          <div className="metrics-grid">
            {[
              { v: metrics.join_count, l: 'JOIN', c: 'var(--purple)' },
              { v: metrics.subquery_count, l: 'Subquery', c: 'var(--cyan)' },
              { v: metrics.condition_count, l: 'Kondisi', c: 'var(--yellow)' },
              { v: metrics.aggregate_count, l: 'Agregat', c: 'var(--pink)' },
              { v: metrics.keyword_count, l: 'Keyword', c: 'var(--blue)' },
              { v: metrics.variable_count || 0, l: 'Variabel', c: 'var(--orange)' },
              { v: metrics.operator_count || 0, l: 'Operator', c: 'var(--green)' },
              { v: metrics.literal_count || 0, l: 'Literal', c: 'var(--red)' },
              { v: metrics.query_length, l: 'Panjang', c: 'var(--text-dim)' },
              { v: metrics.token_count, l: 'Token', c: 'var(--cyan)' },
            ].map((m, i) => (
              <div key={i} className="metric-card">
                <div className="metric-val" style={{color:m.c}}>{m.v}</div>
                <div className="metric-label">{m.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
