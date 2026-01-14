from memory.central import get_conn
from datetime import datetime

def promote_pattern(local_pattern):
    """
    Promote a locally learned pattern to the global memory
    """
    conn = get_conn()
    try:
        cursor = conn.cursor()
        existing = cursor.execute(
            "SELECT pattern_id FROM global_patterns WHERE pattern_id=?", (local_pattern["id"],)
        ).fetchone()

        if existing:
            cursor.execute(
                "UPDATE global_patterns SET trigger_count=trigger_count+1 WHERE pattern_id=?",
                (local_pattern["id"],)
            )
        else:
            cursor.execute(
                "INSERT INTO global_patterns (pattern_id, category, description, severity, trigger_count, false_positive_count, created_at) VALUES (?,?,?,?,?,?,?)",
                (local_pattern["id"], local_pattern["category"], local_pattern["description"], local_pattern["severity"],
                 local_pattern.get("trigger_count",0), local_pattern.get("false_positive_count",0), datetime.utcnow().isoformat())
            )
        conn.commit()
    finally:
        conn.close()

def promote_probe_lineage(probe_info):
    """
    Promote a locally recorded probe lineage to global memory
    """
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO probe_lineage_global (probe_id, pattern_id, bug_id, fix_commit, originating_repo, created_at) VALUES (?,?,?,?,?,?)",
            (probe_info["probe_id"], probe_info["pattern_id"], probe_info["bug_id"], probe_info["fix_commit"],
             probe_info["originating_repo"], datetime.utcnow().isoformat())
        )
        conn.commit()
    finally:
        conn.close()
