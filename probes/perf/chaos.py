import subprocess
from probes.meta import ProbeResult

def run(repo, ctx=None, artifacts=None):
    """
    Chaos testing probe to simulate service disruptions
    """
    scenarios = [
        ["chaos", "kill", "service"],
        ["chaos", "latency", "500ms"],
        ["chaos", "cpu", "90%"]
    ]
    failures = []
    for scenario in scenarios:
        proc = subprocess.run(scenario, cwd=repo, timeout=300)
        if proc.returncode != 0:
            failures.append(scenario)

    if failures:
        return ProbeResult(findings=failures, severity="critical")
    return ProbeResult(findings="chaos tolerated")
