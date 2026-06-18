import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class InjectionFinding:
    type: str
    pattern: str
    severity: str
    description: str
    position: int
    value: str
    recommendation: str

INJECTION_PATTERNS = [
    {
        'type': 'AUTH_BYPASS',
        'patterns': [
            r"(?i)or\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",
            r"(?i)or\s+'1'\s*=\s*'1",
            r"(?i)or\s+1\s*=\s*1",
            r"(?i)or\s+'true'\s*=\s*'true",
            r"(?i)admin'\s*--",
            r"(?i)'\s*or\s+1\s*=\s*1\s*--",
            r"(?i)'\s*or\s+'1'\s*=\s*'1",
        ],
        'severity': 'Critical',
        'description': 'Percobaan bypass autentikasi terdeteksi',
        'recommendation': 'Gunakan prepared statement / parameterized query',
    },
    {
        'type': 'UNION_INJECTION',
        'patterns': [
            r"(?i)union\s+select",
            r"(?i)union\s+all\s+select",
            r"(?i)union\s+distinct\s+select",
        ],
        'severity': 'Critical',
        'description': 'Injeksi UNION-based SQL terdeteksi',
        'recommendation': 'Validasi dan sanitasi semua input pengguna; gunakan ORM atau parameterized query',
    },
    {
        'type': 'COMMENT_INJECTION',
        'patterns': [
            r"--",
            r"#",
            r"/\*.*?\*/",
        ],
        'severity': 'High',
        'description': 'Injeksi komentar SQL terdeteksi (digunakan untuk memotong query)',
        'recommendation': 'Hapus atau encode karakter komentar dari input pengguna',
    },
    {
        'type': 'TIME_BASED',
        'patterns': [
            r"(?i)sleep\s*\(",
            r"(?i)waitfor\s+delay",
            r"(?i)waitfor\s+time",
            r"(?i)pg_sleep\s*\(",
            r"(?i)dbms_lock\.sleep",
        ],
        'severity': 'High',
        'description': 'Injeksi blind SQL berbasis waktu terdeteksi',
        'recommendation': 'Implementasikan validasi input dan gunakan prepared statement',
    },
    {
        'type': 'BOOLEAN_BASED',
        'patterns': [
            r"(?i)'\s*and\s+\d+\s*=\s*\d+",
            r"(?i)'\s*and\s+'1'\s*=\s*'1",
            r"(?i)or\s+\d+\s*=\s*\d+",
            r"(?i)or\s+'1'\s*=\s*'1",
            r"(?i)and\s+\d+\s*=\s*\d+\s*--",
        ],
        'severity': 'High',
        'description': 'Injeksi blind SQL berbasis Boolean terdeteksi',
        'recommendation': 'Gunakan prepared statement dan validasi input',
    },
    {
        'type': 'STACKED_QUERY',
        'patterns': [
            r";\s*(select|insert|update|delete|drop|create|alter|exec|execute)",
        ],
        'severity': 'Critical',
        'description': 'Injeksi query bertumpuk terdeteksi (multi query)',
        'recommendation': 'Gunakan parameterized query; jangan pernah menggabungkan input pengguna secara langsung',
    },
    {
        'type': 'ERROR_BASED',
        'patterns': [
            r"(?i)convert\s*\(.*?\)",
            r"(?i)cast\s*\(.*?\)",
            r"(?i)extractvalue\s*\(",
            r"(?i)updatexml\s*\(",
        ],
        'severity': 'High',
        'description': 'Teknik injeksi SQL berbasis error terdeteksi',
        'recommendation': 'Validasi tipe input dan gunakan prepared statement',
    },
]

class InjectionDetector:
    def __init__(self):
        self.findings: List[InjectionFinding] = []

    def analyze(self, query: str) -> Dict[str, Any]:
        self.findings = []
        if not query:
            return {
                'is_vulnerable': False,
                'risk_level': 'None',
                'findings': [],
                'overall_recommendation': '',
            }

        for rule in INJECTION_PATTERNS:
            for pattern in rule['patterns']:
                for match in re.finditer(pattern, query):
                    existing = [f for f in self.findings if f.type == rule['type'] and f.pattern == pattern]
                    if not existing:
                        self.findings.append(InjectionFinding(
                            type=rule['type'],
                            pattern=pattern,
                            severity=rule['severity'],
                            description=rule['description'],
                            position=match.start(),
                            value=match.group(),
                            recommendation=rule['recommendation'],
                        ))

        self.findings = self._deduplicate(self.findings)

        risk_level = self._calculate_risk_level()
        is_vulnerable = len(self.findings) > 0
        overall_recommendation = self._generate_recommendation()

        return {
            'is_vulnerable': is_vulnerable,
            'risk_level': risk_level,
            'findings': [
                {
                    'type': f.type,
                    'severity': f.severity,
                    'description': f.description,
                    'position': f.position,
                    'value': f.value,
                    'recommendation': f.recommendation,
                }
                for f in self.findings
            ],
            'overall_recommendation': overall_recommendation,
            'findings_count': len(self.findings),
        }

    def _deduplicate(self, findings: List[InjectionFinding]) -> List[InjectionFinding]:
        seen = set()
        unique = []
        for f in findings:
            key = (f.type, f.value)
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _calculate_risk_level(self) -> str:
        if not self.findings:
            return 'None'
        severities = [f.severity for f in self.findings]
        if 'Critical' in severities:
            return 'Critical'
        if 'High' in severities:
            return 'High'
        if 'Medium' in severities:
            return 'Medium'
        return 'Low'

    def _generate_recommendation(self) -> str:
        if not self.findings:
            return 'No SQL injection detected.'

        recommendations = set()
        for f in self.findings:
            recommendations.add(f.recommendation)

        base = 'Kerentanan SQL Injection terdeteksi. '
        steps = [
            '1. Gunakan prepared statement / parameterized query',
            '2. Implementasikan validasi dan sanitasi input yang ketat',
            '3. Gunakan ORM (contoh: SQLAlchemy, Prisma, Hibernate)',
            '4. Terapkan prinsip hak akses minimum pada akun database',
            '5. Gunakan Web Application Firewall (WAF)',
        ]
        return base + 'Rekomendasi mitigasi: ' + '; '.join(steps)
