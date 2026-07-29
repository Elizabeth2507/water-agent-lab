# WaterAgentLab Metrics

WaterAgentLab evaluates each water-allocation proposal using several deterministic metrics.

These metrics help answer different questions:

```text
Was the water budget respected?
How much of stakeholder demand was satisfied?
Did any stakeholder fall below its minimum acceptable water?
Was agreement reached?
How severe was the shortage?
```

---

## Metric overview

| Metric | Meaning | Best value |
|---|---|---:|
| `total_requested` | Total water requested by all stakeholders. | context-dependent |
| `total_allocated` | Total water allocated by the strategy. | must not exceed available water |
| `water_budget_valid` | Whether allocation respects the available water budget. | `True` |
| `fairness_score` | Average request satisfaction across stakeholders. | `1.0` |
| `conflict_score` | Fraction of stakeholders below minimum acceptable water. | `0.0` |
| `minimum_satisfaction_score` | Average satisfaction of minimum acceptable needs. | `1.0` |
| `shortage_score` | Fraction of total demand that remains unmet. | `0.0` |
| `agreement_reached` | Whether budget is valid and no stakeholder is below minimum. | `True` |

---

## Total requested water

`total_requested` is the sum of all stakeholder requests.

Example:

```text
agriculture requests 50
urban requests 35
industry requests 25
ecosystem requests 20
```

Then:

```text
total_requested = 50 + 35 + 25 + 20 = 130
```

This tells us how much water stakeholders would like to receive in total.

---

## Total allocated water

`total_allocated` is the sum of all allocated water.

Example:

```text
agriculture receives 38.46
urban receives 26.92
industry receives 19.23
ecosystem receives 15.38
```

Then:

```text
total_allocated = 100.0
```

This should normally be less than or equal to `available_water`.

---

## Water budget validity

`water_budget_valid` checks whether the allocation exceeds the available water.

```text
water_budget_valid = total_allocated <= available_water
```

Example:

```text
available_water = 100
total_allocated = 100
water_budget_valid = True
```

If a strategy allocates more water than available, the result is invalid.

---

## Fairness score

`fairness_score` measures how much of each stakeholder's requested water was satisfied on average.

For each stakeholder:

```text
stakeholder_satisfaction = allocated_water / requested_water
```

The value is capped at `1.0`, so giving more than requested does not increase fairness beyond full satisfaction.

Then:

```text
fairness_score = average stakeholder satisfaction
```

Example:

```text
agriculture: 38.46 / 50 = 0.769
urban: 26.92 / 35 = 0.769
industry: 19.23 / 25 = 0.769
ecosystem: 15.38 / 20 = 0.769
```

So:

```text
fairness_score = 0.769
```

### Interpretation

| Fairness score | Meaning |
|---|---|
| close to `1.0` | Stakeholders receive close to what they requested. |
| around `0.5` | Stakeholders receive about half of requested demand on average. |
| close to `0.0` | Stakeholders receive very little of requested demand. |

A high fairness score does not always mean agreement was reached. A stakeholder can receive a fair proportional share but still fall below its minimum acceptable water.

---

## Conflict score

`conflict_score` measures the fraction of stakeholders whose allocation is below their minimum acceptable water.

```text
conflict_score = rejected_stakeholders / total_stakeholders
```

Example:

```text
urban receives 26.92 but minimum is 28
ecosystem receives 15.38 but minimum is 18
```

Two out of four stakeholders are below minimum:

```text
conflict_score = 2 / 4 = 0.5
```

### Interpretation

| Conflict score | Meaning |
|---|---|
| `0.0` | No stakeholder is below minimum. |
| `0.25` | One out of four stakeholders is below minimum. |
| `0.5` | Half of stakeholders are below minimum. |
| `1.0` | Every stakeholder is below minimum. |

Conflict is closely related to stakeholder rejection.

If a stakeholder is below minimum acceptable water, the rule-based stakeholder agent returns:

```text
rejected
```

---

## Minimum satisfaction score

`minimum_satisfaction_score` measures how well the allocation satisfies stakeholders' minimum acceptable needs.

For each stakeholder:

```text
minimum_satisfaction = allocated_water / minimum_acceptable_water
```

This value is capped at `1.0`.

Then:

```text
minimum_satisfaction_score = average minimum satisfaction
```

Example:

```text
urban receives 26.92
urban minimum acceptable water = 28
urban minimum satisfaction = 26.92 / 28 = 0.961
```

### Interpretation

| Minimum satisfaction score | Meaning |
|---|---|
| `1.0` | All stakeholder minimum needs are fully satisfied. |
| below `1.0` | At least some minimum needs are not fully satisfied. |
| close to `0.0` | Minimum needs are mostly unsatisfied. |

This metric is stricter than fairness in one sense: it focuses on minimum acceptable thresholds rather than full requested demand.

---

## Shortage score

`shortage_score` measures how much total requested demand remains unmet.

```text
shortage_score = 1 - total_allocated / total_requested
```

Example:

```text
total_requested = 130
total_allocated = 100
```

Then:

```text
shortage_score = 1 - 100 / 130 = 0.231
```

### Interpretation

| Shortage score | Meaning |
|---|---|
| `0.0` | No shortage; all requested demand was allocated. |
| `0.25` | About 25% of total requested demand is unmet. |
| `0.5` | About half of requested demand is unmet. |

A higher shortage score means the drought scenario is more constrained.

---

## Agreement reached

`agreement_reached` is a final boolean metric.

It is true only when:

```text
water_budget_valid == True
conflict_score == 0.0
```

In other words:

```text
agreement_reached = budget is respected and no stakeholder is below minimum
```

This does not mean every stakeholder received everything it requested. It means the allocation is feasible and no stakeholder has a minimum-threshold rejection.

---

## Why fairness and conflict are different

Fairness and conflict measure different things.

A proportional allocation can be fair because every stakeholder receives the same percentage of requested water.

But it can still create conflict if some stakeholders have higher minimum acceptable thresholds.

Example:

```text
proportional allocation:
all stakeholders receive about 76.9% of requested water
fairness_score = 0.769
```

But:

```text
urban is below minimum
ecosystem is below minimum
conflict_score = 0.5
agreement_reached = False
```

So:

```text
fairness_score answers: How evenly was demand satisfaction distributed?
conflict_score answers: Who fell below minimum acceptable water?
```

Both are needed.

---

## Relationship to stakeholder agents

The rule-based stakeholder agents use the same minimum threshold logic.

| Allocation condition | Agent status |
|---|---|
| `allocated_water < minimum_acceptable_water` | `rejected` |
| `allocated_water >= minimum_acceptable_water` but far below request | `concerned` |
| allocation close to request | `accepted` |

So the metric-level and agent-level interpretations are connected:

```text
conflict_score > 0
```

means at least one stakeholder agent should return:

```text
rejected
```

---

## Strategy comparison

The metrics make it possible to compare allocation strategies.

For example:

| Strategy | Expected behavior |
|---|---|
| `proportional` | Often fair in percentage terms, but may create conflict. |
| `priority` | Protects high-priority stakeholders, but may hurt lower-priority stakeholders. |
| `minimum-first` | Reduces conflict by protecting minimum needs first. |
| `minimum-priority` | Protects minimum needs, then distributes remaining water by priority. |

No metric is perfect alone. A good comparison should consider:

```text
fairness_score
conflict_score
minimum_satisfaction_score
agreement_reached
shortage_score
```

---

## Current limitations

These metrics are deterministic and simple.

They do not yet model:

```text
economic loss
legal obligations
seasonal crop needs
ecological damage thresholds
human health constraints
strategic stakeholder behavior
uncertainty in water availability
```

Future versions may add richer domain-specific metrics.