"""Workflow registry."""

from yoak.workflows.base import Workflow
from yoak.workflows.customer_discovery import CustomerDiscoveryWorkflow
from yoak.workflows.customer_validation import CustomerValidationWorkflow
from yoak.workflows.idea_evaluation import IdeaEvaluationWorkflow
from yoak.workflows.pivot_decision import PivotDecisionWorkflow
from yoak.workflows.pmf_assessment import PMFAssessmentWorkflow
from yoak.workflows.product_critique import ProductCritiqueWorkflow

WORKFLOW_REGISTRY: dict[str, type[Workflow]] = {
    "idea_evaluation": IdeaEvaluationWorkflow,
    "customer_discovery": CustomerDiscoveryWorkflow,
    "customer_validation": CustomerValidationWorkflow,
    "pivot_decision": PivotDecisionWorkflow,
    "pmf_assessment": PMFAssessmentWorkflow,
    "product_critique": ProductCritiqueWorkflow,
}


def create_workflow(name: str) -> Workflow | None:
    cls = WORKFLOW_REGISTRY.get(name)
    if cls:
        return cls()
    return None
