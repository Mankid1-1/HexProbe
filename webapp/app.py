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
    """
    Serialize a patch object into a JSON-serializable dictionary.
    
    Parameters:
        patch: An object representing a patch with attributes `id`, `description`,
            `code_snippet`, `rationale`, and `created_at` (a datetime).
    
    Returns:
        dict: A dictionary with keys `id`, `description`, `code_snippet`, `rationale`,
            and `created_at` (ISO 8601 string).
    """
    return {
        "id": patch.id,
        "description": patch.description,
        "code_snippet": patch.code_snippet,
        "rationale": patch.rationale,
        "created_at": patch.created_at.isoformat(),
    }


def _serialize_result(result: ProbeResult) -> Dict[str, Any]:
    """
    Produce a dictionary representation of a ProbeResult suitable for JSON serialization.
    
    Parameters:
        result (ProbeResult): The probe result to serialize.
    
    Returns:
        dict: A dictionary with keys `findings`, `severity`, and `repro` reflecting the corresponding fields of `result`.
    """
    return {
        "findings": result.findings,
        "severity": result.severity,
        "repro": result.repro,
    }


def _safe_probe_runner(runner, repo_path: str) -> ProbeResult:
    """
    Execute a probe runner for the given repository path and convert any raised exception into a critical probe result.
    
    Parameters:
        runner (callable): A callable that accepts a repository path (str) and returns a ProbeResult.
        repo_path (str): Filesystem path of the repository to run the probe against.
    
    Returns:
        ProbeResult: The result returned by `runner`, or a ProbeResult containing a single critical finding with category `"probe_error"` and a message describing the exception if `runner` raised.
    """
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
    """
    Render the web UI's main page populated with current repositories, runs, probes, and agent profiles.
    
    Returns:
        A Flask response with the rendered "index.html" template. The template context includes:
        - repos: list of repository entries from persisted state
        - runs: list of recorded probe runs from persisted state
        - probes: probe registry mapping
        - agents: available agent profiles
    """
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
    """
    Return the persisted application state as a JSON HTTP response.
    
    Returns:
        flask.Response: JSON response containing the current persisted state.
    """
    state = load_state()
    return jsonify(state)


@app.route("/api/repos", methods=["POST"])
def api_repos():
    """
    Create a new repository entry from JSON payload and persist it to the application state.
    
    Accepts a JSON body with `name`, `path`, and optional `notes`. `name` and `path` are required and will be stripped of surrounding whitespace. The created repo object includes an `id` (UUID string), `added_at` (UTC ISO timestamp), and `exists` (boolean whether the given path exists on disk).
    
    Returns:
        A JSON response:
          - On success: the created repository object and HTTP status 201.
          - On validation failure: `{"error": "name and path are required"}` and HTTP status 400.
    """
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
    """
    Run a registered probe against a repository, persist the resulting run record, and return the created run payload.
    
    Expects a JSON request body with:
    - "repo_id": ID of the repository to scan.
    - "probe_key": Key of the probe to execute.
    
    Returns:
    A JSON response containing the created run record and a 201 status code on success; returns a JSON error message with a 404 status code if the repository or probe is not found.
    """
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
        """
        Invoke the configured probe runner for the given repository path, converting any exception into a failure result.
        
        Parameters:
            repo_path (str): Filesystem path to the repository to run the probe against.
            artifacts (Any, optional): Ignored; present for API compatibility with orchestrator/runner signatures.
        
        Returns:
            ProbeResult: The probe's result. If the runner raises an exception, returns a ProbeResult containing a single critical `probe_error` finding describing the failure.
        """
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