from typing import List, Dict, Any
from .lexer import Token

class ComplexityAnalyzer:
    def analyze(self, tokens: List[Token], query: str) -> Dict[str, Any]:
        if not tokens:
            return self._empty(query)

        upper = [t.value.upper() for t in tokens]

        joins = sum(1 for k in ['JOIN', 'INNER', 'LEFT', 'RIGHT', 'CROSS', 'FULL'] for _ in [0] if k in upper)
        joins = max(0, joins - 1) if 'JOIN' in upper else joins

        subqueries = 0
        depth = 0
        for t in tokens:
            if t.value == '(' and t.type == 'SYMBOL': depth += 1
            elif t.value == ')' and t.type == 'SYMBOL': depth -= 1
            if depth > 1: subqueries += 1
        subqueries = max(0, subqueries // 2)

        conditions = sum(upper.count(k) for k in ['AND', 'OR', 'WHERE', 'HAVING'])
        aggregates = sum(1 for t in tokens if t.type == 'AGGREGATE')
        keywords = sum(1 for t in tokens if t.type == 'KEYWORD')
        identifiers = sum(1 for t in tokens if t.type == 'IDENTIFIER')
        variables = sum(1 for t in tokens if t.type in ('VARIABLE', 'TEMP_TABLE'))
        operators = sum(1 for t in tokens if t.type == 'OPERATOR')
        literals = sum(1 for t in tokens if t.type in ('LITERAL', 'NUMBER'))
        length = len(query)
        token_count = len(tokens)

        score = 0
        score += min(joins * 15, 30)
        score += min(subqueries * 12, 25)
        score += min(conditions * 5, 20)
        score += min(aggregates * 8, 20)
        score += min(keywords * 2, 15)
        score += min(variables * 3, 10)
        score += min(operators * 2, 10)
        score += min(length // 100, 10)
        score = min(score, 100)

        category = 'Sederhana' if score <= 20 else 'Sedang' if score <= 40 else 'Kompleks' if score <= 65 else 'Sangat Kompleks'

        return {
            'score': score,
            'category': category,
            'metrics': {
                'join_count': joins,
                'subquery_count': subqueries,
                'condition_count': conditions,
                'aggregate_count': aggregates,
                'keyword_count': keywords,
                'identifier_count': identifiers,
                'variable_count': variables,
                'operator_count': operators,
                'literal_count': literals,
                'query_length': length,
                'token_count': token_count,
            },
            'breakdown': {
                'JOIN': joins,
                'Subquery': subqueries,
                'Kondisi': conditions,
                'Agregat': aggregates,
                'Keyword': keywords,
                'Variabel': variables,
                'Operator': operators,
                'Literal': literals,
            },
        }

    def _empty(self, query):
        return {
            'score': 0, 'category': 'Sederhana',
            'metrics': {k: 0 for k in ['join_count', 'subquery_count', 'condition_count', 'aggregate_count',
                                        'keyword_count', 'identifier_count', 'variable_count', 'operator_count',
                                        'literal_count', 'query_length', 'token_count']},
            'breakdown': {},
        }
