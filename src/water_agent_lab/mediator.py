from typing import Literal

from pydantic import BaseModel, Field

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.models import SimulationResult


MediatorAction = Literal[
    "accept_proposal",
    "revise_strategy",
    "use_counterproposal_candidate",
    "stop_no_improvement",
]


class MediatorRecommendation(BaseModel):
    """
    Structured recommendation produced by a mediator agent.
    """

    action: MediatorAction
    current_strategy: str
    recommended_strategy: str
    rejected_stakeholders: list[str] = Field(default_factory=list)
    concerned_stakeholders: list[str] = Field(default_factory=list)
    total_requested_extra_water: float = 0.0
    current_conflict_score: float | None = None
    revised_strategy_conflict_score: float | None = None
    counterproposal_conflict_score: float | None = None
    summary: str


class RuleBasedMediatorAgent:
    """
    Deterministic mediator agent.

    The mediator compares the normal revised-strategy candidate and the
    counterproposal-adjusted candidate, then chooses the best revision path
    using transparent deterministic rules.
    """

    def recommend(
        self,
        current_strategy: str,
        decisions: list[AgentDecision],
        result: SimulationResult,
        counterproposal_summary: object | None = None,
        counterproposal_adjusted_result: SimulationResult | None = None,
        normal_revised_strategy: str | None = None,
        normal_revised_result: SimulationResult | None = None,
    ) -> MediatorRecommendation:
        rejected_stakeholders = [
            decision.stakeholder_name
            for decision in decisions
            if decision.status == "rejected"
        ]

        concerned_stakeholders = [
            decision.stakeholder_name
            for decision in decisions
            if decision.status == "concerned"
        ]

        total_requested_extra_water = _get_total_requested_extra_water(
            decisions=decisions,
            counterproposal_summary=counterproposal_summary,
        )

        pressure_sentence = _build_counterproposal_pressure_sentence(
            total_requested_extra_water=total_requested_extra_water,
        )

        if not rejected_stakeholders:
            return MediatorRecommendation(
                action="accept_proposal",
                current_strategy=current_strategy,
                recommended_strategy=current_strategy,
                rejected_stakeholders=[],
                concerned_stakeholders=concerned_stakeholders,
                total_requested_extra_water=total_requested_extra_water,
                current_conflict_score=result.conflict_score,
                revised_strategy_conflict_score=(
                    normal_revised_result.conflict_score
                    if normal_revised_result is not None
                    else None
                ),
                counterproposal_conflict_score=(
                    counterproposal_adjusted_result.conflict_score
                    if counterproposal_adjusted_result is not None
                    else None
                ),
                summary=(
                    "No stakeholder rejected the proposal. "
                    "The mediator recommends accepting the current allocation."
                    f"{pressure_sentence}"
                ),
            )

        best_action = _choose_best_revision_action(
            current_result=result,
            normal_revised_result=normal_revised_result,
            counterproposal_adjusted_result=counterproposal_adjusted_result,
            normal_revised_strategy=normal_revised_strategy,
            current_strategy=current_strategy,
        )

        if best_action == "revise_strategy":
            recommended_strategy = (
                normal_revised_strategy
                if normal_revised_strategy is not None
                else current_strategy
            )

            return MediatorRecommendation(
                action="revise_strategy",
                current_strategy=current_strategy,
                recommended_strategy=recommended_strategy,
                rejected_stakeholders=rejected_stakeholders,
                concerned_stakeholders=concerned_stakeholders,
                total_requested_extra_water=total_requested_extra_water,
                current_conflict_score=result.conflict_score,
                revised_strategy_conflict_score=(
                    normal_revised_result.conflict_score
                    if normal_revised_result is not None
                    else None
                ),
                counterproposal_conflict_score=(
                    counterproposal_adjusted_result.conflict_score
                    if counterproposal_adjusted_result is not None
                    else None
                ),
                summary=(
                    "Some stakeholders rejected the proposal. "
                    f"The mediator recommends switching from {current_strategy} "
                    f"to {recommended_strategy} because the normal strategy "
                    "revision is the best deterministic improvement."
                    f"{pressure_sentence}"
                ),
            )

        if best_action == "use_counterproposal_candidate":
            return MediatorRecommendation(
                action="use_counterproposal_candidate",
                current_strategy=current_strategy,
                recommended_strategy=current_strategy,
                rejected_stakeholders=rejected_stakeholders,
                concerned_stakeholders=concerned_stakeholders,
                total_requested_extra_water=total_requested_extra_water,
                current_conflict_score=result.conflict_score,
                revised_strategy_conflict_score=(
                    normal_revised_result.conflict_score
                    if normal_revised_result is not None
                    else None
                ),
                counterproposal_conflict_score=(
                    counterproposal_adjusted_result.conflict_score
                    if counterproposal_adjusted_result is not None
                    else None
                ),
                summary=(
                    "Some stakeholders rejected the proposal. "
                    "The mediator recommends using the counterproposal-adjusted "
                    "candidate because it is the best deterministic improvement."
                    f"{pressure_sentence}"
                ),
            )

        return MediatorRecommendation(
            action="stop_no_improvement",
            current_strategy=current_strategy,
            recommended_strategy=current_strategy,
            rejected_stakeholders=rejected_stakeholders,
            concerned_stakeholders=concerned_stakeholders,
            total_requested_extra_water=total_requested_extra_water,
            current_conflict_score=result.conflict_score,
            revised_strategy_conflict_score=(
                normal_revised_result.conflict_score
                if normal_revised_result is not None
                else None
            ),
            counterproposal_conflict_score=(
                counterproposal_adjusted_result.conflict_score
                if counterproposal_adjusted_result is not None
                else None
            ),
            summary=(
                "Some stakeholders rejected the proposal, but neither the "
                "normal strategy revision nor the counterproposal-adjusted "
                "candidate improves the deterministic metrics."
                f"{pressure_sentence}"
            ),
        )


def _choose_best_revision_action(
    current_result: SimulationResult,
    normal_revised_result: SimulationResult | None,
    counterproposal_adjusted_result: SimulationResult | None,
    normal_revised_strategy: str | None,
    current_strategy: str,
) -> MediatorAction:
    """
    Choose the best deterministic revision action.

    Rules:
    1. Ignore candidates that violate the water budget.
    2. Prefer a candidate that reaches agreement.
    3. Otherwise prefer lower conflict score.
    4. If conflict is tied, prefer higher minimum satisfaction.
    5. If still tied, prefer normal strategy revision for stability.
    6. If no candidate improves the current result, stop.
    """
    candidates: list[tuple[MediatorAction, SimulationResult]] = []

    if (
        normal_revised_strategy is not None
        and normal_revised_strategy != current_strategy
        and normal_revised_result is not None
        and normal_revised_result.water_budget_valid
    ):
        candidates.append(("revise_strategy", normal_revised_result))

    if (
        counterproposal_adjusted_result is not None
        and counterproposal_adjusted_result.water_budget_valid
    ):
        candidates.append(
            (
                "use_counterproposal_candidate",
                counterproposal_adjusted_result,
            )
        )

    if not candidates:
        return "stop_no_improvement"

    best_action, best_result = min(
        candidates,
        key=lambda item: _candidate_ranking_key(
            action=item[0],
            result=item[1],
        ),
    )

    if not _candidate_improves_current_result(
        current_result=current_result,
        candidate_result=best_result,
    ):
        return "stop_no_improvement"

    return best_action


def _candidate_ranking_key(
    action: MediatorAction,
    result: SimulationResult,
) -> tuple[int, float, float, int]:
    """
    Rank candidate revisions.

    Lower tuple is better.
    """
    agreement_penalty = 0 if result.agreement_reached else 1
    strategy_tie_breaker = 0 if action == "revise_strategy" else 1

    return (
        agreement_penalty,
        result.conflict_score,
        -result.minimum_satisfaction_score,
        strategy_tie_breaker,
    )


def _candidate_improves_current_result(
    current_result: SimulationResult,
    candidate_result: SimulationResult,
) -> bool:
    """
    Decide whether a candidate is meaningfully better than the current result.
    """
    if candidate_result.agreement_reached and not current_result.agreement_reached:
        return True

    if candidate_result.conflict_score < current_result.conflict_score:
        return True

    if (
        candidate_result.conflict_score == current_result.conflict_score
        and candidate_result.minimum_satisfaction_score
        > current_result.minimum_satisfaction_score
    ):
        return True

    return False


def _get_total_requested_extra_water(
    decisions: list[AgentDecision],
    counterproposal_summary: object | None,
) -> float:
    """
    Get total requested extra water from a counterproposal summary if available,
    otherwise compute it directly from decisions.
    """
    if counterproposal_summary is not None:
        value = getattr(
            counterproposal_summary,
            "total_requested_extra_water",
            None,
        )

        if isinstance(value, int | float):
            return float(value)

    return sum(decision.requested_extra_water for decision in decisions)


def _build_counterproposal_pressure_sentence(
    total_requested_extra_water: float,
) -> str:
    """
    Build a sentence describing total counterproposal pressure.
    """
    if total_requested_extra_water <= 0:
        return ""

    return f" Stakeholders requested {total_requested_extra_water:.2f} extra water."
