# Negotiation Mode Comparison Report

This report compares deterministic rule-based negotiation with mock LLM-style negotiation across drought scenarios.

The goal is to understand whether the agent-style negotiation layer changes outcomes such as agreement rate, final conflict score, and number of rounds used.

## Summary by mode

| mode       |   scenarios |   agreement_rate |   average_final_conflict |   average_rounds_used |   average_final_fairness |   average_minimum_satisfaction |   average_shortage |
|:-----------|------------:|-----------------:|-------------------------:|----------------------:|-------------------------:|-------------------------------:|-------------------:|
| mock_llm   |          30 |              0.5 |                    0.325 |                   1.5 |                 0.755735 |                       0.950596 |           0.248379 |
| rule_based |          30 |              0.5 |                    0.5   |                   2   |                 0.761123 |                       0.967008 |           0.248379 |

## Main findings

- Highest agreement rate: **mock_llm**.
- Lowest average final conflict: **mock_llm**.
- Fewest average rounds used: **mock_llm**.

These findings should be interpreted as deterministic simulation results, not as real-world policy conclusions.

## Plots

### Final conflict by mode

![Final conflict by mode](outputs/mode_comparison_conflict.png)

### Agreement rate by mode

![Agreement rate by mode](outputs/mode_comparison_agreement.png)

### Average rounds used by mode

![Average rounds used by mode](outputs/mode_comparison_rounds.png)

## Detailed results

|   run_index | mode       | scenario_name                |   available_water | initial_strategy   | agreement_reached   |   rounds_used | final_strategy   |   final_conflict_score |   final_fairness_score |   final_minimum_satisfaction_score |   final_shortage_score | final_mediator_action   |
|------------:|:-----------|:-----------------------------|------------------:|:-------------------|:--------------------|--------------:|:-----------------|-----------------------:|-----------------------:|-----------------------------------:|-----------------------:|:------------------------|
|           1 | rule_based | moderate_drought_mvp_variant |          104.183  | proportional       | True                |             2 | minimum-first    |                   0    |               0.810168 |                           1        |               0.198594 | not_applicable          |
|           1 | mock_llm   | moderate_drought_mvp_variant |          104.183  | proportional       | True                |             2 | minimum-first    |                   0    |               0.810168 |                           1        |               0.198594 | accept_proposal         |
|           2 | rule_based | moderate_drought_mvp_variant |           85.7503 | proportional       | False               |             2 | minimum-first    |                   1    |               0.669924 |                           0.893233 |               0.340382 | not_applicable          |
|           2 | mock_llm   | moderate_drought_mvp_variant |           85.7503 | proportional       | False               |             1 | proportional     |                   0.75 |               0.659618 |                           0.874936 |               0.340382 | stop_no_improvement     |
|           3 | rule_based | moderate_drought_mvp_variant |           93.2509 | proportional       | False               |             2 | minimum-first    |                   1    |               0.728522 |                           0.971363 |               0.282686 | not_applicable          |
|           3 | mock_llm   | moderate_drought_mvp_variant |           93.2509 | proportional       | False               |             1 | proportional     |                   0.5  |               0.717314 |                           0.923415 |               0.282686 | stop_no_improvement     |
|           4 | rule_based | moderate_drought_mvp_variant |           91.6963 | proportional       | False               |             2 | minimum-first    |                   1    |               0.716378 |                           0.95517  |               0.294644 | not_applicable          |
|           4 | mock_llm   | moderate_drought_mvp_variant |           91.6963 | proportional       | False               |             1 | proportional     |                   0.5  |               0.705356 |                           0.916356 |               0.294644 | stop_no_improvement     |
|           5 | rule_based | moderate_drought_mvp_variant |          107.094  | proportional       | True                |             2 | minimum-first    |                   0    |               0.831575 |                           1        |               0.176199 | not_applicable          |
|           5 | mock_llm   | moderate_drought_mvp_variant |          107.094  | proportional       | True                |             2 | minimum-first    |                   0    |               0.831575 |                           1        |               0.176199 | accept_proposal         |
|           6 | rule_based | moderate_drought_mvp_variant |          105.301  | proportional       | True                |             2 | minimum-first    |                   0    |               0.81839  |                           1        |               0.189992 | not_applicable          |
|           6 | mock_llm   | moderate_drought_mvp_variant |          105.301  | proportional       | True                |             2 | minimum-first    |                   0    |               0.81839  |                           1        |               0.189992 | accept_proposal         |
|           7 | rule_based | moderate_drought_mvp_variant |          111.765  | proportional       | True                |             2 | minimum-first    |                   0    |               0.865922 |                           1        |               0.140266 | not_applicable          |
|           7 | mock_llm   | moderate_drought_mvp_variant |          111.765  | proportional       | True                |             2 | minimum-first    |                   0    |               0.865922 |                           1        |               0.140266 | accept_proposal         |
|           8 | rule_based | moderate_drought_mvp_variant |           87.6082 | proportional       | False               |             2 | minimum-first    |                   1    |               0.684439 |                           0.912585 |               0.326091 | not_applicable          |
|           8 | mock_llm   | moderate_drought_mvp_variant |           87.6082 | proportional       | False               |             1 | proportional     |                   0.75 |               0.673909 |                           0.888475 |               0.326091 | stop_no_improvement     |
|           9 | rule_based | moderate_drought_mvp_variant |           97.6577 | proportional       | True                |             2 | minimum-first    |                   0    |               0.762189 |                           1        |               0.248787 | not_applicable          |
|           9 | mock_llm   | moderate_drought_mvp_variant |           97.6577 | proportional       | True                |             2 | minimum-first    |                   0    |               0.762189 |                           1        |               0.248787 | accept_proposal         |
|          10 | rule_based | moderate_drought_mvp_variant |           85.8939 | proportional       | False               |             2 | minimum-first    |                   1    |               0.671046 |                           0.894728 |               0.339278 | not_applicable          |
|          10 | mock_llm   | moderate_drought_mvp_variant |           85.8939 | proportional       | False               |             1 | proportional     |                   0.75 |               0.660722 |                           0.875982 |               0.339278 | stop_no_improvement     |
|          11 | rule_based | moderate_drought_mvp_variant |           91.5591 | proportional       | False               |             2 | minimum-first    |                   1    |               0.715306 |                           0.953741 |               0.295699 | not_applicable          |
|          11 | mock_llm   | moderate_drought_mvp_variant |           91.5591 | proportional       | False               |             1 | proportional     |                   0.5  |               0.704301 |                           0.915733 |               0.295699 | stop_no_improvement     |
|          12 | rule_based | moderate_drought_mvp_variant |          100.161  | proportional       | True                |             2 | minimum-first    |                   0    |               0.780593 |                           1        |               0.229533 | not_applicable          |
|          12 | mock_llm   | moderate_drought_mvp_variant |          100.161  | proportional       | True                |             2 | minimum-first    |                   0    |               0.780593 |                           1        |               0.229533 | accept_proposal         |
|          13 | rule_based | moderate_drought_mvp_variant |           85.7961 | proportional       | False               |             2 | minimum-first    |                   1    |               0.670282 |                           0.893709 |               0.34003  | not_applicable          |
|          13 | mock_llm   | moderate_drought_mvp_variant |           85.7961 | proportional       | False               |             1 | proportional     |                   0.75 |               0.65997  |                           0.875269 |               0.34003  | stop_no_improvement     |
|          14 | rule_based | moderate_drought_mvp_variant |           90.9651 | proportional       | False               |             2 | minimum-first    |                   1    |               0.710665 |                           0.947553 |               0.300268 | not_applicable          |
|          14 | mock_llm   | moderate_drought_mvp_variant |           90.9651 | proportional       | False               |             1 | proportional     |                   0.75 |               0.699732 |                           0.91294  |               0.300268 | stop_no_improvement     |
|          15 | rule_based | moderate_drought_mvp_variant |          104.497  | proportional       | True                |             2 | minimum-first    |                   0    |               0.812475 |                           1        |               0.196181 | not_applicable          |
|          15 | mock_llm   | moderate_drought_mvp_variant |          104.497  | proportional       | True                |             2 | minimum-first    |                   0    |               0.812475 |                           1        |               0.196181 | accept_proposal         |
|          16 | rule_based | moderate_drought_mvp_variant |          101.348  | proportional       | True                |             2 | minimum-first    |                   0    |               0.789325 |                           1        |               0.220398 | not_applicable          |
|          16 | mock_llm   | moderate_drought_mvp_variant |          101.348  | proportional       | True                |             2 | minimum-first    |                   0    |               0.789325 |                           1        |               0.220398 | accept_proposal         |
|          17 | rule_based | moderate_drought_mvp_variant |           91.6132 | proportional       | False               |             2 | minimum-first    |                   1    |               0.715728 |                           0.954304 |               0.295283 | not_applicable          |
|          17 | mock_llm   | moderate_drought_mvp_variant |           91.6132 | proportional       | False               |             1 | proportional     |                   0.5  |               0.704717 |                           0.915979 |               0.295283 | stop_no_improvement     |
|          18 | rule_based | moderate_drought_mvp_variant |          102.678  | proportional       | True                |             2 | minimum-first    |                   0    |               0.799103 |                           1        |               0.210169 | not_applicable          |
|          18 | mock_llm   | moderate_drought_mvp_variant |          102.678  | proportional       | True                |             2 | minimum-first    |                   0    |               0.799103 |                           1        |               0.210169 | accept_proposal         |
|          19 | rule_based | moderate_drought_mvp_variant |          109.283  | proportional       | True                |             2 | minimum-first    |                   0    |               0.847668 |                           1        |               0.159362 | not_applicable          |
|          19 | mock_llm   | moderate_drought_mvp_variant |          109.283  | proportional       | True                |             2 | minimum-first    |                   0    |               0.847668 |                           1        |               0.159362 | accept_proposal         |
|          20 | rule_based | moderate_drought_mvp_variant |           85.195  | proportional       | False               |             2 | minimum-first    |                   1    |               0.665586 |                           0.887448 |               0.344654 | not_applicable          |
|          20 | mock_llm   | moderate_drought_mvp_variant |           85.195  | proportional       | False               |             1 | proportional     |                   0.75 |               0.655346 |                           0.870888 |               0.344654 | stop_no_improvement     |
|          21 | rule_based | moderate_drought_mvp_variant |          109.175  | proportional       | True                |             2 | minimum-first    |                   0    |               0.846872 |                           1        |               0.160196 | not_applicable          |
|          21 | mock_llm   | moderate_drought_mvp_variant |          109.175  | proportional       | True                |             2 | minimum-first    |                   0    |               0.846872 |                           1        |               0.160196 | accept_proposal         |
|          22 | rule_based | moderate_drought_mvp_variant |          105.944  | proportional       | True                |             2 | minimum-first    |                   0    |               0.823119 |                           1        |               0.185045 | not_applicable          |
|          22 | mock_llm   | moderate_drought_mvp_variant |          105.944  | proportional       | True                |             2 | minimum-first    |                   0    |               0.823119 |                           1        |               0.185045 | accept_proposal         |
|          23 | rule_based | moderate_drought_mvp_variant |           95.2075 | proportional       | False               |             2 | minimum-first    |                   1    |               0.743809 |                           0.991745 |               0.267634 | not_applicable          |
|          23 | mock_llm   | moderate_drought_mvp_variant |           95.2075 | proportional       | False               |             1 | proportional     |                   0.5  |               0.732366 |                           0.932299 |               0.267634 | stop_no_improvement     |
|          24 | rule_based | moderate_drought_mvp_variant |           89.6644 | proportional       | False               |             2 | minimum-first    |                   1    |               0.700503 |                           0.934004 |               0.310274 | not_applicable          |
|          24 | mock_llm   | moderate_drought_mvp_variant |           89.6644 | proportional       | False               |             1 | proportional     |                   0.75 |               0.689726 |                           0.903461 |               0.310274 | stop_no_improvement     |
|          25 | rule_based | moderate_drought_mvp_variant |          113.716  | proportional       | True                |             2 | minimum-first    |                   0    |               0.880268 |                           1        |               0.125259 | not_applicable          |
|          25 | mock_llm   | moderate_drought_mvp_variant |          113.716  | proportional       | True                |             2 | minimum-first    |                   0    |               0.880268 |                           1        |               0.125259 | accept_proposal         |
|          26 | rule_based | moderate_drought_mvp_variant |           95.0978 | proportional       | False               |             2 | minimum-first    |                   1    |               0.742952 |                           0.990602 |               0.268478 | not_applicable          |
|          26 | mock_llm   | moderate_drought_mvp_variant |           95.0978 | proportional       | False               |             1 | proportional     |                   0.5  |               0.731522 |                           0.931801 |               0.268478 | stop_no_improvement     |
|          27 | rule_based | moderate_drought_mvp_variant |           87.7824 | proportional       | False               |             2 | minimum-first    |                   1    |               0.6858   |                           0.9144   |               0.324751 | not_applicable          |
|          27 | mock_llm   | moderate_drought_mvp_variant |           87.7824 | proportional       | False               |             1 | proportional     |                   0.75 |               0.675249 |                           0.889745 |               0.324751 | stop_no_improvement     |
|          28 | rule_based | moderate_drought_mvp_variant |           87.9015 | proportional       | False               |             2 | minimum-first    |                   1    |               0.68673  |                           0.915641 |               0.323835 | not_applicable          |
|          28 | mock_llm   | moderate_drought_mvp_variant |           87.9015 | proportional       | False               |             1 | proportional     |                   0.75 |               0.676165 |                           0.890613 |               0.323835 | stop_no_improvement     |
|          29 | rule_based | moderate_drought_mvp_variant |          110.425  | proportional       | True                |             2 | minimum-first    |                   0    |               0.856065 |                           1        |               0.150578 | not_applicable          |
|          29 | mock_llm   | moderate_drought_mvp_variant |          110.425  | proportional       | True                |             2 | minimum-first    |                   0    |               0.856065 |                           1        |               0.150578 | accept_proposal         |
|          30 | rule_based | moderate_drought_mvp_variant |          103.112  | proportional       | True                |             2 | minimum-first    |                   0    |               0.802293 |                           1        |               0.206832 | not_applicable          |
|          30 | mock_llm   | moderate_drought_mvp_variant |          103.112  | proportional       | True                |             2 | minimum-first    |                   0    |               0.802293 |                           1        |               0.206832 | accept_proposal         |

## Interpretation

The rule-based mode represents a transparent deterministic baseline. The mock LLM-style mode adds an agent-style layer with stakeholder decisions, mediator recommendations, and counterproposal pressure. A difference between the two modes indicates that the negotiation protocol can affect the final allocation trajectory, even when the LLM backend is deterministic and offline.
