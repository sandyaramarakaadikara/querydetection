import { GitBranch, AlertCircle } from 'lucide-react'

export default function ParseTreeViewer({ syntax }) {
  if (!syntax || !syntax.parse_tree) {
    return (
      <div className="card">
        <div className="card-header"><span className="label"><GitBranch size={16}/> Parse Tree</span></div>
        <div className="card-body"><div className="empty-state"><AlertCircle size={32}/><p>Parse tree belum tersedia</p></div></div>
      </div>
    )
  }

  const renderTree = (node, depth = 0, prefix = '', isLast = true) => {
    const indent = depth === 0 ? '' : prefix + (isLast ? '└── ' : '├── ')
    const childPrefix = depth === 0 ? '' : prefix + (isLast ? '    ' : '│   ')
    const lines = [indent + (node.value || node.type)]
    if (node.children) {
      node.children.forEach((child, i) => {
        lines.push(...renderTree(child, depth + 1, childPrefix, i === node.children.length - 1))
      })
    }
    return lines
  }

  return (
    <div className="card">
      <div className="card-header">
        <span className="label"><GitBranch size={16}/> Parse Tree</span>
      </div>
      <div className="card-body">
        <div className="parse-tree">
          {renderTree(syntax.parse_tree).map((line, i) => <div key={i}>{line}</div>)}
        </div>
      </div>
    </div>
  )
}
