# API design (Week 5)

Team: T Triple A

## 1. Where do the 164 features come from?

A request to `/predict` is about one applicant, but the full feature set is built from the
application row plus six child tables (bureau, bureau_balance, previous_application,
installments_payments, POS_CASH_balance, credit_card_balance). Most features are aggregates
over many rows: counts of earlier credits, mean overdue days, the share of late instalments,
and so on. The loan screen does not have those rows, and even if it did, asking every caller to
recompute 164 aggregates the same way our Week 2 pipeline does would be slow and fragile. One
small difference (a different join, a different missing-value rule) and the model gets inputs
it never saw in training: training/serving skew, which fails silently with plausible but wrong
probabilities.

There are three ways a service could get the features:

- **The caller sends them all.** Simple service, but a huge request, every client has to
  reimplement the pipeline, and skew is almost guaranteed.
- **The service computes them on demand** from the raw tables for that one applicant. Always
  fresh, but every request needs database access and several joins and aggregations, so it is
  slow (hundreds of milliseconds or more), complex, and it needs a second copy of the feature
  code that must stay identical to training.
- **A feature store**: precompute one row per applicant ahead of time with the *same* code the
  model was trained on, and look it up by id at request time. Fast (one indexed lookup) and no
  skew, but the values are only as fresh as the last time the store was built.

## 2. What we chose, and why

Our service uses a feature store: `models/feature_store.parquet`, one row per applicant,
indexed by `SK_ID_CURR`, written by `python run.py export` from the same Week 2 feature table
the registered model was trained on. It is shipped in the model bundle next to `model.joblib`
and `model_info.json`, so the model and its features always travel together. On Cloud Run the
service downloads the three files from our private bucket once, at start-up, and keeps them in
memory.

A request contains the applicant's id and, optionally, updated amounts from the application
form: `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `AMT_ANNUITY` (each must be > 0). `build_features`
looks up a **copy** of the applicant's row (the shared store is never modified), replaces any
amount the request sends, recomputes the four ratio features (credit/income, annuity/income,
credit/goods, annuity/credit) with the same formulas as Week 2, and returns the model's columns
in training order. Recomputing matters: a new income with the old credit-to-income ratio would
describe an applicant who cannot exist.

This is the right choice here because the applicants are known in advance (the 5,000-applicant
sample), a credit screen needs an answer in milliseconds, and serving reuses the training code
instead of a second implementation.

One thing to be honest about: the model we registered in Week 3 (version 1) ended up using only
**5 features** (`DAYS_EMPLOYED`, `OWN_CAR_AGE`, `EXT_SOURCE_1`, `EXT_SOURCE_2`,
`EXT_SOURCE_3`), and the exported store keeps only those columns. None of them is an amount or a
ratio, so with this model version an updated income or loan amount is accepted and validated but
does not change the probability (applicant 100021 scores 0.0753 with or without a new income).
The override path is still in place, and it starts to matter as soon as a model that uses the
amounts or ratios is registered and exported.

## 3. What can go wrong

- **The applicant is not in the feature store.** The request is valid, but there is nothing to
  score. `build_features` raises `UnknownApplicant` and the endpoint answers **404** with the
  id in the message. We do not guess with default values: a made-up row would produce a
  confident-looking decision about nobody.
- **The request itself is wrong** (missing id, negative or zero amount, text instead of a
  number, a misspelled field). FastAPI rejects it with **422** before our code runs, saying
  which field failed. `extra="forbid"` means a typo such as `AMT_INCOM_TOTAL` is refused
  instead of silently ignored.
- **The store and the model do not match** (the store built from different data or code than
  the model). The service would answer, but with skewed inputs. Our defence is that one
  `export` writes the model, its feature list, its data version and the store together, and
  `/model-info` reports the version and `data_version`, so every answer can be traced back. The
  rule is to always upload all three files together, never only one.
- **An applicant's history changed after the store was built** (a new bureau credit, a missed
  payment). The service still answers from the old row, so the decision can be out of date. The
  form's amounts can be updated in the request, but the child-table aggregates cannot. The fix is
  operational: rebuild and re-export the store on a schedule (for example nightly) and redeploy.
- **The bundle cannot be read at start-up** (bucket permissions, files not at the top level).
  The container fails to start and Cloud Run keeps the previous revision serving. `/health`
  reports `model_loaded`, so monitoring can see it.

## 4. Example requests

Valid request, existing applicant:

```bash
curl -s -X POST https://credit-risk-api-685424255950.us-central1.run.app/predict \
  -H "Content-Type: application/json" -d '{"SK_ID_CURR": 100021}'
```
```json
{"SK_ID_CURR":100021,"probability":0.07529411764705882,"decision":"reject","threshold":0.075,"model_version":"1"}
```

Another applicant, approved: `{"SK_ID_CURR": 100030}` gives
`{"SK_ID_CURR":100030,"probability":0.0337465564738292,"decision":"approve","threshold":0.075,"model_version":"1"}`.

Invalid request (negative income), **422**:

```bash
curl -s -X POST .../predict -H "Content-Type: application/json" \
  -d '{"SK_ID_CURR": 100021, "AMT_INCOME_TOTAL": -5}'
```
```json
{"detail":[{"type":"greater_than","loc":["body","AMT_INCOME_TOTAL"],"msg":"Input should be greater than 0","input":-5,"ctx":{"gt":0.0}}]}
```

Unknown applicant, **404**:

```bash
curl -s -X POST .../predict -H "Content-Type: application/json" -d '{"SK_ID_CURR": 1}'
```
```json
{"detail":"Applicant 1 is not in the feature store"}
```
