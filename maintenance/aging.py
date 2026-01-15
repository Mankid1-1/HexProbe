from knowledge.store import get_conn
from datetime import datetime, timedelta

def prune_old_patterns(max_age_days=180):
    """
    Remove patterns that have not triggered within max_age_days
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        cutoff_date = (datetime.utcnow() - timedelta(days=max_age_days)).isoformat()
        cursor.execute(
            "DELETE FROM patterns WHERE created_at < ?", (cutoff_date,)
        )

def prune_old_probes(max_age_days=180):
    """
    Remove probes that are stale from lineage table
    """
    with get_conn() as conn:
        cursor = conn.cursor()
        cutoff_date = (datetime.utcnow() - timedelta(days=max_age_days)).isoformat()
        cursor.execute(
            "DELETE FROM probe_lineage WHERE created_at < ?", (cutoff_date,)
        )

def aging_cycle(max_age_days=180):
    """
    Run full aging and pruning cycle
    """
    prune_old_patterns(max_age_days)
    prune_old_probes(max_age_days)
