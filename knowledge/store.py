import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "hexprobe_knowledge.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn

conn = get_conn()

def init_db():
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patterns (
        id TEXT PRIMARY KEY,
        category TEXT,
        description TEXT,
        severity TEXT,
        trigger_count INTEGER DEFAULT 0,
        false_positive_count INTEGER DEFAULT 0,
        created_at TEXT
    )""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS probe_lineage (
        probe_id TEXT PRIMARY KEY,
        pattern_id TEXT,
        bug_id TEXT,
        fix_commit TEXT,
        originating_repo TEXT,
        created_at TEXT
    )""")
    conn.commit()

init_db()
