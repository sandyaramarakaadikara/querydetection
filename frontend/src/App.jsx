import { useState, useCallback, useEffect, useRef } from 'react'
import { analyzeQuery, getSamples } from './services/api'
import SQLEditor from './components/SQLEditor'
import TokenResult from './components/TokenResult'
import DFAVisualizer from './components/DFAVisualizer'
import ParseTreeViewer from './components/ParseTreeViewer'
import ASTViewer from './components/ASTViewer'
import ExecutionPlan from './components/ExecutionPlan'
import InjectionDetection from './components/InjectionDetection'
import ComplexityScore from './components/ComplexityScore'
import DecisionTree from './components/DecisionTree'
import SFAVisualizer from './components/SFAVisualizer'
import {
  Play, Database, Zap, Search, BookOpen, Code2, Shield, FileCode, GitBranch,
  CheckCircle2, XCircle, AlertTriangle, BarChart3
} from 'lucide-react'

const ANALYSIS_TABS = [
  { id: 'tokens', label: 'Token', icon: Search },
  { id: 'automata', label: 'Automata', icon: Zap },
  { id: 'tree', label: 'Tree & AST', icon: Code2 },
  { id: 'execution', label: 'Eksekusi', icon: Database },
  { id: 'complexity', label: 'Kompleksitas', icon: BarChart3 },
  { id: 'decision', label: 'Keputusan', icon: GitBranch },
]

export default function App() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('tokens')

  const handleAnalyze = useCallback(async () => {
    if (!query.trim()) return
    setLoading(true); setError(null)
    try {
      const data = await analyzeQuery(query)
      setResult(data)
      setActiveTab('tokens')
    } catch (err) {
      setError(err.message); setResult(null)
    } finally { setLoading(false) }
  }, [query])

  const handleLoadSample = useCallback((q) => { setQuery(q); setResult(null); setError(null) }, [])

  return (
    <div className="app">
      <header className="header animate-in">
        <div className="header-bg-glow header-bg-glow-1"/>
        <div className="header-bg-glow header-bg-glow-2"/>
        <div className="header-bg-grid"/>
        <div className="header-content">
          <div className="header-badge">
            <span className="header-badge-dot"/>
            <span>SQL Compiler &amp; Security Analyzer</span>
          </div>
          <h1 className="header-title">
            <Code2 size={32} className="header-title-icon"/>
            <span className="header-title-text">
              Kompilator Query <span className="header-title-accent">SQL</span>
            </span>
            <span className="header-subtitle-text">&amp; Analisis Keamanan</span>
          </h1>
          <p className="header-description">
            Analisis real-time untuk setiap query SQL — mulai dari tokenisasi, validasi sintaksis, hingga deteksi ancaman injeksi.
          </p>
          <div className="header-features">
            <span className="feature-pill"><Zap size={12}/> Analisis Leksikal</span>
            <span className="feature-pill"><Search size={12}/> Validasi Sintaks</span>
            <span className="feature-pill"><FileCode size={12}/> Parse Tree</span>
            <span className="feature-pill"><Code2 size={12}/> AST</span>
            <span className="feature-pill"><Database size={12}/> Rencana Eksekusi</span>
            <span className="feature-pill"><Shield size={12}/> Deteksi Injeksi</span>
          </div>
        </div>
        <div className="header-actions">
          <SampleQueries onSelect={handleLoadSample} />
          <button className="btn btn-analyze" onClick={handleAnalyze} disabled={loading || !query.trim()}>
            {loading ? (
              <><span className="loading-spinner" style={{width:16,height:16,borderWidth:2}}/><span>Menganalisis...</span></>
            ) : (
              <><Play size={16} fill="currentColor"/> Analisis Query <span className="btn-arrow">→</span></>
            )}
          </button>
        </div>
      </header>

      <div className="grid">
        <div className="grid-full animate-in delay-1">
          <div className="card">
            <div className="card-header">
              <span className="label"><Code2 size={16}/> Editor SQL</span>
            </div>
            <div className="card-body" style={{padding:0}}>
              <div className="editor-wrapper">
                <SQLEditor value={query} onChange={setQuery} />
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="grid-full animate-in">
            <div className="error-banner">❌ {error}</div>
          </div>
        )}

        {loading && (
          <div className="grid-full animate-in delay-1">
            <div className="card tab-panel-card">
              <div className="card-body">
                <div className="skeleton">
                  <div className="skeleton-line" style={{width:'35%'}}/>
                  <div className="skeleton-line" style={{width:'75%'}}/>
                  <div className="skeleton-line" style={{width:'50%'}}/>
                  <div className="skeleton-block" style={{height:180}}/>
                  <div className="skeleton-line" style={{width:'60%'}}/>
                </div>
              </div>
            </div>
          </div>
        )}

        {result && !loading && (
          <>
            <ResultSummary result={result} />

            {result.injection?.is_vulnerable && (
              <div className="grid-full animate-in delay-1">
                <InjectionDetection injection={result.injection} />
              </div>
            )}

            {result.injection && !result.injection.is_vulnerable && (
              <div className="grid-full animate-in delay-1">
                <div className="injection-safe-bar">
                  <Shield size={16}/>
                  <span>Query aman — tidak terdeteksi pola SQL Injection</span>
                </div>
              </div>
            )}

            <div className="grid-full tab-nav animate-in delay-1">
              {ANALYSIS_TABS.map(tab => (
                <button
                  key={tab.id}
                  className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <tab.icon size={14}/>
                  {tab.label}
                </button>
              ))}
            </div>

            <div className="grid-full animate-in delay-2">
              {activeTab === 'tokens' && <TokenResult tokens={result.tokens} />}
              {activeTab === 'automata' && (
                <>
                  <div className="grid-full"><DFAVisualizer dfaStates={result.dfa_states} /></div>
                  <div className="grid-full" style={{marginTop:20}}><SFAVisualizer automaton={result.automaton} /></div>
                </>
              )}
              {activeTab === 'tree' && (
                <>
                  <div className="grid-full"><ParseTreeViewer syntax={result.syntax} /></div>
                  <div className="grid-full"><ASTViewer ast={result.ast} /></div>
                </>
              )}
              {activeTab === 'execution' && <div className="grid-full"><ExecutionPlan plan={result.execution_plan} /></div>}
              {activeTab === 'complexity' && <ComplexityScore complexity={result.complexity} />}
              {activeTab === 'decision' && <div className="grid-full"><DecisionTree tree={result.decision_tree} /></div>}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function ResultSummary({ result }) {
  const { syntax, complexity, injection } = result
  const isValid = syntax?.status === 'VALID'
  const hasErrors = syntax?.errors?.length > 0
  const hasWarnings = syntax?.warnings?.length > 0

  return (
    <div className="grid-full animate-in delay-1">
      <div className="summary-strip">
        <div className={`summary-item ${isValid ? 'summary-valid' : 'summary-invalid'}`}>
          {isValid ? <CheckCircle2 size={18} className="summary-icon-ok"/> : <XCircle size={18} className="summary-icon-err"/>}
          <div className="summary-item-body">
            <div className="summary-item-label">Sintaks</div>
            <div className="summary-item-value">
              {isValid ? 'Valid' : 'Tidak Valid'}
              {hasErrors && ` (${syntax.errors.length} error)`}
              {hasWarnings && !hasErrors && ` (${syntax.warnings.length} peringatan)`}
            </div>
          </div>
        </div>

        {complexity && (
          <div className="summary-item">
            <BarChart3 size={18} className="summary-icon-muted"/>
            <div className="summary-item-body">
              <div className="summary-item-label">Kompleksitas</div>
              <div className="summary-item-value">{complexity.score} — {complexity.category}</div>
            </div>
          </div>
        )}

        {injection && (
          <div className={`summary-item ${injection.is_vulnerable ? 'summary-invalid' : 'summary-valid'}`}>
            {injection.is_vulnerable
              ? <AlertTriangle size={18} className="summary-icon-err"/>
              : <Shield size={18} className="summary-icon-ok"/>
            }
            <div className="summary-item-body">
              <div className="summary-item-label">Injeksi SQL</div>
              <div className="summary-item-value">
                {injection.is_vulnerable
                  ? `${injection.findings_count} ancaman ditemukan`
                  : 'Aman'
                }
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const FALLBACK_SAMPLES = [
  { name: 'SELECT Dasar', query: 'SELECT nama, npm FROM mahasiswa', desc: 'SELECT nama, npm FROM...' },
  { name: 'SELECT + WHERE', query: "SELECT nama, npm FROM mahasiswa WHERE npm = '22001'", desc: "SELECT... WHERE npm =..." },
  { name: 'SELECT + JOIN', query: 'SELECT m.nama, d.nama AS dosen FROM mahasiswa m INNER JOIN dosen d ON m.dosen_id = d.id', desc: 'SELECT... INNER JOIN...' },
  { name: 'SELECT + GROUP BY', query: 'SELECT jurusan, COUNT(*) AS jml FROM mahasiswa GROUP BY jurusan ORDER BY jml DESC', desc: 'GROUP BY + ORDER BY...' },
  { name: 'SELECT Full Query', query: "SELECT m.nama, d.nama AS dosen, SUM(n.nilai) AS total FROM mahasiswa m INNER JOIN dosen d ON m.dosen_id = d.id LEFT JOIN nilai n ON m.npm = n.npm WHERE m.angkatan >= 2020 GROUP BY m.nama, d.nama HAVING SUM(n.nilai) > 100 ORDER BY total DESC", desc: 'JOIN + GROUP + HAVING + ORDER...' },
  { name: 'INSERT INTO', query: "INSERT INTO mahasiswa (npm, nama, jurusan) VALUES ('22005', 'Budi', 'Informatika')", desc: 'INSERT dengan VALUES...' },
  { name: 'INSERT SELECT', query: 'INSERT INTO mahasiswa_baru (npm, nama) SELECT npm, nama FROM mahasiswa WHERE angkatan = 2021', desc: 'INSERT dengan subquery...' },
  { name: 'UPDATE', query: "UPDATE mahasiswa SET jurusan = 'Sistem Informasi' WHERE npm = '22001'", desc: 'UPDATE dengan WHERE...' },
  { name: 'DELETE', query: "DELETE FROM mahasiswa WHERE npm = '22001'", desc: 'DELETE dengan WHERE...' },
  { name: 'CREATE TABLE', query: 'CREATE TABLE mahasiswa (npm VARCHAR(10) PRIMARY KEY, nama VARCHAR(100))', desc: 'DDL: CREATE TABLE...' },
  { name: 'ALTER TABLE', query: 'ALTER TABLE mahasiswa ADD COLUMN email VARCHAR(100)', desc: 'DDL: ALTER TABLE...' },
  { name: 'DROP TABLE', query: 'DROP TABLE mahasiswa', desc: 'DDL: DROP TABLE...' },
  { name: 'TRUNCATE', query: 'TRUNCATE TABLE mahasiswa', desc: 'DDL: TRUNCATE...' },
  { name: 'MERGE', query: 'MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN UPDATE SET t.nama = s.nama WHEN NOT MATCHED THEN INSERT (id, nama) VALUES (s.id, s.nama)', desc: 'MERGE / UPSERT...' },
  { name: 'BEGIN/COMMIT', query: 'BEGIN TRANSACTION; UPDATE rekening SET saldo = saldo - 100000 WHERE id = 1; COMMIT', desc: 'Transaksi TCL...' },
  { name: 'DECLARE', query: 'DECLARE @total INT; SET @total = (SELECT COUNT(*) FROM mahasiswa); SELECT @total AS total_mahasiswa', desc: 'Variable SQL...' },
  { name: 'SQL Injection', query: "SELECT * FROM users WHERE name = 'admin' OR '1'='1' --", desc: "Percobaan bypass autentikasi..." },
  { name: 'CREATE INDEX', query: 'CREATE INDEX idx_npm ON mahasiswa (npm)', desc: 'DDL: INDEX...' },
  { name: 'CREATE VIEW', query: 'CREATE VIEW mahasiswa_aktif AS SELECT npm, nama FROM mahasiswa WHERE angkatan >= 2023', desc: 'DDL: VIEW...' },
  { name: 'DROP INDEX', query: 'DROP INDEX idx_npm', desc: 'DDL: DROP INDEX...' },
]

function SampleQueries({ onSelect }) {
  const [open, setOpen] = useState(false)
  const [samples, setSamples] = useState(FALLBACK_SAMPLES)
  const dropdownRef = useRef(null)

  useEffect(() => {
    getSamples()
      .then(data => {
        if (data && data.samples) {
          setSamples(data.samples.map(s => ({
            ...s,
            desc: s.query.length > 50 ? s.query.substring(0, 50) + '...' : s.query,
          })))
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!open) return
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [open])

  return (
    <div className="dropdown" ref={dropdownRef}>
      <button className="btn btn-ghost" onClick={() => setOpen(!open)}>
        <BookOpen size={14}/> Contoh Query
      </button>
      {open && (
        <div className="dropdown-menu">
          {samples.map((s, i) => (
            <button key={i} className="dropdown-item" onClick={() => { onSelect(s.query); setOpen(false) }}>
              <div className="sample-name">{s.name}</div>
              <div className="sample-preview">{s.desc}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
