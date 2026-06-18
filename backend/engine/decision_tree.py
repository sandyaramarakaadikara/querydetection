from typing import List, Dict, Any
from .lexer import Token

class DecisionTreeBuilder:
    def build(self, query: str, tokens: List[Token], syntax: Dict[str, Any],
              injection: Dict[str, Any], complexity: Dict[str, Any]) -> Dict[str, Any]:
        upper = [t.value.upper() for t in tokens] if tokens else []

        tree = {
            'name': 'Input Query',
            'type': 'root',
            'status': 'success',
            'detail': query[:80] + ('...' if len(query) > 80 else ''),
            'children': []
        }

        token_node = {
            'name': 'Tokenisasi',
            'type': 'step',
            'status': 'success' if tokens else 'error',
            'detail': f'{len(tokens)} token berhasil dikenali',
            'children': []
        }
        tree['children'].append(token_node)

        if tokens:
            stmt_node = self._classify_statement(upper, tokens)
            tree['children'].append(stmt_node)

            valid_node = self._validate_syntax(syntax, upper)
            tree['children'].append(valid_node)

            if injection:
                inject_node = self._check_injection(injection)
                tree['children'].append(inject_node)

            if complexity:
                comp_node = self._assess_complexity(complexity)
                tree['children'].append(comp_node)

        summary = self._build_summary(syntax, injection, complexity)
        tree['children'].append(summary)

        return tree

    def _classify_statement(self, upper, tokens) -> Dict[str, Any]:
        stmt_types = {
            'SELECT': 'SELECT',
            'INSERT': 'INSERT',
            'UPDATE': 'UPDATE',
            'DELETE': 'DELETE',
            'CREATE': 'DDL (CREATE)',
            'DROP': 'DDL (DROP)',
            'ALTER': 'DDL (ALTER)',
            'TRUNCATE': 'DDL (TRUNCATE)',
            'MERGE': 'MERGE',
            'BEGIN': 'TCL (Transaction)',
            'COMMIT': 'TCL (Transaction)',
            'ROLLBACK': 'TCL (Transaction)',
            'DECLARE': 'Stored Procedure',
            'EXEC': 'Stored Procedure',
            'EXECUTE': 'Stored Procedure',
        }
        stmt_found = 'UNKNOWN'
        for kw, label in stmt_types.items():
            if kw in upper:
                stmt_found = label
                break

        has_cte = 'WITH' in upper
        has_join = any(k in upper for k in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'CROSS', 'FULL'])
        has_subquery = False
        depth = 0
        for t in tokens:
            if t.value == '(' and t.type == 'SYMBOL': depth += 1
            elif t.value == ')' and t.type == 'SYMBOL': depth -= 1
            if depth > 0 and t.value.upper() == 'SELECT': has_subquery = True

        details = [f'Statement: {stmt_found}']
        if has_cte: details.append('Menggunakan CTE (WITH)')
        if has_join: details.append('Terdapat JOIN')
        if has_subquery: details.append('Terdapat subquery')

        children = []
        if has_cte:
            children.append({'name': 'CTE', 'type': 'feature', 'status': 'success', 'detail': 'WITH clause terdeteksi', 'children': []})
        if has_join:
            children.append({'name': 'JOIN', 'type': 'feature', 'status': 'success', 'detail': 'Tabel digabungkan', 'children': []})
        if has_subquery:
            children.append({'name': 'Subquery', 'type': 'feature', 'status': 'success', 'detail': 'Query bersarang', 'children': []})

        return {
            'name': 'Klasifikasi',
            'type': 'decision',
            'status': 'success',
            'detail': '; '.join(details),
            'children': children,
        }

    def _validate_syntax(self, syntax, upper) -> Dict[str, Any]:
        is_valid = syntax.get('status') == 'VALID'
        errors = syntax.get('errors', [])
        warnings = syntax.get('warnings', [])

        children = []

        clause_checks = []
        clause_order = ['SELECT', 'FROM', 'WHERE', 'GROUP', 'HAVING', 'ORDER']
        found = [kw for kw in clause_order if kw in upper]
        if found:
            clause_checks.append(f'Klausa: {" → ".join(found)}')
            if is_valid:
                clause_checks.append('Urutan klausa benar')
            else:
                clause_checks.append('Urutan klausa bermasalah')
            children.append({
                'name': 'Urutan Klausa',
                'type': 'check',
                'status': 'success' if is_valid else 'error',
                'detail': ' → '.join(found),
                'children': [],
            })

        if errors:
            for e in errors:
                children.append({
                    'name': 'Error',
                    'type': 'error',
                    'status': 'error',
                    'detail': e.get('message', 'Unknown error'),
                    'children': [],
                })

        if warnings:
            for w in warnings:
                children.append({
                    'name': 'Peringatan',
                    'type': 'warning',
                    'status': 'warning',
                    'detail': w.get('message', ''),
                    'children': [],
                })

        if is_valid and not errors and not warnings:
            children.append({
                'name': 'Grammar',
                'type': 'check',
                'status': 'success',
                'detail': 'Semua aturan sintaks terpenuhi',
                'children': [],
            })

        return {
            'name': 'Validasi Sintaks',
            'type': 'decision',
            'status': 'success' if is_valid else 'error',
            'detail': f'Query {"VALID" if is_valid else "TIDAK VALID"} ({len(errors)} error, {len(warnings)} warning)',
            'children': children,
        }

    def _check_injection(self, injection) -> Dict[str, Any]:
        is_vuln = injection.get('is_vulnerable', False)
        findings = injection.get('findings', [])
        risk = injection.get('risk_level', 'None')

        children = []
        for f in findings:
            children.append({
                'name': f.get('type', 'Unknown'),
                'type': 'finding',
                'status': 'warning' if f.get('severity') in ('Medium', 'Low') else 'error',
                'detail': f.get('description', ''),
                'children': [],
            })

        if not is_vuln:
            children.append({
                'name': 'Aman',
                'type': 'check',
                'status': 'success',
                'detail': 'Tidak terdeteksi pola injeksi',
                'children': [],
            })

        return {
            'name': 'Deteksi Injeksi',
            'type': 'decision',
            'status': 'warning' if is_vuln else 'success',
            'detail': f'Risk Level: {risk} ({len(findings)} temuan)' if is_vuln else 'Tidak ada ancaman',
            'children': children,
        }

    def _assess_complexity(self, complexity) -> Dict[str, Any]:
        score = complexity.get('score', 0)
        category = complexity.get('category', 'Sederhana')
        metrics = complexity.get('metrics', {})

        children = [
            {'name': f'Skor: {score}/100', 'type': 'metric', 'status': 'success' if score <= 40 else 'warning' if score <= 65 else 'error', 'detail': f'Kategori: {category}', 'children': []},
        ]

        active_metrics = {k: v for k, v in metrics.items() if v and v > 0 and k not in ('query_length', 'token_count')}
        for k, v in list(active_metrics.items())[:5]:
            label = k.replace('_', ' ').title()
            children.append({
                'name': label,
                'type': 'metric',
                'status': 'success',
                'detail': f'{v} item',
                'children': [],
            })

        return {
            'name': 'Kompleksitas',
            'type': 'decision',
            'status': 'success' if score <= 40 else 'warning' if score <= 65 else 'error',
            'detail': f'{category} ({score}/100)',
            'children': children,
        }

    def _build_summary(self, syntax, injection, complexity) -> Dict[str, Any]:
        is_valid = syntax.get('status') == 'VALID'
        errors = len(syntax.get('errors', []))
        warnings = len(syntax.get('warnings', []))
        is_vuln = injection.get('is_vulnerable', False) if injection else False
        injection_count = len(injection.get('findings', [])) if injection else 0
        score = complexity.get('score', 0) if complexity else 0

        issues = []
        if not is_valid: issues.append(f'{errors} error sintaks')
        if warnings: issues.append(f'{warnings} peringatan')
        if is_vuln: issues.append(f'{injection_count} kerentanan injeksi')
        if score > 65: issues.append('Kompleksitas tinggi')

        status = 'error' if not is_valid else 'warning' if (warnings or is_vuln or score > 65) else 'success'
        detail = '; '.join(issues) if issues else 'Query aman dan valid'

        return {
            'name': 'Kesimpulan',
            'type': 'summary',
            'status': status,
            'detail': detail,
            'children': [],
        }
