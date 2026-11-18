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

TODO: At least four alerts. For each: the signal, the threshold, how often it is checked,
and what it triggers (who is told, and what they do first).

| Signal | Threshold | Checked | Triggers |
|---|---|---|---|
| TODO | | | |

## 6. Limitations

TODO: What this monitoring cannot see (for example: whether the decisions were right), how
long until it could, and what you would add with more time.
