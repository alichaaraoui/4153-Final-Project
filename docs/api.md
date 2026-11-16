# Credit-risk scoring API

Team: T Triple A

Base URL: https://credit-risk-api-685424255950.us-central1.run.app. Interactive documentation:
`<base URL>/docs`.

The service gives a credit decision for one loan applicant: the estimated probability of
default, and `approve` or `reject` against the threshold chosen in Week 3. Applicants are
identified by `SK_ID_CURR`; their features come from a feature store built with the same
pipeline the model was trained on (see `docs/api_design.md`). No authentication: it is a course
demo with no real customers.

## Endpoints

### `GET /health`

Is the service up, and is a model loaded? Cheap, never touches the model; Cloud Run and the
monitoring use it.

```bash
curl -s https://credit-risk-api-685424255950.us-central1.run.app/health
```
```json
{"status":"ok","model_loaded":true,"model_version":"1"}
```

### `GET /model-info`

Which model is serving, so any answer can be traced back to a registered model version.

```bash
curl -s https://credit-risk-api-685424255950.us-central1.run.app/model-info
```
```json
{"name":"credit-risk","version":"1","threshold":0.075,"n_features":5,"valid_auc":0.7224841816789586,"data_version":"b2c3ac925963","exported":"2026-11-09T19:47:39+00:00"}
```

### `POST /predict`

The decision for one applicant. JSON body:

| Field | Type | Required | Meaning |
|---|---|---|---|
| `SK_ID_CURR` | integer > 0 | yes | the applicant's id (must be in the feature store) |
| `AMT_INCOME_TOTAL` | number > 0 | no | updated yearly income from the form |
| `AMT_CREDIT` | number > 0 | no | updated loan amount |
| `AMT_ANNUITY` | number > 0 | no | updated yearly repayment |

Optional amounts replace the stored values and the ratio features are recomputed. (Model
version 1 uses none of the amounts or ratios, so with this version they do not change the
probability.) Any other field is refused.

```bash
curl -s -X POST https://credit-risk-api-685424255950.us-central1.run.app/predict \
  -H "Content-Type: application/json" -d '{"SK_ID_CURR": 100021}'
```
```json
{"SK_ID_CURR":100021,"probability":0.07529411764705882,"decision":"reject","threshold":0.075,"model_version":"1"}
```

`decision` is `reject` when `probability >= threshold`, otherwise `approve`. For example
`{"SK_ID_CURR": 100030}` answers probability 0.0337 and `approve`.

## Errors

**422 Unprocessable Entity: the request does not fit.** FastAPI checks the body before our
code runs: a missing or non-positive id, an amount that is zero or negative, text instead of a
number, or a field that does not exist. The answer says which field and why.

```bash
curl -s -X POST .../predict -H "Content-Type: application/json" \
  -d '{"SK_ID_CURR": 100021, "AMT_INCOME_TOTAL": -5}'
```
```json
{"detail":[{"type":"greater_than","loc":["body","AMT_INCOME_TOTAL"],"msg":"Input should be greater than 0","input":-5,"ctx":{"gt":0.0}}]}
```

A misspelled field (`{"SK_ID_CURR": 100021, "AMT_INCOM_TOTAL": 5}`) gets `"type":
"extra_forbidden"`, "Extra inputs are not permitted", instead of being silently ignored.

**404 Not Found: unknown applicant.** The request is valid, but the id is not in the feature
store, so there is nothing to score.

```bash
curl -s -X POST .../predict -H "Content-Type: application/json" -d '{"SK_ID_CURR": 1}'
```
```json
{"detail":"Applicant 1 is not in the feature store"}
```

**503: model not loaded yet.** Only possible in the moment a new instance is starting.

## Response times

Measured against the live service on November 16, 2026 from a laptop in Charlotte, NC (to
us-central1, Iowa) with `python run.py latency --url <base URL>`, after leaving the service with
no traffic for about 23 minutes (`reports/latency.json`):

| | |
|---|---|
| First request | 170 ms |
| Requests after it | 100, 0 errors |
| p50 | 68 ms |
| p95 | 76 ms |
| Slowest | 81 ms |
| Mean | 69 ms |

**p50** is the typical wait: half the applicants get their answer in 68 ms or less. **p95** is
what the slowest 1 in 20 waits: 76 ms. Both are far below anything a person on the loan screen
would notice, and most of that time is the network round trip from North Carolina to Iowa, not
the model (on the laptop the same requests took about 9 ms). The spread is small (p50 to max
is only 13 ms) because each request is one indexed lookup and one prediction.

**Cold start.** With `--min-instances=0`, Cloud Run usually shuts the container down after
about 15 idle minutes, and the next request then waits for a new container to start, download
the bundle from the bucket and load the model, typically a few seconds. In this run the first
request took only 170 ms, so Cloud Run had kept the idle instance alive and there was no cold
start to measure; it does not guarantee when an idle instance is removed. The first person
after a long quiet period can still wait a few seconds. If that mattered for real customers,
`--min-instances=1` would remove cold starts at the cost of paying for one instance all the
time.

## Online or batch scoring?

Online scoring answers one applicant at a time, at the moment they apply: this API. Batch
scoring runs the model over many applicants at once on a schedule, for example every night,
and stores the results in a table. Batch is cheaper and simpler to operate: no service has to
stay reachable, the work runs in one job, and a slow run only delays a report. It suits
decisions that are not waiting on a person, such as re-scoring the existing loan book for risk
monitoring or choosing whom to send a pre-approved offer. Online costs more to run and to
watch: a live endpoint, cold starts, latency targets, and errors that a customer sees
immediately. But a credit decision happens while the applicant is on the loan screen, using the
amounts they just typed, and a new applicant has no score from last night's batch. So the
decision itself should be online, with batch alongside it: the expensive part (the feature store
of child-table aggregates) is precomputed in batch, and the API only does a lookup and one
prediction per request, which is what keeps it fast.
