from agents import ALL_AGENTS
from probes.meta import ProbeResult
from ai.propose_patch import synthesize_patch
from knowledge.learn import record_pattern
from memory.promote import promote_pattern, promote_probe_lineage
from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class ResultPayload:
    findings: list
    severity: str = "info"
    repro: list | None = None
    rationale: str | None = None

    def get(self, key, default=None):
        return getattr(self, key, default)

class HexProbeOrchestrator:
    """
    Central orchestrator coordinating:
    - Probes
    - Agents
    - AI-assisted patch synthesis
    - Memory and knowledge promotion
    """
    def __init__(self):
        self.agents = ALL_AGENTS

    def run_probe(self, probe_func, repo, artifacts=None):
        """
        Executes a probe and collects results
        """
        result = probe_func(repo, artifacts=artifacts)
        return result

    def normalize_result_payload(self, result):
        """
        Ensure result payload exposes attribute access for agents
        """
        if isinstance(result, ResultPayload):
            return result
        if isinstance(result, dict):
            rationale = result.get("rationale")
            if rationale is None:
                rationale = ""
            return ResultPayload(
                findings=result.get("findings"),
                severity=result.get("severity", "info"),
                repro=result.get("repro"),
                rationale=rationale,
            )
        if hasattr(result, "rationale"):
            rationale = getattr(result, "rationale")
        else:
            rationale = None
        if rationale is None:
            rationale = ""
        return ResultPayload(
            findings=getattr(result, "findings", None),
            severity=getattr(result, "severity", "info"),
            repro=getattr(result, "repro", None),
            rationale=rationale,
        )

    def evaluate_with_agents(self, result):
        """
        Ask all agents to approve or flag a finding
        """
        result_payload = self.normalize_result_payload(result)
        approvals = {}
        for agent in self.agents:
            try:
                approvals[agent.name] = agent.approve(result_payload)
            except Exception:
                approvals[agent.name] = False
        return approvals

    def propose_fixes(self, result, context=None):
        """
        Generate AI-assisted patch proposals for each finding
        """
        result_payload = self.normalize_result_payload(result)
        patches = []
        for finding in result_payload.findings:
            patch = synthesize_patch(finding, context=context)
            patches.append(patch)
        return patches

    def integrate_memory(self, pattern, probe_info):
        """
        Record patterns in local knowledge and promote to global memory
        """
        record_pattern(pattern["id"], pattern["category"], pattern["description"], pattern["severity"])
        promote_pattern(pattern)
        promote_probe_lineage(probe_info)

    def run_full_cycle(self, probe_func, repo, artifacts=None):
        """
        Run probe → evaluate → synthesize patches → integrate memory
        """
        result = self.run_probe(probe_func, repo, artifacts=artifacts)
        result_payload = self.normalize_result_payload(result)
        approvals = self.evaluate_with_agents(result_payload)
        patches = self.propose_fixes(result_payload)
        for patch in patches:
            # link patch to a dummy pattern for memory integration example
            pattern = {
                "id": str(uuid.uuid4()),
                "category": "auto_generated",
                "description": patch.description,
                "severity": result_payload.severity,
                "trigger_count": 1,
                "false_positive_count": 0
            }
            probe_info = {
                "probe_id": str(uuid.uuid4()),
                "pattern_id": pattern["id"],
                "bug_id": str(uuid.uuid4()),
                "fix_commit": None,
                "originating_repo": repo
            }
            self.integrate_memory(pattern, probe_info)

        return {"result": result_payload, "approvals": approvals, "patches": patches}
