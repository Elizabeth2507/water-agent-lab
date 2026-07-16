# WaterAgentLab

WaterAgentLab is a Python project for simulating water-resource allocation during drought.

The current MVP implements a simple, testable simulation engine. It loads a drought scenario from a YAML configuration file, allocates water with a deterministic baseline, and evaluates the result with basic fairness, conflict, and agreement metrics.

## Why this project?

During drought, available water may be lower than total demand. Different stakeholders — such as agriculture, urban population, industry, and ecosystems — may request more water than the system can provide.

WaterAgentLab is designed to explore this kind of allocation problem in a structured and extensible way.

The long-term goal is to compare simple allocation baselines, rule-based agents, and eventually LLM-powered stakeholder negotiation.

## Current features

- YAML-based drought scenario configuration
- Pydantic data models and validation
- Proportional water-allocation baseline
- Water-budget validation
- Fairness score
- Conflict score
- Agreement detection
- Command-line interface

## Planned extensions

- Unit tests
- Priority-based allocation strategies
- Rule-based stakeholder agents
- LLM-powered negotiation agents
- Experiment tracking
- Model behavior inspection
- Integration with French public drought and hydrometry data

## Installation

This project uses `uv` for dependency and environment management.

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/water-agent-lab.git
cd water-agent-lab
```

Install dependencies:

```bash
uv sync
```

## Usage

Run the default MVP simulation:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml
```

Run the proportional baseline:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy proportional
```

Run the priority-weighted baseline:

```
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy priority
```

Compare available strategies:

```
uv run water-agent-lab compare --config configs/drought_mvp.yaml
```

Run all scenarios and compare strategies:

```bash
uv run water-agent-lab run-all --config-dir configs
```

Export all scenario results:

```bash
uv run water-agent-lab run-all --config-dir configs --output outputs/results.csv
```


Plot fairness and conflict scores:

```
uv run water-agent-lab plot-results --input outputs/results.csv --output outputs/fairness_conflict.png
```


Show CLI help:

```bash
uv run water-agent-lab --help
```

Show help for the simulation command:

```bash
uv run water-agent-lab simulate --help
```



## Example scenario

The default scenario is defined in:

```text
configs/drought_mvp.yaml
```

It represents a moderate drought situation with 100 units of available water and four stakeholders:

| Stakeholder | Requested water | Minimum acceptable water | Priority |
|---|---:|---:|---:|
| agriculture | 50.0 | 35.0 | 0.8 |
| urban | 35.0 | 28.0 | 0.9 |
| industry | 25.0 | 15.0 | 0.5 |
| ecosystem | 20.0 | 18.0 | 1.0 |

Total requested water is 130 units, but only 100 units are available.

## Example output

The proportional baseline gives each stakeholder the same fraction of their requested water.

```json
{
  "scenario_name": "moderate_drought_mvp",
  "country": "France",
  "region": "Occitanie",
  "drought_level": "moderate",
  "available_water": 100.0,
  "total_requested": 130.0,
  "total_allocated": 100.0,
  "water_budget_valid": true,
  "agreement_reached": false,
  "fairness_score": 0.7692307692307692,
  "conflict_score": 0.5,
  "allocations": {
    "agriculture": 38.46153846153846,
    "urban": 26.923076923076923,
    "industry": 19.23076923076923,
    "ecosystem": 15.384615384615383
  }
}
```

In this result, the water budget is valid, but agreement is not reached because two stakeholders receive less than their minimum acceptable amount.

## Metrics

`water_budget_valid` checks whether the total allocated water is less than or equal to available water.

`fairness_score` measures average stakeholder satisfaction:

```text
allocated_water / requested_water
```

`conflict_score` measures the fraction of stakeholders below their minimum acceptable water.

`agreement_reached` is true only when the water budget is valid and no stakeholder is below its minimum acceptable water.


## Development

Run code formatting:

```bash
uv run ruff format .
```

Run linting:

```bash
uv run ruff check .
```

Run tests:

```bash
uv run pytest
```

## Design principle

WaterAgentLab separates responsibilities across modules:

- `models.py` defines validated data structures.
- `config.py` loads YAML scenario files.
- `simulator.py` creates allocation proposals.
- `evaluator.py` computes metrics.
- `cli.py` provides the command-line interface.

This structure keeps the project easy to test, extend, and later connect to rule-based or LLM-powered agents.

## Results

A short explanation of the first scenario comparison is available in:

```text
docs/results.md