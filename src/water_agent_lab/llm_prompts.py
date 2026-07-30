from water_agent_lab.agent_models import AgentProfile, AgentState
from water_agent_lab.models import AllocationProposal, ScenarioConfig, StakeholderConfig


def build_stakeholder_system_prompt(profile: AgentProfile) -> str:
    """
    Build the stable system prompt for an LLM stakeholder agent.
    """
    goals = "\n".join(f"- {goal}" for goal in profile.goals)
    constraints = "\n".join(f"- {constraint}" for constraint in profile.constraints)

    return (
        "You are an LLM stakeholder agent in a drought water-allocation "
        "simulation.\n\n"
        f"Agent name: {profile.name}\n"
        f"Role: {profile.role}\n"
        f"Negotiation style: {profile.negotiation_style}\n\n"
        "Goals:\n"
        f"{goals or '- No explicit goals provided.'}\n\n"
        "Constraints:\n"
        f"{constraints or '- No explicit constraints provided.'}\n\n"
        "You must return only valid JSON. Do not include Markdown, comments, "
        "or extra text."
    )


def build_stakeholder_user_prompt(
    stakeholder: StakeholderConfig,
    state: AgentState,
    scenario: ScenarioConfig | None = None,
    proposal: AllocationProposal | None = None,
    allocated_water: float | None = None,
    round_number: int = 1,
) -> str:
    """
    Build the user prompt for one stakeholder allocation evaluation.

    This function supports both usage styles:

    1. prompt tests:
       build_stakeholder_user_prompt(
           scenario=scenario,
           stakeholder=stakeholder,
           proposal=proposal,
           state=state,
       )

    2. LLMStakeholderAgent:
       build_stakeholder_user_prompt(
           stakeholder=stakeholder,
           state=state,
           allocated_water=allocated_water,
           round_number=round_number,
       )
    """
    if allocated_water is None:
        if proposal is None:
            raise ValueError("Either allocated_water or proposal must be provided.")

        allocated_water = proposal.allocations.get(stakeholder.name, 0.0)

    scenario_lines: list[str] = []

    if scenario is not None:
        total_requested = sum(item.requested_water for item in scenario.stakeholders)

        scenario_lines = [
            f"Scenario name: {scenario.scenario_name}",
            f"Country: {scenario.country}",
            f"Region: {scenario.region}",
            f"Drought level: {scenario.drought_level}",
            f"Available water: {scenario.available_water}",
            f"Total requested water: {total_requested}",
            "",
        ]

        return "\n".join(
            [
                "Evaluate the proposed allocation for this stakeholder.",
                "",
                f"round_number: {round_number}",
                *scenario_lines,
                f"stakeholder_name: {stakeholder.name}",
                f"requested_water: {stakeholder.requested_water}",
                f"minimum_acceptable_water: {stakeholder.minimum_acceptable_water}",
                f"allocated_water: {allocated_water}",
                f"priority: {stakeholder.priority}",
                f"current_frustration: {state.frustration}",
                f"trust_in_mediator: {state.trust_in_mediator}",
                f"concessions_made: {state.concessions_made}",
                f"last_status: {state.last_status}",
                "",
                "output_schema:",
                "{",
                '  "stakeholder_name": "...",',
                '  "status": "accepted | concerned | rejected",',
                '  "argument": "...",',
                '  "requested_extra_water": 0.0,',
                '  "willingness_to_compromise": 0.0',
                "}",
            ]
        )
