import sys
sys.stdout.reconfigure(encoding='utf-8')
from engine.lexer import SQLLexer
from engine.parser import SQLParser

lexer = SQLLexer()
parser = SQLParser()

queries = [
    "SELECT nama, npm FROM mahasiswa WHERE npm = '22001'",
    "INSERT INTO mahasiswa (npm, nama) VALUES ('22005', 'Budi')",
    "UPDATE mahasiswa SET jurusan = 'Sistem Informasi' WHERE npm = '22001'",
    "DELETE FROM mahasiswa WHERE npm = '22001'",
    "CREATE TABLE mahasiswa (npm VARCHAR(10) PRIMARY KEY, nama VARCHAR(100))",
    "ALTER TABLE mahasiswa ADD COLUMN email VARCHAR(100)",
    "DROP TABLE mahasiswa",
    "TRUNCATE TABLE mahasiswa",
    "MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN UPDATE SET t.nama = s.nama WHEN NOT MATCHED THEN INSERT (id, nama) VALUES (s.id, s.nama)",
    "BEGIN TRANSACTION; UPDATE rekening SET saldo = saldo - 100000 WHERE id = 1; COMMIT",
    "DECLARE @total INT; SET @total = (SELECT COUNT(*) FROM mahasiswa); SELECT @total AS total_mahasiswa",
    "SELECT * FROM users WHERE name = 'admin' OR '1'='1' --",
]

for q in queries:
    try:
        tokens, states, _ = lexer.tokenize(q)
        result = parser.validate(tokens)
        status_ok = '+' if result['status'] == 'VALID' else '-'
        print(f'{status_ok} [{result["status"]:7s}] {q[:75]}')
        if result.get('warnings'):
            for w in result['warnings']:
                print(f'      WARN:  {w["message"]}')
        if result['errors']:
            for e in result['errors']:
                print(f'      ERROR: {e["message"]}')
    except Exception as e:
        print(f'! [ERROR]   {q[:75]}')
        print(f'      {e!r}')
