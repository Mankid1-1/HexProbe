from typing import Any, Callable, Dict, List

from agents import ALL_AGENTS
from probes.quick_scan import run as quick_scan
from probes.static.surface_sweep import run as surface_sweep


ProbeRunner = Callable[[str], Any]


def agent_profiles() -> List[Dict[str, Any]]:
    """
    Collects public profile information for every registered agent.
    
    Each profile is a dictionary with keys:
    - `name`: the agent's name.
    - `domains`: a list of domains associated with the agent, or an empty list if the agent has no `domains` attribute.
    
    Returns:
        profiles (List[Dict[str, Any]]): List of agent profile dictionaries.
    """
    profiles = []
    for agent in ALL_AGENTS:
        profiles.append({
            "name": agent.name,
            "domains": getattr(agent, "domains", []),
        })
    return profiles


def probe_registry() -> Dict[str, Dict[str, Any]]:
    """
    Return a registry mapping probe identifiers to their metadata.
    
    Each entry maps a probe id to a dict containing:
    - "name": human-friendly probe name
    - "description": brief explanation of the probe's purpose
    - "runner": a callable that accepts a repository path (str) and returns the probe result
    - "supports_artifacts": boolean indicating whether the probe accepts artifact inputs
    
    Returns:
        Dict[str, Dict[str, Any]]: Mapping from probe identifier to its metadata dictionary.
    """
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