<!-- PROVIDED template. Copy it to docs/feature_dictionary.md and fill that copy in:
       cp docs/feature_dictionary_template.md docs/feature_dictionary.md   (Windows: copy ...)
     Replace every "TODO(student)". Keep the table format: python run.py check reads it.
     Add a row for every feature you create yourself. -->

# Feature dictionary

Team: T Triple A

One row per engineered feature in `data/features/features.parquet`. Someone who has never
seen your code should understand each feature from this page alone.

- **Meaning:** what the number says about the applicant, in plain language.
- **How it was built:** the source columns, the aggregation, any filtering or special cases
  (missing values, the 365243 sentinel, zero denominators), and what an applicant with no
  records gets (0 or missing).

| Feature | Source table | Meaning | How it was built |
|---|---|---|---|
| BUREAU_COUNT | bureau | How many credits other lenders report for the applicant, open or closed. | Count of the applicant's rows in bureau (`aggregate_bureau`, named aggregation on SK_ID_BUREAU). 0 for applicants with no bureau record (filled in `join_features`). |
| BUREAU_AMT_CREDIT_SUM_MEAN | bureau | Average size of the credits other lenders report for the applicant. | Mean of AMT_CREDIT_SUM over the applicant's bureau rows (`aggregate_bureau`). Missing for applicants with no bureau record. |
| BUREAU_AMT_CREDIT_SUM_MAX | bureau | The largest single credit another lender has given the applicant. | Max of AMT_CREDIT_SUM over the applicant's bureau rows. Missing for applicants with no bureau record. |
| BUREAU_AMT_DEBT_MEAN | bureau | How much the applicant still owes, on average, per bureau credit. | Mean of AMT_CREDIT_SUM_DEBT, skipping missing values. Missing for applicants with no bureau record. |
| BUREAU_AMT_OVERDUE_SUM | bureau | Total money currently overdue across all the applicant's other credits. | Sum of AMT_CREDIT_SUM_OVERDUE over the applicant's bureau rows. Missing for applicants with no bureau record. |
| BUREAU_DAYS_OVERDUE_MAX | bureau | The worst current lateness, in days, on any of the applicant's other credits. | Max of CREDIT_DAY_OVERDUE over the applicant's bureau rows. Missing for applicants with no bureau record. |
| BUREAU_DAYS_CREDIT_MAX | bureau | How recently the applicant opened a credit elsewhere (closer to 0 = more recent). | Max of DAYS_CREDIT (days before this application, negative). Missing for applicants with no bureau record. |
| BUREAU_ACTIVE_COUNT | bureau | How many of the applicant's other credits are still open. | Count of bureau rows with CREDIT_ACTIVE = "Active" (`count_where`). 0 for applicants with no bureau record (filled in `join_features`). |
| BUREAU_CLOSED_COUNT | bureau | How many of the applicant's other credits are already closed. | Count of bureau rows with CREDIT_ACTIVE = "Closed" (`count_where`). 0 for applicants with no bureau record (filled in `join_features`). |
| PREV_COUNT | previous_application | How many times the applicant applied to Home Credit before. | Number of the applicant's rows in previous_application (`aggregate_previous`). 0 for applicants with no previous_application record (filled in `join_features`). |
| PREV_APPROVED_RATE | previous_application | Share of earlier Home Credit applications that were approved (0 to 1). | Rows with NAME_CONTRACT_STATUS = "Approved" divided by PREV_COUNT (`share_where`). Canceled and Unused offer also exist, so it does not add up to 1 with the refused rate. Missing for applicants with no previous_application record. |
| PREV_REFUSED_RATE | previous_application | Share of earlier Home Credit applications that were refused (0 to 1). | Rows with NAME_CONTRACT_STATUS = "Refused" divided by PREV_COUNT (`share_where`). Missing for applicants with no previous_application record. |
| PREV_AMT_APPLICATION_MEAN | previous_application | Average amount the applicant asked Home Credit for before. | Mean of AMT_APPLICATION over earlier applications. Missing for applicants with no previous_application record. |
| PREV_AMT_CREDIT_MEAN | previous_application | Average amount Home Credit actually offered on earlier applications. | Mean of AMT_CREDIT over earlier applications. Missing for applicants with no previous_application record. |
| PREV_DAYS_DECISION_MAX | previous_application | How recently Home Credit last decided on an application from this person. | Max of DAYS_DECISION, after the 365243 "no date" code is turned into missing (`replace_sentinel`). Missing for applicants with no previous_application record. |
| PREV_DAYS_TERMINATION_MEAN | previous_application | On average, how long ago the applicant's earlier Home Credit loans ended. | Mean of DAYS_TERMINATION after the 365243 "no date" code is turned into missing, so open loans do not drag the average up by hundreds of days. Missing for applicants with no previous_application record. |
| PREV_LAST_STATUS | previous_application | The outcome of the applicant's most recent earlier application (text: Approved, Refused, Canceled, Unused offer). | NAME_CONTRACT_STATUS of the row with the largest DAYS_DECISION; ties broken by the larger SK_ID_PREV. Missing for applicants with no previous_application record. |
| BB_CREDIT_COUNT | bureau_balance | How many of the applicant's bureau credits come with a monthly history. | Stage 1: one row per SK_ID_BUREAU; stage 2: merge SK_ID_CURR from bureau (many-to-one) and count credits. Credits with no monthly rows are not counted. 0 for applicants with no bureau_balance record (filled in `join_features`). |
| BB_MONTHS_COUNT | bureau_balance | How many months of bureau history the applicant has in total. | Count of MONTHS_BALANCE rows per credit, summed per applicant. 0 for applicants with no bureau_balance record (filled in `join_features`). |
| BB_LATE_MONTHS_COUNT | bureau_balance | How many months the applicant was late on another lender's credit. | STATUS turned into a number ("C" and "X" become missing); months with STATUS 1 to 5 counted per credit, then summed per applicant. 0 for applicants with no bureau_balance record (filled in `join_features`). |
| BB_LATE_SHARE | bureau_balance | Fraction of the applicant's bureau months that were late (0 to 1). | BB_LATE_MONTHS_COUNT / BB_MONTHS_COUNT, from the applicant's totals so long credits weigh more than short ones. Missing for applicants with no bureau_balance record. |
| BB_WORST_STATUS | bureau_balance | The worst lateness level ever reached on another lender's credit (0 = never late, 5 = 120+ days or written off). | Max numeric STATUS over all months; "C" and "X" ignored, missing if the applicant only has those. Missing for applicants with no bureau_balance record. |
| POS_LOAN_COUNT | POS_CASH_balance | How many earlier point-of-sale or cash loans the applicant had with Home Credit. | Number of distinct SK_ID_PREV in POS_CASH_balance (`aggregate_pos_cash`). 0 for applicants with no POS_CASH_balance record (filled in `join_features`). |
| POS_MONTHS_COUNT | POS_CASH_balance | How many months of POS/cash loan history the applicant has. | Number of the applicant's POS_CASH_balance rows. 0 for applicants with no POS_CASH_balance record (filled in `join_features`). |
| POS_DPD_MAX | POS_CASH_balance | The most days the applicant was ever past due on a POS/cash loan. | Max of SK_DPD over the applicant's months. Missing for applicants with no POS_CASH_balance record. |
| POS_DPD_MEAN | POS_CASH_balance | Average days past due per month on POS/cash loans. | Mean of SK_DPD over the applicant's months. Missing for applicants with no POS_CASH_balance record. |
| POS_LATE_SHARE | POS_CASH_balance | Fraction of POS/cash months in which the applicant was past due (0 to 1). | Months with SK_DPD > 0 divided by all the applicant's months (`share_where`). Missing for applicants with no POS_CASH_balance record. |
| POS_COMPLETED_SHARE | POS_CASH_balance | Fraction of the applicant's POS/cash loans that were paid off (0 to 1). | Per loan: any month with NAME_CONTRACT_STATUS = "Completed"; then the mean over the applicant's loans (denominator is loans, not months). Missing for applicants with no POS_CASH_balance record. |
| INST_COUNT | installments_payments | How many installment payments the applicant has on record. | Number of the applicant's installments_payments rows, including the few with no payment recorded (`aggregate_installments`). 0 for applicants with no installments record (filled in `join_features`). |
| INST_LATE_SHARE | installments_payments | Fraction of payments made after the due date (0 to 1). | DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT, averaged over payments that were actually recorded; rows with no payment are left out instead of counting as on time. Missing for applicants with no installments record. |
| INST_DAYS_LATE_MAX | installments_payments | The most days any single payment was late (0 if never late). | Max of DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT, clipped at 0, over recorded payments. Missing for applicants with no installments record. |
| INST_UNDERPAID_SHARE | installments_payments | Fraction of payments smaller than the amount due (0 to 1). | AMT_PAYMENT < AMT_INSTALMENT, averaged over recorded payments. Missing for applicants with no installments record. |
| INST_PAYMENT_DIFF_MEAN | installments_payments | Whether the applicant tends to pay more or less than due (negative = pays less). | Mean of AMT_PAYMENT - AMT_INSTALMENT over recorded payments. Missing for applicants with no installments record. |
| CC_MONTHS_COUNT | credit_card_balance | How many months of Home Credit card history the applicant has. | Number of the applicant's credit_card_balance rows (`aggregate_credit_card`). 0 for applicants with no credit card record (filled in `join_features`). |
| CC_BALANCE_MEAN | credit_card_balance | Average monthly card balance (can be slightly negative after an overpayment). | Mean of AMT_BALANCE over the applicant's card months. Missing for applicants with no credit card record. |
| CC_UTILIZATION_MEAN | credit_card_balance | How much of the card limit the applicant uses on average (1 = maxed out). | AMT_BALANCE / AMT_CREDIT_LIMIT_ACTUAL per month with `safe_divide`; months with a limit of 0 (about 1 in 5) become missing and are skipped in the mean. Missing for applicants with no credit card record. Also missing if no month has a limit. |
| CC_UTILIZATION_MAX | credit_card_balance | The highest share of the card limit the applicant ever used. | Max of the same monthly utilization, skipping zero-limit months. Missing for applicants with no credit card record. |
| CC_DRAWINGS_MEAN | credit_card_balance | Average money taken from the card per month. | Mean of AMT_DRAWINGS_CURRENT over the applicant's card months. Missing for applicants with no credit card record. |
| CC_DPD_MAX | credit_card_balance | The most days the applicant was ever past due on the card. | Max of SK_DPD over the applicant's card months. Missing for applicants with no credit card record. |
| CREDIT_INCOME_RATIO | application_train | Loan size measured in years of income. | AMT_CREDIT / AMT_INCOME_TOTAL with `safe_divide` (`add_ratio_features`). Every applicant has one; missing only if income is 0 or missing. |
| ANNUITY_INCOME_RATIO | application_train | Share of yearly income that goes to the yearly loan payment. | AMT_ANNUITY / AMT_INCOME_TOTAL with `safe_divide`. Missing if income is 0 or either value is missing. |
| CREDIT_GOODS_RATIO | application_train | Whether the applicant borrows more than the price of what they buy (above 1 = more). | AMT_CREDIT / AMT_GOODS_PRICE with `safe_divide`. Missing when the goods price is 0 or missing. |
| ANNUITY_CREDIT_RATIO | application_train | Yearly payment as a share of the loan; a rough inverse of how many years the loan lasts. | AMT_ANNUITY / AMT_CREDIT with `safe_divide`. Missing if either value is missing or the credit is 0. |

The application columns (from `application_train`) are described in
`HomeCredit_columns_description.csv` and in your data card; they do not need rows here.
