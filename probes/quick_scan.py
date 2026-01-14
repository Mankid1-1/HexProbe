from collections import Counter
from pathlib import Path
from typing import List

from probes.meta import Finding, ProbeResult

SEVERITY_ORDER = ["info", "low", "medium", "high", "critical"]


def _severity_for_findings(findings: List[Finding]) -> str:
    if not findings:
        return "info"
    return max((f.severity for f in findings), key=lambda s: SEVERITY_ORDER.index(s))


def run(repo: str, artifacts=None):
    """
    Quick inventory and heuristics probe.
    """
    repo_path = Path(repo)
    findings: List[Finding] = []

    if not repo_path.exists():
        findings.append(Finding("repo", "critical", "Repository path does not exist", str(repo_path)))
        return ProbeResult(findings=[f.__dict__ for f in findings], severity="critical")

    if not (repo_path / "README.md").exists():
        findings.append(Finding("structure", "low", "Missing README.md", str(repo_path)))

    file_counter = Counter()
    todo_hits = 0
    scanned_files = 0
    for path in repo_path.rglob("*"):
        if path.is_dir():
            continue
        scanned_files += 1
        if scanned_files > 500:
            break
        file_counter[path.suffix or "(no ext)"] += 1
        if path.suffix in {".py", ".js", ".ts", ".md", ".yaml", ".yml"}:
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            todo_hits += content.count("TODO") + content.count("FIXME")

    if todo_hits >= 10:
        findings.append(Finding("hygiene", "medium", f"High TODO/FIXME volume detected ({todo_hits})"))
    elif 1 <= todo_hits < 10:
        findings.append(Finding("hygiene", "low", f"Open TODO/FIXME markers detected ({todo_hits})"))

    if not file_counter:
        findings.append(Finding("structure", "high", "Repository appears empty", str(repo_path)))
    else:
        top_ext = ", ".join([f"{ext}: {count}" for ext, count in file_counter.most_common(5)])
        findings.append(Finding("inventory", "info", f"Top file types: {top_ext}"))

    severity = _severity_for_findings(findings)
    return ProbeResult(findings=[f.__dict__ for f in findings], severity=severity)
