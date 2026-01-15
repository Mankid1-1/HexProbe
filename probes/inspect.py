from memory.central import get_conn

def probe_origin(probe_id):
    """
    Returns original repo, bug, and fix commit
    """
    with get_conn() as conn:
        return conn.execute(
            "SELECT originating_repo, bug_id, fix_commit FROM probe_lineage WHERE probe_id=?",
            (probe_id,)
        ).fetchall()
