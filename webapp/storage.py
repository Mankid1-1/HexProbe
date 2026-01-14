import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATE_PATH = DATA_DIR / "hexprobe_state.json"


def _default_state() -> Dict[str, Any]:
    """
    Return a fresh default state dictionary for the application.
    
    The dictionary contains:
    - "repos": an empty list of repository records.
    - "runs": an empty list of run records.
    - "created_at": current UTC timestamp in ISO 8601 format.
    - "updated_at": current UTC timestamp in ISO 8601 format.
    
    Returns:
        state (Dict[str, Any]): A new state dictionary with the keys described above.
    """
    return {
        "repos": [],
        "runs": [],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def load_state() -> Dict[str, Any]:
    """
    Load the persisted application state from disk, or produce a new default state if no state file exists.
    
    Returns:
        dict: The application state. If the state file is missing, returns a default state containing the keys `repos`, `runs`, `created_at`, and `updated_at`.
    """
    if not STATE_PATH.exists():
        return _default_state()
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: Dict[str, Any]) -> None:
    """
    Persist the provided state dictionary to the JSON state file.
    
    Creates the data directory if missing, updates state["updated_at"] to the current UTC time in ISO format, and writes the state as pretty-printed JSON with sorted keys to STATE_PATH. The function mutates the given state in-place.
    
    Parameters:
        state (Dict[str, Any]): Application state mapping; will be updated in-place and persisted to disk.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state["updated_at"] = datetime.utcnow().isoformat()
    with STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)


def append_repo(state: Dict[str, Any], repo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Append a repository entry to the state's repository list and persist the updated state.
    
    Parameters:
        state (Dict[str, Any]): Mutable state dictionary containing a "repos" list.
        repo (Dict[str, Any]): Repository record to append to `state["repos"]`.
    
    Returns:
        Dict[str, Any]: The same state dictionary after appending the repo and saving it.
    """
    state["repos"].append(repo)
    save_state(state)
    return state


def append_run(state: Dict[str, Any], run: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert a run record at the front of the state's runs list and persist the updated state.
    
    Parameters:
        state (Dict[str, Any]): Mutable state dictionary to update and save.
        run (Dict[str, Any]): Run record to prepend to `state["runs"]`.
    
    Returns:
        Dict[str, Any]: The updated state dictionary with `run` at index 0 and `state["runs"]` truncated to at most 100 entries.
    """
    state["runs"].insert(0, run)
    state["runs"] = state["runs"][:100]
    save_state(state)
    return state