# Results: Drought Scenario Comparison

This report summarizes the first experimental results from WaterAgentLab.

The current experiment compares two allocation strategies across four drought scenarios:

- mild drought
- moderate drought
- severe drought
- extreme drought

Each scenario uses the same stakeholder demands, but changes the amount of available water. This allows us to observe how allocation quality changes as drought severity increases.

## Compared strategies

### Proportional allocation

The proportional strategy allocates water according to each stakeholder's requested demand.

This means every stakeholder receives the same percentage of what they asked for.

### Priority-weighted allocation

The priority-weighted strategy allocates water according to both requested demand and stakeholder priority.

This means higher-priority stakeholders receive a larger share of the available water.

## Metrics

The comparison uses three main evaluation signals:

- `fairness_score`: average stakeholder satisfaction
- `conflict_score`: fraction of stakeholders below their minimum acceptable water
- `agreement_reached`: whether all stakeholders receive at least their minimum acceptable amount while staying within the water budget

A high fairness score is good.

A low conflict score is good.

Agreement is reached only when the allocation is valid and no stakeholder is below its minimum acceptable water.

## Observed results

The results show that drought severity has a strong effect on allocation quality.

In the mild drought scenario, the system has enough water to satisfy most stakeholder needs. The fairness score is high, and conflict is relatively low, especially when using the priority-weighted strategy.

In the moderate drought scenario, available water becomes more limited. The proportional strategy keeps satisfaction balanced across stakeholders, but some stakeholders fall below their minimum acceptable water. The priority-weighted strategy reduces conflict by protecting higher-priority stakeholders, especially urban and ecosystem needs.

In the severe drought scenario, both strategies struggle. The proportional strategy keeps the distribution balanced, but several stakeholders remain below their minimum acceptable level. The priority-weighted strategy improves protection for high-priority stakeholders, but this comes at the cost of lower allocation for lower-priority stakeholders.

In the extreme drought scenario, agreement becomes impossible with the current simple strategies. Available water is too low to satisfy stakeholder minimum requirements. Both strategies result in a high conflict score.

## Main interpretation

The proportional strategy is simple and transparent, but it does not account for stakeholder importance.

The priority-weighted strategy is more policy-aware because it uses priority values, but it can create trade-offs by shifting scarcity toward lower-priority stakeholders.

The results suggest that allocation strategy matters most in moderate and severe drought conditions. In mild drought, there is enough water for most needs. In extreme drought, the shortage is too large for simple allocation rules to solve.

## Current limitation

These results are based on synthetic scenario data.

The current MVP does not yet include:

- real hydrological data
- legal drought restrictions
- negotiation between stakeholders
- adaptive multi-round decision-making
- LLM-based agents

Therefore, the results should be interpreted as a first technical demonstration, not as a real policy recommendation.

## Next direction

The next development step is to add richer allocation logic and negotiation behavior.

Possible extensions include:

- minimum-first allocation
- priority-aware minimum protection
- rule-based stakeholder agents
- multi-round negotiation
- LLM-powered stakeholder argumentation
- integration with French drought and hydrometry data