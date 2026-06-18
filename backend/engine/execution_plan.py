from typing import List, Dict, Any
from .lexer import Token

STEPS_SELECT = [
    ('TABLE_SCAN', 'Memindai tabel', 10),
    ('INDEX_SCAN', 'Memindai indeks', 5),
    ('JOIN', 'Menggabungkan tabel', 15),
    ('FILTER', 'Menyaring baris (WHERE)', 3),
    ('GROUP_BY', 'Mengelompokkan baris', 7),
    ('HAVING', 'Menyaring grup', 4),
    ('AGGREGATE', 'Menghitung fungsi agregat', 6),
    ('SORT', 'Mengurutkan hasil', 8),
    ('PROJECTION', 'Memilih kolom', 2),
    ('RESULT', 'Mengembalikan hasil', 1),
]

STEPS_INSERT = [
    ('TABLE_SCAN', 'Memeriksa constraint tabel', 5),
    ('VALIDATE', 'Memvalidasi data input', 3),
    ('WRITE', 'Menulis baris baru', 8),
    ('LOG', 'Mencatat ke transaction log', 2),
    ('RESULT', 'Mengembalikan jumlah baris', 1),
]

STEPS_UPDATE = [
    ('TABLE_SCAN', 'Memindai tabel target', 8),
    ('FILTER', 'Menyaring baris (WHERE)', 4),
    ('COMPUTE', 'Menghitung nilai baru', 5),
    ('WRITE', 'Menulis perubahan', 8),
    ('LOG', 'Mencatat ke transaction log', 2),
    ('RESULT', 'Mengembalikan jumlah baris', 1),
]

STEPS_DELETE = [
    ('TABLE_SCAN', 'Memindai tabel target', 8),
    ('FILTER', 'Menyaring baris (WHERE)', 4),
    ('DELETE', 'Menghapus baris', 10),
    ('LOG', 'Mencatat ke transaction log', 2),
    ('RESULT', 'Mengembalikan jumlah baris', 1),
]

STEPS_DDL = [
    ('VALIDATE', 'Memvalidasi pernyataan DDL', 3),
    ('SCHEMA_LOCK', 'Mengunci skema database', 5),
    ('EXECUTE_DDL', 'Menjalankan perintah DDL', 15),
    ('UPDATE_CATALOG', 'Memperbarui katalog sistem', 5),
    ('COMMIT_DDL', 'Menyelesaikan perubahan', 2),
    ('RESULT', 'Mengembalikan hasil', 1),
]

STEPS_TCL = [
    ('BEGIN_TXN', 'Memulai transaksi', 2),
    ('COMMIT_TXN', 'Menyelesaikan transaksi', 3),
    ('ROLLBACK_TXN', 'Membatalkan transaksi', 4),
    ('RESULT', 'Mengembalikan hasil', 1),
]

STEPS_SP = [
    ('PARSE', 'Mengurai pernyataan', 3),
    ('COMPILE', 'Mengkompilasi', 8),
    ('EXECUTE', 'Menjalankan', 10),
    ('RETURN', 'Mengembalikan hasil', 2),
    ('RESULT', 'Selesai', 1),
]

class ExecutionPlanSimulator:
    def simulate(self, tokens: List[Token]) -> Dict[str, Any]:
        upper = [t.value.upper() for t in tokens]
        steps = []

        if 'INSERT' in upper:
            steps = self._build_steps(STEPS_INSERT, upper, tokens)
        elif 'UPDATE' in upper:
            steps = self._build_steps(STEPS_UPDATE, upper, tokens)
        elif 'DELETE' in upper and 'SELECT' not in upper:
            steps = self._build_steps(STEPS_DELETE, upper, tokens)
        elif 'CREATE' in upper or 'DROP' in upper or 'ALTER' in upper or 'TRUNCATE' in upper:
            steps = self._build_steps(STEPS_DDL, upper, tokens)
        elif 'BEGIN' in upper or 'COMMIT' in upper or 'ROLLBACK' in upper:
            steps = self._build_steps(STEPS_TCL, upper, tokens)
        elif 'EXEC' in upper or 'DECLARE' in upper:
            steps = self._build_steps(STEPS_SP, upper, tokens)
        elif 'MERGE' in upper:
            steps_steps = [('TABLE_SCAN', 'Memindai tabel sumber & target', 10),
                           ('MATCH', 'Mencocokkan baris', 8),
                           ('INSERT', 'Menyisipkan baris baru', 8),
                           ('UPDATE', 'Memperbarui baris yang cocok', 8),
                           ('LOG', 'Mencatat perubahan', 2),
                           ('RESULT', 'Mengembalikan hasil', 1)]
            steps = self._build_steps(steps_steps, upper, tokens)
        else:
            has_join = any(k in upper for k in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'CROSS', 'FULL'])
            has_where = 'WHERE' in upper
            has_order = 'ORDER' in upper
            has_group = 'GROUP' in upper
            has_having = 'HAVING' in upper
            has_agg = any(t.type == 'AGGREGATE' for t in tokens)

            sel_steps = []
            sel_steps.append(('TABLE_SCAN', 'Memindai tabel', 10))
            if has_join: sel_steps.append(('JOIN', 'Menggabungkan tabel', 15))
            if has_where: sel_steps.append(('FILTER', 'Menyaring baris (WHERE)', 3))
            if has_group: sel_steps.append(('GROUP_BY', 'Mengelompokkan baris', 7))
            if has_having: sel_steps.append(('HAVING', 'Menyaring grup', 4))
            if has_agg: sel_steps.append(('AGGREGATE', 'Menghitung fungsi agregat', 6))
            if has_order: sel_steps.append(('SORT', 'Mengurutkan hasil', 8))
            sel_steps.append(('PROJECTION', 'Memilih kolom', 2))
            sel_steps.append(('RESULT', 'Mengembalikan hasil', 1))
            steps = self._build_steps(sel_steps, upper, tokens)

        total_cost = sum(s['cost'] for s in steps)
        return {'steps': steps, 'total_cost': total_cost, 'total_steps': len(steps), 'estimated_rows': self._estimate(tokens)}

    def _build_steps(self, template, upper, tokens):
        has_agg = any(t.type == 'AGGREGATE' for t in tokens)
        steps = []
        for i, (op, detail, cost) in enumerate(template):
            include = True
            if op == 'FILTER' and 'WHERE' not in upper: include = False
            if op == 'SORT' and 'ORDER' not in upper: include = False
            if op == 'GROUP_BY' and 'GROUP' not in upper: include = False
            if op == 'HAVING' and 'HAVING' not in upper: include = False
            if op == 'JOIN' and not any(k in upper for k in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'CROSS', 'FULL']): include = False
            if op == 'AGGREGATE' and not has_agg: include = False
            if include:
                steps.append({'id': f'step_{i+1}', 'operation': op, 'label': op.replace('_', ' '), 'detail': detail, 'cost': cost, 'order': len(steps)+1})
        return steps

    def _estimate(self, tokens):
        upper = [t.value.upper() for t in tokens]
        base = 1000
        if 'WHERE' in upper: base = int(base * 0.3)
        if 'GROUP' in upper: base = int(base * 0.5)
        if any(k in upper for k in ['JOIN', 'INNER', 'LEFT', 'RIGHT']): base *= 5
        if 'HAVING' in upper: base = int(base * 0.4)
        if 'INSERT' in upper: base = 1
        if 'UPDATE' in upper: base = int(base * 0.2)
        if 'DELETE' in upper: base = int(base * 0.2)
        return max(base, 1)
