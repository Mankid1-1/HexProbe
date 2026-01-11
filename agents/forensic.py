class ForensicAgent:
    """
    Ethan - Forensic and root cause agent
    Specializes in causal tracing, bug lineage, and patch verification
    """
    name = "Ethan"
    domains = ["repro", "causality"]

    def approve(self, patch):
        """
        Approves patch if the rationale contains root cause explanation
        """
        return "root cause" in patch.rationale.lower()
