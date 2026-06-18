from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple, Optional

# ---------------------------------------------------------------------------
# Character class predicates (used by SFA)
# ---------------------------------------------------------------------------
def is_letter(c: str) -> bool:
    return c.isalpha() or c == '_'

def is_digit(c: str) -> bool:
    return c.isdigit()

def is_alnum_ext(c: str) -> bool:
    return c.isalnum() or c in '_@#$'

def is_operator_char(c: str) -> bool:
    return c in '=<>!+*-/%|'

def is_symbol_char(c: str) -> bool:
    return c in '(),.;'

def is_whitespace(c: str) -> bool:
    return c in ' \t\n\r'

def is_quote_single(c: str) -> bool:
    return c == "'"

def is_quote_double(c: str) -> bool:
    return c == '"'

def is_bracket_open(c: str) -> bool:
    return c == '['

def is_bracket_close(c: str) -> bool:
    return c == ']'

def is_dash(c: str) -> bool:
    return c == '-'

def is_slash(c: str) -> bool:
    return c == '/'

def is_star(c: str) -> bool:
    return c == '*'

def is_at(c: str) -> bool:
    return c == '@'

def is_hash(c: str) -> bool:
    return c == '#'

def is_newline(c: str) -> bool:
    return c == '\n'

def is_semicolon(c: str) -> bool:
    return c == ';'

def is_dot(c: str) -> bool:
    return c == '.'

# ---------------------------------------------------------------------------
# Predicate → predicate name mapping (for SFA display)
# ---------------------------------------------------------------------------
PRED_MAP = {
    'is_letter': is_letter, 'is_digit': is_digit, 'is_alnum_ext': is_alnum_ext,
    'is_operator_char': is_operator_char, 'is_symbol_char': is_symbol_char,
    'is_whitespace': is_whitespace, 'is_quote_single': is_quote_single,
    'is_quote_double': is_quote_double, 'is_bracket_open': is_bracket_open,
    'is_bracket_close': is_bracket_close, 'is_dash': is_dash, 'is_slash': is_slash,
    'is_star': is_star, 'is_at': is_at, 'is_hash': is_hash, 'is_newline': is_newline,
    'is_semicolon': is_semicolon, 'is_dot': is_dot,
}

# ---------------------------------------------------------------------------
# State / Transition definitions
# ---------------------------------------------------------------------------
EPSILON = 'EPSILON'
PREDICATE = 'PREDICATE'

@dataclass
class Transition:
    kind: str
    target: int
    predicate: Optional[str] = None  # for PREDICATE type

@dataclass
class NFAState:
    id: int
    label: str
    transitions: List[Transition] = field(default_factory=list)
    is_start: bool = False
    is_accept: bool = False
    accept_type: str = ''

# ---------------------------------------------------------------------------
# SQL Lexer NFA
# ---------------------------------------------------------------------------
def build_sql_nfa() -> Dict[int, NFAState]:
    s: Dict[int, NFAState] = {}
    def add(sid, label, start=False, accept=False, atype=''):
        s[sid] = NFAState(id=sid, label=label, is_start=start, is_accept=accept, accept_type=atype)
    def eps(fr, to):
        s[fr].transitions.append(Transition(kind=EPSILON, target=to))
    def pred(fr, to, pname):
        s[fr].transitions.append(Transition(kind=PREDICATE, target=to, predicate=pname))

    # ── States ──────────────────────────────────────────────────────────
    add(0,  'START', start=True)
    add(1,  'IN_KEYWORD')
    add(2,  'IN_NUMBER')
    add(3,  'IN_STRING')
    add(4,  'IN_OPERATOR')
    add(5,  'IN_LINE_COMMENT')
    add(6,  'IN_BLOCK_COMMENT')
    add(7,  'IN_QUOTED_ID')
    add(8,  'IN_BRACKET_ID')
    add(9,  'IN_VARIABLE')
    add(10, 'IN_TEMP_TABLE')
    add(11, 'IN_AGGREGATE')
    add(12, 'IN_SYMBOL')
    add(13, 'IN_DECIMAL')
    add(14, 'DONE_KEYWORD', accept=True, atype='KEYWORD')
    add(15, 'DONE_NUMBER', accept=True, atype='NUMBER')
    add(16, 'DONE_STRING', accept=True, atype='LITERAL')
    add(17, 'DONE_OPERATOR', accept=True, atype='OPERATOR')
    add(18, 'DONE_SYMBOL', accept=True, atype='SYMBOL')
    add(19, 'DONE_IDENTIFIER', accept=True, atype='IDENTIFIER')
    add(20, 'DONE_VARIABLE', accept=True, atype='VARIABLE')
    add(21, 'DONE_TEMP', accept=True, atype='TEMP_TABLE')
    add(22, 'DONE_AGGREGATE', accept=True, atype='AGGREGATE')
    add(23, 'DONE_QUOTED_ID', accept=True, atype='IDENTIFIER')
    add(24, 'DONE_BRACKET_ID', accept=True, atype='IDENTIFIER')

    # ── Transitions from START based on first character class ───────────
    pred(0, 1, 'is_letter')          # letter → keyword/identifier
    pred(0, 2, 'is_digit')           # digit → number
    pred(0, 3, 'is_quote_single')    # ' → string literal
    pred(0, 4, 'is_operator_char')   # operator → operator
    pred(0, 5, 'is_dash')            # - may be line comment
    pred(0, 6, 'is_slash')           # / may be block comment
    pred(0, 7, 'is_quote_double')    # " → quoted identifier
    pred(0, 8, 'is_bracket_open')    # [ → bracket identifier
    pred(0, 9, 'is_at')              # @ → variable
    pred(0, 10, 'is_hash')           # # → temp table
    pred(0, 12, 'is_symbol_char')    # ( ) , . ; → symbol
    pred(0, 0, 'is_whitespace')      # whitespace → loop to start
    pred(0, 0, 'is_semicolon')       # ; → delimiter
    pred(0, 12, 'is_star')           # * → symbol (special case)

    # ── 1 IN_KEYWORD / IDENTIFIER ──────────────────────────────────────
    pred(1, 1, 'is_alnum_ext')       # continue consuming alphanumeric
    eps(1, 14)                       # could end as keyword
    eps(1, 11)                       # or be aggregate function
    eps(1, 19)                       # or be identifier

    # ── 11 IN_AGGREGATE ────────────────────────────────────────────────
    eps(11, 22)

    # ── 2 IN_NUMBER ─────────────────────────────────────────────────────
    pred(2, 2, 'is_digit')
    pred(2, 13, 'is_dot')
    eps(2, 15)

    # ── 13 IN_DECIMAL ──────────────────────────────────────────────────
    pred(13, 13, 'is_digit')
    eps(13, 15)

    # ── 3 IN_STRING ────────────────────────────────────────────────────
    pred(3, 3, 'is_alnum_ext')
    pred(3, 3, 'is_whitespace')
    pred(3, 3, 'is_operator_char')
    pred(3, 3, 'is_symbol_char')
    pred(3, 3, 'is_dash')
    pred(3, 3, 'is_slash')
    pred(3, 3, 'is_at')
    pred(3, 3, 'is_hash')
    pred(3, 3, 'is_bracket_open')
    pred(3, 3, 'is_bracket_close')
    pred(3, 3, 'is_star')
    pred(3, 3, 'is_digit')
    pred(3, 16, 'is_quote_single')   # closing quote

    # ── 4 IN_OPERATOR ──────────────────────────────────────────────────
    eps(4, 17)                       # single-char operator
    # multi-char operator: read next operator char
    pred(4, 4, 'is_operator_char')
    eps(4, 17)

    # ── 5 IN_LINE_COMMENT (-- ... \n) ──────────────────────────────────
    # first '-' was consumed, need another '-' to start comment
    # We re-enter from start with the second character
    pred(5, 5, 'is_letter')
    pred(5, 5, 'is_digit')
    pred(5, 5, 'is_alnum_ext')
    pred(5, 5, 'is_whitespace')
    pred(5, 5, 'is_operator_char')
    pred(5, 5, 'is_symbol_char')
    pred(5, 5, 'is_quote_single')
    pred(5, 5, 'is_quote_double')
    pred(5, 5, 'is_dash')
    pred(5, 5, 'is_slash')
    pred(5, 5, 'is_star')
    pred(5, 5, 'is_at')
    pred(5, 5, 'is_hash')
    pred(5, 5, 'is_bracket_open')
    pred(5, 5, 'is_bracket_close')
    pred(5, 0, 'is_newline')         # end of line → back to start

    # ── 6 IN_BLOCK_COMMENT (/* ... */) ────────────────────────────────
    # We simplify: first '/' consumed, '*' consumed in next transition
    pred(6, 6, 'is_alnum_ext')
    pred(6, 6, 'is_whitespace')
    pred(6, 6, 'is_operator_char')
    pred(6, 6, 'is_symbol_char')
    pred(6, 6, 'is_quote_single')
    pred(6, 6, 'is_quote_double')
    pred(6, 6, 'is_dash')
    pred(6, 6, 'is_slash')
    pred(6, 6, 'is_star')
    pred(6, 6, 'is_at')
    pred(6, 6, 'is_hash')
    pred(6, 6, 'is_bracket_open')
    pred(6, 6, 'is_bracket_close')
    pred(6, 6, 'is_newline')
    pred(6, 6, 'is_digit')
    pred(6, 6, 'is_letter')
    # When we see '/', could be end with star following. Simplified.
    pred(6, 0, 'is_star')            # crude: * ends block comment

    # ── 7 IN_QUOTED_ID ────────────────────────────────────────────────
    pred(7, 7, 'is_alnum_ext')
    pred(7, 7, 'is_whitespace')
    pred(7, 7, 'is_operator_char')
    pred(7, 7, 'is_symbol_char')
    pred(7, 7, 'is_dash')
    pred(7, 7, 'is_slash')
    pred(7, 7, 'is_star')
    pred(7, 7, 'is_digit')
    pred(7, 7, 'is_letter')
    pred(7, 7, 'is_at')
    pred(7, 23, 'is_quote_double')

    # ── 8 IN_BRACKET_ID ───────────────────────────────────────────────
    pred(8, 8, 'is_alnum_ext')
    pred(8, 8, 'is_whitespace')
    pred(8, 8, 'is_operator_char')
    pred(8, 8, 'is_symbol_char')
    pred(8, 8, 'is_dash')
    pred(8, 8, 'is_slash')
    pred(8, 8, 'is_star')
    pred(8, 8, 'is_digit')
    pred(8, 8, 'is_letter')
    pred(8, 8, 'is_at')
    pred(8, 24, 'is_bracket_close')

    # ── 9 IN_VARIABLE ───────────────────────────────────────────────────
    pred(9, 1, 'is_alnum_ext')       # @name → continue as identifier

    # ── 10 IN_TEMP_TABLE ───────────────────────────────────────────────
    pred(10, 1, 'is_alnum_ext')      # #temp → continue as identifier

    # ── Restart transitions: accept states → START ────────────────────
    for done_state in [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]:
        eps(done_state, 0)

    # ── 12 IN_SYMBOL ────────────────────────────────────────────────────
    eps(12, 18)

    # ── Handle '.' for decimal ───────────────────────────────────────
    # Override: when in number state, '.' goes to decimal.
    # But '.' from start goes to symbol. Already handled above.

    return s

# ---------------------------------------------------------------------------
# NFA simulation (ε-closure + step)
# ---------------------------------------------------------------------------
def epsilon_closure(states: Set[int], nfa: Dict[int, NFAState]) -> Set[int]:
    stack = list(states)
    closure = set(states)
    while stack:
        sid = stack.pop()
        for t in nfa[sid].transitions:
            if t.kind == EPSILON and t.target not in closure:
                closure.add(t.target)
                stack.append(t.target)
    return closure

def nfa_step(states: Set[int], ch: str, nfa: Dict[int, NFAState]) -> Set[int]:
    result: Set[int] = set()
    for sid in states:
        for t in nfa[sid].transitions:
            if t.kind == EPSILON:
                continue  # handled by closure
            if t.predicate:
                pred_fn = PRED_MAP.get(t.predicate)
                if pred_fn and pred_fn(ch):
                    result.add(t.target)
    return result

# ---------------------------------------------------------------------------
# NFA simulation (set of active states per character)
# ---------------------------------------------------------------------------
def nfa_simulation(query: str, nfa: Dict[int, NFAState]) -> List[dict]:
    steps: List[dict] = []
    current = epsilon_closure({0}, nfa)
    steps.append({
        'char': 'START',
        'active_states': sorted(current),
        'active_labels': [nfa[s].label for s in sorted(current) if s in nfa],
        'is_accept': any(s in nfa and nfa[s].is_accept for s in current),
    })
    for ch in query:
        current = epsilon_closure(nfa_step(current, ch, nfa), nfa)
        steps.append({
            'char': ch,
            'active_states': sorted(current),
            'active_labels': [nfa[s].label for s in sorted(current) if s in nfa],
            'is_accept': any(s in nfa and nfa[s].is_accept for s in current),
        })
    return steps

# ---------------------------------------------------------------------------
# DFA simulation (determinized — pick first accept state per step)
# ---------------------------------------------------------------------------
def dfa_simulation(query: str, nfa: Dict[int, NFAState]) -> Tuple[List[int], List[str]]:
    state_ids: List[int] = []
    labels: List[str] = []
    current = epsilon_closure({0}, nfa)
    # Find first accept or min state
    def pick(ss: Set[int]) -> Tuple[int, str]:
        for sid in sorted(ss):
            if sid in nfa and nfa[sid].is_accept:
                return sid, nfa[sid].label
        mid = min(ss) if ss else 0
        return mid, nfa[mid].label if mid in nfa else '?'
    sid, lbl = pick(current)
    state_ids.append(sid); labels.append(lbl)
    for ch in query:
        if ch in ' \t\n\r':
            continue
        current = epsilon_closure(nfa_step(current, ch, nfa), nfa)
        sid, lbl = pick(current)
        state_ids.append(sid); labels.append(lbl)
    return state_ids, labels

# ---------------------------------------------------------------------------
# SFA simulation — same as NFA but annotates predicate class per char
# ---------------------------------------------------------------------------
def sfa_simulation(query: str, nfa: Dict[int, NFAState]) -> List[dict]:
    steps = nfa_simulation(query, nfa)
    for step in steps:
        ch = step['char']
        if ch == 'START':
            step['predicate'] = 'ε'
        elif is_letter(ch):
            step['predicate'] = 'is_letter'
        elif is_digit(ch):
            step['predicate'] = 'is_digit'
        elif is_whitespace(ch):
            step['predicate'] = 'is_whitespace'
        elif is_operator_char(ch):
            step['predicate'] = 'is_operator'
        elif is_symbol_char(ch):
            step['predicate'] = 'is_symbol'
        elif is_quote_single(ch):
            step['predicate'] = "is_quote(')"
        elif is_quote_double(ch):
            step['predicate'] = 'is_quote(")'
        elif is_bracket_open(ch):
            step['predicate'] = 'is_bracket_open'
        elif is_bracket_close(ch):
            step['predicate'] = 'is_bracket_close'
        elif is_dash(ch):
            step['predicate'] = 'is_dash'
        elif is_slash(ch):
            step['predicate'] = 'is_slash'
        elif is_star(ch):
            step['predicate'] = 'is_star'
        elif is_at(ch):
            step['predicate'] = 'is_at'
        elif is_hash(ch):
            step['predicate'] = 'is_hash'
        elif is_semicolon(ch):
            step['predicate'] = 'is_semicolon'
        elif is_newline(ch):
            step['predicate'] = 'is_newline'
        elif ch == '.':
            step['predicate'] = 'is_dot'
        else:
            step['predicate'] = 'char(%s)' % repr(ch)
    return steps

NFA = build_sql_nfa()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def simulate_all(query: str) -> dict:
    nfa_steps = nfa_simulation(query, NFA)
    dfa_state_ids, dfa_labels = dfa_simulation(query, NFA)
    sfa_steps = sfa_simulation(query, NFA)
    return {
        'nfa_steps': nfa_steps,
        'nfa_state_count': len(NFA),
        'dfa_states': [
            {'state': s, 'label': lbl, 'is_final': i == len(dfa_labels) - 1, 'is_accepted': True}
            for i, (s, lbl) in enumerate(zip(dfa_state_ids, dfa_labels))
        ],
        'sfa_steps': sfa_steps,
    }
