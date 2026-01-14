import subprocess
from probes.meta import Finding, ProbeResult
from pathlib import Path

def run(repo, ctx=None, artifacts=None):
    """
    Perform static analysis on a repository: run linting and type checking, and detect unvalidated input in Python files.
    
    Parameters:
        repo (str | pathlib.Path): Path to the repository to analyze.
    
    Returns:
        ProbeResult: An object containing:
            - findings: a list of dictionaries describing issues; each entry includes `name`, `severity`, `message`, and optionally `path`.
            - severity: the overall severity string ("info", "low", "medium", "high", or "critical") representing the highest-severity finding.
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