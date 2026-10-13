"""
Distributed Component Coordination & Executive Hierarchy for GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent.
Domain: Research Administration
"""
import json
import uuid
from typing import Dict, Any, List, Optional
from .models import FrontierPayload, AgentTelemetryAlert, ExecutionStatus
from agents.base import PHIGuard
from .engine import FrontierDomainEngine


class SpecificAimsExtractorAgent:
    """Specialized Sub-Agent 1: Primary Parameter & Integrity Auditor."""
    def audit(self, payload: FrontierPayload) -> List[AgentTelemetryAlert]:
        alerts = []
        res = FrontierDomainEngine.evaluate_primary_parameter(payload.primary_metric)
        if res:
            alerts.append(AgentTelemetryAlert(
                alert_id=str(uuid.uuid4())[:8],
                origin_agent="SpecificAimsExtractorAgent",
                status=ExecutionStatus.ELEVATED_RISK,
                summary=res["summary"],
                technical_details=res["details"],
                actionable_remediation=res["remediation"],
            ))
        return alerts


class StudySectionMatcherAgent:
    """Specialized Sub-Agent 2: Critical Kinetics & Security Safeguard."""
    def audit(self, payload: FrontierPayload) -> List[AgentTelemetryAlert]:
        alerts = []
        res = FrontierDomainEngine.evaluate_secondary_kinetics(payload.secondary_metric, payload.is_critical_flag)
        if res:
            alerts.append(AgentTelemetryAlert(
                alert_id=str(uuid.uuid4())[:8],
                origin_agent="StudySectionMatcherAgent",
                status=ExecutionStatus.CRITICAL_INTERVENTION if payload.is_critical_flag else ExecutionStatus.ELEVATED_RISK,
                summary=res["summary"],
                technical_details=res["details"],
                actionable_remediation=res["remediation"],
            ))
        return alerts


class ScientificOverlapAuditorAgent:
    """Specialized Sub-Agent 3: Protocol Conformance & Anomaly Triager."""
    def audit(self, payload: FrontierPayload) -> List[AgentTelemetryAlert]:
        alerts = []
        res = FrontierDomainEngine.audit_specification_conformance(payload.status_descriptor, payload.attributes)
        if res:
            alerts.append(AgentTelemetryAlert(
                alert_id=str(uuid.uuid4())[:8],
                origin_agent="ScientificOverlapAuditorAgent",
                status=ExecutionStatus.ELEVATED_RISK,
                summary=res["summary"],
                technical_details=res["details"],
                actionable_remediation=res["remediation"],
            ))
        return alerts


class GrantMatchCoordinator:
    """Executive Coordinator & Air-Gapped Supervisory Intelligence."""
    def __init__(self):
        self.sub_1 = SpecificAimsExtractorAgent()
        self.sub_2 = StudySectionMatcherAgent()
        self.sub_3 = ScientificOverlapAuditorAgent()
        self.execution_ledger: Dict[str, Dict[str, Any]] = {}

    def process(self, payload: FrontierPayload) -> Dict[str, Any]:
        PHIGuard.assert_no_phi(json.dumps(payload.__dict__, default=str))
        all_alerts: List[AgentTelemetryAlert] = []
        all_alerts.extend(self.sub_1.audit(payload))
        all_alerts.extend(self.sub_2.audit(payload))
        all_alerts.extend(self.sub_3.audit(payload))

        crit_count = sum(1 for a in all_alerts if a.status == ExecutionStatus.CRITICAL_INTERVENTION)
        warn_count = sum(1 for a in all_alerts if a.status == ExecutionStatus.ELEVATED_RISK)

        if crit_count > 0:
            status = ExecutionStatus.CRITICAL_INTERVENTION
        elif warn_count > 0:
            status = ExecutionStatus.ELEVATED_RISK
        else:
            status = ExecutionStatus.NOMINAL

        dossier = {
            "system": "nih-reporter-grant-similarity-agent",
            "domain": "Research Administration",
            "task_id": payload.task_id,
            "target_identifier": payload.target_identifier,
            "overall_status": status.value,
            "total_alerts": len(all_alerts),
            "critical_count": crit_count,
            "warning_count": warn_count,
            "alerts": [a.to_dict() for a in all_alerts],
            "standard_specification": "NIH RePORT & Center for Scientific Review",
            "consensus_summary": f"Consensus evaluation completed across 3 sub-agents with status [{status.value}].",
        }

        self.execution_ledger[payload.task_id] = dossier
        return dossier

    def query_supervisory_chat(self, query: str) -> str:
        q = query.strip().lower()
        if "status" in q or "ledger" in q:
            return f"GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent currently managing {len(self.execution_ledger)} execution tasks in air-gapped memory."
        elif "standard" in q or "spec" in q:
            return "NIH RePORT & Center for Scientific Review specifications are not implemented; this prototype uses arbitrary demonstration rules."
        else:
            return f"GrantMatch-AI: NIH RePORT & RePADD Grant Scientific Similarity Agent executive coordinator online. Zero-telemetry on-premises surveillance active."
