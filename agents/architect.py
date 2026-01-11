class ArchitectAgent:
    """
    Maya - Structural and architecture probing agent
    Specializes in detecting structural issues, enforceable architecture rules, and observability gaps
    """
    name = "Maya"
    domains = ["architecture", "observability"]

    def approve(self, result):
        """
        Approves a finding if no critical structure or architecture violation is present.
        """
        for f in result.get("findings", []):
            if f["category"] == "structure" and f["severity"] in ("high", "critical"):
                return False
        return True
