from datetime import datetime
import uuid

class ProposedPatch:
    def __init__(self, description, code_snippet, rationale):
        self.id = str(uuid.uuid4())
        self.description = description
        self.code_snippet = code_snippet
        self.rationale = rationale
        self.created_at = datetime.utcnow()

def synthesize_patch(finding, context=None):
    """
    Generates a suggested patch for a given finding.
    """
    # Example logic (AI-assisted):
    # In a real system, this could call a GPT model or custom ML model
    if "lint" in finding["category"]:
        code_snippet = "# Fixed lint issues according to project style guide"
        rationale = "Applies auto-lint corrections to comply with code style"
    elif "type" in finding["category"]:
        code_snippet = "# Added type annotations to match static types"
        rationale = "Corrects type mismatches detected by type checker"
    elif "boundary" in finding["category"]:
        code_snippet = "# Validate input with safe guards"
        rationale = "Prevents unsafe user input to reduce security risk"
    else:
        code_snippet = "# Manual review required"
        rationale = "No automatic patch available; requires human review"

    return ProposedPatch(description=finding["message"],
                         code_snippet=code_snippet,
                         rationale=rationale)
