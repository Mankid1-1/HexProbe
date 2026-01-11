class FuzzAgent:
    """
    Diego - Fuzzing and security agent
    Specializes in memory safety, input boundary testing, and crash detection
    """
    name = "Diego"
    domains = ["security", "memory safety"]

    def approve(self, result):
        """
        Approves findings if no reproducible crashes are detected
        """
        return result.get("repro") is None
