from knowledge.store import conn
from datetime import datetime

def record_lineage(probe_id, pattern_id, bug_id, fix_commit, repo):
    """
    Records the origin of each auto-generated probe
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO probe_lineage (probe_id, pattern_id, bug_id, fix_commit, originating_repo, created_at) VALUES (?,?,?,?,?,?)",
        (probe_id, pattern_id, bug_id, fix_commit, repo, datetime.utcnow().isoformat())
    )
    conn.commit()

def get_probe_lineage(probe_id):
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT probe_id, pattern_id, bug_id, fix_commit, originating_repo, created_at FROM probe_lineage WHERE probe_id=?",
        (probe_id,)
    ).fetchone()
    if row:
        return {
            "probe_id": row[0],
            "pattern_id": row[1],
            "bug_id": row[2],
            "fix_commit": row[3],
            "originating_repo": row[4],
            "created_at": row[5]
        }
    return None
