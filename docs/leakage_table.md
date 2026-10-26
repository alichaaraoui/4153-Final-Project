<!-- PROVIDED template. Copy it to docs/leakage_table.md and fill that copy in:
       cp docs/leakage_table_template.md docs/leakage_table.md      (Windows: copy ...)
     For each feature, answer Yes or No in the third column and give your reason in the fourth.
     Replace every "?" and every "TODO(student)". Keep the table format: python run.py check
     reads it. Add a row for every feature you create, including ones you add yourself. -->

# Leakage table

Team: T Triple A

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
| PREV_COUNT | previous_application | Yes | Counts earlier Home Credit applications. DAYS_DECISION max is -2 (no 365243 codes), so every earlier application was decided before this one. |
| PREV_APPROVED_RATE | previous_application | Yes | NAME_CONTRACT_STATUS is the decision on each earlier application. DAYS_DECISION max is -2 (no 365243 codes), so every earlier application was decided before this one. |
| PREV_REFUSED_RATE | previous_application | Yes | Same source as the approved rate: decisions on earlier applications. DAYS_DECISION max is -2 (no 365243 codes), so every earlier application was decided before this one. |
| PREV_AMT_APPLICATION_MEAN | previous_application | Yes | The amount asked for is fixed when the earlier application is filed. DAYS_DECISION max is -2 (no 365243 codes), so every earlier application was decided before this one. |
| PREV_AMT_CREDIT_MEAN | previous_application | Yes | The amount offered is set at the earlier decision. DAYS_DECISION max is -2 (no 365243 codes), so every earlier application was decided before this one. |
| PREV_DAYS_DECISION_MAX | previous_application | Yes | This feature is DAYS_DECISION itself. Its max is -2, so the latest decision came 2 days before this application. |
| PREV_DAYS_TERMINATION_MEAN | previous_application | Yes | After replacing the 3,102 365243 "no date" codes with missing, DAYS_TERMINATION max is -2, so every termination averaged here happened before the application. |
| PREV_LAST_STATUS | previous_application | Yes | Status of the earlier application with the largest DAYS_DECISION. DAYS_DECISION max is -2 (no 365243 codes), so every earlier application was decided before this one. |
| BB_CREDIT_COUNT | bureau_balance | Yes | Counts bureau credits with monthly history. MONTHS_BALANCE max is 0 across 231,091 rows, so no month is after the application month. |
| BB_MONTHS_COUNT | bureau_balance | Yes | Counts monthly records. MONTHS_BALANCE max is 0, so every month is on or before the application month (5,519 rows are month 0, the report pulled at application). |
| BB_LATE_MONTHS_COUNT | bureau_balance | Yes | STATUS of months up to the application. MONTHS_BALANCE max is 0, so no late month comes from the future. |
| BB_LATE_SHARE | bureau_balance | Yes | Late months divided by months, both built from rows with MONTHS_BALANCE at most 0. |
| BB_WORST_STATUS | bureau_balance | Yes | Highest STATUS over months with MONTHS_BALANCE at most 0 (max is 0), so it is the worst status seen up to the application month. |
| POS_LOAN_COUNT | POS_CASH_balance | Yes | Distinct earlier loans with POS/cash history. MONTHS_BALANCE max is -1, so every record is from before the application month. |
| POS_MONTHS_COUNT | POS_CASH_balance | Yes | Counts monthly records. MONTHS_BALANCE max is -1, so all are from before the application. |
| POS_DPD_MAX | POS_CASH_balance | Yes | SK_DPD is days past due in a given month. MONTHS_BALANCE max is -1, so it only covers months before the application. |
| POS_DPD_MEAN | POS_CASH_balance | Yes | Same source as POS_DPD_MAX; MONTHS_BALANCE max is -1. |
| POS_LATE_SHARE | POS_CASH_balance | Yes | Share of months with SK_DPD above 0, over months with MONTHS_BALANCE at most -1. |
| POS_COMPLETED_SHARE | POS_CASH_balance | Yes | A loan counts as Completed only from a monthly status row, and MONTHS_BALANCE max is -1, so it was completed before the application. |
| INST_COUNT | installments_payments | Yes | Counts payment rows. DAYS_INSTALMENT max is -2, so every installment was due before the application. |
| INST_LATE_SHARE | installments_payments | Yes | Compares payment date to due date. DAYS_ENTRY_PAYMENT max is -2 and DAYS_INSTALMENT max is -2, so both happened before the application. |
| INST_DAYS_LATE_MAX | installments_payments | Yes | DAYS_ENTRY_PAYMENT minus DAYS_INSTALMENT; both columns max out at -2, so every payment was made before the application. |
| INST_UNDERPAID_SHARE | installments_payments | Yes | Compares amounts of payments already made. DAYS_ENTRY_PAYMENT max is -2, so no future payment is included. |
| INST_PAYMENT_DIFF_MEAN | installments_payments | Yes | Average of AMT_PAYMENT minus AMT_INSTALMENT over payments with DAYS_ENTRY_PAYMENT max -2, all before the application. |
| CC_MONTHS_COUNT | credit_card_balance | Yes | Counts card-month rows. MONTHS_BALANCE max is -1, so all are from before the application month. |
| CC_BALANCE_MEAN | credit_card_balance | Yes | AMT_BALANCE in months with MONTHS_BALANCE at most -1 (max is -1). |
| CC_UTILIZATION_MEAN | credit_card_balance | Yes | Balance divided by limit in the same month; MONTHS_BALANCE max is -1, so only past months. |
| CC_UTILIZATION_MAX | credit_card_balance | Yes | Same source as the mean; MONTHS_BALANCE max is -1. |
| CC_DRAWINGS_MEAN | credit_card_balance | Yes | Drawings in months with MONTHS_BALANCE at most -1 (max is -1). |
| CC_DPD_MAX | credit_card_balance | Yes | SK_DPD per card month; MONTHS_BALANCE max is -1, so it only covers months before the application. |
| CREDIT_INCOME_RATIO | application_train | Yes | AMT_CREDIT and AMT_INCOME_TOTAL are both on this application form, filled in before the decision. |
| ANNUITY_INCOME_RATIO | application_train | Yes | AMT_ANNUITY and AMT_INCOME_TOTAL both come from this application form. |
| CREDIT_GOODS_RATIO | application_train | Yes | AMT_CREDIT and AMT_GOODS_PRICE both come from this application form. |
| ANNUITY_CREDIT_RATIO | application_train | Yes | AMT_ANNUITY and AMT_CREDIT both come from this application form. |

## Application columns worth a second look

These already sit in `application_train` and went into your Week 1 baseline. Some are less
obvious than they look. Find each one in `HomeCredit_columns_description.csv` (in your
download) before you answer.

| Feature | Source table | Known at application time? | Why / how you checked |
|---|---|---|---|
| TARGET | application_train | No | TARGET is the outcome: whether the client later had payment difficulties on this loan. It only exists after the loan runs, so it is the label, never a feature. |
| EXT_SOURCE_2 | application_train | Yes | A normalized score from an external data source (column description), obtained when the application is scored. Every value is between 0 and 0.81, with no date that could point to the future. |
| DEF_30_CNT_SOCIAL_CIRCLE | application_train | Yes | How many people in the client's social circle defaulted 30+ days. It describes other people's past loans as of the application, not this loan's outcome. |
| AMT_REQ_CREDIT_BUREAU_HOUR | application_train | Yes | The column description says enquiries to the bureau one hour before the application, so it is counted before the decision. |
| DAYS_LAST_PHONE_CHANGE | application_train | Yes | Days before the application that the phone was changed. Its max is 0 in our sample, so no change happened after the application. |

## Beyond single columns

Leakage can also come from **how** a feature is computed, not only from which column it uses.
In two or three sentences: name one way your feature code could leak even if every column
above is a Yes, and how your code avoids it.

A feature could leak through statistics computed across applicants, for example a target-mean encoding or an imputer fit on the whole sample, because the validation rows would then shape the training features. Our history features only summarize each applicant's own rows and never read TARGET, and the median imputer and scaler sit inside the sklearn Pipeline, which is fit on the training split only (`model.fit(train[...])` in `src/compare.py`).
