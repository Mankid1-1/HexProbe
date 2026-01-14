from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import uuid

from flask import Flask, jsonify, render_template, request

from core.synthesis import HexProbeOrchestrator
from probes.meta import ProbeResult
from webapp.registry import agent_profiles, probe_registry
from webapp.storage import append_repo, append_run, load_state

app = Flask(__name__)


def _serialize_patch(patch) -> Dict[str, Any]:
    return {
        "id": patch.id,
        "description": patch.description,
        "code_snippet": patch.code_snippet,
        "rationale": patch.rationale,
        "created_at": patch.created_at.isoformat(),
    }


def _serialize_result(result: ProbeResult) -> Dict[str, Any]:
    return {
        "findings": result.findings,
        "severity": result.severity,
        "repro": result.repro,
    }


def _safe_probe_runner(runner, repo_path: str) -> ProbeResult:
    try:
        return runner(repo_path)
    except Exception as exc:
        return ProbeResult(
            findings=[{
                "category": "probe_error",
                "severity": "critical",
                "message": f"Probe failed: {exc}",
                "location": repo_path,
            }],
            severity="critical",
        )


@app.route("/")
def index():
    state = load_state()
    probes = probe_registry()
    return render_template(
        "index.html",
        repos=state["repos"],
        runs=state["runs"],
        probes=probes,
        agents=agent_profiles(),
    )


@app.route("/api/state")
def api_state():
    state = load_state()
    return jsonify(state)


@app.route("/api/repos", methods=["POST"])
def api_repos():
    payload = request.get_json(force=True)
    name = payload.get("name", "").strip()
    path = payload.get("path", "").strip()
    notes = payload.get("notes", "").strip()

    if not name or not path:
        return jsonify({"error": "name and path are required"}), 400

    repo_path = Path(path)
    repo = {
        "id": str(uuid.uuid4()),
        "name": name,
        "path": str(repo_path),
        "notes": notes,
        "added_at": datetime.utcnow().isoformat(),
        "exists": repo_path.exists(),
    }

    state = load_state()
    append_repo(state, repo)
    return jsonify(repo), 201


@app.route("/api/runs", methods=["POST"])
def api_runs():
    payload = request.get_json(force=True)
    repo_id = payload.get("repo_id")
    probe_key = payload.get("probe_key")

    state = load_state()
    repo = next((item for item in state["repos"] if item["id"] == repo_id), None)
    if repo is None:
        return jsonify({"error": "repo not found"}), 404

    probes = probe_registry()
    if probe_key not in probes:
        return jsonify({"error": "probe not found"}), 404

    orchestrator = HexProbeOrchestrator()
    runner = probes[probe_key]["runner"]

    def wrapped_runner(repo_path, artifacts=None):
        return _safe_probe_runner(runner, repo_path)

    result_bundle = orchestrator.run_full_cycle(wrapped_runner, repo["path"])
    result = result_bundle["result"]
    approvals = result_bundle["approvals"]
    patches = result_bundle["patches"]

    run = {
        "id": str(uuid.uuid4()),
        "repo_id": repo_id,
        "repo_name": repo["name"],
        "probe_key": probe_key,
        "probe_name": probes[probe_key]["name"],
        "status": "completed",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "result": _serialize_result(result),
        "approvals": approvals,
        "patches": [_serialize_patch(patch) for patch in patches],
    }

    append_run(state, run)
    return jsonify(run), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
