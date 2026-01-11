from dataclasses import dataclass

@dataclass
class Finding:
    category: str
    severity: str
    message: str
    location: str = None

@dataclass
class ProbeResult:
    findings: list
    severity: str = "info"
    repro: list = None
