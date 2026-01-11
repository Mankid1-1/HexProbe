def detect_conflicts(probes):
    conflicts = []
    seen = {}
    for p in probes:
        key = (p.meta.category, p.trigger_signature)
        if key in seen:
            conflicts.append((seen[key], p))
        else:
            seen[key] = p
    return conflicts
