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
- Proportional allocation baseline
- Priority-weighted allocation baseline
- Minimum-first allocation baseline
- Minimum-priority allocation baseline
- Water-budget validation
- Fairness score
- Conflict score
- Agreement detection
- Command-line interface
- Rule-based stakeholder responses
- Simple rule-based negotiation round
- Multi-round rule-based negotiation
- Negotiation history summarization
- Structured JSON logging for simulation and negotiation runs
- Run metadata with unique run IDs and UTC timestamps
- Lightweight experiment registry for tracking exported runs
- Terminal dashboard for experiment registry summaries

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

Run the minimum-first baseline:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy minimum-first
```

Run the minimum-priority baseline:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy minimum-priority
```

Compare available strategies:

```bash
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

Show stakeholder responses to an allocation:

```bash
uv run water-agent-lab agent-responses --config configs/drought_mvp.yaml --strategy minimum-first
```

Plot fairness and conflict scores:

```bash
uv run water-agent-lab plot-results --input outputs/results.csv --output outputs/fairness_conflict.png
```


Run a multi-round negotiation:

```bash
uv run water-agent-lab negotiate-multi --config configs/drought_mvp.yaml --strategy proportional
```

Run a multi-round negotiation and save the full negotiation history:

```bash
uv run water-agent-lab negotiate-multi --config configs/drought_mvp.yaml --strategy proportional --output outputs/negotiation_history.json
```

```markdown
The saved negotiation history includes each negotiation round, the strategy used, evaluation metrics, stakeholder responses, and rejected stakeholders.


Summarize a saved negotiation history:

```bash
uv run water-agent-lab summarize-negotiation --input outputs/negotiation_history.json
```

```markdown
The negotiation summary command reads a saved negotiation history JSON file and prints a compact explanation of the strategy sequence, rejected stakeholders, final metrics, and agreement status.
```

Run a simulation with structured logs:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy proportional --log-file outputs/simulation.log
```

Show CLI help:

```bash
uv run water-agent-lab --help
```

Show help for the simulation command:

```bash
uv run water-agent-lab simulate --help
```


### `generate-report`

Generate a Markdown experiment summary report from CSV results.

```bash
uv run water-agent-lab generate-report \
  --input outputs/all_results.csv \
  --output docs/experiment_report.md
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


## Allocation strategies

WaterAgentLab currently supports several deterministic allocation baselines.

| Strategy | Command name | Main idea | Best for | Limitation |
|---|---|---|---|---|
| Proportional allocation | `proportional` | Allocates water in proportion to each stakeholder's requested demand. | Simple and transparent baseline. | Does not consider stakeholder priority or minimum acceptable needs. |
| Priority-weighted allocation | `priority` | Allocates water according to requested demand multiplied by stakeholder priority. | Testing how priority values affect scarcity distribution. | Can leave lower-priority stakeholders below minimum acceptable water. |
| Minimum-first allocation | `minimum-first` | First tries to satisfy every stakeholder's minimum acceptable water, then distributes remaining water proportionally to unmet demand. | Reducing conflict and protecting minimum needs. | If minimum needs cannot all be satisfied, conflict still remains. |
| Minimum-priority allocation | `minimum-priority` | First protects minimum acceptable water, then distributes remaining water using priority-weighted unmet demand. | Combining minimum protection with policy priority. | May shift remaining scarcity toward lower-priority stakeholders. |

These strategies are intentionally simple and deterministic. They provide baselines for later comparison with rule-based agents, multi-round negotiation, and LLM-powered stakeholder simulations.


```markdown
## Rule-based stakeholder agents

WaterAgentLab includes simple rule-based stakeholder agents.

Each agent evaluates an allocation proposal and returns one of three statuses:

| Status | Meaning |
|---|---|
| `accepted` | The allocation is close to the stakeholder's requested demand. |
| `concerned` | The allocation is above the minimum acceptable level but below requested demand. |
| `rejected` | The allocation is below the minimum acceptable level. |

These agents are deterministic and transparent. They are the first step toward future multi-round negotiation and LLM-powered stakeholder simulation.


## Simple negotiation

WaterAgentLab includes a first simple negotiation loop.

The system first runs an initial allocation strategy. Stakeholder agents then evaluate the proposal. If any stakeholder rejects the proposal because it falls below minimum acceptable water, the system revises the allocation using the `minimum-first` strategy.

This is not yet full multi-round negotiation, but it provides the first step toward agent-based stakeholder interaction.


## Multi-round negotiation

WaterAgentLab includes a simple multi-round negotiation loop.

The system starts with an initial allocation strategy, collects stakeholder responses, and revises the strategy when stakeholders reject the proposal. The process stops when agreement is reached or the scenario's `max_rounds` limit is reached.

This is still rule-based and deterministic, but it provides the foundation for future agent-based and LLM-powered negotiation.


## Structured logging

WaterAgentLab can write structured JSON logs for simulation and negotiation runs.

Each log line is a JSON object containing an event name, message, level, and context fields. This makes runs easier to inspect, debug, and later connect to experiment tracking tools.


## Run metadata

Simulation and negotiation runs include metadata such as a unique `run_id`, UTC timestamp, and command name.

This makes it easier to connect logs, exported results, and negotiation history files from the same experiment run.

Batch scenario exports also include run metadata, so every CSV or JSON row can be traced back to the experiment run that produced it.


## Experiment registry

WaterAgentLab records exported experiment runs in a lightweight JSONL registry.

The registry stores run metadata, command name, status, and output paths. This makes it easier to trace which command produced which result file.

List recorded runs:

```bash
uv run water-agent-lab list-runs
```


By default, records are saved to:

```text
outputs/experiment_registry.jsonl
```

You can choose a custom registry path:
```bash
uv run water-agent-lab run-all --config-dir configs --output outputs/results.csv --registry outputs/my_registry.jsonl
```

List runs from a custom registry:

```bash
uv run water-agent-lab list-runs --registry outputs/my_registry.jsonl
```

Show details for one recorded run:

```bash
uv run water-agent-lab show-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
```

```markdown
The `show-run` command displays the metadata and output files associated with one experiment run. This is useful when the registry contains many simulations or negotiation experiments.

Registry records also include SHA256 hashes of the scenario config files. This helps make experiment runs reproducible, because a run can be linked not only to a config path but also to the exact config content used at the time.


Example registry fields:

```json
{
  "run_id": "...",
  "command": "run-all",
  "config_dir": "configs",
  "config_hashes": {
    "configs/drought_mvp.yaml": "..."
  },
  "outputs": {
    "results": "outputs/results.csv"
  }
}
```

Verify whether the current config files still match a recorded run:

```bash
uv run water-agent-lab verify-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
```

Reproduce a recorded run:

```bash
uv run water-agent-lab reproduce-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
```

The `reproduce-run` command verifies that config hashes still match before re-running the recorded experiment. It then writes a new output file and records the reproduced run in the registry with a `reproduced_from_run_id` field.


Compare an original run with a reproduced run:

```bash
uv run water-agent-lab compare-runs --run-id ORIGINAL_RUN_ID --reproduced-run-id REPRODUCED_RUN_ID --registry outputs/my_registry.jsonl
```

Show a dashboard summary of recorded runs:

```bash
uv run water-agent-lab dashboard --registry outputs/my_registry.jsonl
```


## Experiment report

Generate a Markdown experiment report:

```bash
uv run water-agent-lab generate-report --input outputs/results.csv --output docs/experiment_report.md
```


Generate a report from a recorded `run-all` experiment:

```bash
uv run water-agent-lab generate-run-report --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl --output docs/experiment_report.md
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

```markdown
- [Experiment report](docs/experiment_report.md)