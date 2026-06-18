import { useMemo } from 'react'
import ReactFlow, { Position, Handle } from 'reactflow'
import 'reactflow/dist/style.css'
import { AlertCircle } from 'lucide-react'

function ASTNodeComponent({ data }) {
  const colors = {
    PROGRAM: '#3b82f6',      // Blue
    STATEMENT: '#6366f1',    // Indigo
    SELECT_CLAUSE: '#10b981',// Emerald green
    FROM_CLAUSE: '#06b6d4',  // Cyan
    WHERE_CLAUSE: '#d97706',  // Dark amber
    GROUP_CLAUSE: '#f97316',  // Orange
    HAVING_CLAUSE: '#ef233c', // Vibrant Red
    ORDER_CLAUSE: '#db2777',  // Pink
    CONDITION: '#8b5cf6',    // Purple
    IDENTIFIER: '#0891b2',   // Saturated cyan
    LITERAL: '#059669',      // Saturated emerald
    NUMBER: '#ea580c',       // Saturated orange
    OPERATOR: '#b45309',     // Saturated yellow/amber
    AGGREGATE: '#db2777',    // Pink
  }
  const bg = colors[data.nodeType] || '#475569'
  return (
    <div style={{
      background: `linear-gradient(135deg, ${bg}, ${bg}ee)`,
      color: '#fff',
      padding: '8px 16px',
      borderRadius: '12px',
      fontSize: '0.75rem',
      fontWeight: 700,
      border: `1.5px solid rgba(255, 255, 255, 0.15)`,
      boxShadow: `0 4px 14px ${bg}25`,
      minWidth: 50,
      textAlign: 'center',
      fontFamily: "'JetBrains Mono', monospace",
    }}>
      <Handle type="target" position={Position.Top} style={{opacity:0.6,background:bg,width:6,height:6}}/>
      {data.label}
      <Handle type="source" position={Position.Bottom} style={{opacity:0.6,background:bg,width:6,height:6}}/>
    </div>
  )
}

const nodeTypes = { astNode: ASTNodeComponent }

function flattenTree(node, parentId = null, nodes = [], edges = [], idC = { c: 0 }) {
  if (!node) return { nodes, edges }
  const id = `n${idC.c++}`
  nodes.push({ id, type:'astNode', position:{x:0,y:0}, data:{ label:node.value||node.type, nodeType:node.type } })
  if (parentId) edges.push({ id:`e_${parentId}_${id}`, source:parentId, target:id, style:{stroke:'rgba(56,97,251,0.3)',strokeWidth:1.5} })
  if (node.children) node.children.forEach(c => flattenTree(c, id, nodes, edges, idC))
  return { nodes, edges }
}

export default function ASTViewer({ ast }) {
  const layout = useMemo(() => {
    if (!ast) return null
    const { nodes, edges } = flattenTree(ast)
    if (!nodes.length) return null
    const lvlMap = {}
    const visit = (nid, lv, vis = new Set()) => {
      if (vis.has(nid)) return; vis.add(nid)
      if (!lvlMap[lv]) lvlMap[lv] = []; lvlMap[lv].push(nid)
      edges.filter(e => e.source === nid).forEach(e => visit(e.target, lv + 1, vis))
    }
    visit(nodes[0].id, 0)
    const pn = nodes.map(n => {
      let lv = 0
      for (const [l, ids] of Object.entries(lvlMap)) { if (ids.includes(n.id)) { lv = +l; break } }
      const sibs = lvlMap[lv] || []; const idx = sibs.indexOf(n.id)
      const xS = 200, yS = 90, tw = sibs.length * xS
      return { ...n, position: { x: idx * xS - tw / 2 + xS / 2, y: lv * yS + 30 } }
    })
    return { nodes: pn, edges }
  }, [ast])

  if (!layout) return (
    <div className="card">
      <div className="card-header"><span className="label"><AlertCircle size={16}/> AST</span></div>
      <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>AST belum tersedia</p></div></div>
    </div>
  )

  return (
    <div className="card">
      <div className="card-header">
        <span className="label">Abstract Syntax Tree (AST)</span>
        <span className="badge badge-keyword">{layout.nodes.length} node</span>
      </div>
      <div className="card-body" style={{padding:0}}>
        <div className="react-flow-wrapper">
          <ReactFlow nodes={layout.nodes} edges={layout.edges} nodeTypes={nodeTypes}
            fitView proOptions={{hideAttribution:true}}
            style={{background:'#f8fafc', borderTop:'1px solid var(--border)'}}/>
        </div>
      </div>
    </div>
  )
}
