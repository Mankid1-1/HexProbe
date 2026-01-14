import os
import sqlite3

from core.appwrite_backend import init_knowledge_schema

DB_PATH = os.path.join(os.getcwd(), "hexprobe_knowledge.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    if init_knowledge_schema():
        return
    conn = get_conn()
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
    conn.close()

init_db()
