from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .lexer import Token

CLAUSE_ORDER = ['SELECT', 'FROM', 'WHERE', 'GROUP', 'HAVING', 'ORDER']

@dataclass
class ParseNode:
    type: str
    value: str = ''
    children: List['ParseNode'] = field(default_factory=list)
    token: Optional[Token] = None

    def to_dict(self) -> Dict[str, Any]:
        return {'type': self.type, 'value': self.value, 'children': [c.to_dict() for c in self.children]}

class SQLParser:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate(self, tokens: List[Token]) -> Dict[str, Any]:
        self.errors = []
        self.warnings = []
        if not tokens:
            return {'status': 'VALID', 'errors': [], 'warnings': [], 'parse_tree': self._build_generic_tree(tokens)}

        upper = [t.value.upper() for t in tokens]

        # CTE handling: skip to the main SELECT (last occurrence) for validation
        if 'WITH' in upper:
            select_indices = [i for i, v in enumerate(upper) if v == 'SELECT']
            if select_indices:
                main_start = select_indices[-1]
                tokens = tokens[main_start:]
                upper = upper[main_start:]

        if 'SELECT' in upper:
            return self._validate_select(tokens, upper)
        elif 'INSERT' in upper:
            return self._validate_insert(tokens, upper)
        elif 'UPDATE' in upper:
            return self._validate_update(tokens, upper)
        elif 'DELETE' in upper:
            return self._validate_delete(tokens, upper)
        elif 'CREATE' in upper:
            if 'TABLE' in upper:
                return self._validate_create_table(tokens, upper)
            elif 'INDEX' in upper:
                return self._validate_create_index(tokens, upper)
            elif 'VIEW' in upper:
                return self._validate_create_view(tokens, upper)
            else:
                return self._validate_ddl(tokens, upper, 'CREATE')
        elif 'DROP' in upper:
            return self._validate_ddl(tokens, upper, 'DROP')
        elif 'ALTER' in upper:
            if 'TABLE' in upper:
                return self._validate_alter_table(tokens, upper)
            else:
                return self._validate_ddl(tokens, upper, 'ALTER')
        elif 'TRUNCATE' in upper:
            return self._validate_ddl(tokens, upper, 'TRUNCATE')
        elif 'MERGE' in upper:
            return self._validate_merge(tokens, upper)
        elif 'BEGIN' in upper or 'COMMIT' in upper or 'ROLLBACK' in upper:
            return self._validate_tcl(tokens, upper)
        elif 'DECLARE' in upper or 'EXEC' in upper or 'EXECUTE' in upper:
            return self._validate_sp(tokens, upper)
        else:
            pt = self._build_generic_tree(tokens)
            return {'status': 'VALID', 'errors': [], 'warnings': [], 'parse_tree': pt.to_dict()}

    def _validate_select(self, tokens, upper):
        pt = self._build_select_tree(tokens, upper)
        self._check_select_order(tokens, upper)
        self._check_cartesian_join(tokens, upper)
        status = 'VALID' if not self.errors else 'INVALID'
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_insert(self, tokens, upper):
        status = 'VALID'
        if 'INTO' not in upper:
            self.errors.append({'message': 'Diharapkan INTO setelah INSERT', 'line': tokens[0].line, 'column': tokens[0].column + 6})
            status = 'INVALID'
        pt = self._build_generic_tree(tokens)
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_update(self, tokens, upper):
        status = 'VALID'
        if 'SET' not in upper:
            self.errors.append({'message': 'Diharapkan SET setelah UPDATE', 'line': tokens[0].line, 'column': tokens[0].column + 6})
            status = 'INVALID'
        self._check_cartesian_join(tokens, upper)
        pt = self._build_generic_tree(tokens)
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_delete(self, tokens, upper):
        status = 'VALID'
        if 'FROM' not in upper and 'TABLE' not in tokens[1].value.upper():
            pass
        pt = self._build_generic_tree(tokens)
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_ddl(self, tokens, upper, keyword):
        status = 'VALID'
        pt = self._build_generic_tree(tokens)
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_create_table(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        ct_idx = upper.index('CREATE')

        if 'TABLE' not in upper:
            self.errors.append({'message': 'Diharapkan TABLE setelah CREATE', 'line': tokens[ct_idx].line, 'column': tokens[ct_idx].column + 6})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        table_idx = upper.index('TABLE')
        if table_idx + 1 >= len(tokens):
            self.errors.append({'message': 'Nama tabel tidak boleh kosong', 'line': tokens[table_idx].line, 'column': tokens[table_idx].column + 5})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        open_paren = None
        close_paren = None
        paren_depth = 0
        for i, t in enumerate(tokens):
            if t.value == '(' and t.type == 'SYMBOL':
                if open_paren is None:
                    open_paren = i
                paren_depth += 1
            elif t.value == ')' and t.type == 'SYMBOL':
                paren_depth -= 1
                if paren_depth == 0:
                    close_paren = i
                    break

        if open_paren is None:
            self.errors.append({'message': 'Diharapkan ( setelah nama tabel untuk mendefinisikan kolom', 'line': tokens[table_idx].line, 'column': tokens[table_idx].column + 5})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        if close_paren is None:
            self.errors.append({'message': 'Kurung tutup ) tidak ditemukan - definisi kolom tidak lengkap', 'line': tokens[-1].line, 'column': tokens[-1].column + 1})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        if close_paren < open_paren:
            self.errors.append({'message': 'Urutan kurung salah: ) muncul sebelum (', 'line': tokens[close_paren].line, 'column': tokens[close_paren].column})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        defs = tokens[open_paren + 1:close_paren]
        def_upper = upper[open_paren + 1:close_paren]

        if not defs:
            self.errors.append({'message': 'Definisi kolom tidak boleh kosong', 'line': tokens[open_paren].line, 'column': tokens[open_paren].column})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        if def_upper and def_upper[-1] == ',':
            last_comma = [i for i, v in enumerate(def_upper) if v == ','][-1]
            self.errors.append({'message': 'Koma sebelum kurung tutup tidak diperbolehkan', 'line': defs[last_comma].line, 'column': defs[last_comma].column})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        constraint_kw = {'PRIMARY', 'FOREIGN', 'UNIQUE', 'CHECK', 'CONSTRAINT', 'INDEX', 'KEY'}
        data_types = {'INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT', 'VARCHAR', 'CHAR', 'TEXT', 'BOOLEAN',
                      'FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC', 'REAL', 'DATE', 'TIME', 'DATETIME', 'TIMESTAMP',
                      'BLOB', 'CLOB', 'BINARY', 'VARBINARY', 'ENUM', 'SET', 'JSON', 'UUID', 'SERIAL',
                      'INT2', 'INT4', 'INT8', 'FLOAT4', 'FLOAT8', 'BOOL', 'BPCHAR', 'NAME'}

        i = 0
        while i < len(defs):
            t = defs[i]
            val = def_upper[i]

            if val in constraint_kw:
                if val == 'CONSTRAINT':
                    if i + 1 < len(defs):
                        i += 1
                    else:
                        self.errors.append({'message': 'Nama constraint tidak boleh kosong setelah CONSTRAINT', 'line': t.line, 'column': t.column})
                        break
                    val = def_upper[i] if i < len(defs) else ''
                    t = defs[i]

                if val == 'PRIMARY':
                    if i + 1 < len(defs) and def_upper[i + 1] == 'KEY':
                        i += 1
                    else:
                        self.errors.append({'message': 'Diharapkan KEY setelah PRIMARY', 'line': t.line, 'column': t.column + 7})
                        break
                    i += 1
                    if i < len(defs) and defs[i].value == '(':
                        i += 1
                        while i < len(defs) and defs[i].value != ')':
                            i += 1
                        if i < len(defs):
                            i += 1
                    continue
                elif val == 'FOREIGN':
                    if i + 1 < len(defs) and def_upper[i + 1] == 'KEY':
                        i += 2
                    else:
                        i += 1
                    self._validate_ref_constraint(defs, def_upper, i)
                    break
                elif val == 'UNIQUE':
                    i += 1
                    if i < len(defs) and defs[i].value == '(':
                        i += 1
                        while i < len(defs) and defs[i].value != ')':
                            i += 1
                        if i < len(defs):
                            i += 1
                    continue
                elif val == 'CHECK':
                    i += 1
                    if i < len(defs) and defs[i].value == '(':
                        paren = 1
                        i += 1
                        while i < len(defs) and paren > 0:
                            if defs[i].value == '(': paren += 1
                            elif defs[i].value == ')': paren -= 1
                            i += 1
                    else:
                        self.errors.append({'message': 'Diharapkan ( setelah CHECK untuk kondisi constraint', 'line': t.line, 'column': t.column + 5})
                        break
                    continue
            else:
                if t.type == 'IDENTIFIER':
                    i += 1
                    if i >= len(defs) or (def_upper[i] not in data_types and def_upper[i] not in constraint_kw and defs[i].value not in ('(', ',', ')')):
                        self.errors.append({'message': 'Tipe data wajib ada setelah nama kolom', 'line': t.line, 'column': t.column})
                        break
                    if i < len(defs) and def_upper[i] in data_types:
                            i += 1
                            if i < len(defs) and defs[i].value == '(':
                                i += 1
                                while i < len(defs) and defs[i].value != ')':
                                    i += 1
                                if i < len(defs):
                                    i += 1
                            col_constraint_keywords = {'NOT', 'DEFAULT', 'UNIQUE', 'PRIMARY', 'REFERENCES', 'CHECK', ',', ')'}
                            while i < len(defs) and def_upper[i] not in (',', ')') and def_upper[i] not in constraint_kw:
                                cv = def_upper[i]
                                if cv == 'NOT':
                                    if i + 1 < len(defs) and def_upper[i + 1] == 'NULL':
                                        i += 2
                                    else:
                                        self.errors.append({'message': 'Diharapkan NULL setelah NOT', 'line': defs[i].line, 'column': defs[i].column + 3})
                                        break
                                elif cv == 'DEFAULT':
                                    i += 1
                                    if i >= len(defs):
                                        self.errors.append({'message': 'Nilai DEFAULT tidak boleh kosong', 'line': defs[i-1].line, 'column': defs[i-1].column + 7})
                                        break
                                    i += 1
                                elif cv == 'REFERENCES':
                                    i += 1
                                    while i < len(defs) and def_upper[i] not in (',', ')'):
                                        i += 1
                                else:
                                    i += 1
                    continue
                elif t.type == 'KEYWORD' and val in data_types:
                    self.errors.append({'message': 'Nama kolom tidak boleh berupa tipe data', 'line': t.line, 'column': t.column})
                    break

            if i < len(defs) and def_upper[i] == ',':
                i += 1
            elif i < len(defs) and def_upper[i] == ')':
                break

        status = 'VALID' if not self.errors else 'INVALID'
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_ref_constraint(self, defs, def_upper, start):
        i = start
        if i >= len(defs):
            self.errors.append({'message': 'Definisi REFERENCES tidak lengkap', 'line': defs[-1].line, 'column': defs[-1].column})
            return
        if defs[i].value == '(':
            i += 1
            while i < len(defs) and defs[i].value != ')':
                i += 1
            if i < len(defs):
                i += 1
            else:
                self.errors.append({'message': 'Kurung tutup ) tidak ditemukan pada kolom REFERENCES', 'line': defs[-1].line, 'column': defs[-1].column})
                return
        if i < len(defs) and def_upper[i] == 'REFERENCES':
            i += 1
            if i >= len(defs):
                self.errors.append({'message': 'Nama tabel tujuan REFERENCES tidak boleh kosong', 'line': defs[-1].line, 'column': defs[-1].column})
                return
            i += 1
            if i < len(defs) and defs[i].value == '(':
                i += 1
                while i < len(defs) and defs[i].value != ')':
                    i += 1
                if i < len(defs):
                    i += 1
                else:
                    self.errors.append({'message': 'Kurung tutup ) tidak ditemukan pada REFERENCES', 'line': defs[-1].line, 'column': defs[-1].column})
                    return

    def _validate_create_index(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        idx = upper.index('INDEX') if 'INDEX' in upper else -1
        if idx < 0 or idx + 1 >= len(tokens):
            self.errors.append({'message': 'Nama index tidak boleh kosong setelah INDEX', 'line': tokens[0].line, 'column': tokens[0].column + 6})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        idx_name_end = idx + 1
        if 'ON' in upper:
            on_idx = upper.index('ON')
            if on_idx <= idx:
                self.errors.append({'message': 'Diharapkan ON setelah nama index', 'line': tokens[idx_name_end].line, 'column': tokens[idx_name_end].column})
                return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

            open_paren = None
            for i in range(on_idx + 1, len(tokens)):
                if tokens[i].value == '(':
                    open_paren = i
                    break
            if open_paren is None:
                self.errors.append({'message': 'Diharapkan ( setelah ON untuk nama tabel', 'line': tokens[on_idx].line, 'column': tokens[on_idx].column + 2})
                return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

            paren_depth = 1
            for i in range(open_paren + 1, len(tokens)):
                if tokens[i].value == '(': paren_depth += 1
                elif tokens[i].value == ')':
                    paren_depth -= 1
                    if paren_depth == 0:
                        break
            if paren_depth > 0:
                self.errors.append({'message': 'Kurung tutup ) tidak ditemukan untuk daftar kolom index', 'line': tokens[-1].line, 'column': tokens[-1].column + 1})

        status = 'VALID' if not self.errors else 'INVALID'
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_create_view(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        view_idx = upper.index('VIEW') if 'VIEW' in upper else -1
        if view_idx < 0 or view_idx + 1 >= len(tokens):
            self.errors.append({'message': 'Nama view tidak boleh kosong setelah VIEW', 'line': tokens[0].line, 'column': tokens[0].column + 6})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        if 'AS' not in upper:
            self.errors.append({'message': 'Diharapkan AS setelah nama view untuk menentukan query', 'line': tokens[-1].line, 'column': tokens[-1].column})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        status = 'VALID' if not self.errors else 'INVALID'
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_alter_table(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        alter_idx = upper.index('ALTER')
        table_idx = upper.index('TABLE')

        if table_idx + 1 >= len(tokens):
            self.errors.append({'message': 'Nama tabel tidak boleh kosong setelah ALTER TABLE', 'line': tokens[table_idx].line, 'column': tokens[table_idx].column + 5})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        after_table = upper[table_idx + 2:] if table_idx + 2 < len(upper) else []
        if not after_table:
            self.errors.append({'message': 'Tidak ada operasi yang ditentukan (contoh: ADD, DROP, MODIFY)', 'line': tokens[table_idx].line, 'column': tokens[table_idx].column + 5})
            return {'status': 'INVALID', 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

        alter_ops = after_table
        if alter_ops[0] in ('ADD', 'DROP', 'MODIFY', 'RENAME', 'ALTER'):
            if alter_ops[0] == 'ADD' and len(alter_ops) > 1:
                if alter_ops[1] in ('COLUMN', 'CONSTRAINT'):
                    pass
            elif alter_ops[0] == 'DROP' and len(alter_ops) > 1:
                if alter_ops[1] in ('COLUMN', 'CONSTRAINT', 'INDEX', 'KEY', 'PRIMARY'):
                    pass
            elif alter_ops[0] == 'RENAME' and len(alter_ops) > 1:
                if alter_ops[1] in ('TO', 'COLUMN', 'INDEX'):
                    pass
        else:
            self.errors.append({'message': f'Operasi ALTER TABLE tidak dikenal: {alter_ops[0]}', 'line': tokens[table_idx + 2].line, 'column': tokens[table_idx + 2].column})

        status = 'VALID' if not self.errors else 'INVALID'
        return {'status': status, 'errors': self.errors, 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_merge(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        return {'status': 'VALID', 'errors': [], 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_tcl(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        return {'status': 'VALID', 'errors': [], 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _validate_sp(self, tokens, upper):
        pt = self._build_generic_tree(tokens)
        return {'status': 'VALID', 'errors': [], 'warnings': self.warnings, 'parse_tree': pt.to_dict()}

    def _check_select_order(self, tokens, upper):
        if 'FROM' in upper and 'SELECT' in upper:
            si, fi = upper.index('SELECT'), upper.index('FROM')
            if fi < si:
                self.errors.append({'message': 'Klausa FROM harus muncul setelah SELECT', 'line': tokens[fi].line, 'column': tokens[fi].column})
            if si + 1 >= fi:
                self.errors.append({'message': 'Daftar kolom SELECT tidak boleh kosong', 'line': tokens[si].line, 'column': tokens[si].column})
            clause_pos = {}
            for kw in CLAUSE_ORDER:
                try: clause_pos[kw] = upper.index(kw)
                except ValueError: pass
            for i in range(len(CLAUSE_ORDER) - 1):
                k1, k2 = CLAUSE_ORDER[i], CLAUSE_ORDER[i+1]
                if k1 in clause_pos and k2 in clause_pos and clause_pos[k1] > clause_pos[k2]:
                    self.errors.append({'message': f'Urutan klausa salah: {k2} muncul sebelum {k1}',
                        'line': tokens[clause_pos[k2]].line, 'column': tokens[clause_pos[k2]].column})
            for kw in ['GROUP', 'ORDER']:
                if kw in clause_pos:
                    idx = clause_pos[kw]
                    if idx + 1 < len(tokens) and upper[idx + 1] != 'BY':
                        self.errors.append({'message': f'Diharapkan BY setelah {kw}', 'line': tokens[idx].line, 'column': tokens[idx].column + 5})

    def _check_cartesian_join(self, tokens, upper):
        join_indices = [i for i, v in enumerate(upper) if v == 'JOIN']
        if not join_indices:
            return
        for ji in join_indices:
            if ji > 0 and upper[ji - 1] == 'CROSS':
                continue
            on_after = [i for i, v in enumerate(upper[ji:], ji) if v == 'ON']
            next_clause = None
            for kw in ['WHERE', 'GROUP', 'ORDER', 'HAVING', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL']:
                candidates = [i for i, v in enumerate(upper[ji:], ji) if v == kw]
                if candidates:
                    for c in candidates:
                        if c != ji:
                            next_clause = c if next_clause is None else min(next_clause, c)
                            break
            on_found = on_after and (on_after[0] < next_clause if next_clause else True)
            if not on_found:
                self.warnings.append({
                    'type': 'CARTESIAN_JOIN',
                    'message': f'JOIN pada baris {tokens[ji].line} tidak memiliki kondisi ON - ini menghasilkan Cartesian product',
                    'line': tokens[ji].line,
                    'column': tokens[ji].column,
                    'suggestion': 'Tambahkan kondisi ON setelah JOIN (contoh: ... JOIN t2 ON t1.id = t2.id)'
                })

    def _build_select_tree(self, tokens, upper):
        root = ParseNode(type='QUERY', value='SQL Query')
        stmt = ParseNode(type='STATEMENT', value='SELECT')
        root.children.append(stmt)

        clause_pos = {}
        for kw in CLAUSE_ORDER:
            try: clause_pos[kw] = upper.index(kw)
            except ValueError: pass

        if 'SELECT' in clause_pos:
            n = ParseNode(type='CLAUSE', value='SELECT')
            si = clause_pos['SELECT']
            end = clause_pos.get('FROM') if 'FROM' in clause_pos else len(tokens)
            for t in tokens[si:end]:
                n.children.append(ParseNode(type=t.type, value=t.value, token=t))
            stmt.children.append(n)

        if 'FROM' in clause_pos:
            n = ParseNode(type='CLAUSE', value='FROM')
            fi = clause_pos['FROM']
            end = clause_pos.get('WHERE') or clause_pos.get('GROUP') or clause_pos.get('HAVING') or clause_pos.get('ORDER') or len(tokens)
            for t in tokens[fi:end]:
                n.children.append(ParseNode(type=t.type, value=t.value, token=t))
            stmt.children.append(n)

        for kw in ['WHERE', 'GROUP', 'HAVING', 'ORDER']:
            if kw in clause_pos:
                n = ParseNode(type='CLAUSE', value=kw)
                ki = clause_pos[kw]
                next_kws = {'WHERE': 'GROUP', 'GROUP': 'HAVING', 'HAVING': 'ORDER', 'ORDER': None}
                next_kw = next_kws.get(kw)
                end = clause_pos.get(next_kw) if next_kw and next_kw in clause_pos else len(tokens)
                for t in tokens[ki:end]:
                    n.children.append(ParseNode(type=t.type, value=t.value, token=t))
                stmt.children.append(n)

        return root

    def _build_generic_tree(self, tokens):
        root = ParseNode(type='QUERY', value='SQL Query')

        keywords = []
        current_group = []
        for t in tokens:
            if t.type == 'KEYWORD':
                if current_group:
                    keywords.append(current_group)
                current_group = [t]
            else:
                current_group.append(t)
        if current_group:
            keywords.append(current_group)

        for group in keywords:
            kw = group[0].value.upper()
            if kw in ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'MERGE',
                       'BEGIN', 'COMMIT', 'ROLLBACK', 'DECLARE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE'):
                stmt = ParseNode(type='STATEMENT', value=kw)
                for t in group:
                    stmt.children.append(ParseNode(type=t.type, value=t.value, token=t))
                root.children.append(stmt)
            else:
                parent = root
                if root.children and root.children[-1].type == 'STATEMENT':
                    parent = root.children[-1]
                for t in group:
                    parent.children.append(ParseNode(type=t.type, value=t.value, token=t))

        if not root.children:
            for t in tokens:
                root.children.append(ParseNode(type=t.type, value=t.value, token=t))

        return root
