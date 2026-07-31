from pydantic import BaseModel

from water_agent_lab.models import SimulationResult


class CounterproposalImpact(BaseModel):
    """
    Comparison between the original result and the counterproposal-adjusted result.
    """

    fairness_delta: float
    conflict_delta: float
    minimum_satisfaction_delta: float
    shortage_delta: float
    agreement_changed: bool


def compare_counterproposal_impact(
    original_result: SimulationResult,
    adjusted_result: SimulationResult,
) -> CounterproposalImpact:
    """
    Compare the effect of a counterproposal-adjusted allocation.
    """
    return CounterproposalImpact(
        fairness_delta=adjusted_result.fairness_score - original_result.fairness_score,
        conflict_delta=adjusted_result.conflict_score - original_result.conflict_score,
        minimum_satisfaction_delta=(
            adjusted_result.minimum_satisfaction_score
            - original_result.minimum_satisfaction_score
        ),
        shortage_delta=adjusted_result.shortage_score - original_result.shortage_score,
        agreement_changed=(
            adjusted_result.agreement_reached != original_result.agreement_reached
        ),
    )
