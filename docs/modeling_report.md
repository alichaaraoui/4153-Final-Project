# Modeling report (Week 3)

Team: T Triple A

## 1. The production model

Our production model is a `HistGradientBoostingClassifier` using the settings from Optuna
trial 29, the best of 30 trials: `learning_rate` 0.0102, `max_iter` 450, `max_leaf_nodes` 7,
`min_samples_leaf` 156, `l2_regularization` 0.0011, and `max_features` 0.367. That trial
reached a CV AUC of 0.748 on all 164 features.

The model uses 5 features: `EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3`, `DAYS_EMPLOYED`,
and `OWN_CAR_AGE`. They come from `python run.py prune`, which keeps the fewest features whose
CV AUC is within one standard deviation of the best count. It is wrapped in isotonic
calibration and rejects applicants when the score is at or above a threshold of 0.075. It is
registered as `models:/credit-risk@staging`, version 1.

## 2. Production model against the decision tree

| | Production model | tree_tuned |
|---|---|---|
| Validation ROC-AUC [95% CI] | 0.722 [0.662, 0.782] | 0.703 [0.645, 0.756] |
| CV ROC-AUC (train split) | 0.738 ± 0.020 | 0.697 ± 0.010 |
| Latency p95, one applicant (ms) | 48.4 | 4.6 |
| Model size (KB) | 396 | 18 |
| Features | 5 | 164 |
| Explainability | 450 small trees: needs a tool such as permutation importance or SHAP, but only 5 inputs to explain | One tree with `max_depth` 5 and `min_samples_leaf` 50: each decision is a short list of rules you can read |

The validation AUC difference (production minus tree) is +0.020, with a paired 95% interval of
[-0.043, +0.085]. The interval includes 0, so on validation we cannot say the production model
is better by more than chance. The CV gap of 0.041 is about twice the production model's
standard deviation, which points the same way but is not proof, and we tuned on those same
folds.

- **AUC:** the production model is higher on both CV and validation, but the validation
  difference could be noise.
- **Speed:** the tree is about 10 times faster. 48 ms is still fast for one loan application,
  and these timings come from one laptop.
- **Size:** the tree is about 22 times smaller. 396 KB is still small enough to deploy.
- **Explainability:** the tree is easier to read. A loan decision may need explaining, so this
  is the main thing we give up. The production model limits the damage by using only 5 inputs.

We chose the production model because its ranking looks better, and neither its speed nor its
size is a real problem for this service. This is a judgment call and not a clear win. If the
lender needed fully readable decisions, `tree_tuned` would be a reasonable choice.

## 3. The decision threshold

The threshold is 0.075. It comes from our Week 1 costs: approving someone who defaults costs
10, and rejecting someone who would have repaid costs 1. A missed default is 10 times worse, so
the cheapest rule rejects at a score far below 0.5. If the scores are true probabilities, theory
says to reject at about 1 / (1 + 10) = 0.09, and our threshold is close to that.

It was chosen on calibrated out-of-fold scores from the train split, where each applicant is
scored by a model that never saw them. We did not use the validation split because choosing on
those 1,000 applicants would fit the threshold to them and make the validation cost look better
than it will be on real applicants.

| Rule | Validation cost per applicant |
|---|---|
| Our threshold (0.075) | 0.576 |
| Threshold 0.5 | 0.810 |
| Approve everyone | 0.810 |

Our threshold saves 0.234 per applicant, about 29% compared with approving everyone. Scoring at
0.5 costs the same as approving everyone (to three decimals), so it adds nothing here. The cost
is that it rejects 39.3% of validation applicants, even though only 8.1% of them default.

`reports/threshold.json` shows a different number, 0.090, because it describes the uncalibrated
model on all 164 features. That model had a validation cost of 0.528 and rejected 26.8%, so the
5-feature list may carry a real cost. We report this but did not choose by it, because
validation is not used for choosing.

## 4. Calibration

We used isotonic calibration, learned on out-of-fold scores. On the validation split the Brier
score moved from 0.0703 to 0.0700, and the mean predicted probability moved from 0.080 to 0.081
against a true default rate of 0.081.

The reliability plot (`reports/figures/reliability.png`) shows that the model was already close
to the diagonal before calibration, because it trains on the real default rate with no
undersampling. After calibration, the points stay close to the diagonal at low scores. The top
two bins are still noisy: about 0.17 predicted against 0.22 observed, and about 0.28 predicted
against 0.20 observed. With only 81 validation defaults, those bins do not hold many.

Calibration barely helped this model, and the improvement is too small to treat as real. We
keep it because the threshold depends on it: the cost rule treats a score as a probability, so
0.075 only means "a 7.5% chance of default" if the scores are calibrated.

## 5. Limitations and risks

- **Small validation set:** it has only 81 defaults. The AUC intervals are about 0.12 wide, which
  is much larger than the differences between our models.
- **Choices made on the same train split:** the 30 Optuna trials, the feature list, and the
  threshold all used the same 4,000 applicants, so our CV numbers are likely a little optimistic.
  The feature list also came from an earlier prune run and was not repeated with trial 29's
  settings.
- **Costs leave things out:** the 10 and 1 are simplified costs. They ignore loan size, review
  capacity, and what a 39.3% rejection rate would do to the business. A different ratio moves
  the threshold.
- **Sensitive features and proxies:** the model does not use `CODE_GENDER` or `DAYS_BIRTH`
  directly, but that does not make it fair. `DAYS_EMPLOYED` can track age, `OWN_CAR_AGE` can track
  wealth, and the `EXT_SOURCE` scores come from outside sources we cannot inspect and may carry
  their own biases. We have not yet measured error rates across gender and age groups.
- **Heavy reliance on external scores:** three of the five features are `EXT_SOURCE` scores. If
  those sources change or become unavailable, the model could degrade quickly.
