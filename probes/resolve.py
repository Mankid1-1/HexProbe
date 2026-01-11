def resolve_conflict(p1, p2):
    """
    Deterministic resolution:
    - Prefer core over active
    - Higher score
    - Older lineage
    """
    return max([p1, p2], key=lambda p: (
        p.meta.status == "core",
        p.meta.trigger_count - p.meta.false_positive_count,
        p.meta.created_at
    ))

def deprecate(loser, winner):
    loser.meta.status = "deprecated"
    loser.meta.redirect = winner.meta.id
