import os
import sqlite3

GLOBAL_DB_PATH = os.path.join(os.getcwd(), "global.db")


def get_conn():
    """
    Open a SQLite connection to the central memory database.
    
    Returns:
        sqlite3.Connection: Connection to the SQLite database file at GLOBAL_DB_PATH.
    """
    conn = sqlite3.connect(GLOBAL_DB_PATH)
    return conn


conn = get_conn()


def init_global_db():
    """
    Initialize the central global SQLite database schema.
    
    Creates the `global_patterns` table and the `probe_lineage_global` table if they do not exist, then commits the transaction. `global_patterns` has columns: pattern_id (TEXT PRIMARY KEY), category (TEXT), description (TEXT), severity (TEXT), trigger_count (INTEGER DEFAULT 0), false_positive_count (INTEGER DEFAULT 0), created_at (TEXT). `probe_lineage_global` has columns: probe_id (TEXT PRIMARY KEY), pattern_id (TEXT), bug_id (TEXT), fix_commit (TEXT), originating_repo (TEXT), created_at (TEXT).
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS global_patterns (
            pattern_id TEXT PRIMARY KEY,
            category TEXT,
            description TEXT,
            severity TEXT,
            trigger_count INTEGER DEFAULT 0,
            false_positive_count INTEGER DEFAULT 0,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS probe_lineage_global (
            probe_id TEXT PRIMARY KEY,
            pattern_id TEXT,
            bug_id TEXT,
            fix_commit TEXT,
            originating_repo TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()


init_global_db()