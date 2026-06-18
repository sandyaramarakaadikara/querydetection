import { Database, AlertCircle } from 'lucide-react'

const ICONS = {
  TABLE_SCAN:'🗂',INDEX_SCAN:'📑',FILTER:'🔍',PROJECTION:'📋',SORT:'↕️',
  GROUP_BY:'📊',HAVING:'🔎',JOIN:'🔗',AGGREGATE:'∑',RESULT:'✅',
  WRITE:'📝',LOG:'📜',DELETE:'🗑',VALIDATE:'🔒',COMPUTE:'🧮',
  SCHEMA_LOCK:'🔐',EXECUTE_DDL:'⚙️',UPDATE_CATALOG:'📚',COMMIT_DDL:'✅',
  BEGIN_TXN:'🟢',COMMIT_TXN:'✅',ROLLBACK_TXN:'🔴',
  PARSE:'📖',COMPILE:'⚡',EXECUTE:'▶️',RETURN:'📤',
  MATCH:'🔍',INSERT:'📥',MATCHED:'✅',
}

const COLORS = {
  TABLE_SCAN:'#3861fb',INDEX_SCAN:'#00d4ff',FILTER:'#ffd32a',PROJECTION:'#00e68a',
  SORT:'#ff9f43',GROUP_BY:'#a855f7',HAVING:'#ff4757',JOIN:'#ec4899',AGGREGATE:'#a855f7',
  RESULT:'#00e68a',WRITE:'#00d4ff',LOG:'#5a6478',DELETE:'#ff4757',VALIDATE:'#ffd32a',
  COMPUTE:'#ff9f43',SCHEMA_LOCK:'#3861fb',EXECUTE_DDL:'#ec4899',UPDATE_CATALOG:'#a855f7',
  COMMIT_DDL:'#00e68a',BEGIN_TXN:'#00e68a',COMMIT_TXN:'#00d4ff',ROLLBACK_TXN:'#ff4757',
  PARSE:'#ffd32a',COMPILE:'#ff9f43',EXECUTE:'#ec4899',RETURN:'#3861fb',
  MATCH:'#a855f7',INSERT:'#00e68a',MATCHED:'#00d4ff',
}

const LABELS = {
  TABLE_SCAN:'SCAN TABEL',INDEX_SCAN:'SCAN INDEX',FILTER:'FILTER',PROJECTION:'PROYEKSI',
  SORT:'PENGURUTAN',GROUP_BY:'GROUP BY',HAVING:'HAVING',JOIN:'JOIN',AGGREGATE:'AGREGASI',
  RESULT:'HASIL',WRITE:'TULIS',LOG:'LOG',DELETE:'HAPUS',VALIDATE:'VALIDASI',
  COMPUTE:'HITUNG',SCHEMA_LOCK:'KUNCI SCHEMA',EXECUTE_DDL:'JALANKAN DDL',UPDATE_CATALOG:'UPDATE KATALOG',
  COMMIT_DDL:'SELESAI DDL',BEGIN_TXN:'MULAI TRANSAKSI',COMMIT_TXN:'SELESAI TRANSAKSI',ROLLBACK_TXN:'BATAL TRANSAKSI',
  PARSE:'ANALISIS',COMPILE:'KOMPILASI',EXECUTE:'EKSEKUSI',RETURN:'KEMBALI',
  MATCH:'COCOKKAN',INSERT:'SISIPKAN',MATCHED:'COCOK',
}

export default function ExecutionPlan({ plan }) {
  if (!plan || !plan.steps || plan.steps.length === 0) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><Database size={16}/> Rencana Eksekusi</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Belum ada rencana eksekusi</p></div></div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><Database size={16}/> Simulasi Rencana Eksekusi</span>
        <div style={{display:'flex',gap:8}}>
          <span className="badge badge-keyword">{plan.total_steps} langkah</span>
          <span className="badge badge-identifier">Beban: {plan.total_cost}</span>
          <span className="badge badge-literal">~{plan.estimated_rows} baris</span>
        </div>
      </div>
      <div className="card-body">
        <div className="exec-flow">
          {plan.steps.map((step, i) => (
            <div key={step.id}>
              <div className="exec-step">
                <div className="exec-icon" style={{background:`${COLORS[step.operation] || '#5a6478'}22`}}>
                  {ICONS[step.operation] || '•'}
                </div>
                <div className="exec-info">
                  <div className="exec-label" style={{color:COLORS[step.operation] || 'var(--text-dim)'}}>
                    {LABELS[step.operation] || step.label}
                  </div>
                  <div className="exec-detail">{step.detail}</div>
                </div>
                <div className="exec-cost">Beban: {step.cost}</div>
              </div>
              {i < plan.steps.length - 1 && <div className="exec-arrow">↓</div>}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
