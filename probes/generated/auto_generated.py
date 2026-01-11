from hexprobe.probes.meta import Finding, ProbeResult
from knowledge.lineage import record_lineage
import uuid
from datetime import datetime

def generate_probe(pattern, bug_id, fix_commit, repo, artifacts=None):
    """
    Auto-generates a probe from memory/past bugs
    """
    probe_id = str(uuid.uuid4())
    record_lineage(probe_id, pattern, bug_id, fix_commit, repo)

    findings = [Finding(category=pattern["category"],
                        severity=pattern["severity"],
                        message=pattern["description"])]

    return ProbeResult(findings=[f.__dict__ for f in findings], severity=pattern["severity"])
