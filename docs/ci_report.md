<!-- PROVIDED: copy this file to docs/ci_report.md and fill in every placeholder.
     The check fails while the word in capitals below is still anywhere in the file. -->

# CI and the quality gate (Week 4)

Team: 1

## The pipeline

Cloud Build project: credit-risk-ttriplea. Trigger: pr-checks, on pull requests to
`main`. Branch protection on `main` requires the check: `pr-checks`.

| Step | What it runs | Why it is there |
|---|---|---|
| install | `pip install -r requirements.txt` | the same packages as on our laptops |
| lint | `/workspace/.venv/bin/python -m ruff check .` | makes sure the style of the code is good |
| test | `/workspace/.venv/bin/python -m pytest` | 	Runs the project's automated tests. Tests requiring local data or trained models skip themselves because Cloud Build starts without the project's local data or MLflow database. All other tests must pass. |
| gate | `/workspace/.venv/bin/python -m scripts.quality_gate` | Checks candidate model quality against the configured thresholds and registered Week 3 baseline. Blocks merging if the candidate violates any quality rule or its metrics are stale. |

## Gate thresholds, and why

For each threshold in `config/gate.yaml`: the value, the number it is compared with today,
and why this value (what you looked at, and what passing or failing it would mean).

- **min_auc** = 0.700: The candidate model must achieve validation ROC-AUC of at least 0.700. This establishes a minimum acceptable level of predictive performance.
- **max_cost** = 0.537: Expected cost per applicant must not exceed 0.537 at the selected decision threshold. This is stricter than approving everyone, which costs approximately 0.81 per applicant.
- **max_auc_drop** = 0.051: Candidate validation AUC cannot fall more than 0.051 below the registered Week 3 model's validation AUC. This prevents a substantial regression in model performance.
- **allow_failing_model_tests** = 0: No failing model tests are allowed. Known failures explicitly marked as expected failures (xfail) do not count as failures.

## Evidence

- A green Cloud Build run on a pull request: https://console.cloud.google.com/cloud-build/builds;region=global/9a812902-8316-4797-9a34-3e50a181e82a?authuser=1&project=credit-risk-ttriplea
- A red run, and what made it red (https://console.cloud.google.com/cloud-build/builds;region=global/e21daf48-a652-4da0-b90e-197521100f14?authuser=1&project=credit-risk-ttriplea):
    - The build failed after I changed the hgb_default configuration in the model settings.
    - I added max_iter: 1 to the HistGradientBoosting model, limiting it to one boosting iteration instead of its normal default.
    - This intentionally weakened the candidate model and was used to test whether the quality gate would detect a model performance regression and block the merge.
- How the red pull request was handled: I  did not merge the failing pull request. GitHub branch protection prevented merging because the required Cloud Build check was unsuccessful. I closed the pull request without merging, ensuring the intentionally weakened model configuration did not reach main.
