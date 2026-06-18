import { CheckCircle2, XCircle, AlertCircle, AlertTriangle } from 'lucide-react'

export default function SyntaxResult({ syntax }) {
  if (!syntax) return null
  const isValid = syntax.status === 'VALID'
  const hasErrors = syntax.errors && syntax.errors.length > 0
  const hasWarnings = syntax.warnings && syntax.warnings.length > 0

  return (
    <div className="card">
      <div className="card-header">
        <span className="label">
          {isValid ? <CheckCircle2 size={16} style={{color:'var(--green)'}}/> : <XCircle size={16} style={{color:'var(--red)'}}/>}
          Validasi Sintaks
        </span>
        <span style={{display:'flex',gap:8,alignItems:'center'}}>
          {hasWarnings && <span className="badge badge-warning">{syntax.warnings.length} Peringatan</span>}
          <span className={`badge ${isValid ? 'badge-valid' : 'badge-invalid'}`}>
            {isValid ? 'VALID' : 'TIDAK VALID'}
          </span>
        </span>
      </div>
      <div className="card-body">
        {isValid && !hasErrors && !hasWarnings && (
          <div className="syntax-valid">
            <CheckCircle2 size={20}/>
            <div>
              <strong>Sintaks query valid.</strong><br/>
              <span style={{opacity:0.7,fontSize:'0.78rem'}}>Semua klausa berurutan dengan benar dan sesuai aturan grammar.</span>
            </div>
          </div>
        )}
        {isValid && hasWarnings && (
          <div className="syntax-valid" style={{marginBottom:12}}>
            <CheckCircle2 size={20}/>
            <div>
              <strong>Sintaks query valid.</strong><br/>
              <span style={{opacity:0.7,fontSize:'0.78rem'}}>Namun terdapat beberapa peringatan yang perlu diperhatikan.</span>
            </div>
          </div>
        )}
        {hasWarnings && (
          <div style={{marginBottom:hasErrors ? 12 : 0}}>
            {syntax.warnings.map((w, i) => (
              <div key={i} className="warning-item">
                <AlertTriangle size={16} className="warning-icon"/>
                <div>
                  <div className="warning-msg">{w.message}</div>
                  {w.line != null && <div className="warning-loc">Baris {w.line}, Kolom {w.column}</div>}
                  {w.suggestion && <div style={{fontSize:'0.72rem',color:'var(--text-dim)',marginTop:4}}>Saran: {w.suggestion}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
        {hasErrors && (
          <div className="syntax-invalid">
            {syntax.errors.map((err, i) => (
              <div key={i} className="error-item">
                <AlertCircle size={16} className="error-icon"/>
                <div>
                  <div className="error-msg">{err.message}</div>
                  {err.line != null && <div className="error-loc">Baris {err.line}, Kolom {err.column}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
