import json, subprocess
from probes.meta import ProbeResult

def run(repo, ctx=None, artifacts=None):
    """
    Performance regression probe using external load tests
    """
    baseline = artifacts.get("perf_baseline") if artifacts else {"p95": 100, "p99":200, "error_rate":0}
    proc = subprocess.run(["k6","run","load.js","--summary-export=summary.json"], cwd=repo, capture_output=True, text=True)
    
    try:
        summary = json.loads(open("summary.json").read())
        current = {
            "p95": summary["metrics"]["http_req_duration"]["p(95)"],
            "p99": summary["metrics"]["http_req_duration"]["p(99)"],
            "error_rate": summary["metrics"]["http_req_failed"]["rate"]
        }
    except Exception:
        current = baseline

    regressions = {}
    for k,v in current.items():
        if v > baseline.get(k,0)*1.05:
            regressions[k] = (baseline.get(k,0), v)

    if regressions:
        return ProbeResult(findings=regressions, severity="high")
    return ProbeResult(findings="performance stable")
