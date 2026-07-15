from pydantic import BaseModel, Field, model_validator


class StakeholderConfig(BaseModel):
    """
    Configuration for one water-demand stakeholder.

    Example stakeholders:
    - agriculture
    - urban population
    - industry
    - ecosystem
    """

    name: str
    requested_water: float = Field(gt=0)
    minimum_acceptable_water: float = Field(ge=0)
    priority: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def minimum_cannot_exceed_request(self) -> "StakeholderConfig":
        if self.minimum_acceptable_water > self.requested_water:
            raise ValueError("minimum_acceptable_water cannot exceed requested_water")
        return self


class ScenarioConfig(BaseModel):
    """
    Full drought scenario configuration.

    This object represents one complete water-allocation problem.
    """

    scenario_name: str
    country: str
    region: str
    drought_level: str
    available_water: float = Field(gt=0)
    max_rounds: int = Field(gt=0)
    stakeholders: list[StakeholderConfig]

    @model_validator(mode="after")
    def scenario_must_have_stakeholders(self) -> "ScenarioConfig":
        if not self.stakeholders:
            raise ValueError("scenario must contain at least one stakeholder")
        return self


class AllocationProposal(BaseModel):
    """
    A proposed allocation of water.

    Example:
    {
        "agriculture": 38.46,
        "urban": 26.92,
        "industry": 19.23,
        "ecosystem": 15.38
    }
    """

    allocations: dict[str, float]

    @model_validator(mode="after")
    def allocations_must_be_non_negative(self) -> "AllocationProposal":
        for stakeholder_name, amount in self.allocations.items():
            if amount < 0:
                raise ValueError(
                    f"Allocation for {stakeholder_name} cannot be negative"
                )
        return self


class SimulationResult(BaseModel):
    """
    Final evaluated result of one simulation run.
    """

    scenario_name: str
    country: str
    region: str
    drought_level: str
    available_water: float
    total_requested: float
    total_allocated: float
    water_budget_valid: bool
    agreement_reached: bool
    fairness_score: float
    conflict_score: float
    allocations: dict[str, float]
