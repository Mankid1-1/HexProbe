import subprocess
from probes.meta import ProbeResult
from pathlib import Path

def run(repo, ctx=None, artifacts=None):
    """
    Fuzz testing probe for memory safety and crash detection
    """
    crash_dir = Path("artifacts/fuzz/crashes")
    crash_dir.mkdir(parents=True, exist_ok=True)

    proc = subprocess.run(["./fuzz/run.sh"], cwd=repo, timeout=1800)
    crashes = list(crash_dir.glob("*"))

    if crashes:
        if artifacts:
            artifacts.store("fuzz_crashes", crashes)
        return ProbeResult(findings="fuzz crashes detected", repro=crashes, severity="critical")
    return ProbeResult(findings="fuzz stable")
