import { useState, useEffect, useRef } from 'react'
import Editor from '@monaco-editor/react'
import { Wand2 } from 'lucide-react'

function formatSQL(sql) {
  const keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'OFFSET',
    'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN', 'CROSS JOIN', 'JOIN',
    'ON', 'UNION', 'UNION ALL', 'INSERT INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
    'CREATE TABLE', 'ALTER TABLE', 'DROP TABLE', 'TRUNCATE', 'MERGE', 'INTO',
    'BEGIN', 'COMMIT', 'ROLLBACK', 'DECLARE', 'EXEC', 'EXECUTE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
    'OVER', 'PARTITION BY', 'ORDER BY', 'ROW_NUMBER', 'RANK', 'DENSE_RANK',
    'NOT', 'IN', 'LIKE', 'BETWEEN', 'EXISTS', 'IS NULL', 'IS NOT NULL']

  let formatted = sql
    .replace(/\s+/g, ' ')
    .trim()

  for (const kw of keywords) {
    const parts = kw.split(' ')
    if (parts.length === 1) {
      formatted = formatted.replace(new RegExp(`\\b${kw}\\b`, 'gi'), `\n${kw}`)
    } else {
      formatted = formatted.replace(new RegExp(`\\b${parts.join('\\s+')}\\b`, 'gi'), `\n${kw}`)
    }
  }

  const lines = formatted.split('\n').map(l => l.trim()).filter(Boolean)
  let indent = 0
  const result = []
  for (const line of lines) {
    const upper = line.toUpperCase().trimStart()
    if (upper.startsWith(')')) indent = Math.max(0, indent - 1)
    result.push('  '.repeat(indent) + line)
    if (upper.endsWith('(')) indent++
    if (/^SELECT\b/i.test(line)) indent = 1
    if (/^FROM\b/i.test(line) || /^WHERE\b/i.test(line) || /^(INNER|LEFT|RIGHT|CROSS|FULL|JOIN)\b/i.test(line) ||
        /^GROUP\b/i.test(line) || /^HAVING\b/i.test(line) || /^ORDER\b/i.test(line) ||
        /^ON\b/i.test(line)) {
      indent = 1
    }
    if (/^UNION\b/i.test(line)) indent = 0
  }
  return result.join('\n')
}

export default function SQLEditor({ value, onChange }) {
  const [mode, setMode] = useState('loading')
  const mountedRef = useRef(false)
  const timerRef = useRef(null)

  useEffect(() => {
    timerRef.current = setTimeout(() => {
      if (!mountedRef.current) {
        setMode('fallback')
      }
    }, 8000)
    return () => clearTimeout(timerRef.current)
  }, [])

  const handleMount = () => {
    mountedRef.current = true
    setMode('editor')
    clearTimeout(timerRef.current)
  }

  const handleFormat = () => {
    const formatted = formatSQL(value)
    onChange(formatted)
  }

  const textareaStyle = mode === 'fallback'
    ? { width:'100%',height:'100%',background:'#fff',color:'#1d1d1f',
        border:'none',padding:12,fontSize:13,fontFamily:'Consolas,monospace',
        resize:'none',outline:'none',lineHeight:1.6 }
    : { width:'100%',height:'100%',background:'#fff',color:'#1d1d1f',
        border:'none',padding:12,fontSize:13,fontFamily:'Consolas,monospace',
        resize:'none',outline:'none',lineHeight:1.6 }

  return (
    <div style={{display:'flex',flexDirection:'column',height:'100%'}}>
      <div className="editor-toolbar">
        <button className="btn btn-format" onClick={handleFormat} title="Rapikan query">
          <Wand2 size={14}/> Format
        </button>
      </div>
      <div style={{flex:1,minHeight:0}}>
        {mode === 'fallback' ? (
          <textarea
            value={value}
            onChange={e => onChange(e.target.value)}
            style={textareaStyle}
            placeholder="Tulis query SQL di sini..."
          />
        ) : (
          <Editor
            height="100%"
            defaultLanguage="sql"
            theme="vs"
            value={value}
            onChange={onChange}
            loading={<div style={{padding:20,color:'var(--text-dim)',fontSize:13}}>Memuat editor...</div>}
            options={{
              minimap: { enabled: false },
              fontSize: 13,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              automaticLayout: true,
              tabSize: 2,
            }}
            onMount={handleMount}
          />
        )}
      </div>
    </div>
  )
}
