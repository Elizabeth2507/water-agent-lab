from water_agent_lab.agent_models import AgentDecision
from water_agent_lab.config import load_scenario_config
from water_agent_lab.evaluator import evaluate_proposal
from water_agent_lab.mediator import RuleBasedMediatorAgent
from water_agent_lab.simulator import minimum_first_allocation, proportional_allocation
from water_agent_lab.counterproposals import summarize_counterproposals


def test_mediator_recommends_revision_when_normal_revision_is_best() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    current_proposal = proportional_allocation(scenario)
    current_result = evaluate_proposal(scenario, current_proposal)

    normal_revised_proposal = minimum_first_allocation(scenario)
    normal_revised_result = evaluate_proposal(scenario, normal_revised_proposal)

    decisions = [
        AgentDecision(
            stakeholder_name="urban",
            status="rejected",
            argument="Urban rejects the proposal.",
            requested_extra_water=1.0,
            willingness_to_compromise=0.4,
        ),
        AgentDecision(
            stakeholder_name="ecosystem",
            status="rejected",
            argument="Ecosystem rejects the proposal.",
            requested_extra_water=2.0,
            willingness_to_compromise=0.3,
        ),
    ]

    counterproposal_summary = summarize_counterproposals(decisions)

    mediator = RuleBasedMediatorAgent()

    recommendation = mediator.recommend(
        current_strategy="proportional",
        decisions=decisions,
        result=current_result,
        counterproposal_summary=counterproposal_summary,
        counterproposal_adjusted_result=current_result,
        normal_revised_strategy="minimum-first",
        normal_revised_result=normal_revised_result,
    )

    assert recommendation.action == "revise_strategy"
    assert recommendation.recommended_strategy == "minimum-first"
    assert recommendation.rejected_stakeholders == ["urban", "ecosystem"]
    assert recommendation.total_requested_extra_water == 3.0
    assert recommendation.current_conflict_score == current_result.conflict_score
    assert recommendation.revised_strategy_conflict_score == (
        normal_revised_result.conflict_score
    )


def test_mediator_accepts_when_no_stakeholder_rejects() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = minimum_first_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    decisions = [
        AgentDecision(
            stakeholder_name="agriculture",
            status="concerned",
            argument="Agriculture is concerned but does not reject.",
            requested_extra_water=2.0,
            willingness_to_compromise=0.6,
        ),
        AgentDecision(
            stakeholder_name="urban",
            status="accepted",
            argument="Urban accepts the proposal.",
            requested_extra_water=0.0,
            willingness_to_compromise=0.9,
        ),
    ]

    mediator = RuleBasedMediatorAgent()

    recommendation = mediator.recommend(
        current_strategy="minimum-first",
        decisions=decisions,
        result=result,
    )

    assert recommendation.action == "accept_proposal"
    assert recommendation.recommended_strategy == "minimum-first"
    assert recommendation.rejected_stakeholders == []
    assert recommendation.concerned_stakeholders == ["agriculture"]


def test_mediator_stops_when_no_revision_available() -> None:
    scenario = load_scenario_config("configs/extreme_drought.yaml")
    proposal = minimum_first_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    decisions = [
        AgentDecision(
            stakeholder_name="ecosystem",
            status="rejected",
            argument="Ecosystem rejects the proposal.",
            requested_extra_water=4.0,
            willingness_to_compromise=0.2,
        ),
    ]

    mediator = RuleBasedMediatorAgent()

    recommendation = mediator.recommend(
        current_strategy="minimum-first",
        decisions=decisions,
        result=result,
    )

    assert recommendation.action == "stop_no_improvement"
    assert recommendation.current_strategy == "minimum-first"
    assert recommendation.recommended_strategy == "minimum-first"
    assert recommendation.rejected_stakeholders == ["ecosystem"]


def test_mediator_includes_counterproposal_pressure() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")
    proposal = proportional_allocation(scenario)
    result = evaluate_proposal(scenario, proposal)

    decisions = [
        AgentDecision(
            stakeholder_name="urban",
            status="rejected",
            argument="Urban requests more water.",
            requested_extra_water=4.0,
            willingness_to_compromise=0.3,
        )
    ]

    counterproposal_summary = summarize_counterproposals(decisions)

    mediator = RuleBasedMediatorAgent()

    recommendation = mediator.recommend(
        current_strategy="proportional",
        decisions=decisions,
        result=result,
        counterproposal_summary=counterproposal_summary,
    )

    assert recommendation.total_requested_extra_water == 4.0
    assert "4.00 extra water" in recommendation.summary


def test_mediator_can_choose_normal_revision_over_counterproposal_candidate() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    current_proposal = proportional_allocation(scenario)
    current_result = evaluate_proposal(scenario, current_proposal)

    normal_revised_proposal = minimum_first_allocation(scenario)
    normal_revised_result = evaluate_proposal(scenario, normal_revised_proposal)

    decisions = [
        AgentDecision(
            stakeholder_name="ecosystem",
            status="rejected",
            argument="Ecosystem needs more water.",
            requested_extra_water=4.0,
            willingness_to_compromise=0.2,
        )
    ]

    counterproposal_summary = summarize_counterproposals(decisions)

    mediator = RuleBasedMediatorAgent()

    recommendation = mediator.recommend(
        current_strategy="proportional",
        decisions=decisions,
        result=current_result,
        counterproposal_summary=counterproposal_summary,
        counterproposal_adjusted_result=current_result,
        normal_revised_strategy="minimum-first",
        normal_revised_result=normal_revised_result,
    )

    assert recommendation.action == "revise_strategy"
    assert recommendation.recommended_strategy == "minimum-first"
    assert recommendation.revised_strategy_conflict_score == (
        normal_revised_result.conflict_score
    )


def test_mediator_can_choose_counterproposal_candidate() -> None:
    scenario = load_scenario_config("configs/drought_mvp.yaml")

    current_proposal = proportional_allocation(scenario)
    current_result = evaluate_proposal(scenario, current_proposal)

    normal_revised_proposal = minimum_first_allocation(scenario)
    normal_revised_result = evaluate_proposal(scenario, normal_revised_proposal)

    decisions = [
        AgentDecision(
            stakeholder_name="ecosystem",
            status="rejected",
            argument="Ecosystem needs a targeted increase.",
            requested_extra_water=4.0,
            willingness_to_compromise=0.2,
        )
    ]

    counterproposal_summary = summarize_counterproposals(decisions)

    mediator = RuleBasedMediatorAgent()

    recommendation = mediator.recommend(
        current_strategy="proportional",
        decisions=decisions,
        result=current_result,
        counterproposal_summary=counterproposal_summary,
        counterproposal_adjusted_result=normal_revised_result,
        normal_revised_strategy="minimum-first",
        normal_revised_result=current_result,
    )

    assert recommendation.action == "use_counterproposal_candidate"
    assert recommendation.total_requested_extra_water == 4.0
    assert recommendation.counterproposal_conflict_score == (
        normal_revised_result.conflict_score
    )
