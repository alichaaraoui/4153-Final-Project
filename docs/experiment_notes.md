# Experiment notes (Week 3)

Team: 1

## Setup

Every run below trained on the same rows: the train split of our feature table (4,000
applicants, 323 defaults), compared with 5-fold stratified cross-validation, data_version
b2c3ac925963. Exported table: reports/mlflow_runs.csv.

## Results

One row per run. Copy the numbers from `python run.py train` or the MLflow UI. Every
boosting variation must appear here **by its run name**.

| Run | What changed from hgb_default | CV AUC ± std | Train AUC | Valid AUC [95% CI] |
|---|---|---:|---:|---:|
| baseline_lr | Logistic regression (Week 1 pipeline) | 0.7227 ± 0.0319 | 0.8455 | 0.7273 [0.6658, 0.7831] |
| tree_unlimited | Decision tree, no limits | 0.5401 ± 0.0212 | 1.0000 | 0.5389 [0.4980, 0.5815] |
| tree_tuned | Best decision tree from grid: max_depth=5, min_samples_leaf=50 | 0.6965 ± 0.0095 | 0.7824 | 0.7026 [0.6450, 0.7558] |
| dt_balanced | Decision tree with class_weight=balanced | 0.5483 ± 0.0224 | 1.0000 | 0.5438 [0.5046, 0.5851] |
| hgb_default | Nothing (default histogram gradient boosting) | 0.7251 ± 0.0390 | 1.0000 | 0.6968 [0.6358, 0.7597] |
| hgb_balanced | Used class_weight=balanced | 0.7125 ± 0.0446 | 1.0000 | 0.7262 [0.6656, 0.7826] |
| hgb_undersample | Undersampled the majority class (undersample=3) | 0.7217 ± 0.0245 | 0.9987 | 0.7550 [0.6973, 0.8089] |
| hgb_l2 | Added L2 regularization (l2_regularization=1.0) | 0.7321 ± 0.0328 | 1.0000 | 0.7454 [0.6972, 0.7958] |
| hgb_lr003 | Reduced learning_rate to 0.003 | 0.7112 ± 0.0223 | 0.8786 | 0.7071 [0.6487, 0.7639] |
| hgb_balanced_l2 | Combined class_weight=balanced with l2_regularization=1.0 | 0.7267 ± 0.0433 | 1.0000 | 0.7388 [0.6831, 0.7898] |

## Overfitting

tree_unlimited has a perfect training AUC of 1.0000 but a CV AUC of only 0.5401,
showing severe overfitting and poor generalization. The grid-selected tree_tuned has a
smaller train-to-CV gap (0.7824 versus 0.6965) and selected max_depth=5 and
min_samples_leaf=50.

## What helped and what did not

No single change clearly beat the noise in cross-validation. hgb_l2 had the highest CV
AUC (0.7321), but its 0.0070 increase over hgb_default is smaller than the CV standard
deviations; the combined hgb_balanced_l2 result (0.7267) was effectively the same as
the default. hgb_undersample had the highest validation AUC (0.7550), but its CV AUC
was 0.0034 below the default, so the validation result alone is not enough to establish
a repeatable improvement. hgb_balanced and hgb_lr003 had lower CV AUCs than the
default, but the differences (0.0126 and 0.0139) are still smaller than the reported
fold-to-fold standard deviations. The dt_balanced and tree_unlimited models performed
poorly, while the tuned tree generalized better but remained below the boosting and
logistic-regression CV results. A useful next step would be repeated stratified
cross-validation with additional seeds to determine whether the small differences persist.
