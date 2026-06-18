import { useMemo } from 'react'
import ReactFlow, { Position, Handle, Background } from 'reactflow'
import 'reactflow/dist/style.css'
import { GitBranch, AlertTriangle, Shuffle, Search, Shield, BarChart3, Flag, Zap, Code2, XCircle } from 'lucide-react'

const TYPE_CONFIG = {
  root: { icon: GitBranch, color: '#ed0707' },
  step: { icon: Zap, color: '#2563eb' },
  decision: { icon: Shuffle, color: '#9333ea' },
  feature: { icon: Code2, color: '#0891b2' },
  check: { icon: Search, color: '#16a34a' },
  error: { icon: XCircle, color: '#ed0707' },
  warning: { icon: AlertTriangle, color: '#ea580c' },
  finding: { icon: Shield, color: '#ea580c' },
  metric: { icon: BarChart3, color: '#ca8a04' },
  summary: { icon: Flag, color: '#ed0707' },
}

const STATUS_STYLES = {
  success: { bg: 'rgba(22,163,74,0.07)', border: 'rgba(22,163,74,0.25)', text: '#16a34a' },
  error: { bg: 'rgba(237,7,7,0.07)', border: 'rgba(237,7,7,0.25)', text: '#ed0707' },
  warning: { bg: 'rgba(234,88,12,0.07)', border: 'rgba(234,88,12,0.25)', text: '#ea580c' },
}

function DTNodeComponent({ data }) {
  const cfg = TYPE_CONFIG[data.nodeType] || TYPE_CONFIG.step
  const st = STATUS_STYLES[data.status] || STATUS_STYLES.success
  const Icon = cfg.icon

  return (
    <div style={{
      background: st.bg,
      border: `1.5px solid ${st.border}`,
      borderRadius: 10,
      padding: '10px 14px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      cursor: 'grab',
      fontFamily: 'Inter,system-ui,sans-serif',
    }}>
      <Handle type="target" position={Position.Top} style={{ opacity: 0.4, width: 7, height: 7, background: '#aaa' }}/>
      <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
        <div style={{
          width: 26, height: 26, borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: `${cfg.color}18`, color: cfg.color, flexShrink: 0,
        }}>
          <Icon size={12} />
        </div>
        <div style={{
          fontSize: 11, fontWeight: 700, color: '#1d1d1f', textTransform: 'uppercase', letterSpacing: '0.02em',
          whiteSpace: 'nowrap',
        }}>
          {data.name}
        </div>
        <span style={{
          fontSize: 9, fontWeight: 700, padding: '1px 7px', borderRadius: 10,
          border: `1px solid ${st.text}25`, background: `${st.text}12`, color: st.text,
          letterSpacing: '0.04em', flexShrink: 0,
        }}>
          {data.status === 'success' ? 'OK' : data.status === 'error' ? 'FAIL' : 'WARN'}
        </span>
      </div>
      {data.detail && (
        <div style={{
          fontSize: 10, color: '#6b7280', marginTop: 4, lineHeight: 1.4,
        }}>
          {data.detail}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0.4, width: 7, height: 7, background: '#aaa' }}/>
    </div>
  )
}

const nodeTypes = { dtNode: DTNodeComponent }

function flattenTree(node, parentId = null, nodes = [], edges = [], idC = { c: 0 }) {
  if (!node) return { nodes, edges }
  const id = `n${idC.c++}`
  nodes.push({
    id, type: 'dtNode', position: { x: 0, y: 0 },
    data: { label: node.name, name: node.name, nodeType: node.type, status: node.status, detail: node.detail },
  })
  if (parentId) {
    edges.push({
      id: `e_${parentId}_${id}`, source: parentId, target: id,
      style: { stroke: 'rgba(0,0,0,0.12)', strokeWidth: 1.5 },
    })
  }
  if (node.children) {
    node.children.forEach(c => flattenTree(c, id, nodes, edges, idC))
  }
  return { nodes, edges }
}

function estimateNodeWidth(data) {
  const cw = (text, sz) => text ? text.length * sz * 0.58 : 0
  const nameW = cw(data.name, 11)
  const detailW = cw(data.detail, 10)
  const icon = 26, badge = 40, gaps = 14, pad = 28
  const w = Math.max(130, nameW + icon + badge + gaps + pad, detailW + pad + 8)
  return Math.min(w, 380)
}

function buildLayout(tree) {
  if (!tree) return null
  const { nodes, edges } = flattenTree(tree)
  if (!nodes.length) return null

  const lvlMap = {}
  const visit = (nid, lv, vis = new Set()) => {
    if (vis.has(nid)) return
    vis.add(nid)
    if (!lvlMap[lv]) lvlMap[lv] = []
    lvlMap[lv].push(nid)
    edges.filter(e => e.source === nid).forEach(e => visit(e.target, lv + 1, vis))
  }
  visit(nodes[0].id, 0)

  const levelWidths = {}
  for (const [lv, ids] of Object.entries(lvlMap)) {
    let maxW = 0
    ids.forEach(id => {
      const n = nodes.find(x => x.id === id)
      if (n) maxW = Math.max(maxW, estimateNodeWidth(n.data))
    })
    levelWidths[lv] = maxW
  }

  const maxLevelWidth = Math.max(...Object.values(levelWidths), 130)
  const xS = maxLevelWidth + 45
  const yS = 120

  const pn = nodes.map(n => {
    let lv = 0
    for (const [l, ids] of Object.entries(lvlMap)) {
      if (ids.includes(n.id)) { lv = +l; break }
    }
    const sibs = lvlMap[lv] || []
    const idx = sibs.indexOf(n.id)
    const tw = sibs.length * xS
    return { ...n, position: { x: idx * xS - tw / 2 + xS / 2, y: lv * yS + 20 } }
  })

  return { nodes: pn, edges }
}

export default function DecisionTree({ tree }) {
  const layout = useMemo(() => buildLayout(tree), [tree])

  if (!layout) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><GitBranch size={16}/> Decision Tree</span></div>
        <div className="card-body">
          <div className="empty-state"><GitBranch size={32}/><p>Decision tree belum tersedia</p></div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><GitBranch size={16}/> Decision Tree</span>
        <span className={`badge ${tree.status === 'success' ? 'badge-valid' : tree.status === 'warning' ? 'badge-warning' : 'badge-invalid'}`}>
          {tree.status === 'success' ? 'AMAN' : tree.status === 'warning' ? 'PERINGATAN' : 'BERMASALAH'}
        </span>
      </div>
      <div className="card-body" style={{ padding: 0 }}>
        <div className="react-flow-wrapper">
          <ReactFlow
            nodes={layout.nodes}
            edges={layout.edges}
            nodeTypes={nodeTypes}
            fitView
            proOptions={{ hideAttribution: true }}
            style={{ background: '#ffffff' }}
          >
            <Background color="#f0f0f0" gap={20} size={1} />
          </ReactFlow>
        </div>
      </div>
    </div>
  )
}
