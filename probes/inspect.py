from memory.central import get_conn

def probe_origin(probe_id):
    """
    Returns original repo, bug, and fix commit
    """
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT originating_repo, bug_id, fix_commit FROM probe_lineage WHERE probe_id=?",
            (probe_id,)
        ).fetchall()
    finally:
        conn.close()
