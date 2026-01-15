import sqlite3

from core.storage import get_data_dir

GLOBAL_DB_PATH = get_data_dir() / "global.db"


def get_conn():
    """
    Returns connection to central memory database shared across repos.
    """
    return sqlite3.connect(GLOBAL_DB_PATH)


def init_global_db():
    with get_conn() as conn:
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


init_global_db()
