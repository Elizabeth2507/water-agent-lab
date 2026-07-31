from typing import Literal

from pydantic import BaseModel, Field

from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.models import SimulationResult
from water_agent_lab.negotiation import choose_revision_strategy
from water_agent_lab.counterproposals import CounterproposalSummary


MediatorAction = Literal[
    "accept_proposal",
    "revise_strategy",
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
    summary: str


class RuleBasedMediatorAgent:
    """
    Deterministic mediator agent.

    The mediator reads stakeholder decisions and simulation metrics,
    then recommends whether to accept the proposal, revise the strategy,
    or stop because no further deterministic improvement is available.
    """

    def recommend(
        self,
        current_strategy: str,
        decisions: list[AgentDecision],
        result: SimulationResult,
        counterproposal_summary: CounterproposalSummary | None = None,
    ) -> MediatorRecommendation:

        total_requested_extra_water = (
            counterproposal_summary.total_requested_extra_water
            if counterproposal_summary is not None
            else sum(decision.requested_extra_water for decision in decisions)
        )

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

        if not rejected_stakeholders:
            return MediatorRecommendation(
                action="accept_proposal",
                current_strategy=current_strategy,
                recommended_strategy=current_strategy,
                rejected_stakeholders=[],
                concerned_stakeholders=concerned_stakeholders,
                summary=(
                    "No stakeholder rejected the proposal. "
                    "The mediator recommends accepting the current allocation."
                ),
            )

        recommended_strategy = choose_revision_strategy(current_strategy)

        if recommended_strategy == current_strategy:
            return MediatorRecommendation(
                action="stop_no_improvement",
                current_strategy=current_strategy,
                recommended_strategy=current_strategy,
                rejected_stakeholders=rejected_stakeholders,
                concerned_stakeholders=concerned_stakeholders,
                summary=(
                    "Some stakeholders rejected the proposal, but the current "
                    "strategy has no deterministic revision available."
                ),
            )

        return MediatorRecommendation(
            action="revise_strategy",
            current_strategy=current_strategy,
            recommended_strategy=recommended_strategy,
            rejected_stakeholders=rejected_stakeholders,
            concerned_stakeholders=concerned_stakeholders,
            summary=(
                "Some stakeholders rejected the proposal. "
                f"The mediator recommends switching from {current_strategy} "
                f"to {recommended_strategy}. "
                f"Stakeholders requested {total_requested_extra_water:.2f} extra water units."
            ),
            total_requested_extra_water=total_requested_extra_water,
        )
