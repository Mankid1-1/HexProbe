from knowledge.store import get_conn

def find_recurrent_patterns(min_triggers=3):
    """
    Returns patterns that frequently triggered
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        rows = cursor.execute(
            "SELECT id, category, description, severity, trigger_count FROM patterns WHERE trigger_count>=?",
            (min_triggers,),
        ).fetchall()
    return [dict(id=r[0], category=r[1], description=r[2], severity=r[3], trigger_count=r[4]) for r in rows]
