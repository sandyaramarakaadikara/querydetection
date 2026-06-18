import { Network, AlertCircle } from 'lucide-react'

export default function DFAVisualizer({ dfaStates }) {
  if (!dfaStates || dfaStates.length === 0) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><Network size={16}/> DFA</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Belum ada state DFA</p></div></div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><Network size={16}/> Transisi State DFA</span>
        <span className="badge badge-keyword">{dfaStates.length} state</span>
      </div>
      <div className="card-body">
        <div className="dfa-flow">
          {dfaStates.map((s, i) => (
            <span key={i} style={{display:'inline-flex',alignItems:'center'}}>
              {i > 0 && <span className="dfa-arrow">→</span>}
              <span className={`dfa-state ${s.is_final ? 'final' : ''} ${s.is_accepted ? 'accepted' : ''}`}>
                q{s.state}
              </span>
            </span>
          ))}
        </div>
        <div className="dfa-legend">
          <span><span className="dfa-dot" style={{borderColor:'var(--red)'}}/> State Final</span>
          <span><span className="dfa-dot" style={{borderColor:'var(--green)'}}/> Diterima</span>
        </div>
      </div>
    </div>
  )
}
