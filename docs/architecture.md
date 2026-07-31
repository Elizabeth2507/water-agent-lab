# WaterAgentLab Architecture

WaterAgentLab is a simulation and experiment framework for studying water-resource allocation during drought.

The project models a drought scenario, applies deterministic allocation strategies, evaluates outcomes, collects stakeholder responses, and records experiment metadata for reproducibility.

## High-level architecture

```mermaid
flowchart TD
    A[Scenario YAML configs] --> B[Config loader]
    B --> C[Pydantic scenario models]
    C --> D[Allocation strategies]
    D --> E[Allocation proposal]
    E --> F[Evaluator metrics]
    E --> G[Rule-based stakeholder agents]
    G --> H[Negotiation loop]
    F --> I[Simulation result]
    H --> J[Negotiation history]
    I --> K[CSV/JSON exports]
    J --> L[Negotiation JSON export]
    K --> M[Plots and reports]
    K --> N[Experiment registry]
    L --> N
    M --> N
```

## Core data flow

A typical simulation follows this flow:

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant Strategy
    participant Evaluator

    User->>CLI: simulate --config ... --strategy ...
    CLI->>Config: load_scenario_config()
    Config-->>CLI: ScenarioConfig
    CLI->>Strategy: create allocation proposal
    Strategy-->>CLI: AllocationProposal
    CLI->>Evaluator: evaluate_proposal()
    Evaluator-->>CLI: SimulationResult
    CLI-->>User: JSON result
```

## Main components

| Component | File | Responsibility |
|---|---|---|
| Config loader | `config.py` | Loads and validates scenario YAML files. |
| Data models | `models.py` | Defines scenario, stakeholder, allocation, and simulation result models. |
| Strategies | `strategies.py`, `simulator.py` | Provides deterministic allocation baselines. |
| Evaluator | `evaluator.py` | Computes fairness, conflict, satisfaction, shortage, and agreement metrics. |
| Agents | `agents.py` | Produces rule-based stakeholder responses. |
| Negotiation | `negotiation.py` | Runs simple and multi-round negotiation loops. |
| Exporter | `exporter.py` | Saves CSV and JSON outputs. |
| Plotter | `plotter.py` | Generates fairness/conflict plots. |
| Reporting | `reporting.py` | Generates Markdown experiment reports. |
| Registry | `experiment_registry.py` | Records experiment metadata and output paths. |
| Reproducibility | `hashing.py`, `reproduction.py`, `run_comparison.py` | Tracks config hashes, reproduces runs, and compares outputs. |
| Project health | `doctor.py` | Checks whether the project is ready to run. |
| CLI | `cli.py` | Exposes the user-facing commands. |

## Allocation strategies

WaterAgentLab currently supports four deterministic allocation strategies.

| Strategy | Command name | Description |
|---|---|---|
| Proportional | `proportional` | Allocates water proportional to requested demand. |
| Priority-weighted | `priority` | Allocates water by requested demand multiplied by stakeholder priority. |
| Minimum-first | `minimum-first` | Satisfies minimum acceptable water first, then distributes the remainder. |
| Minimum-priority | `minimum-priority` | Satisfies minimums first, then distributes remaining water using priority-weighted unmet demand. |

These strategies are deterministic baselines. They provide a stable reference before adding more complex rule-based or LLM-based negotiation.

## Agent architecture

Stakeholder agents evaluate allocation proposals.

```mermaid
flowchart LR
    A[AllocationProposal] --> B[Agriculture agent]
    A --> C[Urban agent]
    A --> D[Industry agent]
    A --> E[Ecosystem agent]

    B --> F[StakeholderResponse]
    C --> F
    D --> F
    E --> F
```

Each agent returns one of three statuses:

| Status | Meaning |
|---|---|
| `accepted` | The allocation is close to requested demand. |
| `concerned` | The allocation is above minimum acceptable water but below requested demand. |
| `rejected` | The allocation is below minimum acceptable water. |

## Negotiation loop

The multi-round negotiation system uses stakeholder responses to revise the allocation strategy.

```mermaid
flowchart TD
    A[Initial strategy] --> B[Allocation proposal]
    B --> C[Stakeholder responses]
    C --> D{Any rejected stakeholders?}
    D -- No --> E[Agreement reached]
    D -- Yes --> F[Choose revision strategy]
    F --> G[New allocation proposal]
    G --> C
    D -- Max rounds reached --> H[Stop without agreement]
```

The current revision rules are simple:

| Current strategy | Revised strategy |
|---|---|
| `proportional` | `minimum-first` |
| `priority` | `minimum-priority` |
| `minimum-first` | `minimum-first` |
| `minimum-priority` | `minimum-priority` |

## Experiment tracking

WaterAgentLab includes lightweight experiment tracking.

```mermaid
flowchart TD
    A[Run command] --> B[Create run metadata]
    B --> C[Run simulation or negotiation]
    C --> D[Save outputs]
    D --> E[Compute config hashes]
    E --> F[Append registry record]
    F --> G[Verify / reproduce / compare runs]
```

Each recorded run can include:

```text
run_id
created_at_utc
command
status
config paths
config hashes
output paths
```

This allows the project to support:

```text
list-runs
show-run
verify-run
reproduce-run
compare-runs
dashboard
```

## End-to-end workflow

The easiest way to run the full experiment pipeline is:

```bash
uv run water-agent-lab run-experiment
```

This command runs:

```mermaid
flowchart LR
    A[Scenario configs] --> B[Batch simulation]
    B --> C[Results CSV]
    C --> D[Markdown report]
    C --> E[Fairness/conflict plot]
    C --> F[Experiment registry]
    D --> F
    E --> F
```

For a quick demo, run:

```bash
uv run water-agent-lab demo
```

The LLM backend layer supports multiple implementations. The default test backend is `MockLLMBackend`; an optional `QwenLocalBackend` can be used locally for real model inference without changing the agent interface.

## Current limitations

WaterAgentLab currently uses synthetic drought scenarios. It does not yet use real hydrological data, legal restriction data, or LLM-based stakeholder negotiation.

The current agent system is deterministic and rule-based. This is intentional: it provides a reliable and testable foundation before adding more complex agent behavior.

## Future extensions

Planned directions include:

1. Real drought and hydrological data integration.
2. More sophisticated stakeholder utility functions.
3. Richer negotiation policies.
4. LLM-based stakeholder agents.
5. Experiment tracking integration with MLflow or Weights & Biases.
6. Web dashboard or Streamlit demo.