def probe_score(meta):
    return meta.trigger_count*3 - meta.false_positive_count*5 + (50 if meta.status=="core" else 0)

