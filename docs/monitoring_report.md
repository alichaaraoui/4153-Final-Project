# Monitoring report (Week 6)

Team: T Triple A

## 1. What we monitor, and where the data comes from

Every call to `/predict` writes one JSON record, and logging can never break a prediction. The record holds:

- `request_id`: a new id for every call, so one call can be traced.
- `timestamp` (UTC): when it happened; we used it to separate batch 1 from batch 2.
- `model_version`: which model answered (version 1).
- `SK_ID_CURR`: the applicant.
- `overrides`: the amounts the caller changed, if any.
- `features`: what the model actually received. This is what we measure drift on.
- `probability`, `decision`, `threshold`: what the model answered.

On Cloud Run the record is printed to stdout, so it lands in Cloud Logging (the fields are under `jsonPayload`). We downloaded it in Cloud Shell with:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="credit-risk-api" AND jsonPayload.event="prediction"' \
  --freshness=7d --limit=5000 --format=json > predictions.json
```

This gave 1,950 prediction records from Nov 16, 2026, 20:15 to 20:17 UTC: 961 for batch 1 and 988 for batch 2.

The reference is X_train, the 4,000 rows the model was trained on. That is what the model learned from, so any change from it is drift that the model has never seen.

## 2. Batch 1

Batch 1 looks like the training data:

| | Validation | Batch 1 |
|---|---|---|
| Requests | | 961 |
| Approval rate | 60.7% | 60.5% |
| Mean score | 0.081 | 0.086 |
| Score PSI | | 0.009 |

No feature had a PSI above 0.1. The largest was DAYS_EMPLOYED at 0.022, then EXT_SOURCE_1 at 0.019. Evidently flagged 0 of the 5 columns it checked. Even if it had flagged a few, that would be expected by chance when testing many columns at once. Batch 1 is a normal week.

## 3. Batch 2: what changed?

| Feature | PSI | KS statistic | Missing (training → batch 2) | Mean (training → batch 2) | What changed |
|---|---|---|---|---|---|
| EXT_SOURCE_3 | 0.540 (major) | 0.037 (p = 0.64) | 20.0% → 53.6% | 0.511 → 0.509 | Missing far more often; the values that are present look the same |

Only one feature changed. Every other feature stayed below a PSI of 0.02 (the next one, EXT_SOURCE_2, is 0.019).

Most likely the external credit score source behind EXT_SOURCE_3 stopped returning a score for about a third of applicants, for example an outage or a broken feed or join. The applicants did not change, the data pipeline did.

The model's output barely moved: approval rate 58.3% (60.7% on validation), mean score 0.0875, score PSI 0.008. That is not reassuring. The model fills in the missing value silently and keeps answering with the same confidence. Its output cannot tell us yet whether those decisions are worse, because we will only know which loans default much later, and we have no labels yet.

## 4. How we measured it

**PSI** splits the training values into 10 equal-size bins, plus one bin for missing values, and compares the share of the new batch in each bin with the training share. Below 0.1 is stable, 0.1 to 0.25 is moderate drift, above 0.25 is major drift.

**KS** is the largest gap between the two cumulative distributions, and it only looks at non-missing values. That is why it missed EXT_SOURCE_3 (0.037, p = 0.64): the values that were present did not change, only how often they were missing. The KS p-value is also misleading with large samples, where tiny differences come out "significant", and when many columns are tested, where some come out significant by chance.

**Missing values must count as drift.** A feature going from 20% to 54% missing was the biggest change in the data, and a test that ignores missing values does not see it.

**Our PSI and Evidently agree:** Evidently flagged 0 of 5 columns in batch 1 and 1 of 5 in batch 2.

## 5. Proposed alerts

We propose four alerts covering data quality, feature drift, model output changes, and service reliability. These alerts should be checked automatically so that a problem is detected during a batch, rather than only when someone downloads the logs and analyses them.

| Signal | Threshold | Checked | Triggers |
|---|---|---|---|
| Missing feature values | 	Alert if any important feature's missing rate increases by more than 10 percentage points from its training baseline, or exceeds 40% missing. | Every 15 minutes, using a rolling window of predictions. | Notify the ML engineer and data pipeline owner through email or the team alert channel. The data pipeline owner first checks the upstream data source, API responses, and joins to identify whether values are missing because of an outage or a pipeline failure. |
| Feature drift (PSI) | Warning at PSI above 0.1; critical alert above 0.25 for any monitored feature. | Every hour, provided at least 100 new predictions are available. | Notify the ML engineer. They first compare the affected feature's distribution with X_train and investigate changes in the upstream data source. If major drift is confirmed, they assess whether predictions should be paused or the model retrained. |
| Prediction score or approval-rate change | Alert if the approval rate changes by more than 5 percentage points from the validation baseline (60.7%), or mean prediction score changes by more than 0.03 from its validation baseline (0.081). | Every 15 minutes, using a rolling window of at least 100 predictions. | Notify the ML engineer and product/business owner. They first check whether the change is caused by a threshold or model-version change, then investigate feature distributions and recent prediction logs before deciding whether to restrict model use. |
| Prediction service failures | Alert if more than 2% of /predict requests return errors over a 5-minute window, or if the service stops producing prediction logs for 5 minutes while requests are expected. | Continuously, with a 5-minute rolling check. | Notify the API/service owner and ML engineer. The service owner first checks Cloud Run logs, recent deployments, application errors, and service health, then works to restore normal prediction service.

## 6. Limitations

Our monitoring can identify changes in the input data and model outputs, but it cannot yet establish whether individual credit decisions are correct.

The main limitations are:

* No immediate outcome labels: We do not know whether approved applicants actually repay their loans or whether rejected applicants would have defaulted. Loan repayment and default outcomes only become available after applicants have had enough time to make repayments. This can take months or longer, depending on the loan and repayment schedule. Without these labels, we cannot directly measure real-world model accuracy, precision, recall, or default prediction performance.
* Drift does not necessarily mean worse predictions: PSI identifies changes in feature distributions, not whether those changes make the model less accurate. A feature can drift without harming predictions, while a model can become less accurate even when its input distributions appear stable.
* No visibility into upstream causes: We log the features received by /predict, but we do not currently monitor the external data providers or every step of the data pipeline. For example, we detected the increase in missing EXT_SOURCE_3 values but could not determine from prediction logs alone whether the cause was an external provider outage, a failed API request, or an incorrect database join.
* No direct fairness monitoring: We do not yet have alerts that check whether approval rates or prediction errors differ unfairly between applicant groups. This would require carefully governed demographic information and additional analysis.
* Limited sample size and batch coverage: Our analysis used 961 and 988 predictions in two batches. These are useful for identifying large changes, but smaller or gradual changes may be missed. Short monitoring windows can also produce noisy results.
* Monitoring depends on logging: If predictions are not logged correctly, our drift analysis may be incomplete. Although logging is designed never to break a prediction, we still need independent monitoring to detect missing logs or logging failures.

With more time, we would improve monitoring in four ways:

* Add delayed outcome monitoring: Join prediction records to loan repayment and default outcomes when they become available. This would allow us to measure actual model performance and compare it with validation results.
* Monitor upstream data sources: Add checks for external data availability, API failures, unexpected missing values, and pipeline join failures, particularly for EXT_SOURCE_3.
* Add fairness checks: Monitor differences in approval rates and, once outcome labels are available, model error rates across appropriately governed applicant groups.
* Improve drift detection: Monitor gradual changes over longer periods, use minimum sample-size requirements, and combine PSI with missing-value rates and other statistical tests to reduce false alarms.

Overall, our current monitoring tells us whether the data entering the model and the predictions coming out of it are changing. It does not yet tell us whether the model is making good lending decisions. Adding delayed loan outcome data is the most important next step because it would allow us to monitor actual performance rather than relying only on changes in distributions and prediction statistics.
