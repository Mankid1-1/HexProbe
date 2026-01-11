class AutomationAgent:
    """
    Priya - CI/CD and automation agent
    Specializes in rollout safety, pipeline integration, and automated verification
    """
    name = "Priya"
    domains = ["CI", "rollout"]

    def approve(self, result):
        """
        Always approves findings to allow automated pipeline enforcement
        """
        return True
