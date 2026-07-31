# WaterAgentLab

WaterAgentLab is a Python project for simulating water-resource allocation during drought.

The project started as a small MVP: load a drought scenario from YAML, allocate a limited amount of water between stakeholders, and evaluate the result with simple metrics. It has now grown into a more complete experiment workflow with multiple allocation strategies, stakeholder responses, negotiation loops, reports, plots, run metadata, and reproducibility tools.

The current version is intentionally deterministic by default. This makes the simulations easy to test, compare, and reproduce before adding more complex LLM-based agents.

---

## Why this project?

During drought, available water can be lower than total demand. Agriculture, cities, industry, and ecosystems may all need water, but they do not have the same priorities, constraints, or minimum acceptable levels.

WaterAgentLab explores this kind of allocation problem in a structured way. The goal is not to make real policy decisions, but to build a small research environment where different allocation and negotiation approaches can be compared.

The project is designed to answer questions such as:

- How do different allocation strategies behave under drought?
- Which strategies reduce stakeholder conflict?
- Which stakeholders fall below their minimum acceptable water level?
- Can negotiation improve the initial allocation?
- Can experiments be tracked and reproduced cleanly?

In the longer term, the same structure can be extended with LLM-powered stakeholder agents and more realistic water data.

---

## What the project does now

WaterAgentLab currently supports:

- YAML-based drought scenario configuration
- Pydantic validation for scenarios, stakeholders, proposals, and results
- Four deterministic allocation strategies
- Fairness, conflict, shortage, agreement, and minimum-satisfaction metrics
- Rule-based stakeholder responses
- Simple and multi-round negotiation
- Negotiation history export and summarization
- CSV and JSON result export
- Markdown experiment reports
- Optional fairness/conflict plots
- Structured JSON logging
- Run metadata with run IDs and UTC timestamps
- Experiment registry in JSONL format
- Config hashing for reproducibility checks
- Run verification, reproduction, and comparison
- A small terminal dashboard for experiment summaries
- One-command demo workflow
- Safe cleanup command for demo outputs
- Project health check command
- Tests, formatting, and linting with `pytest` and `ruff`
- Mock real-data adapter for future drought data integration
- VigiEau sample data-source skeleton
- Unified data-source registry
- Scenario export from registered data sources
- Combined VigiEau + Hub’Eau sample scenario builder
- Mock LLM stakeholder-agent workflow
- Mock LLM multi-round negotiation with transcript export
- Structured agent memory extracted from AI-agent transcripts
- Monte Carlo runner for mock LLM negotiations
- Monte Carlo reports and plots for mock LLM negotiations
- Rule-based vs mock LLM negotiation mode comparison
- Reports and plots for rule-based vs mock LLM negotiation comparison

---

## Documentation

More detailed documentation is available in the `docs/` directory:

- [Architecture overview](docs/architecture.md)
- [CLI command reference](docs/commands.md)
- [Scenario configuration guide](docs/scenarios.md)
- [Metrics guide](docs/metrics.md)
- [Allocation strategies guide](docs/strategies.md)
- [Agents and negotiation guide](docs/agents_and_negotiation.md)
- [Experiment results](docs/results.md)

---

## Installation

This project uses `uv` for dependency and environment management.

Clone the repository:

```bash
git clone https://github.com/Elizabeth2507/water-agent-lab.git
cd water-agent-lab
````

Install dependencies:

```bash
uv sync
```

Check that the project is ready to run:

```bash
uv run water-agent-lab doctor
```

---

## Quick demo

Run the full demo workflow:

```bash
uv run water-agent-lab demo
```

This creates demo outputs under:

```text
outputs/demo/
```

You can inspect the demo registry with:

```bash
uv run water-agent-lab dashboard --registry outputs/demo/experiment_registry.jsonl
```

To preview cleanup without deleting anything:

```bash
uv run water-agent-lab clean-demo --output-dir outputs/demo
```

To actually remove the demo output directory:

```bash
uv run water-agent-lab clean-demo --output-dir outputs/demo --yes
```

---

## Basic usage

Run the default drought simulation:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml
```

Run a specific allocation strategy:

```bash
uv run water-agent-lab simulate \
  --config configs/drought_mvp.yaml \
  --strategy proportional
```

Compare all strategies on one scenario:

```bash
uv run water-agent-lab compare --config configs/drought_mvp.yaml
```

Run all scenario configs with all strategies:

```bash
uv run water-agent-lab run-all --config-dir configs
```

Export all results to CSV:

```bash
uv run water-agent-lab run-all \
  --config-dir configs \
  --output outputs/results.csv
```

Create a fairness/conflict plot:

```bash
uv run water-agent-lab plot-results \
  --input outputs/results.csv \
  --output outputs/fairness_conflict.png
```

---

## Experiment reports

Generate a Markdown report from exported results:

```bash
uv run water-agent-lab generate-report \
  --input outputs/results.csv \
  --output docs/experiment_report.md
```

Generate a report and include a plot:

```bash
uv run water-agent-lab generate-report \
  --input outputs/results.csv \
  --output docs/experiment_report.md \
  --plot outputs/fairness_conflict.png
```

A typical experiment workflow is:

```bash
uv run water-agent-lab run-all \
  --config-dir configs \
  --output outputs/results.csv

uv run water-agent-lab generate-report \
  --input outputs/results.csv \
  --output docs/experiment_report.md \
  --plot outputs/fairness_conflict.png
```

---

## Negotiation

WaterAgentLab includes simple rule-based stakeholder agents. Each stakeholder evaluates an allocation and returns one of three statuses:

| Status      | Meaning                                                             |
| ----------- | ------------------------------------------------------------------- |
| `accepted`  | The allocation is close enough to the requested amount              |
| `concerned` | The allocation is acceptable, but lower than requested              |
| `rejected`  | The allocation is below the stakeholder's minimum acceptable amount |

Show stakeholder responses to an allocation:

```bash
uv run water-agent-lab agent-responses \
  --config configs/drought_mvp.yaml \
  --strategy minimum-first
```

Run a multi-round negotiation:

```bash
uv run water-agent-lab negotiate-multi \
  --config configs/drought_mvp.yaml \
  --strategy proportional
```

Save the full negotiation history:

```bash
uv run water-agent-lab negotiate-multi \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/negotiation_history.json
```

Summarize a saved negotiation history:

```bash
uv run water-agent-lab summarize-negotiation \
  --input outputs/negotiation_history.json
```

The negotiation history stores each round, the strategy used, the evaluation metrics, stakeholder responses, and the stakeholders that rejected the proposal.

---

## Experiment registry and reproducibility

WaterAgentLab can record exported runs in a lightweight JSONL registry.

By default, registry records are saved to:

```text
outputs/experiment_registry.jsonl
```

Run an experiment and save it to the registry:

```bash
uv run water-agent-lab run-all \
  --config-dir configs \
  --output outputs/results.csv \
  --registry outputs/experiment_registry.jsonl
```

List recorded runs:

```bash
uv run water-agent-lab list-runs \
  --registry outputs/experiment_registry.jsonl
```

Show details for one run:

```bash
uv run water-agent-lab show-run \
  --run-id YOUR_RUN_ID \
  --registry outputs/experiment_registry.jsonl
```

Verify that the current config files still match a recorded run:

```bash
uv run water-agent-lab verify-run \
  --run-id YOUR_RUN_ID \
  --registry outputs/experiment_registry.jsonl
```

Reproduce a recorded run:

```bash
uv run water-agent-lab reproduce-run \
  --run-id YOUR_RUN_ID \
  --registry outputs/experiment_registry.jsonl
```

Compare an original run with a reproduced run:

```bash
uv run water-agent-lab compare-runs \
  --run-id ORIGINAL_RUN_ID \
  --reproduced-run-id REPRODUCED_RUN_ID \
  --registry outputs/experiment_registry.jsonl
```

Generate a report from a recorded `run-all` experiment:

```bash
uv run water-agent-lab generate-run-report \
  --run-id YOUR_RUN_ID \
  --registry outputs/experiment_registry.jsonl \
  --output docs/experiment_report.md
```

The registry also stores config hashes. This makes it possible to check whether a run can still be reproduced with the current scenario files.

---

## Example scenario

The default scenario is defined in:

```text
configs/drought_mvp.yaml
```

It represents a moderate drought situation in Occitanie, France.

There are 100 units of available water, while total requested water is 130 units.

| Stakeholder | Requested water | Minimum acceptable water | Priority |
| ----------- | --------------: | -----------------------: | -------: |
| agriculture |            50.0 |                     35.0 |      0.8 |
| urban       |            35.0 |                     28.0 |      0.9 |
| industry    |            25.0 |                     15.0 |      0.5 |
| ecosystem   |            20.0 |                     18.0 |      1.0 |

---

## Allocation strategies

The project currently includes four deterministic strategies:

| Strategy                     | Command name       | Main idea                                                                         |
| ---------------------------- | ------------------ | --------------------------------------------------------------------------------- |
| Proportional allocation      | `proportional`     | Allocates water in proportion to each stakeholder's requested amount              |
| Priority-weighted allocation | `priority`         | Allocates water using requested demand weighted by priority                       |
| Minimum-first allocation     | `minimum-first`    | Tries to satisfy minimum acceptable water first, then distributes what remains    |
| Minimum-priority allocation  | `minimum-priority` | Protects minimum acceptable water first, then uses priority-weighted distribution |

These strategies are simple on purpose. They provide clear baselines before moving to more complex negotiation or LLM-agent behavior.

---

## Metrics

WaterAgentLab evaluates allocation proposals with several metrics:

| Metric                       | Meaning                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| `water_budget_valid`         | Whether total allocated water stays within available water                           |
| `fairness_score`             | Average satisfaction relative to requested water                                     |
| `conflict_score`             | Fraction of stakeholders below their minimum acceptable water                        |
| `minimum_satisfaction_score` | Average satisfaction relative to minimum acceptable needs                            |
| `shortage_score`             | Overall shortage pressure in the scenario                                            |
| `agreement_reached`          | Whether the budget is valid and no stakeholder is below its minimum acceptable water |

A lower conflict score usually means fewer stakeholders are pushed below their minimum acceptable threshold.

---

## Example output

The proportional strategy gives every stakeholder the same fraction of their requested water:

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
  "minimum_satisfaction_score": 0.9540598290598291,
  "shortage_score": 0.23076923076923078,
  "allocations": {
    "agriculture": 38.46153846153846,
    "urban": 26.923076923076923,
    "industry": 19.23076923076923,
    "ecosystem": 15.384615384615383
  }
}
```

The water budget is valid, but agreement is not reached because some stakeholders receive less than their minimum acceptable amount.

---

## Development

Format code:

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

Run the full local check:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

---


## Data sources

Current scenarios are synthetic YAML files. WaterAgentLab includes a data-source abstraction so future versions can generate scenarios from real drought and hydrological data sources.

Potential future sources include VigiEau drought restriction data and Hub’Eau hydrometry or groundwater APIs.

WaterAgentLab includes a mock drought JSON snapshot adapter:

```bash
uv run water-agent-lab load-mock-data --snapshot data/mock/occitanie_drought_snapshot.json
```

WaterAgentLab also includes a VigiEau sample adapter:

```bash
uv run water-agent-lab load-vigieau-sample --sample data/sample_vigieau/occitanie_restrictions_sample.json
```


```markdown
WaterAgentLab also includes a Hub’Eau hydrometry sample adapter:

```bash
uv run water-agent-lab load-hubeau-sample --sample data/sample_hubeau/occitanie_hydrometry_sample.json
```

```markdown
This is currently a local sample-based skeleton. It prepares the project for future integration with river-flow or hydrometric data.



Export a generated scenario from a data source:

```bash
uv run water-agent-lab export-scenario-from-data \
  --source hubeau-sample \
  --path data/sample_hubeau/occitanie_hydrometry_sample.json \
  --output configs/generated_hubeau_occitanie.yaml
```

The generated YAML file can then be used with simulate, compare, run-all, or negotiate-multi.


Build a combined sample scenario:

```bash
uv run water-agent-lab build-combined-scenario \
  --vigieau data/sample_vigieau/occitanie_restrictions_sample.json \
  --hubeau data/sample_hubeau/occitanie_hydrometry_sample.json \
  --output configs/generated_combined_occitanie.yaml
  ```


Build a combined sample scenario:

```bash
uv run water-agent-lab build-combined-scenario \
  --vigieau data/sample_vigieau/occitanie_restrictions_sample.json \
  --hubeau data/sample_hubeau/occitanie_hydrometry_sample.json \
  --output configs/generated_combined_occitanie.yaml
```

--
## AI-agent layer

WaterAgentLab includes an early AI-agent architecture with a deterministic mock LLM backend.

```bash
uv run water-agent-lab llm-agent-responses --config configs/drought_mvp.yaml --strategy proportional
```


Run a mock LLM multi-round negotiation:

```bash
uv run water-agent-lab llm-negotiate-mock \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/mock_llm_negotiation.json
  ```


  Summarize memory from a mock LLM negotiation transcript:

```bash
uv run water-agent-lab summarize-agent-memory --transcript outputs/mock_llm_negotiation.json --stakeholder ecosystem
```


Run repeated mock LLM negotiations:

```bash
uv run water-agent-lab monte-carlo-mock \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --runs 20 \
  --seed 42 \
  --output outputs/monte_carlo_mock.csv
  ```


Generate a Monte Carlo report:

```bash
uv run water-agent-lab monte-carlo-report \
  --input outputs/monte_carlo_mock.csv \
  --output docs/monte_carlo_report.md
```


Compare rule-based negotiation with mock LLM-style negotiation:

```bash
uv run water-agent-lab compare-negotiation-modes \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --runs 20 \
  --seed 42 \
  --output outputs/negotiation_mode_comparison.csv
  ```


Generate a comparison report:

```bash
uv run water-agent-lab compare-negotiation-modes-report \
  --input outputs/negotiation_mode_comparison.csv \
  --output docs/negotiation_mode_comparison_report.md
```


### Optional local Qwen backend

WaterAgentLab includes an optional local Qwen backend for future real-model experiments.

Install optional dependencies:

```bash
uv sync --extra local-llm
```

The default workflow still uses deterministic mock LLM agents, so CI and tests do not require GPU access or model downloads.


### Local Qwen smoke test

Install optional local LLM dependencies:

```bash
uv sync --extra local-llm
```


## Design notes

The main branch is kept deterministic because reproducibility matters for this kind of simulation. Before adding LLM agents, it is useful to have a baseline where every run can be tested and compared exactly.

The project keeps simulation logic separate from the CLI. Most commands are thin wrappers around smaller modules, which makes the system easier to test and extend.

Outputs are structured whenever possible: CSV for experiment results, JSON for negotiation history, JSONL for the registry, Markdown for reports, and PNG for plots.

---

## Planned extensions

Possible next steps include:

* LLM-powered stakeholder agents
* Local model backends such as Qwen or Ollama
* LLM-as-a-judge evaluation for negotiation quality
* Richer stakeholder profiles and memory
* Larger scenario variation and Monte Carlo experiments
* Integration with French public drought and hydrometry data
* More detailed model behavior inspection

---

```
```
