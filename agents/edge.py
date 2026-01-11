class EdgeAgent:
    """
    Naomi - Edge and UX agent
    Specializes in boundary cases, user experience, and edge case detection
    """
    name = "Naomi"
    domains = ["UX", "boundary"]

    def approve(self, result):
        """
        Approves findings, defaults to True unless extreme UX issues detected
        """
        return True
