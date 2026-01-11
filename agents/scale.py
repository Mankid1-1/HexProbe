class ScaleAgent:
    """
    Omar - Performance and chaos agent
    Specializes in system scalability, chaos testing, and performance monitoring
    """
    name = "Omar"
    domains = ["performance", "resilience"]

    def approve(self, result):
        """
        Approves only non-critical performance findings
        """
        return result.severity not in ("high", "critical")
