from .architect import ArchitectAgent
from .fuzz import FuzzAgent
from .forensic import ForensicAgent
from .scale import ScaleAgent
from .edge import EdgeAgent
from .automation import AutomationAgent

ALL_AGENTS = [
    ArchitectAgent(),
    FuzzAgent(),
    ForensicAgent(),
    ScaleAgent(),
    EdgeAgent(),
    AutomationAgent()
]
