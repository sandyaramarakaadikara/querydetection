import { Shield, ShieldAlert, ShieldCheck, AlertTriangle, AlertCircle } from 'lucide-react'

const TYPE_LABELS = {
  AUTH_BYPASS: 'Bypass Autentikasi',
  UNION_INJECTION: 'Injeksi UNION',
  COMMENT_INJECTION: 'Injeksi Komentar',
  TIME_BASED: 'Injeksi Berbasis Waktu',
  BOOLEAN_BASED: 'Injeksi Berbasis Boolean',
  STACKED_QUERY: 'Query Bertumpuk',
  ERROR_BASED: 'Injeksi Berbasis Error',
}

const SEVERITY_LABELS = {
  Critical: 'Kritis',
  High: 'Tinggi',
  Medium: 'Sedang',
  Low: 'Rendah',
}

export default function InjectionDetection({ injection }) {
  if (!injection) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><Shield size={16}/> Deteksi SQL Injection</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Belum ada analisis</p></div></div>
      </div>
    )
  }

  const { is_vulnerable, risk_level, findings, overall_recommendation, findings_count } = injection

  return (
    <div className="card">
      <div className="card-header">
        <span className="label">
          {is_vulnerable ? <ShieldAlert size={16} style={{color:'var(--red)'}}/> : <ShieldCheck size={16} style={{color:'var(--green)'}}/>}
          Deteksi SQL Injection
        </span>
        <span className={`badge badge-${risk_level.toLowerCase()}`}>{SEVERITY_LABELS[risk_level] || risk_level}</span>
      </div>
      <div className="card-body">
        {!is_vulnerable && (
          <div className="syntax-valid" style={{borderColor:'rgba(0,230,138,0.2)',background:'rgba(0,230,138,0.04)'}}>
            <ShieldCheck size={20}/>
            <div>
              <strong style={{color:'var(--green)'}}>Query terdeteksi aman</strong><br/>
              <span style={{opacity:0.7,fontSize:'0.78rem'}}>Tidak ditemukan pola SQL Injection yang mencurigakan.</span>
            </div>
          </div>
        )}

        {findings_count > 0 && (
          <div>
            <div style={{fontSize:'0.78rem',color:'var(--text-dim)',marginBottom:12,display:'flex',alignItems:'center',gap:6}}>
              <AlertTriangle size={14} style={{color:'var(--orange)'}}/>
              Ditemukan <strong>{findings_count}</strong> potensi ancaman keamanan
            </div>
            {findings.map((f, i) => (
              <div key={i} className="finding-item">
                <div className="finding-header">
                  <span className="finding-type">{TYPE_LABELS[f.type] || f.type.replace(/_/g, ' ')}</span>
                  <span className={`badge badge-${f.severity.toLowerCase()}`}>{SEVERITY_LABELS[f.severity] || f.severity}</span>
                </div>
                <div className="finding-desc">{f.description}</div>
                <div className="finding-pattern">Pola: {f.value}</div>
                <div className="finding-recommendation">{f.recommendation}</div>
              </div>
            ))}
            {overall_recommendation && (
              <div className="recommendation-box">
                <strong>Rekomendasi Mitigasi:</strong><br/>
                {overall_recommendation}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
