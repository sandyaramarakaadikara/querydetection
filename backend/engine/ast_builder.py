from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .parser import ParseNode

@dataclass
class ASTNode:
    type: str
    value: str = ''
    children: List['ASTNode'] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {'type': self.type, 'value': self.value, 'properties': self.properties, 'children': [c.to_dict() for c in self.children]}

class ASTBuilder:
    def build(self, parse_tree: dict) -> Optional[dict]:
        if not parse_tree:
            return None
        root = ASTNode(type='PROGRAM', value='SQL')
        self._walk(parse_tree, root)
        return root.to_dict()

    def _walk(self, node: dict, parent: ASTNode):
        nt, nv = node.get('type', ''), node.get('value', '')
        children = node.get('children', [])

        if nt == 'STATEMENT':
            stmt = ASTNode(type='STATEMENT', value=nv)
            parent.children.append(stmt)
            for child in children:
                self._walk(child, stmt)
        elif nt == 'CLAUSE' and nv in ('SELECT', 'FROM', 'WHERE', 'GROUP', 'HAVING', 'ORDER'):
            clause = ASTNode(type=f'{nv}_CLAUSE', value=nv)
            parent.children.append(clause)
            for child in children:
                self._walk(child, clause)
        elif nt in ('KEYWORD',):
            pass
        elif nt in ('IDENTIFIER', 'LITERAL', 'NUMBER', 'OPERATOR', 'SYMBOL', 'AGGREGATE', 'VARIABLE', 'TEMP_TABLE'):
            parent.children.append(ASTNode(type=nt, value=nv))
        else:
            for child in children:
                self._walk(child, parent)

        i = 0
        while i < len(parent.children):
            c = parent.children[i]
            if c.type in ('KEYWORD',) and c.value in ('SELECT', 'FROM', 'WHERE', ',', 'BY', 'GROUP', 'ORDER', 'HAVING', 'SET', 'INTO', 'VALUES', 'TABLE', 'INDEX', 'VIEW'):
                parent.children.pop(i)
                continue
            i += 1
