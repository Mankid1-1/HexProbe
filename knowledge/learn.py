from datetime import datetime
from knowledge.store import get_conn

def record_pattern(pattern_id, category, description, severity):
    """
    Records a new pattern or increments trigger count
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        existing = cursor.execute(
            "SELECT * FROM patterns WHERE id=?", (pattern_id,)
        ).fetchone()

        if existing:
            cursor.execute(
                "UPDATE patterns SET trigger_count=trigger_count+1 WHERE id=?", (pattern_id,)
            )
        else:
            cursor.execute(
                "INSERT INTO patterns (id, category, description, severity, created_at) VALUES (?,?,?,?,?)",
                (pattern_id, category, description, severity, datetime.utcnow().isoformat())
            )
