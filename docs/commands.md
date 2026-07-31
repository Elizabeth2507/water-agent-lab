# WaterAgentLab CLI Commands

WaterAgentLab provides a command-line interface for running drought allocation simulations, stakeholder negotiation, experiment tracking, reproducibility checks, reports, and demos.

All commands use:

```bash
uv run water-agent-lab <command>
```

## Health and demo commands

### `doctor`

Check whether the project is ready to run.

```bash
uv run water-agent-lab doctor
```

Checks scenario configs, registered strategies, and writable output/report directories.

### `demo`

Run a complete demo workflow.

```bash
uv run water-agent-lab demo
```

Use a custom output directory:

```bash
uv run water-agent-lab demo --output-dir outputs/custom_demo
```

The demo creates:

```text
results.csv
experiment_report.md
fairness_conflict.png
experiment_registry.jsonl
```

### `clean-demo`

Preview deletion of demo outputs:

```bash
uv run water-agent-lab clean-demo --output-dir outputs/custom_demo
```

Actually delete them:

```bash
uv run water-agent-lab clean-demo --output-dir outputs/custom_demo --yes
```

Without `--yes`, this command only performs a dry run.

---

## Simulation commands

### `simulate`

Run one allocation strategy on one scenario.

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy proportional
```

With structured logs:

```bash
uv run water-agent-lab simulate --config configs/drought_mvp.yaml --strategy proportional --log-file outputs/simulation.log
```

Available strategies:

```text
proportional
priority
minimum-first
minimum-priority
```

### `compare`

Compare all available strategies on one scenario.

```bash
uv run water-agent-lab compare --config configs/drought_mvp.yaml
```

### `run-all`

Run all scenario configs with all available strategies.

```bash
uv run water-agent-lab run-all --config-dir configs
```

Export results:

```bash
uv run water-agent-lab run-all --config-dir configs --output outputs/results.csv
```

Use a custom registry:

```bash
uv run water-agent-lab run-all --config-dir configs --output outputs/results.csv --registry outputs/my_registry.jsonl
```

### `run-experiment`

Run the full experiment pipeline.

```bash
uv run water-agent-lab run-experiment
```

This command:

```text
runs all scenarios
exports results CSV
generates a Markdown report
creates a fairness/conflict plot
records the run in the registry
```

Custom paths:

```bash
uv run water-agent-lab run-experiment \
  --config-dir configs \
  --results outputs/results.csv \
  --report docs/experiment_report.md \
  --plot outputs/report_fairness_conflict.png \
  --registry outputs/experiment_registry.jsonl
```

---

## Agent and negotiation commands

### `agent-responses`

Show rule-based stakeholder responses to an allocation proposal.

```bash
uv run water-agent-lab agent-responses --config configs/drought_mvp.yaml --strategy proportional
```

Each stakeholder response is one of:

```text
accepted
concerned
rejected
```

### `negotiate`

Run a simple one-step negotiation.

```bash
uv run water-agent-lab negotiate --config configs/drought_mvp.yaml --strategy proportional
```

If stakeholders reject the initial proposal, the system revises using `minimum-first`.

### `negotiate-multi`

Run a multi-round rule-based negotiation.

```bash
uv run water-agent-lab negotiate-multi --config configs/drought_mvp.yaml --strategy proportional
```

Save full negotiation history:

```bash
uv run water-agent-lab negotiate-multi \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/negotiation_history.json
```

With logs and custom registry:

```bash
uv run water-agent-lab negotiate-multi \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/negotiation_history.json \
  --log-file outputs/negotiation.log \
  --registry outputs/my_registry.jsonl
```

### `summarize-negotiation`

Summarize a saved negotiation history JSON file.

```bash
uv run water-agent-lab summarize-negotiation --input outputs/negotiation_history.json
```

---

## Plot and report commands

### `plot-results`

Generate a fairness/conflict plot from exported results.

```bash
uv run water-agent-lab plot-results --input outputs/results.csv --output outputs/fairness_conflict.png
```

### `generate-report`

Generate a Markdown report from a results CSV.

```bash
uv run water-agent-lab generate-report --input outputs/results.csv --output docs/experiment_report.md
```

Generate a report with an embedded plot:

```bash
uv run water-agent-lab generate-report \
  --input outputs/results.csv \
  --output docs/experiment_report.md \
  --plot outputs/report_fairness_conflict.png
```

### `generate-run-report`

Generate a report from a recorded `run-all` registry entry.

```bash
uv run water-agent-lab generate-run-report \
  --run-id YOUR_RUN_ID \
  --registry outputs/my_registry.jsonl \
  --output docs/experiment_report.md
```

With a plot:

```bash
uv run water-agent-lab generate-run-report \
  --run-id YOUR_RUN_ID \
  --registry outputs/my_registry.jsonl \
  --output docs/experiment_report.md \
  --plot outputs/report_fairness_conflict.png
```

---

## Experiment registry commands

### `list-runs`

List recorded experiment runs.

```bash
uv run water-agent-lab list-runs
```

With custom registry:

```bash
uv run water-agent-lab list-runs --registry outputs/my_registry.jsonl
```

### `show-run`

Show details for one recorded run.

```bash
uv run water-agent-lab show-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
```

### `dashboard`

Show a dashboard summary of the experiment registry.

```bash
uv run water-agent-lab dashboard --registry outputs/my_registry.jsonl
```

The dashboard summarizes:

```text
total runs
runs by command
reproduced runs
latest run
outputs by type
```

---

## Reproducibility commands

### `verify-run`

Check whether current config files still match the hashes recorded for a run.

```bash
uv run water-agent-lab verify-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
```

### `reproduce-run`

Reproduce a recorded run if config hashes still match.

```bash
uv run water-agent-lab reproduce-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
```

The reproduced run is recorded in the registry with:

```text
reproduced_from_run_id
```

### `compare-runs`

Compare an original run with a reproduced run.

```bash
uv run water-agent-lab compare-runs \
  --run-id ORIGINAL_RUN_ID \
  --reproduced-run-id REPRODUCED_RUN_ID \
  --registry outputs/my_registry.jsonl
```

The comparison ignores run-specific metadata such as run IDs and timestamps.

---

## Config validation

### `validate-config`

Validate one scenario config.

```bash
uv run water-agent-lab validate-config --config configs/drought_mvp.yaml
```

---


### `load-mock-data`

Load a mock drought JSON snapshot and show the generated scenario.

```bash
uv run water-agent-lab load-mock-data --snapshot data/mock/occitanie_drought_snapshot.json
```

### `load-vigieau-sample`

Load a simplified VigiEau-style sample response and show the generated scenario.

```bash
uv run water-agent-lab load-vigieau-sample --sample data/sample_vigieau/occitanie_restrictions_sample.json
```


### `load-hubeau-sample`

Load a simplified Hub’Eau hydrometry-style sample response and show the generated scenario.

```bash
uv run water-agent-lab load-hubeau-sample --sample data/sample_hubeau/occitanie_hydrometry_sample.json
```

### `load-hubeau-sample`

Load a simplified Hub’Eau hydrometry-style sample response and show the generated scenario.

```bash
uv run water-agent-lab load-hubeau-sample --sample data/sample_hubeau/occitanie_hydrometry_sample.json
```


### `load-data-source`

Load any registered data source and show the generated scenario.

Synthetic YAML source:

```bash
uv run water-agent-lab load-data-source --source synthetic --path configs/drought_mvp.yaml
```

Mock drought snapshot:

```bash
uv run water-agent-lab load-data-source --source mock --path data/mock/occitanie_drought_snapshot.json
```

VigiEau sample:

```bash
uv run water-agent-lab load-data-source --source vigieau-sample --path data/sample_vigieau/occitanie_restrictions_sample.json
```

Hub’Eau hydrometry sample:

```bash
uv run water-agent-lab load-data-source --source hubeau-sample --path data/sample_hubeau/occitanie_hydrometry_sample.json
```


### `export-scenario-from-data`

Export a generated scenario from a registered data source to YAML.

```bash
uv run water-agent-lab export-scenario-from-data \
  --source hubeau-sample \
  --path data/sample_hubeau/occitanie_hydrometry_sample.json \
  --output configs/generated_hubeau_occitanie.yaml
```

Then run the generated scenario:

```bash
uv run water-agent-lab simulate --config configs/generated_hubeau_occitanie.yaml --strategy minimum-first
```


### `build-combined-scenario`

Build a combined drought scenario from VigiEau and Hub’Eau sample sources.

```bash
uv run water-agent-lab build-combined-scenario \
  --vigieau data/sample_vigieau/occitanie_restrictions_sample.json \
  --hubeau data/sample_hubeau/occitanie_hydrometry_sample.json \
  --output configs/generated_combined_occitanie.yaml
```

Then run:

```bash
uv run water-agent-lab simulate --config configs/generated_combined_occitanie.yaml --strategy minimum-first
```

Current combination rules:

drought_level = most severe drought level from the two sources
available_water = minimum available-water proxy from the two sources
stakeholders = VigiEau-derived stakeholder profile

---

## Version

### `version`

Show the package version.

```bash
uv run water-agent-lab version
```

### `llm-agent-responses`

Run mock LLM stakeholder agents on an allocation proposal.

```bash
uv run water-agent-lab llm-agent-responses --config configs/drought_mvp.yaml --strategy proportional
```

This command does not call a real LLM yet. It uses a deterministic `MockLLMBackend` that returns validated `AgentDecision` outputs. The command tests the future LLM-agent workflow without API cost or model randomness.


## Mock LLM stakeholder responses

WaterAgentLab can run mock LLM stakeholder agents with:

```bash
uv run water-agent-lab llm-agent-responses --config configs/drought_mvp.yaml --strategy proportional
```


Save a mock LLM transcript:

```bash
uv run water-agent-lab llm-agent-responses \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/mock_llm_transcript.json
```

### `llm-negotiate-mock`

Run a deterministic mock LLM multi-round negotiation.

```bash
uv run water-agent-lab llm-negotiate-mock --config configs/drought_mvp.yaml --strategy proportional
```


Save a transcript:

```bash
uv run water-agent-lab llm-negotiate-mock \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/mock_llm_negotiation.json
```

This command uses mock LLM stakeholder agents and stores round-by-round decisions, messages, proposals, and evaluation results.

The command also reports average frustration and trust across stakeholder agents.

The command reports stakeholder rejection, average agent state, and mediator action for each round.

The command also reports the total extra water requested by stakeholder counterproposals.

The command also reports the conflict score of the counterproposal-adjusted candidate when one is available.

The command reports the mediator action for each round.


### `summarize-agent-memory`

Build and summarize agent memory from a saved AI-agent transcript.

```bash
uv run water-agent-lab summarize-agent-memory \
  --transcript outputs/mock_llm_negotiation.json
```

Filter memory for one stakeholder:

```bash
uv run water-agent-lab summarize-agent-memory \
  --transcript outputs/mock_llm_negotiation.json \
  --stakeholder ecosystem
```

Save extracted memory:

```bash
uv run water-agent-lab summarize-agent-memory \
  --transcript outputs/mock_llm_negotiation.json \
  --output outputs/agent_memory.json
```

### `monte-carlo-mock`

Run repeated mock LLM negotiations over scenario variations.

```bash
uv run water-agent-lab monte-carlo-mock \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --runs 20 \
  --seed 42 \
  --output outputs/monte_carlo_mock.csv
```

The command varies available water, runs mock LLM negotiations, and saves one row per run.

Useful output fields include:

```text
agreement_reached
rounds_used
final_conflict_score
final_fairness_score
final_minimum_satisfaction_score
final_mediator_action
```


### `monte-carlo-report`

Generate a Markdown report and plots from Monte Carlo mock LLM results.

```bash
uv run water-agent-lab monte-carlo-report \
  --input outputs/monte_carlo_mock.csv \
  --output docs/monte_carlo_report.md \
  --conflict-plot outputs/monte_carlo_conflict_histogram.png \
  --rounds-plot outputs/monte_carlo_rounds_histogram.png
```

---

## Recommended workflows

### Quick demo

```bash
uv run water-agent-lab demo
uv run water-agent-lab dashboard --registry outputs/demo/experiment_registry.jsonl
```

### Full experiment

```bash
uv run water-agent-lab run-experiment
```

### Manual experiment workflow

```bash
uv run water-agent-lab run-all --config-dir configs --output outputs/results.csv
uv run water-agent-lab generate-report --input outputs/results.csv --output docs/experiment_report.md --plot outputs/report_fairness_conflict.png
uv run water-agent-lab dashboard
```

### Reproducibility workflow

```bash
uv run water-agent-lab list-runs --registry outputs/my_registry.jsonl
uv run water-agent-lab verify-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
uv run water-agent-lab reproduce-run --run-id YOUR_RUN_ID --registry outputs/my_registry.jsonl
uv run water-agent-lab compare-runs --run-id ORIGINAL_RUN_ID --reproduced-run-id REPRODUCED_RUN_ID --registry outputs/my_registry.jsonl
```