# Champion or challenger

Champion version 1 (threshold 0.075), challenger version 2 (threshold 0.090). Each model at its own threshold. Intervals: 95% paired bootstrap of challenger minus champion. Written by python run.py champion.

## The validation slice (1000 applicants, 81 defaults)

| | AUC | Cost per applicant | Approval rate | Bad rate among approved |
|---|---|---|---|---|
| champion | 0.722 | 0.576 | 60.7% | 4.0% |
| challenger | 0.722 | 0.566 | 63.9% | 4.1% |
| difference [95% interval] | -0.000 [-0.015, +0.015] | -0.010 [-0.040, +0.027] | | |

## The recent slice (564 applicants, 72 defaults)

| | AUC | Cost per applicant | Approval rate | Bad rate among approved |
|---|---|---|---|---|
| champion | 0.716 | 0.745 | 59.6% | 7.1% |
| challenger | 0.722 | 0.734 | 58.7% | 6.9% |
| difference [95% interval] | +0.006 [-0.017, +0.029] | -0.011 [-0.110, +0.082] | | |

## Quality gate on the challenger

FAILED: cost 0.566 is above the ceiling 0.54
(model tests: {'passed': 4, 'failed': 0, 'xfail': 0, 'skipped': 0})

## Decision: KEEP

- gate: cost 0.566 is above the ceiling 0.54
