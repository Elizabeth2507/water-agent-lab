# WaterAgentLab Scenario Configuration

WaterAgentLab uses YAML files to define drought water-allocation scenarios.

A scenario describes:

- the country and region
- drought severity
- total available water
- stakeholder water requests
- minimum acceptable water levels
- stakeholder priority values

Scenario files are stored in:

```text
configs/
```

Example:

```text
configs/drought_mvp.yaml
configs/mild_drought.yaml
configs/severe_drought.yaml
configs/extreme_drought.yaml
```

---

## Basic scenario structure

A scenario config has this structure:

```yaml
scenario_name: moderate_drought_mvp
country: France
region: Occitanie
drought_level: moderate
available_water: 100.0
max_rounds: 5

stakeholders:
  - name: agriculture
    requested_water: 50.0
    minimum_acceptable_water: 35.0
    priority: 0.8

  - name: urban
    requested_water: 35.0
    minimum_acceptable_water: 28.0
    priority: 0.9
```

---

## Top-level fields

| Field | Type | Required | Description |
|---|---:|---:|---|
| `scenario_name` | string | yes | Unique name for the scenario. |
| `country` | string | yes | Country where the drought scenario is located. |
| `region` | string | yes | Region or area represented by the scenario. |
| `drought_level` | string | yes | Drought severity label. |
| `available_water` | float | yes | Total water available for allocation. |
| `max_rounds` | integer | yes | Maximum number of negotiation rounds. |
| `stakeholders` | list | yes | List of stakeholder water demands. |

---

## Stakeholder fields

Each stakeholder must include:

| Field | Type | Required | Description |
|---|---:|---:|---|
| `name` | string | yes | Stakeholder name. |
| `requested_water` | float | yes | Amount of water requested by the stakeholder. |
| `minimum_acceptable_water` | float | yes | Minimum amount of water the stakeholder can accept without rejecting the proposal. |
| `priority` | float | yes | Policy priority between `0.0` and `1.0`. |

Example:

```yaml
- name: ecosystem
  requested_water: 20.0
  minimum_acceptable_water: 18.0
  priority: 1.0
```

---

## Validation rules

WaterAgentLab validates scenario configs with Pydantic models.

The main validation rules are:

| Rule | Explanation |
|---|---|
| `available_water > 0` | A scenario must have positive available water. |
| `max_rounds > 0` | Negotiation must allow at least one round. |
| `requested_water > 0` | Each stakeholder must request a positive amount of water. |
| `minimum_acceptable_water >= 0` | Minimum acceptable water cannot be negative. |
| `minimum_acceptable_water <= requested_water` | A stakeholder cannot require more than it requested. |
| `0 <= priority <= 1` | Priority must be between 0 and 1. |
| `stakeholders` cannot be empty | A scenario must contain at least one stakeholder. |

---

## Drought levels

The project currently uses this drought severity order:

```text
mild
moderate
severe
extreme
```

This order is used when sorting scenarios in batch results and plots.

Unknown drought levels are allowed, but they are sorted after the known levels.

---

## Example full scenario

```yaml
scenario_name: moderate_drought_mvp
country: France
region: Occitanie
drought_level: moderate
available_water: 100.0
max_rounds: 5

stakeholders:
  - name: agriculture
    requested_water: 50.0
    minimum_acceptable_water: 35.0
    priority: 0.8

  - name: urban
    requested_water: 35.0
    minimum_acceptable_water: 28.0
    priority: 0.9

  - name: industry
    requested_water: 25.0
    minimum_acceptable_water: 15.0
    priority: 0.5

  - name: ecosystem
    requested_water: 20.0
    minimum_acceptable_water: 18.0
    priority: 1.0
```

In this scenario:

```text
available water = 100
total requested water = 130
total minimum acceptable water = 96
```

This means there is enough water to satisfy all minimum acceptable levels, but not enough water to satisfy every full request.

---

## Validate a scenario

Use:

```bash
uv run water-agent-lab validate-config --config configs/drought_mvp.yaml
```

If the config is valid, the command should pass.

You can also run the full project health check:

```bash
uv run water-agent-lab doctor
```

---

## Run one scenario

Run one allocation strategy:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy proportional
```

Compare all strategies on one scenario:

```bash
uv run water-agent-lab compare --config configs/drought_mvp.yaml
```

Run stakeholder responses:

```bash
uv run water-agent-lab agent-responses --config configs/drought_mvp.yaml --strategy proportional
```

Run multi-round negotiation:

```bash
uv run water-agent-lab negotiate-multi --config configs/drought_mvp.yaml --strategy proportional
```

---

## Add a new scenario

To add a new scenario:

1. Create a new YAML file in `configs/`.
2. Use the same schema as the existing configs.
3. Validate it with `validate-config`.
4. Run it with `simulate`, `compare`, or `run-all`.

Example:

```bash
uv run water-agent-lab validate-config --config configs/my_new_scenario.yaml
```

Then run:

```bash
uv run water-agent-lab simulate --config configs/my_new_scenario.yaml --strategy minimum-first
```

---


## Mock drought snapshots

WaterAgentLab also includes a mock JSON drought snapshot format.

Example:

```text
data/mock/occitanie_drought_snapshot.json
```


## VigiEau sample adapter

WaterAgentLab includes a skeleton adapter for simplified VigiEau-style drought restriction data.

Example sample file:

```text
data/sample_vigieau/occitanie_restrictions_sample.json
```


## Hub’Eau hydrometry sample adapter

WaterAgentLab includes a skeleton adapter for simplified Hub’Eau hydrometry-style data.

Example sample file:

```text
data/sample_hubeau/occitanie_hydrometry_sample.json
```


## Hub’Eau hydrometry sample adapter

WaterAgentLab includes a skeleton adapter for simplified Hub’Eau hydrometry-style data.

Example sample file:

```text
data/sample_hubeau/occitanie_hydrometry_sample.json
```

## Registered data sources

WaterAgentLab includes a unified data-source registry.

Available source names include:

```text
synthetic
mock
vigieau-sample
hubeau-sample
```


## Export scenarios from data sources

Registered data sources can be converted into normal YAML scenario configs.

Example:

```bash
uv run water-agent-lab export-scenario-from-data \
  --source hubeau-sample \
  --path data/sample_hubeau/occitanie_hydrometry_sample.json \
  --output configs/generated_hubeau_occitanie.yaml
  ```


The exported scenario can then be validated and used by the existing simulation commands:
```bash
uv run water-agent-lab validate-config --config configs/generated_hubeau_occitanie.yaml
uv run water-agent-lab simulate --config configs/generated_hubeau_occitanie.yaml --strategy minimum-first
```


## Notes for future real-data scenarios

Current scenarios are synthetic. Future versions may include fields for:

```text
data_source
observation_date
river_basin
restriction_level
hydrological_indicator
legal_constraints
```

These fields are not currently part of the validated schema.