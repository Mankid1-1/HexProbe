SEVERITY_ORDER = ["low","medium","high","critical"]

def adjust_severity(meta):
    idx = SEVERITY_ORDER.index(meta.severity)
    if meta.trigger_count >= 5 and meta.false_positive_count <= 1:
        idx = min(idx+1, len(SEVERITY_ORDER)-1)
    if meta.false_positive_count >= 3:
        idx = max(idx-1, 0)
    meta.severity = SEVERITY_ORDER[idx]
    return meta
