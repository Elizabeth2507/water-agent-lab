# Monte Carlo Mock LLM Negotiation Report

This report summarizes repeated mock LLM negotiations over scenario variations.

## Summary

| metric                       |   value |
|:-----------------------------|--------:|
| total_runs                   |  50     |
| agreement_count              |  27     |
| agreement_rate               |   0.54  |
| average_final_conflict       |   0.29  |
| average_final_fairness       |   0.762 |
| average_minimum_satisfaction |   0.956 |
| average_shortage             |   0.242 |
| average_rounds_used          |   1.54  |

## Final mediator actions

| mediator_action     |   count |   share |
|:--------------------|--------:|--------:|
| accept_proposal     |      27 |    0.54 |
| stop_no_improvement |      23 |    0.46 |

## Interpretation

Monte Carlo simulation helps evaluate how robust the negotiation system is under small changes in scenario conditions.

A high agreement rate suggests that the negotiation mechanism often finds acceptable allocations.

A high average conflict score suggests that stakeholders frequently remain below minimum acceptable water levels.

Average rounds used indicates how quickly negotiations converge.

