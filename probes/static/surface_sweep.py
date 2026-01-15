import subprocess
from probes.meta import Finding, ProbeResult
from pathlib import Path

def run(repo, ctx=None, artifacts=None):
    """
    Static analysis probe for linting, type checking, and boundary input detection
    """
    findings = []

    # Lint check (ruff)
    lint = subprocess.run(["ruff", repo], capture_output=True, text=True)
    if lint.returncode != 0:
        findings.append(Finding("lint","medium",lint.stdout))

    # Type checking (mypy)
    mypy = subprocess.run(["mypy", repo], capture_output=True, text=True)
    if mypy.returncode != 0:
        findings.append(Finding("type","high",mypy.stdout))

    # Boundary heuristic
    for path in Path(repo).rglob("*.py"):
        if "input(" in path.read_text(errors="ignore"):
            findings.append(Finding("boundary","high","Unvalidated input",str(path)))

    severity_order = ["info","low","medium","high","critical"]
    severity = max([f.severity for f in findings], default="info",
                   key=lambda s: severity_order.index(s))

    return ProbeResult(findings=[f.__dict__ for f in findings], severity=severity)
