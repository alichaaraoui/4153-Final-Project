# Model card: credit-risk (draft)

Team: T Triple A · Last updated: 2026-11-23

**In one sentence:** this model estimates the chance that a loan applicant will have trouble
repaying, and suggests "approve" or "reject". It is a course project trained on 4,000 historical
applicants. It is **not ready to make real lending decisions** (see Fairness and Limitations).

## Model details

| | |
|---|---|
| Registered model | `models:/credit-risk@staging`, version 1 (MLflow run `d04567b3ef5744a88b2faa4cbdae3938`) |
| Algorithm | Gradient boosting (`HistGradientBoostingClassifier`, 450 small trees, settings from Optuna trial 29 of 30), wrapped in isotonic calibration so its scores behave like probabilities |
| Inputs | 5 features: `EXT_SOURCE_1`, `EXT_SOURCE_2`, `EXT_SOURCE_3` (three credit scores from outside sources), `DAYS_EMPLOYED` (time in the current job) and `OWN_CAR_AGE` (age of the applicant's car). Chosen by `python run.py prune` from 164 candidates |
| Output | A probability of default between 0 and 1, and a decision: **reject** if the probability is 0.075 or higher, otherwise **approve** |
| Threshold | 0.075. We assumed that approving someone who defaults costs 10 times more than rejecting someone who would have repaid. With that 10:1 ratio, rejecting is cheaper once the risk passes about 1 / (1 + 10) ≈ 0.09. We picked the exact value that gave the lowest cost on the training applicants' out-of-fold scores, not on the validation set |
| Live service | https://credit-risk-api-685424255950.us-central1.run.app (`POST /predict`; see `docs/api.md`) on Google Cloud Run, project `credit-risk-ttriplea` |
| Owner | Team T Triple A (ITAI 4153, Fall 2026) |

## Intended use

**What it is for.** The lender's underwriting staff, or their software, call `/predict` with an
applicant id after the application has been collected and before any loan is issued. The answer
is meant to help a person decide: approve, send for a manual review, or reject (see
`docs/problem.md`). It helps rank applicants by risk so reviewers can spend their time on the
risky and borderline cases.

**It supports a person; it does not decide alone.** A "reject" from this model should mean
"look at this application carefully", not "decline automatically". This matters because the
model rejects about 39% of applicants, while only about 8% of them actually default (see
Performance).

**It must NOT be used:**

- to decline anyone automatically, without a human review and a way to appeal;
- for anything other than consumer loan applications like the Home Credit ones (for example
  mortgages, business loans, insurance, hiring or renting);
- for applicants outside the population it was trained on (other countries, other lenders,
  other years) without checking it again first;
- to set prices, loan amounts or interest rates: it was not trained or checked for that;
- as evidence about any person's character or about a group of people.

At the moment it is a course demonstration with no real customers.

## Data

- **Source.** The [Home Credit Default Risk](https://www.kaggle.com/competitions/home-credit-default-risk)
  competition on Kaggle. Its rules allow use for the competition but do not allow us to
  redistribute the data, so the raw data is never committed to the repository.
- **Sample.** 5,000 applicants out of 307,511, drawn with seed 42 so that the share of defaulters
  stays the same, together with their whole credit history from the six other tables.
- **Split.** A fixed split (`config/split_ids.csv`): 4,000 applicants for training and 1,000 for
  validation. Validation was used only to report results, never to choose settings.
- **One row** is one loan application (`SK_ID_CURR`). The history tables (previous loans,
  credit bureau, payments) are summarised into one row per applicant by our Week 2 pipeline.
- **Target.** `TARGET = 1` means *payment difficulties*: a payment more than some number of days
  late on one of the first installments. Kaggle does not say exactly how many. "Default" in this
  card is shorthand for that label, not total non-payment. About 8.1% of applicants have
  `TARGET = 1` (323 in training, 81 in validation).
- **Known quirks.**
  - `DAYS_EMPLOYED` holds an impossible value, 365243 (about 1,000 years), for about 18% of
    applicants, mostly pensioners and people without a job. We replace it with "missing" and
    keep a flag for it.
  - The external scores are often missing: `EXT_SOURCE_1` for about 57% of training applicants,
    `EXT_SOURCE_3` for about 20%, `OWN_CAR_AGE` for about 66% (people without a car). The model
    handles missing values itself, but a missing score can push the risk up (see Explanations).

Full details: `docs/data_card.md`, `docs/feature_dictionary.md`.

## Performance

All numbers are on the 1,000 validation applicants, whom the model never saw in training.

| | This model | Baseline (logistic regression, 164 features) | Decision tree (`tree_tuned`) |
|---|---|---|---|
| ROC-AUC (how well it ranks risky above safe; 0.5 = random) | **0.722** [95% CI 0.662 to 0.782] | 0.710 | 0.703 [0.645 to 0.756] |
| PR-AUC (no skill ≈ 0.08) | 0.204 | 0.169 | 0.159 |
| KS | 0.359 | 0.356 | 0.339 |

**Cost and approvals at the 0.075 threshold** (cost units: 10 per approved defaulter, 1 per
rejected good payer, divided by all applicants):

| Rule | Cost per applicant | Approval rate |
|---|---|---|
| This model at 0.075 | **0.576** | 60.7% |
| Approve everyone | 0.810 | 100% |
| This model at 0.5 | 0.810 | (no better than approving everyone) |
| Reject everyone | 0.919 | 0% |

The model costs about 29% less than approving everyone. The price is that it rejects 39.3% of
applicants, and most of them would have repaid.

**Calibration.** On average the scores match reality: mean predicted probability 0.081 against a
real default rate of 0.081 (Brier score 0.0700). In the highest-risk bins the match is rough
(for example 0.28 predicted against 0.20 observed), because few applicants fall there.

**How sure are we?** These numbers rest on 1,000 applicants and only **81 defaulters**. One
defaulter more or less caught moves the catch rate by about 1.2 points. The AUC interval is about
0.12 wide, much wider than the gap between this model and the baseline, so we **cannot say it is
better than the simple baseline or the tree by more than chance**. The training-set
cross-validation AUC (0.738 ± 0.020) points the same way but was also used for tuning, so it is
slightly optimistic.

## Explanations

**What the model relies on overall** (mean absolute SHAP value, `reports/explain/shap_global.png`):

| Feature | Plain meaning | Importance |
|---|---|---|
| `EXT_SOURCE_2` | external credit score 2 | 0.36 |
| `EXT_SOURCE_3` | external credit score 3 | 0.33 |
| `DAYS_EMPLOYED` | time in the current job | 0.29 |
| `EXT_SOURCE_1` | external credit score 1 | 0.29 |
| `OWN_CAR_AGE` | age of the applicant's car | 0.18 |

Low external scores and a short time in the current job raise the risk. Three of the five
inputs are scores bought from outside providers whose methods we cannot inspect.

**Reasons for a declined applicant.** `python run.py explain` turns each decision into the
features that pushed the score up the most, written as plain sentences
(`reports/explain/explanations.md`). For example, the typical declined applicant (122934, risk
13.3%) gets: "external credit score 2 is 0.344 (typical: 0.564)", "external credit score 3 is
missing", "time in the current job is 2.3 years (typical: 4.4 years)".

Two cautions for anyone giving these reasons to an applicant:

- **"Score is missing" is a reason** in two of the three examples. The applicant cannot fix a
  score the provider did not send, so a human should check the missing data before declining.
- **The borderline case** (applicant 270289) scores 7.5%, exactly at the threshold. Small changes
  would flip it, so cases near 0.075 should always go to a reviewer.

## Fairness

We compared groups by gender (`CODE_GENDER`) and age band (from `DAYS_BIRTH`) on the validation
set. Neither column is a model input. Full analysis: `docs/fairness_analysis.md`.

| Group | n | Approval rate | Real default rate | Good payers wrongly declined (FPR) |
|---|---|---|---|---|
| Women | 669 | 64.4% [61, 68] | 5.7% | 33.6% [30, 37] |
| Men | 331 | 53.2% [48, 58] | 13.0% | 43.1% [37, 49] |
| Age 18 to 29 | 143 | 29.4% [23, 37] | 11.2% | 67.7% [59, 75] |
| Age 60+ | 124 | 83.9% [76, 89] | 4.8% | 15.3% [10, 23] |

- **Age is the main concern.** Applicants under 30 are approved less than half as often as those
  over 60. Part of this matches a real difference in default rates (11.2% against 4.8%), but
  **two in three young applicants who would have repaid are declined**, against about one in
  seven of the oldest. Those intervals do not overlap, so this gap is real in our sample.
- **Gender.** Men are approved 11 points less often. Men also defaulted more often in this
  sample, which explains part of it, but men who would repay are still declined more often
  (43% against 34%; the intervals only just touch, so this is suggestive, not proven).
- **How reliable.** Approval rates and false-decline rates rest on 120 to 670 people per group
  and are fairly solid. Catch rates for defaulters (TPR) rest on 6 to 43 defaulters per group
  and are **not reliable**: the 60+ group has only 6 defaulters.
- **Proxies.** A small model can guess gender from the five inputs with an AUC of 0.69
  (0.5 = no information). `EXT_SOURCE_1` and `DAYS_EMPLOYED` carry the most. `DAYS_EMPLOYED`
  also tracks age (pensioners have it missing). Leaving gender and age out of the model does
  **not** keep them out of its decisions.

**Our recommendation: do not use this version for real lending decisions** until the age gap
has been investigated, other feature sets have been tested, and legal and compliance staff have
reviewed it (in the US, the Equal Credit Opportunity Act covers sex and age).

## Monitoring

**What is logged.** Every answered `/predict` call writes one JSON line to Cloud Logging:
request id, time, model version, applicant id, any amounts the caller changed, the exact feature
values the model received, the probability, the decision and the threshold. Logging can never
break a prediction.

**How drift is measured.** `python run.py monitor` compares each batch of logged requests with
the 4,000 training rows: PSI per feature, with missing values counted as their own bin (below
0.1 stable, 0.1 to 0.25 moderate, above 0.25 major), the KS statistic, an Evidently report, and
the approval rate and score distribution against validation.

**What we found.**

- **Batch 1** (961 requests): no change. Every feature PSI below 0.03, approval rate 60.5% against
  60.7% on validation.
- **Batch 2** (988 requests): `EXT_SOURCE_3` became missing for **53.6%** of applicants instead
  of 20% (PSI 0.54, major). The values that did arrive looked normal, so the KS test missed it.
  Most likely an outside data feed broke. **The model kept answering with the same confidence**
  (approval rate 58.3%, score PSI 0.008), so watching only the output would not have caught it.

**Alerts we propose** (details in `docs/monitoring_report.md`):

| Signal | Threshold | Who is told |
|---|---|---|
| Missing values in a feature | Up more than 10 points from training, or above 40% | ML engineer and data pipeline owner |
| Feature drift (PSI) | Warning above 0.1, critical above 0.25 (at least 100 new requests) | ML engineer |
| Approval rate or mean score | Approval rate more than 5 points from 60.7%, or mean score more than 0.03 from 0.081 | ML engineer and business owner |
| Service errors | More than 2% of `/predict` calls failing in 5 minutes, or no logs for 5 minutes | Service owner and ML engineer |

We cannot yet measure whether live decisions are right: repayment outcomes arrive months later.

## Limitations

**Do not trust the model when:**

- **An outside score is missing or the provider changed.** Three of five inputs come from outside
  providers. When one goes missing (as in batch 2), the model quietly guesses and its risk
  estimates can be wrong without any visible sign. Treat these decisions as "needs review".
- **The applicant is unlike the training data**: a different country, product, time period or
  lender, or people who were declined in the past (they never appear in the training data with
  an outcome).
- **The applicant belongs to a small group.** Young applicants, applicants over 60 and other
  small groups have few defaulters in our data; the model's error rates for them are uncertain.
- **The score is close to 0.075.** Tiny changes in the inputs flip the decision.
- **Someone changed the threshold or the costs.** The 10:1 cost ratio is our assumption, not a
  measured business fact. It ignores loan size, review capacity and the business effect of
  rejecting 39% of applicants. A different ratio gives a different threshold.

**What we do not know yet:**

- How well it performs on live applicants: we have no outcomes for them yet.
- Whether it is really better than the simple baseline: the difference is within the noise of
  81 validation defaulters.
- Whether the 5 features cost accuracy: the same model on all 164 features had a lower
  validation cost (0.528 against 0.576), but we did not choose by validation.
- How the decisions behave under a human-review step, since review cost and accuracy are not
  measured.

## Ethical considerations

**Who could be harmed, and how:**

- **Good payers who are declined** lose access to credit they could have handled. With this
  threshold that happens often (about a third of all good payers) and much more often to young
  applicants and to men. They may turn to more expensive lenders.
- **Defaulters who are approved** may end up with debt they cannot afford, collection actions
  and damaged credit records, and the lender loses money.
- **Applicants with a missing outside score** can be declined for something they cannot see or
  fix.

**What protects them, and what is still missing:**

- **Human review:** the model is decision support. A reviewer should look at every rejection, and
  always at borderline scores and applications with missing outside scores.
- **Reasons and appeal:** every decline can be explained with readable reasons
  (`python run.py explain`), so an applicant can be told why and can challenge wrong data. A
  formal appeal process still has to be set up by the lender.
- **Monitoring:** every decision is logged and traceable to a model version; drift and missing
  data alerts catch broken inputs. Fairness metrics by group are **not yet** monitored live; that
  needs governed access to gender and age data.
- **Privacy:** applicant data stays in a private bucket and is never committed; the logs hold
  only model features and ids.
- **Compliance:** before any real use, legal and compliance staff must review the age and gender
  gaps against anti-discrimination law.
