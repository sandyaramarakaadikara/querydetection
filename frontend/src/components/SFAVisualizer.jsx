import { useMemo, useState } from 'react'
import { Network, AlertCircle, ZoomIn, ZoomOut } from 'lucide-react'

const PRED_COLORS = {
  'is_letter': '#0891b2',     // Cyan-600
  'is_digit': '#ea580c',      // Orange-600
  'is_alnum_ext': '#0d9488',  // Teal-600
  'is_operator': '#b45309',   // Amber-700
  'is_symbol': '#475569',     // Slate-600
  "is_quote(')": '#059669',   // Emerald-600
  'is_quote(")': '#7c3aed',   // Purple-600
  'is_whitespace': '#64748b',  // Slate-500
  'is_bracket_open': '#9333ea',// Purple-600
  'is_bracket_close': '#9333ea',
  'is_dash': '#ef233c',       // Vibrant Red
  'is_slash': '#ef233c',
  'is_star': '#b45309',
  'is_at': '#ef233c',
  'is_hash': '#ef233c',
  'is_dot': '#ea580c',
  'is_semicolon': '#b45309',
  'is_newline': '#475569',
  'ε': '#2563eb',             // Blue-600
}

const SHORT_PRED = {
  'is_letter': 'α',
  'is_digit': '#',
  'is_alnum_ext': 'α#',
  'is_operator': 'op',
  'is_symbol': 'sym',
  "is_quote(')": "'",
  'is_quote(")': '"',
  'is_whitespace': '␣',
  'is_bracket_open': '[',
  'is_bracket_close': ']',
  'is_dash': '-',
  'is_slash': '/',
  'is_star': '*',
  'is_at': '@',
  'is_hash': '#',
  'is_dot': '.',
  'is_semicolon': ';',
  'is_newline': '\\n',
  'ε': 'ε',
}

export default function SFAVisualizer({ automaton }) {
  if (!automaton || !automaton.sfa_steps || automaton.sfa_steps.length === 0) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><Network size={16}/> SFA</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Belum ada data SFA</p></div></div>
      </div>
    )
  }

  const steps = automaton.sfa_steps
  const [zoom, setZoom] = useState(1)

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><Network size={16}/> SFA (Symbolic Finite Automaton)</span>
        <div style={{display:'flex',gap:8,alignItems:'center'}}>
          <span className="badge badge-keyword">{steps.length} langkah</span>
          <button className="btn-icon" onClick={() => setZoom(z => Math.min(z + 0.25, 3))} title="Perbesar">
            <ZoomIn size={14}/>
          </button>
          <button className="btn-icon" onClick={() => setZoom(z => Math.max(z - 0.25, 0.5))} title="Perkecil">
            <ZoomOut size={14}/>
          </button>
        </div>
      </div>
      <div className="card-body" style={{overflow:'auto'}}>
        <div className="automaton-container" style={{transform:`scale(${zoom})`, transformOrigin:'top left'}}>
          <div className="sfa-flow">
            {steps.map((step, i) => (
              <div key={i} className="sfa-step-group" style={{display:'inline-flex',alignItems:'center',marginRight:0}}>
                {i > 0 && (
                  <div className="sfa-predicate" style={{
                    display:'flex', flexDirection:'column', alignItems:'center', padding:'0 4px',
                  }}>
                    <div className="sfa-pred-label" style={{
                      fontSize:'0.6rem', fontWeight:700,
                      color: PRED_COLORS[step.predicate] || 'var(--text-dim)',
                      background: `${PRED_COLORS[step.predicate] || '#5a6478'}18`,
                      padding:'2px 6px', borderRadius:8, whiteSpace:'nowrap',
                      fontFamily:"'JetBrains Mono',monospace",
                    }}>
                      {SHORT_PRED[step.predicate] || step.predicate}
                    </div>
                    <div className="sfa-arrow" style={{
                      width:2, height:20, background: PRED_COLORS[step.predicate] || '#5a6478',
                      margin:'2px 0', opacity:0.5,
                    }}/>
                  </div>
                )}
                <div className="sfa-state" style={{
                  background: step.is_accept
                    ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05))'
                    : 'rgba(59, 130, 246, 0.08)',
                  border: step.is_accept
                    ? '2.5px double rgba(16, 185, 129, 0.5)'
                    : '2px solid rgba(59, 130, 246, 0.25)',
                  borderRadius: 14,
                  padding: '8px 14px',
                  display: 'flex', flexDirection: 'column', alignItems: 'center',
                  minWidth: 90, gap: 2,
                  boxShadow: step.is_accept 
                    ? '0 4px 12px rgba(16, 185, 129, 0.08)' 
                    : '0 4px 12px rgba(59, 130, 246, 0.05)'
                }}>
                  <div style={{fontSize:'0.65rem',fontWeight:700,color:'var(--text-dim)'}}>
                    q{step.active_states[0] || 0}
                  </div>
                  <div style={{fontSize:'0.6rem',color:'var(--text-muted)'}}>
                    {step.char === 'START' ? 'START' : step.char === ' ' ? '␣' : step.char || 'ε'}
                  </div>
                  <div style={{
                    fontSize:'0.58rem', fontWeight:700,
                    color: step.is_accept ? 'var(--green)' : 'var(--text-dim)',
                    marginTop:2,
                  }}>
                    {step.active_labels.slice(0, 2).join(', ')}
                    {step.active_labels.length > 2 ? '...' : ''}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="sfa-legend" style={{display:'flex',gap:12,marginTop:16,flexWrap:'wrap'}}>
            {Object.entries(SHORT_PRED).slice(0, 12).map(([pred, label]) => (
              <span key={pred} style={{
                fontSize:'0.65rem', color:'var(--text-dim)',
                background:`${PRED_COLORS[pred] || '#5a6478'}18`,
                padding:'2px 8px', borderRadius:6,
                fontFamily:"'JetBrains Mono',monospace",
              }}>
                {label}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
