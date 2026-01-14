from pathlib import Path
import sqlite3

from core.appwrite_backend import init_global_schema

GLOBAL_DB_PATH = Path(__file__).resolve().parent / "global.db"

def get_conn():
    """
    Returns connection to central memory database shared across repos
    """
    GLOBAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(GLOBAL_DB_PATH)

def init_global_db():
    if init_global_schema():
        return
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_patterns (
            pattern_id TEXT PRIMARY KEY,
            category TEXT,
            description TEXT,
            severity TEXT,
            trigger_count INTEGER DEFAULT 0,
            false_positive_count INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS probe_lineage_global (
            probe_id TEXT PRIMARY KEY,
            pattern_id TEXT,
            bug_id TEXT,
            fix_commit TEXT,
            originating_repo TEXT,
            created_at TEXT
        )
        """)
        conn.commit()
    finally:
        conn.close()

init_global_db()
