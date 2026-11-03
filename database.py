"""
Resumely AI — SQLite Persistence Layer
Stores analysis results, metadata, and JSON output with lightweight SQLite.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with dict-like row access."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the analyses table if it does not already exist."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                target_role TEXT,
                job_description TEXT,
                overall_score INTEGER NOT NULL,
                ats_score INTEGER NOT NULL,
                job_match_score INTEGER,
                analysis_json TEXT NOT NULL
            )
        """)
        conn.commit()


def save_analysis(
    analysis_id: str,
    filename: str,
    target_role: Optional[str],
    job_description: Optional[str],
    analysis_data: Dict[str, Any]
) -> str:
    """Persists a validated resume analysis record."""
    init_db()
    created_at = datetime.now(timezone.utc).isoformat()
    overall_score = analysis_data.get("overall_score", 0)
    ats_score = analysis_data.get("ats", {}).get("score", 0)
    job_match = analysis_data.get("job_match")
    job_match_score = job_match.get("percentage") if job_match else None
    json_str = json.dumps(analysis_data, ensure_ascii=False)

    with get_db_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO analyses (
                id, created_at, filename, target_role, job_description,
                overall_score, ats_score, job_match_score, analysis_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id, created_at, filename, target_role, job_description,
            overall_score, ats_score, job_match_score, json_str
        ))
        conn.commit()
    return analysis_id


def get_analysis(analysis_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves an analysis by its ID, parsing the inner JSON data."""
    init_db()
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?",
            (analysis_id,)
        ).fetchone()

    if not row:
        return None

    data = dict(row)
    data["analysis"] = json.loads(data["analysis_json"])
    return data


def list_recent_analyses(limit: int = 10) -> List[Dict[str, Any]]:
    """Lists recent analyses for navigation or history."""
    init_db()
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT id, created_at, filename, target_role, overall_score, ats_score FROM analyses ORDER BY created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
