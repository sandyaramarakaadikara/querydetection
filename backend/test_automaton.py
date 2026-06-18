import sys
sys.stdout.reconfigure(encoding='utf-8')
from engine.automaton import simulate_all

queries = [
    'SELECT',
    'SELECT * FROM t',
    "SELECT name FROM users WHERE id = '123'",
    '123',
    '@var',
    '#temp',
]

for q in queries:
    r = simulate_all(q)
    print('=== %s ===' % q)
    print('NFA steps:', len(r['nfa_steps']))
    for s in r['nfa_steps'][:8]:
        print('  %s: states=%s accept=%s' % (
            repr(s['char']), s['active_states'][:6], s['is_accept']))
    print('DFA states:', len(r['dfa_states']))
    print('SFA steps:', len(r['sfa_steps']))
    print()
