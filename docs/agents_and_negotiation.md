# WaterAgentLab Agents and Negotiation

WaterAgentLab includes simple rule-based stakeholder agents and deterministic negotiation loops.

The goal is to model how different stakeholders respond to water-allocation proposals during drought.

Current agents are not LLM agents. They are deterministic rule-based agents designed to be transparent, testable, and reproducible.

---

## What is an agent in WaterAgentLab?

In WaterAgentLab, an agent represents one stakeholder.

Example stakeholders include:

```text
agriculture
urban
industry
ecosystem
```

Each stakeholder agent receives an allocation proposal and decides whether the proposal is acceptable.

The agent does not change the allocation directly. It evaluates the allocation and returns a structured response.

---

## Agent input

Each agent uses information from two sources.

From the scenario config:

```text
stakeholder name
requested water
minimum acceptable water
priority
```

From the allocation proposal:

```text
allocated water
```

Example:

```text
stakeholder: ecosystem
requested_water: 20
minimum_acceptable_water: 18
allocated_water: 15.38
```

---

## Agent output

Each agent returns a `StakeholderResponse`.

The response contains:

```text
stakeholder_name
requested_water
minimum_acceptable_water
allocated_water
satisfaction_ratio
status
message
```

Example:

```text
stakeholder_name: ecosystem
allocated_water: 15.38
requested_water: 20.0
minimum_acceptable_water: 18.0
satisfaction_ratio: 0.769
status: rejected
message: ecosystem rejects the proposal because allocated water is below the minimum acceptable level.
```

---

## Response statuses

Each stakeholder response has one of three statuses.

| Status | Meaning |
|---|---|
| `accepted` | The stakeholder receives an allocation close to its requested demand. |
| `concerned` | The stakeholder receives at least its minimum acceptable water, but less than its requested demand. |
| `rejected` | The stakeholder receives less than its minimum acceptable water. |

---

## Rule-based agent logic

The current rule-based logic is:

```text
if allocated_water < minimum_acceptable_water:
    status = rejected

else if allocated_water / requested_water < 0.9:
    status = concerned

else:
    status = accepted
```

This means:

```text
below minimum threshold -> rejected
above minimum but below desired request -> concerned
close to full request -> accepted
```

The `0.9` threshold is a simple rule. It means that a stakeholder is considered fully satisfied if it receives at least 90% of its requested water.

---

## Why use rule-based agents first?

WaterAgentLab uses rule-based agents before LLM agents because rule-based agents are:

```text
deterministic
easy to test
easy to debug
transparent
reproducible
```

This makes them a good foundation for future LLM-powered stakeholder simulations.

---

## Relationship between agents and metrics

The agent system is connected to the evaluator metrics.

If a stakeholder receives less than its minimum acceptable water, then:

```text
agent status = rejected
```

At the metric level, this contributes to:

```text
conflict_score
```

Example:

```text
4 stakeholders total
2 stakeholders below minimum
conflict_score = 2 / 4 = 0.5
```

So:

```text
conflict_score > 0
```

means at least one stakeholder should reject the proposal.

---

## Simple negotiation

The simple negotiation command is:

```bash
uv run water-agent-lab negotiate --config configs/drought_mvp.yaml --strategy proportional
```

The logic is:

```text
1. Run the initial strategy.
2. Ask stakeholder agents to evaluate the proposal.
3. If nobody rejects, keep the proposal.
4. If at least one stakeholder rejects, revise using minimum-first.
5. Evaluate stakeholder responses again.
```

This creates the first interaction between allocation strategies and stakeholder agents.

---

## Multi-round negotiation

The multi-round negotiation command is:

```bash
uv run water-agent-lab negotiate-multi --config configs/drought_mvp.yaml --strategy proportional
```

The loop is:

```text
1. Generate allocation proposal.
2. Collect stakeholder responses.
3. Check rejected stakeholders.
4. If no stakeholders reject, stop with agreement.
5. If stakeholders reject, choose a revised strategy.
6. Repeat until agreement or max_rounds is reached.
```

---

## Multi-round negotiation flow

```mermaid
flowchart TD
    A[Initial allocation strategy] --> B[Generate allocation proposal]
    B --> C[Stakeholder agents evaluate proposal]
    C --> D{Any rejected stakeholders?}
    D -- No --> E[Agreement reached]
    D -- Yes --> F[Choose revised strategy]
    F --> G[Generate revised allocation]
    G --> C
    D -- Max rounds reached --> H[Stop without agreement]
```

---

## Revision strategy logic

Current revision rules are simple:

| Current strategy | Revised strategy |
|---|---|
| `proportional` | `minimum-first` |
| `priority` | `minimum-priority` |
| `minimum-first` | `minimum-first` |
| `minimum-priority` | `minimum-priority` |

The idea is:

```text
If stakeholders reject a proposal, move toward a strategy that protects minimum acceptable water.
```

Example:

```text
Round 1: proportional
urban rejects
ecosystem rejects

Round 2: minimum-first
no stakeholder rejects
agreement reached
```

---

## When negotiation cannot succeed

Negotiation cannot always reach agreement.

Example:

```text
available_water = 60
total_minimum_required = 96
```

In this case, even `minimum-first` cannot satisfy every stakeholder's minimum acceptable water.

The system should not falsely claim agreement.

Instead:

```text
agreement_reached = False
conflict_score > 0
```

This is realistic because some drought scenarios are too severe to satisfy all minimum needs.

---

## Negotiation history

Multi-round negotiation can save a full JSON history:

```bash
uv run water-agent-lab negotiate-multi \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/negotiation_history.json
```

The saved history includes:

```text
scenario name
initial strategy
agreement status
rounds used
strategy used in each round
stakeholder responses in each round
rejected stakeholders in each round
evaluation metrics in each round
```

This is useful for debugging, reporting, and future LLM-agent analysis.

---

## Current limitations

The current agents are simple.

They do not yet model:

```text
strategic bargaining
coalition formation
economic loss
legal constraints
long-term ecological damage
human health priority
uncertainty
memory across negotiations
stakeholder personality
natural language argumentation
```

The current negotiation loop also uses fixed revision rules rather than learned or optimized negotiation policies.

---


## Generic agent models

WaterAgentLab now includes generic agent models that prepare the project for future LLM-based agents.

The main models are:

| Model | Purpose |
|---|---|
| `AgentProfile` | Stable identity, role, goals, constraints, and negotiation style. |
| `AgentState` | Mutable state such as frustration, trust, concessions, and last status. |
| `AgentMessage` | Structured message exchanged between agents. |
| `AgentDecision` | Structured decision produced by an agent after evaluating a proposal. |

These models are useful because they allow both rule-based agents and future LLM agents to produce validated, comparable outputs.

A future LLM stakeholder agent should not return only free text. It should return a validated `AgentDecision`.


## LLM backend interface

WaterAgentLab uses an `LLMBackend` interface to keep AI-agent logic separate from model execution.

The agent should not directly depend on a specific model such as Qwen. Instead, it sends a structured `LLMGenerationRequest` to a backend.

Current backend:

| Backend | Purpose |
|---|---|
| `MockLLMBackend` | Deterministic backend for tests and offline development. |

Future backends:

| Backend | Purpose |
|---|---|
| `QwenLocalBackend` | Run a local Qwen instruct model for stakeholder reasoning. |
| `OpenAIBackend` | Optional hosted API backend. |

This design allows the same `LLMStakeholderAgent` to work with mock responses during tests and real model responses during experiments.


## LLM stakeholder prompt structure

Future LLM stakeholder agents use structured prompts instead of ad hoc free-text instructions.

Each LLM decision uses two prompts:

| Prompt | Purpose |
|---|---|
| System prompt | Defines the stakeholder identity, goals, constraints, and negotiation style. |
| User prompt | Provides the drought scenario, allocation proposal, agent state, and required JSON schema. |

The LLM is instructed to return only valid JSON.

The returned text is parsed and validated as an `AgentDecision`.

This keeps LLM-based agents compatible with deterministic evaluation, testing, and experiment tracking.


## AI-agent transcripts

Mock LLM and future Qwen-based negotiations can be saved as structured transcripts.

A transcript stores:

| Field | Meaning |
|---|---|
| Scenario metadata | Country, region, drought level, scenario name. |
| Backend metadata | Backend name and model name. |
| Round transcript | Strategy, allocation proposal, decisions, messages, and evaluation result. |
| Agent decisions | Validated stakeholder decisions. |
| Agent messages | Structured messages derived from decisions. |

Example:

```bash
uv run water-agent-lab llm-agent-responses \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/mock_llm_transcript.json
  ```

## Mock LLM multi-round negotiation

WaterAgentLab can run a deterministic mock LLM multi-round negotiation:

```bash
uv run water-agent-lab llm-negotiate-mock \
  --config configs/drought_mvp.yaml \
  --strategy proportional \
  --output outputs/mock_llm_negotiation.json
```


## Agent memory

WaterAgentLab includes a simple structured memory model for AI-agent negotiations.

The memory stores events such as:

```text
proposal
decision
message
rejection
concession
agreement
summary
```


## Memory-aware LLM prompts

LLM stakeholder prompts can now include a compact memory summary.

This allows future Qwen-based agents to condition their decisions on previous negotiation rounds.

The memory summary can contain events such as:

```text
Round 1 | ecosystem | rejection | Ecosystem rejected because allocation was below minimum.
Round 1 | agriculture | decision | Agriculture was concerned because allocation was below request.
```


## Persistent agent state

WaterAgentLab now tracks stakeholder state across mock LLM negotiation rounds.

Each stakeholder has an `AgentState` with:

| Field | Meaning |
|---|---|
| `frustration` | Increases when the stakeholder is concerned or rejects a proposal. |
| `trust_in_mediator` | Decreases after rejection and increases after acceptance. |
| `concessions_made` | Counts cases where an agent moves from concern/rejection to acceptance. |
| `last_status` | Stores the stakeholder's previous decision status. |

This is useful because future Qwen-based agents should not only remember previous messages. They should also have a compact internal state that changes over the negotiation.

The current state update rules are deterministic and simple. They are not meant to be a psychological model. They are an engineering foundation for future experiments.


## Mediator agent

WaterAgentLab includes a deterministic mediator agent.

The mediator reads:

```text
stakeholder decisions
rejected stakeholders
concerned stakeholders
simulation metrics
current strategy
```

## Future LLM-agent extension

In a future version, stakeholder agents could be extended with LLM-based behavior.

For example, an LLM stakeholder agent could generate:

```text
a natural language objection
a justification based on stakeholder goals
a counterproposal
a compromise offer
```

However, the deterministic rule-based system should remain as a baseline.

A useful future architecture would be:

```text
rule-based evaluator
+ deterministic metrics
+ LLM-generated stakeholder explanations
```

This keeps the system measurable and reproducible while adding richer interaction.