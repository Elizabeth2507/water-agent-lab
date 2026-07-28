# WaterAgentLab Experiment Report

This report summarizes allocation strategy results produced by WaterAgentLab.

## Input file

```text
outputs\all_results.csv
```

## Overview

| Field | Value |
|---|---|
| Number of rows | `16` |
| Number of scenarios | `4` |
| Number of strategies | `4` |
| Drought levels | `extreme, mild, moderate, severe` |

## Summary by strategy

| strategy         |   runs |   agreement_rate |   average_fairness |   average_conflict |   average_minimum_satisfaction |   average_shortage |
|:-----------------|-------:|-----------------:|-------------------:|-------------------:|-------------------------------:|-------------------:|
| minimum-first    |      4 |             0.5  |              0.7   |              0.5   |                          0.865 |              0.308 |
| minimum-priority |      4 |             0.5  |              0.698 |              0.5   |                          0.865 |              0.308 |
| priority         |      4 |             0    |              0.68  |              0.625 |                          0.84  |              0.308 |
| proportional     |      4 |             0.25 |              0.692 |              0.562 |                          0.854 |              0.308 |

## Summary by drought level

| drought_level   |   runs |   agreement_rate |   average_fairness |   average_conflict |   average_minimum_satisfaction |   average_shortage |
|:----------------|-------:|-----------------:|-------------------:|-------------------:|-------------------------------:|-------------------:|
| extreme         |      4 |             0    |              0.465 |              1     |                          0.622 |              0.538 |
| mild            |      4 |             0.75 |              0.911 |              0.062 |                          0.998 |              0.077 |
| moderate        |      4 |             0.5  |              0.774 |              0.188 |                          0.976 |              0.231 |
| severe          |      4 |             0    |              0.62  |              0.938 |                          0.827 |              0.385 |

## Best strategy per scenario

The best strategy is selected by:

1. Lower conflict score
2. Higher minimum satisfaction score
3. Higher fairness score
4. Lower shortage score

| scenario_name        | drought_level   |   available_water | strategy      |   total_requested |   total_allocated | water_budget_valid   |   fairness_score |   conflict_score | agreement_reached   |   minimum_satisfaction_score |   shortage_score |
|:---------------------|:----------------|------------------:|:--------------|------------------:|------------------:|:---------------------|-----------------:|-----------------:|:--------------------|-----------------------------:|-----------------:|
| extreme_drought      | extreme         |                60 | proportional  |               130 |                60 | True                 |            0.462 |             1    | False               |                        0.63  |            0.538 |
| mild_drought         | mild            |               120 | minimum-first |               130 |               120 | True                 |            0.926 |             0    | True                |                        1     |            0.077 |
| moderate_drought_mvp | moderate        |               100 | minimum-first |               130 |               100 | True                 |            0.779 |             0    | True                |                        1     |            0.231 |
| severe_drought       | severe          |                80 | proportional  |               130 |                80 | True                 |            0.615 |             0.75 | False               |                        0.833 |            0.385 |

## Interpretation guide

| Metric | Meaning |
|---|---|
| `agreement_rate` | Share of runs where all stakeholders met minimum acceptable water |
| `average_fairness` | Average fairness score across scenarios |
| `average_conflict` | Average share of stakeholders below minimum acceptable water |
| `average_minimum_satisfaction` | Average satisfaction of minimum needs |
| `average_shortage` | Average shortage pressure |

A lower conflict score is usually the most important signal because it means fewer stakeholders fall below their minimum acceptable water.
