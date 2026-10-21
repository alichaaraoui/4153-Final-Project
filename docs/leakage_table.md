<!-- PROVIDED template. Copy it to docs/leakage_table.md and fill that copy in:
       cp docs/leakage_table_template.md docs/leakage_table.md      (Windows: copy ...)
     For each feature, answer Yes or No in the third column and give your reason in the fourth.
     Replace every "?" and every "TODO(student)". Keep the table format: python run.py check
     reads it. Add a row for every feature you create, including ones you add yourself. -->

# Leakage table

Team: TODO(student)

**The question for every feature:** at the moment an applicant submits this application,
before we decide, would we already know this value?

If the answer is No, the feature **leaks**: it carries information from the future (often from
the outcome itself). A leaking feature makes validation scores look great and then fails in
real use, because the value does not exist yet when the decision is made.

**How to check, not guess:** the `DAYS_*` and `MONTHS_*` columns count days or months
**relative to this application** (negative = before it). Look at the largest value of each
time column a feature is built from. If it is above 0, part of that feature describes the
future. One look at `df["COL"].max()` is better than an opinion.

## Features you built (and the worked example)

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| BUREAU_COUNT | bureau | Yes | The bureau report is pulled when the application arrives. Every DAYS_CREDIT in our sample is negative (max -2), so all counted credits were opened before this application. |
| BUREAU_ACTIVE_COUNT | bureau | Yes | CREDIT_ACTIVE is the status in the bureau report at its last update. DAYS_CREDIT_UPDATE max is 0 across the 8,878 active credits, so no status was updated after the application. |
| BUREAU_CLOSED_COUNT | bureau | Yes | A credit counts as Closed only if it actually ended. DAYS_ENDDATE_FACT max is 0 across the 14,728 closed credits, so every closing happened on or before the application day. |
| BUREAU_AMT_CREDIT_SUM_MEAN | bureau | Yes | The credit amount is fixed when a credit opens. DAYS_CREDIT max is -2, so every credit averaged here opened before the application. |
| BUREAU_AMT_CREDIT_SUM_MAX | bureau | Yes | Same source as the mean: amounts set at opening, and DAYS_CREDIT max is -2, so every credit existed before the application. |
| BUREAU_AMT_DEBT_MEAN | bureau | Yes | Debt is the balance as of the bureau's last update. DAYS_CREDIT_UPDATE max is 0 across the 20,101 credits with a debt value, so no balance was refreshed after the application. |
| BUREAU_AMT_OVERDUE_SUM | bureau | Yes | The overdue amount is as of the bureau's last update. DAYS_CREDIT_UPDATE max is 0, so it reflects what was overdue on or before the application day. |
| BUREAU_DAYS_OVERDUE_MAX | bureau | Yes | CREDIT_DAY_OVERDUE is a count of days overdue as of the last bureau update, not a date. DAYS_CREDIT_UPDATE max is 0, so it was measured no later than the application day. |
| BUREAU_DAYS_CREDIT_MAX | bureau | Yes | This feature is DAYS_CREDIT itself. Its max is -2, so the newest credit opened 2 days before the application, never after. |
| PREV_COUNT | previous_application | ? | TODO(student) |
| PREV_APPROVED_RATE | previous_application | ? | TODO(student) |
| PREV_REFUSED_RATE | previous_application | ? | TODO(student) |
| PREV_AMT_APPLICATION_MEAN | previous_application | ? | TODO(student) |
| PREV_AMT_CREDIT_MEAN | previous_application | ? | TODO(student) |
| PREV_DAYS_DECISION_MAX | previous_application | ? | TODO(student) |
| PREV_DAYS_TERMINATION_MEAN | previous_application | ? | TODO(student) |
| PREV_LAST_STATUS | previous_application | ? | TODO(student) |
| BB_CREDIT_COUNT | bureau_balance | ? | TODO(student) |
| BB_MONTHS_COUNT | bureau_balance | ? | TODO(student) |
| BB_LATE_MONTHS_COUNT | bureau_balance | ? | TODO(student) |
| BB_LATE_SHARE | bureau_balance | ? | TODO(student) |
| BB_WORST_STATUS | bureau_balance | ? | TODO(student) |
| POS_LOAN_COUNT | POS_CASH_balance | ? | TODO(student) |
| POS_MONTHS_COUNT | POS_CASH_balance | ? | TODO(student) |
| POS_DPD_MAX | POS_CASH_balance | ? | TODO(student) |
| POS_DPD_MEAN | POS_CASH_balance | ? | TODO(student) |
| POS_LATE_SHARE | POS_CASH_balance | ? | TODO(student) |
| POS_COMPLETED_SHARE | POS_CASH_balance | ? | TODO(student) |

## Application columns worth a second look

These already sit in `application_train` and went into your Week 1 baseline. Some are less
obvious than they look. Find each one in `HomeCredit_columns_description.csv` (in your
download) before you answer.

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| TARGET | application_train | ? | TODO(student) |
| EXT_SOURCE_2 | application_train | ? | TODO(student) |
| DEF_30_CNT_SOCIAL_CIRCLE | application_train | ? | TODO(student) |
| AMT_REQ_CREDIT_BUREAU_HOUR | application_train | ? | TODO(student) |
| DAYS_LAST_PHONE_CHANGE | application_train | ? | TODO(student) |

## Beyond single columns

Leakage can also come from **how** a feature is computed, not only from which column it uses.
In two or three sentences: name one way your feature code could leak even if every column
above is a Yes, and how your code avoids it.

TODO(student)
