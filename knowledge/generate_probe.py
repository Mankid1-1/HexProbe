from hexprobe.probes.meta import Finding, ProbeResult
from knowledge.lineage import record_lineage
import uuid
from datetime import datetime

def generate_probe_from_pattern(pattern, bug_id, fix_commit, repo, artifacts=None):
    """
    Auto-generates a probe based on past patterns and bug history
    """
    probe_id = str(uuid.uuid4())

    # Record lineage
    record_lineage(probe_id, pattern["id"], bug_id, fix_commit, repo)

    findings = [Finding(category=pattern["category"],
                        severity=pattern["severity"],
                        message=pattern["description"])]

    return ProbeResult(findings=[f.__dict__ for f in findings], severity=pattern["severity"])
