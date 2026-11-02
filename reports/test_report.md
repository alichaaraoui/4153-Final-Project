# Test report (Week 4)

Commit `c1d2231`, 2026-11-02T20:33:49+00:00.

## Unit tests (5 passed)

| Test | Outcome | Message |
|---|---|---|
| test_bureau_features_depend_only_on_own_credits | passed |  |
| test_previous_features_ignore_row_order | passed |  |
| test_join_keeps_applicants_without_history | passed |  |
| test_join_refuses_a_table_that_was_not_aggregated | passed |  |
| test_ratios_are_never_infinite | passed |  |

## Data tests (5 passed)

| Test | Outcome | Message |
|---|---|---|
| test_one_row_per_applicant | passed |  |
| test_schema | passed |  |
| test_value_ranges | passed |  |
| test_missing_values | passed |  |
| test_default_rate | passed |  |

## Model tests (1 failed, 3 passed)

| Test | Outcome | Message |
|---|---|---|
| test_minimum_auc | passed |  |
| test_application_weekday_does_not_change_the_score | passed |  |
| test_gender_does_not_change_the_score | passed |  |
| test_higher_income_does_not_raise_risk | failed | KeyError: 'AMT_INCOME_TOTAL' |
