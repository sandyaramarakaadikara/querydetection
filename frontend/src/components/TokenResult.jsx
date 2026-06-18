import { Hash, AlertCircle } from 'lucide-react'

export default function TokenResult({ tokens }) {
  if (!tokens || tokens.length === 0) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><Hash size={16}/> Token</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Belum ada token</p></div></div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><Hash size={16}/> Hasil Token</span>
        <span className="badge badge-keyword">{tokens.length} token</span>
      </div>
      <div className="card-body" style={{padding:0,maxHeight:320,overflowY:'auto'}}>
        <table className="token-table">
          <thead><tr><th>Token</th><th>Tipe</th><th>Baris</th><th>Kolom</th></tr></thead>
          <tbody>
            {tokens.map((t, i) => (
              <tr key={i}>
                <td><code className={`token-val tok-${t.type.toLowerCase()}`}>{t.value}</code></td>
                <td><span className={`badge badge-${t.type.toLowerCase()}`}>{t.type}</span></td>
                <td style={{color:'var(--text-muted)',fontSize:'0.7rem'}}>{t.line}</td>
                <td style={{color:'var(--text-muted)',fontSize:'0.7rem'}}>{t.column}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
