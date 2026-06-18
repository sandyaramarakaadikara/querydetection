from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json

from engine.lexer import SQLLexer
from engine.parser import SQLParser
from engine.ast_builder import ASTBuilder
from engine.execution_plan import ExecutionPlanSimulator
from engine.injection_detector import InjectionDetector
from engine.complexity import ComplexityAnalyzer
from engine.automaton import simulate_all
from engine.decision_tree import DecisionTreeBuilder

app = FastAPI(
    title="SQL Query Compiler & Security Analysis API",
    description="Analisis query SQL: Tokenization, Parsing, AST, Execution Plan, Injection Detection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lexer = SQLLexer()
parser = SQLParser()
ast_builder = ASTBuilder()
exec_plan = ExecutionPlanSimulator()
injection_detector = InjectionDetector()
complexity_analyzer = ComplexityAnalyzer()
decision_tree = DecisionTreeBuilder()

SAMPLE_QUERIES = [
    {"name": "SELECT Dasar", "query": "SELECT nama, npm FROM mahasiswa"},
    {"name": "SELECT + WHERE", "query": "SELECT nama, npm FROM mahasiswa WHERE npm = '22001'"},
    {"name": "SELECT + JOIN", "query": "SELECT m.nama, d.nama AS dosen FROM mahasiswa m INNER JOIN dosen d ON m.dosen_id = d.id"},
    {"name": "SELECT + GROUP BY", "query": "SELECT jurusan, COUNT(*) AS jml FROM mahasiswa GROUP BY jurusan ORDER BY jml DESC"},
    {"name": "SELECT Full Query", "query": "SELECT m.nama, d.nama AS dosen, SUM(n.nilai) AS total FROM mahasiswa m INNER JOIN dosen d ON m.dosen_id = d.id LEFT JOIN nilai n ON m.npm = n.npm WHERE m.angkatan >= 2020 GROUP BY m.nama, d.nama HAVING SUM(n.nilai) > 100 ORDER BY total DESC"},
    {"name": "INSERT INTO", "query": "INSERT INTO mahasiswa (npm, nama, jurusan) VALUES ('22005', 'Budi', 'Informatika')"},
    {"name": "INSERT SELECT", "query": "INSERT INTO mahasiswa_baru (npm, nama) SELECT npm, nama FROM mahasiswa WHERE angkatan = 2021"},
    {"name": "UPDATE", "query": "UPDATE mahasiswa SET jurusan = 'Sistem Informasi' WHERE npm = '22001'"},
    {"name": "DELETE", "query": "DELETE FROM mahasiswa WHERE npm = '22001'"},
    {"name": "CREATE TABLE", "query": "CREATE TABLE mahasiswa (npm VARCHAR(10) PRIMARY KEY, nama VARCHAR(100), jurusan VARCHAR(50), angkatan INT)"},
    {"name": "CREATE INDEX", "query": "CREATE INDEX idx_npm ON mahasiswa (npm)"},
    {"name": "CREATE VIEW", "query": "CREATE VIEW mahasiswa_aktif AS SELECT npm, nama FROM mahasiswa WHERE angkatan >= 2023"},
    {"name": "ALTER TABLE", "query": "ALTER TABLE mahasiswa ADD COLUMN email VARCHAR(100)"},
    {"name": "DROP TABLE", "query": "DROP TABLE mahasiswa"},
    {"name": "DROP INDEX", "query": "DROP INDEX idx_npm"},
    {"name": "TRUNCATE", "query": "TRUNCATE TABLE mahasiswa"},
    {"name": "MERGE", "query": "MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN UPDATE SET t.nama = s.nama WHEN NOT MATCHED THEN INSERT (id, nama) VALUES (s.id, s.nama)"},
    {"name": "BEGIN/COMMIT", "query": "BEGIN TRANSACTION; UPDATE rekening SET saldo = saldo - 100000 WHERE id = 1; UPDATE rekening SET saldo = saldo + 100000 WHERE id = 2; COMMIT"},
    {"name": "DECLARE Variable", "query": "DECLARE @total INT; SET @total = (SELECT COUNT(*) FROM mahasiswa); SELECT @total AS total_mahasiswa"},
    {"name": "SQL Injection", "query": "SELECT * FROM users WHERE name = 'admin' OR '1'='1' --"},
]

@app.get("/")
def root():
    return {
        "name": "SQL Query Compiler & Security Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/analyze": "Analyze a SQL query",
            "GET /api/samples": "Get sample queries",
            "GET /health": "Health check",
        },
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/samples")
def get_samples():
    return {"samples": SAMPLE_QUERIES}

@app.post("/api/analyze")
async def analyze_query(request: Request):
    try:
        body = await request.json()
        query = body.get("query", "")
    except Exception:
        try:
            raw = await request.body()
            body = json.loads(raw)
            query = body.get("query", "")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query = query.strip()

    try:
        tokens, dfa_states, _ = lexer.tokenize(query)

        syntax_result = parser.validate(tokens)

        if syntax_result['status'] == 'VALID' and syntax_result['parse_tree']:
            ast_result = ast_builder.build(syntax_result['parse_tree'])
        else:
            ast_result = None

        plan_result = exec_plan.simulate(tokens)

        injection_result = injection_detector.analyze(query)

        complexity_result = complexity_analyzer.analyze(tokens, query)

        automaton_result = simulate_all(query)

        decision_tree_result = decision_tree.build(query, tokens, syntax_result, injection_result, complexity_result)

        return {
            "tokens": [t.to_dict() for t in tokens],
            "dfa_states": dfa_states,
            "syntax": syntax_result,
            "ast": ast_result,
            "execution_plan": plan_result,
            "injection": injection_result,
            "complexity": complexity_result,
            "automaton": automaton_result,
            "decision_tree": decision_tree_result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
