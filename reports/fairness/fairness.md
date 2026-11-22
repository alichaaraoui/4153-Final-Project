# Fairness tables

Model version 1, threshold 0.075, 1,000 validation applicants. Written by python run.py fairness. Brackets: 95% Wilson interval.

## By gender

| Group | n | Defaulters | Approval rate | Default rate | Mean score | TPR (risk caught) | FPR (good payers declined) | Note |
|---|---|---|---|---|---|---|---|---|
| F | 669 | 38 | 64.4% [61%, 68%] | 5.7% | 0.074 | 68.4% [53%, 81%] | 33.6% [30%, 37%] |  |
| M | 331 | 43 | 53.2% [48%, 58%] | 13.0% | 0.096 | 72.1% [57%, 83%] | 43.1% [37%, 49%] |  |

Largest gaps: approval 0.1125, TPR 0.0367, FPR 0.0946; lowest / highest approval rate: 0.8253.

## By age_band

| Group | n | Defaulters | Approval rate | Default rate | Mean score | TPR (risk caught) | FPR (good payers declined) | Note |
|---|---|---|---|---|---|---|---|---|
| 18-29 | 143 | 16 | 29.4% [23%, 37%] | 11.2% | 0.129 | 93.8% [72%, 99%] | 67.7% [59%, 75%] | fewer than 30 defaulters: TPR unreliable |
| 30-39 | 282 | 28 | 53.2% [47%, 59%] | 9.9% | 0.088 | 71.4% [53%, 85%] | 44.1% [38%, 50%] | fewer than 30 defaulters: TPR unreliable |
| 40-49 | 235 | 18 | 67.7% [61%, 73%] | 7.7% | 0.075 | 66.7% [44%, 84%] | 29.5% [24%, 36%] | fewer than 30 defaulters: TPR unreliable |
| 50-59 | 216 | 13 | 70.4% [64%, 76%] | 6.0% | 0.067 | 61.5% [36%, 82%] | 27.6% [22%, 34%] | fewer than 30 defaulters: TPR unreliable |
| 60+ | 124 | 6 | 83.9% [76%, 89%] | 4.8% | 0.048 | 33.3% [10%, 70%] | 15.3% [10%, 23%] | fewer than 30 defaulters: TPR unreliable |

Largest gaps: approval 0.545, TPR 0.6042, FPR 0.5246; lowest / highest approval rate: 0.3502.

## Proxy check

Predicting CODE_GENDER (M vs F) from the other 4 features: AUC 0.693 (0.5 = they carry no information about gender). Strongest single features: EXT_SOURCE_1 (0.585), DAYS_EMPLOYED (0.566), EXT_SOURCE_3 (0.55), OWN_CAR_AGE (0.532), EXT_SOURCE_2 (0.527).
