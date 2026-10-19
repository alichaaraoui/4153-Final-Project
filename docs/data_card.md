# Data card: Home Credit Default Risk (Week 1 sample)

## 1. Source and license terms

Home Credit supplied the dataset for the [Home Credit Default Risk competition on Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk).
Each member must accept the competition rules before downloading it. Following
the project README, we do not share, upload, or commit the raw data or sample.
The repository's `.gitignore` excludes `data/`, ZIP files, and `kaggle.json`;
we share code and aggregate reports. Access does not imply unrestricted permission
to redistribute the data; the competition rules govern its use.

## 2. What each table holds

| Table | One row is... | Links by |
|---|---|---|
| application_train | A current application and its outcome label | SK_ID_CURR |
| bureau | A credit reported by another lender | SK_ID_CURR; SK_ID_BUREAU identifies the credit |
| bureau_balance | A monthly status of a bureau credit | SK_ID_BUREAU → bureau → SK_ID_CURR |
| previous_application | A previous Home Credit application | SK_ID_CURR and SK_ID_PREV |
| POS_CASH_balance | A monthly snapshot of a previous POS/cash loan | SK_ID_CURR and SK_ID_PREV |
| installments_payments | A payment record for a previous loan installment; one installment can have multiple records | SK_ID_CURR and SK_ID_PREV |
| credit_card_balance | A monthly snapshot of a previous credit-card account | SK_ID_CURR and SK_ID_PREV |

`bureau_balance` has no applicant ID and must link through `bureau`.

## 3. Full size versus sample size

| Table | Full rows | Sample rows |
|---|---:|---:|
| application_train | 307,511 | 5,000 |
| bureau | 1,716,428 | 23,680 |
| bureau_balance | 27,299,925 | 231,091 |
| previous_application | 1,670,214 | 23,009 |
| POS_CASH_balance | 10,001,358 | 138,350 |
| installments_payments | 13,605,401 | 186,311 |
| credit_card_balance | 3,840,312 | 50,668 |

Counts come from `reports/sample_row_counts.json`.
The current `reports/table_summary.json` reports total sample memory shrinking
from **96.93 to 18.09 MiB** after dtype reduction. The provided sampler selects
5,000 applicants within TARGET classes using seed 42 and retains their linked
history. Sampling whole applicants preserves relationships and complete histories
that random sampling of individual history rows would break.

## 4. Target definition and class balance

TARGET = 1 means payment difficulties: a payment more than X days late on at least
one of the first Y installments; the supplied dictionary does not disclose X or Y.
TARGET = 0 covers other cases. “Default” is therefore shorthand for this label,
not necessarily total nonpayment. Positive counts and rates are **24,825/307,511
(8.073%)** in the full application data, **404/5,000 (8.080%)** in the sample,
**323/4,000 (8.075%)** in training, and **81/1,000 (8.100%)** in validation.
Class-preserving sampling and the fixed split keep these proportions similar.
Predicting zero for everyone would achieve 91.92% sample accuracy while finding
none of the payment-difficulty cases.

## 5. Known issues

The notebook finds **48 of 122 columns more than half empty**, including the
COMMONAREA fields (71.4% missing) and NONLIVINGAPARTMENTS fields (71.0%).
Imputation must be fitted on training data only. The impossible DAYS_EMPLOYED
value **365243** occurs for **897 applicants (17.94%)**; their positive rate is
4.91%, versus 8.77% for other applicants. Replace it with missing and retain an
anomaly flag. Negative DAYS_BIRTH counts days before application; approximate age
is -DAYS_BIRTH / 365.25. Interpret each DAYS_* field using its definition.
The notebook also reports different observed rates for CODE_GENDER groups;
these associations do not by themselves establish causation or fair decisions.

## 6. Sensitive columns

CODE_GENDER and DAYS_BIRTH describe gender and age; NAME_FAMILY_STATUS and
CNT_CHILDREN describe personal circumstances. Income, education, occupation,
housing, regional ratings, and external scores may act as proxies. We will
restrict access, examine group error and decision rates with group counts,
and compare models with and without sensitive inputs. Removing explicit
attributes alone does not eliminate proxy effects. TARGET and applicant IDs
must not be model inputs.

## 7. Limitations of a small sample

Only **81 validation positives** support evaluation: one changed positive
classification changes recall by about **1.23 percentage points**. ROC-AUC,
PR-AUC, and KS can fluctuate; bootstrap applicants to estimate uncertainty
rather than claim an unmeasured margin. Rare categories, unusual histories,
and small demographic groups may be absent or poorly represented. Historical
borrowers may differ from future applicants. This sample supports an initial
baseline, not confident subgroup conclusions or deployment readiness.
 