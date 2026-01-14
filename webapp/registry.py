from typing import Any, Callable, Dict, List

from agents import ALL_AGENTS
from probes.quick_scan import run as quick_scan
from probes.static.surface_sweep import run as surface_sweep


ProbeRunner = Callable[[str], Any]


def agent_profiles() -> List[Dict[str, Any]]:
    profiles = []
    for agent in ALL_AGENTS:
        profiles.append({
            "name": agent.name,
            "domains": getattr(agent, "domains", []),
        })
    return profiles


def probe_registry() -> Dict[str, Dict[str, Any]]:
    return {
        "quick_scan": {
            "name": "Quick Inventory",
            "description": "Fast inventory and risk scan for repo structure and TODO density.",
            "runner": quick_scan,
            "supports_artifacts": False,
        },
        "surface_sweep": {
            "name": "Surface Sweep",
            "description": "Static checks for linting, typing, and boundary inputs (ruff/mypy required).",
            "runner": surface_sweep,
            "supports_artifacts": False,
        },
    }
