import re
from dataclasses import dataclass
from typing import List, Tuple

SQL_KEYWORDS = {
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'EXISTS',
    'ORDER', 'BY', 'GROUP', 'HAVING', 'DISTINCT', 'AS', 'ON',
    'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER', 'CROSS', 'FULL', 'NATURAL',
    'UNION', 'ALL', 'INTERSECT', 'EXCEPT',
    'IS', 'NULL', 'TRUE', 'FALSE',
    'ASC', 'DESC', 'LIMIT', 'OFFSET', 'TOP',
    'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
    'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
    'CREATE', 'TABLE', 'DROP', 'ALTER', 'TRUNCATE',
    'INDEX', 'VIEW', 'SEQUENCE', 'SCHEMA', 'DATABASE',
    'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE', 'CHECK', 'DEFAULT', 'CONSTRAINT',
    'ADD', 'COLUMN', 'MODIFY', 'RENAME', 'CASCADE', 'RESTRICT',
    'IF', 'THEN', 'ELSE', 'END',
    'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT', 'TRANSACTION',
    'GRANT', 'REVOKE', 'DENY',
    'EXEC', 'EXECUTE', 'PROCEDURE', 'FUNCTION', 'TRIGGER', 'PACKAGE',
    'DECLARE', 'CURSOR', 'FETCH', 'OPEN', 'CLOSE',
    'WITH', 'RECURSIVE', 'TEMP', 'TEMPORARY',
    'REPLACE', 'RETURN', 'RETURNS',
    'SLEEP', 'WAITFOR', 'DELAY',
    'PRINT', 'RAISERROR', 'THROW',
    'USE', 'GO', 'SET',
    'ROW', 'ROWS', 'RANGE', 'UNBOUNDED', 'PRECEDING', 'FOLLOWING',
    'OVER', 'PARTITION', 'LATERAL', 'PIVOT', 'UNPIVOT',
    'MERGE', 'MATCHED',
    'FOR', 'XML', 'JSON', 'PATH', 'ROOT', 'AUTO',
    'OUTPUT', 'INTO', 'BULK', 'OPENROWSET', 'OPENDATASOURCE',
    'SERIALIZABLE', 'READ', 'REPEATABLE', 'COMMITTED', 'UNCOMMITTED',
    'NOCHECK', 'WITH', 'TABLOCK', 'XLOCK', 'UPDLOCK', 'HOLDLOCK', 'NOLOCK',
    'OPTIMIZE', 'RECOMPILE',
}

AGGREGATE_FUNCTIONS = {'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'}

SQL_OPERATORS = {
    '>=', '<=', '!=', '<>', '=', '>', '<', '+', '-', '*', '/', '%', '||',
}

@dataclass
class Token:
    type: str
    value: str
    position: int
    line: int
    column: int

    def to_dict(self):
        return {'type': self.type, 'value': self.value, 'position': self.position, 'line': self.line, 'column': self.column}

class SQLLexer:
    def __init__(self):
        self.state_count = 0

    def tokenize(self, query: str) -> Tuple[List[Token], List[dict], str]:
        self.state_count = 0
        tokens = []
        i = 0
        line = 1
        last_newline = 0

        while i < len(query):
            ch = query[i]

            if ch == '\n':
                line += 1; last_newline = i + 1; i += 1
                continue

            if ch in ' \t\r':
                i += 1
                continue

            column = i - last_newline + 1

            if ch == '-' and i + 1 < len(query) and query[i + 1] == '-':
                end = query.find('\n', i)
                i = len(query) if end == -1 else end
                continue

            if ch == '/' and i + 1 < len(query) and query[i + 1] == '*':
                end = query.find('*/', i + 2)
                i = len(query) if end == -1 else end + 2
                continue

            if ch == "'":
                self.state_count += 1
                start = i; i += 1
                while i < len(query):
                    if query[i] == "'" and (i + 1 >= len(query) or query[i + 1] != "'"):
                        i += 1; break
                    if query[i] == "'" and i + 1 < len(query) and query[i + 1] == "'":
                        i += 2; continue
                    if query[i] == '\n':
                        line += 1; last_newline = i + 1
                    i += 1
                tokens.append(Token(type='LITERAL', value=query[start:i], position=start, line=line, column=column))
                continue

            if ch.isdigit():
                self.state_count += 1
                start = i
                while i < len(query) and (query[i].isdigit() or query[i] == '.'):
                    i += 1
                tokens.append(Token(type='NUMBER', value=query[start:i], position=start, line=line, column=column))
                continue

            if ch.isalpha() or ch == '_' or ch == '@' or ch == '#':
                self.state_count += 1
                start = i
                if ch == '@':
                    i += 1
                while i < len(query) and (query[i].isalnum() or query[i] in '_@#$'):
                    i += 1
                val = query[start:i]
                upper_val = val.upper()
                if upper_val in SQL_KEYWORDS:
                    token_type = 'AGGREGATE' if upper_val in AGGREGATE_FUNCTIONS else 'KEYWORD'
                elif val.startswith('@@'):
                    token_type = 'SYSTEM_VARIABLE'
                elif val.startswith('@'):
                    token_type = 'VARIABLE'
                elif val.startswith('#'):
                    token_type = 'TEMP_TABLE'
                else:
                    token_type = 'IDENTIFIER'
                tokens.append(Token(type=token_type, value=val, position=start, line=line, column=column))
                continue

            if ch in '=<>!+*-/%|':
                start = i
                two_ch = query[i:i+2] if i + 1 < len(query) else ''
                if two_ch in SQL_OPERATORS:
                    tokens.append(Token(type='OPERATOR', value=two_ch, position=start, line=line, column=column))
                    i += 2; continue
                elif ch in '=<>!+*-/%|':
                    tokens.append(Token(type='OPERATOR', value=ch, position=start, line=line, column=column))
                    i += 1; continue

            if ch in '(),.;*':
                tokens.append(Token(type='SYMBOL', value=ch, position=i, line=line, column=column))
                i += 1
                continue

            if ch == '[':
                start = i; i += 1
                while i < len(query) and query[i] != ']':
                    if query[i] == '\n': line += 1; last_newline = i + 1
                    i += 1
                if i < len(query): i += 1
                tokens.append(Token(type='IDENTIFIER', value=query[start:i], position=start, line=line, column=column))
                continue

            if ch == '"':
                start = i; i += 1
                while i < len(query) and query[i] != '"':
                    if query[i] == '\n': line += 1; last_newline = i + 1
                    i += 1
                if i < len(query): i += 1
                tokens.append(Token(type='IDENTIFIER', value=query[start:i], position=start, line=line, column=column))
                continue

            i += 1

        dfa_states = [{'state': i+1, 'token_type': t.type, 'is_final': i == len(tokens) - 1, 'is_accepted': True} for i, t in enumerate(tokens)]
        return tokens, dfa_states, ''
