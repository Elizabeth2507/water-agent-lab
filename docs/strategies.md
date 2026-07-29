# WaterAgentLab Allocation Strategies

WaterAgentLab currently supports 4 deterministic allocation strategies.

These strategies are intentionally simple. They provide transparent baselines for comparing water allocation outcomes before adding more complex stakeholder behavior or LLM-based negotiation.

---

## Strategy overview

| Strategy | Command name | Main idea |
|---|---|---|
| Proportional allocation | `proportional` | Allocate water in proportion to each stakeholder's requested demand. |
| Priority-weighted allocation | `priority` | Allocate water according to requested demand multiplied by priority. |
| Minimum-first allocation | `minimum-first` | Satisfy stakeholder minimum acceptable water first, then distribute the remainder. |
| Minimum-priority allocation | `minimum-priority` | Satisfy minimums first, then distribute remaining water using priority-weighted unmet demand. |

---

## Proportional allocation

Command name:

```text
proportional
```

Proportional allocation gives every stakeholder the same percentage of its requested water.

Formula:

```text
allocation_ratio = available_water / total_requested_water
stakeholder_allocation = stakeholder_requested_water * allocation_ratio
```

Example:

```text
available_water = 100
total_requested_water = 130
allocation_ratio = 100 / 130 = 0.769
```

If agriculture requests 50:

```text
agriculture_allocation = 50 * 0.769 = 38.46
```

### Strengths

```text
simple
transparent
easy to explain
treats requested demand symmetrically
```

### Limitations

Proportional allocation does not consider:

```text
minimum acceptable water
stakeholder priority
legal obligations
ecological thresholds
```

This means it can look fair in percentage terms but still create conflict.

Example:

```text
urban receives 76.9% of requested water
but urban falls below its minimum acceptable water
```

So:

```text
fairness_score may be reasonable
conflict_score may still be high
```

---

## Priority-weighted allocation

Command name:

```text
priority
```

Priority-weighted allocation multiplies each stakeholder's requested water by its priority.

Formula:

```text
weighted_demand = requested_water * priority
stakeholder_allocation = available_water * weighted_demand / total_weighted_demand
```

Example:

```text
agriculture requested water = 50
agriculture priority = 0.8
agriculture weighted demand = 50 * 0.8 = 40
```

A stakeholder with a higher priority receives a larger share, all else equal.

### Strengths

This strategy can represent policy preferences.

For example:

```text
urban water supply may have high priority
ecosystem protection may have high priority
industry may have lower priority during drought
```

### Limitations

Priority-weighted allocation can push lower-priority stakeholders below their minimum acceptable water.

This means it can reduce conflict for some stakeholders while increasing conflict for others.

It also depends strongly on how priority values are chosen.

---

## Minimum-first allocation

Command name:

```text
minimum-first
```

Minimum-first allocation first tries to satisfy every stakeholder's minimum acceptable water.

The logic is:

```text
1. Compute total minimum required.
2. If available water is less than total minimum required:
   allocate proportionally to minimum needs.
3. Otherwise:
   give every stakeholder its minimum acceptable water.
4. Distribute remaining water proportionally to unmet requested demand.
```

Example:

```text
available_water = 100
total_minimum_required = 96
remaining_water = 4
```

The strategy first gives each stakeholder its minimum acceptable amount, then distributes the remaining 4 units.

### Strengths

Minimum-first allocation directly targets conflict reduction.

It is useful when the goal is:

```text
avoid stakeholder rejection
protect minimum needs
reach agreement when possible
```

In the moderate drought MVP scenario, this strategy can reach agreement because:

```text
available_water = 100
total_minimum_required = 96
```

There is enough water to satisfy all minimum acceptable thresholds.

### Limitations

If available water is less than total minimum required, this strategy cannot avoid conflict.

Example:

```text
available_water = 60
total_minimum_required = 96
```

In this case, some stakeholders must receive less than their minimum acceptable water.

Minimum-first also does not use policy priority when distributing remaining water.

---

## Minimum-priority allocation

Command name:

```text
minimum-priority
```

Minimum-priority allocation combines minimum protection with priority weighting.

The logic is:

```text
1. Compute total minimum required.
2. If available water is less than total minimum required:
   allocate proportionally to minimum needs.
3. Otherwise:
   give every stakeholder its minimum acceptable water.
4. Distribute remaining water using priority-weighted unmet demand.
```

Formula for remaining water distribution:

```text
unmet_demand = requested_water - minimum_acceptable_water
weighted_unmet_demand = unmet_demand * priority
extra_allocation = remaining_water * weighted_unmet_demand / total_weighted_unmet_demand
```

### Strengths

Minimum-priority allocation is useful when the project needs to balance two goals:

```text
protect minimum needs
respect stakeholder priority
```

It can reduce conflict while still giving more remaining water to high-priority stakeholders.

### Limitations

This strategy still cannot solve situations where total available water is below total minimum acceptable water.

It may also allocate less remaining water to low-priority stakeholders even if they have large unmet demand.

---

## How strategies relate to metrics

The strategies are evaluated using the same metrics:

```text
fairness_score
conflict_score
minimum_satisfaction_score
shortage_score
agreement_reached
```

Typical behavior:

| Strategy | Fairness | Conflict | Priority-aware | Minimum-aware |
|---|---:|---:|---:|---:|
| `proportional` | often high | can be high | no | no |
| `priority` | variable | can be high | yes | no |
| `minimum-first` | sometimes lower | usually lower | no | yes |
| `minimum-priority` | variable | usually lower | yes | yes |

---

## How strategies relate to agents

Stakeholder agents evaluate the allocation produced by a strategy.

If a strategy allocates less than a stakeholder's minimum acceptable water, that stakeholder agent returns:

```text
rejected
```

So strategies that protect minimum acceptable water usually produce fewer rejected stakeholder responses.

Example:

```text
proportional allocation
→ urban below minimum
→ ecosystem below minimum
→ two rejected stakeholder agents
```

Then a negotiation loop can revise the strategy:

```text
proportional → minimum-first
```

---

## Current design choice

WaterAgentLab uses deterministic strategies first because they are:

```text
testable
transparent
reproducible
easy to compare
```

This creates a stable baseline before adding:

```text
richer negotiation policies
stakeholder utility functions
LLM-based agents
real hydrological data
legal restriction rules
```