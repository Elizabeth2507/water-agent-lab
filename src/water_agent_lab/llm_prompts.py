import json

from water_agent_lab.agent_memory import AgentMemory
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
    proposal: AllocationProposal,
    state: AgentState,
    scenario: ScenarioConfig | None = None,
    round_number: int = 1,
    memory: AgentMemory | None = None,
    memory_limit: int = 5,
) -> str:
    """
    Build the user prompt asking the stakeholder agent to evaluate a proposal.

    This is the Step 74 prompt interface. It uses the full proposal and optional
    scenario/memory context instead of receiving only allocated_water.
    """
    allocated_water = proposal.allocations.get(stakeholder.name, 0.0)

    memory_summary = _summarize_memory(
        memory=memory,
        stakeholder_name=stakeholder.name,
        memory_limit=memory_limit,
    )

    context: dict[str, object] = {
        "round_number": round_number,
        "stakeholder": {
            "name": stakeholder.name,
            "requested_water": stakeholder.requested_water,
            "minimum_acceptable_water": stakeholder.minimum_acceptable_water,
            "priority": stakeholder.priority,
            "allocated_water": allocated_water,
        },
        "proposal": {
            "allocations": proposal.allocations,
        },
        "agent_state": {
            "frustration": state.frustration,
            "trust_in_mediator": state.trust_in_mediator,
            "concessions_made": state.concessions_made,
            "last_status": state.last_status,
        },
        "memory_summary": memory_summary,
        "output_schema": {
            "stakeholder_name": stakeholder.name,
            "status": "accepted | concerned | rejected",
            "argument": "short explanation from the stakeholder perspective",
            "requested_extra_water": "non-negative number",
            "willingness_to_compromise": "number between 0 and 1",
        },
    }

    if scenario is not None:
        total_requested = sum(item.requested_water for item in scenario.stakeholders)

        context["scenario"] = {
            "scenario_name": scenario.scenario_name,
            "country": scenario.country,
            "region": scenario.region,
            "drought_level": scenario.drought_level,
            "available_water": scenario.available_water,
            "total_requested_water": total_requested,
            "max_rounds": scenario.max_rounds,
        }

    return f"""
Evaluate the following water-allocation proposal.

Use the memory summary to remain consistent with previous negotiation rounds.
Do not invent events that are not present in memory.

Return only valid JSON matching the requested output_schema.

Decision rules:
- Use "rejected" if allocated_water is below the minimum_acceptable_water.
- Use "concerned" if allocated_water is at least the minimum but still meaningfully below requested_water.
- Use "accepted" if the allocation is close to the requested_water.
- requested_extra_water must be 0 if status is "accepted".
- requested_extra_water should describe how much additional water would make the proposal more acceptable.

Context:
{json.dumps(context, indent=2)}
""".strip()


def _summarize_memory(
    memory: AgentMemory | None,
    stakeholder_name: str,
    memory_limit: int,
) -> str:
    """
    Summarize optional memory for one stakeholder.

    The helper is defensive so prompt construction does not break if AgentMemory
    evolves slightly.
    """
    if memory is None:
        return "No relevant memory entries."

    summarize = getattr(memory, "summarize", None)

    if callable(summarize):
        try:
            return str(
                summarize(
                    stakeholder_name=stakeholder_name,
                    limit=memory_limit,
                )
            )
        except TypeError:
            return str(summarize())

    return "No relevant memory entries."
