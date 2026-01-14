import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_PATH = DATA_DIR / "hexprobe_state.json"


def _default_state() -> Dict[str, Any]:
    return {
        "repos": [],
        "runs": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return _default_state()
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.utcnow().isoformat()
    with STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)


def append_repo(state: Dict[str, Any], repo: Dict[str, Any]) -> Dict[str, Any]:
    state["repos"].append(repo)
    save_state(state)
    return state


def append_run(state: Dict[str, Any], run: Dict[str, Any]) -> Dict[str, Any]:
    state["runs"].insert(0, run)
    state["runs"] = state["runs"][:100]
    save_state(state)
    return state
