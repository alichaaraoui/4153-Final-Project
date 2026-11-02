# Test report (Week 4)

Commit `e2862d4`, 2026-11-02T20:13:09+00:00.

## Unit tests (5 passed)

| Test | Outcome | Message |
|---|---|---|
| test_bureau_features_depend_only_on_own_credits | passed |  |
| test_previous_features_ignore_row_order | passed |  |
| test_join_keeps_applicants_without_history | passed |  |
| test_join_refuses_a_table_that_was_not_aggregated | passed |  |
| test_ratios_are_never_infinite | passed |  |

## Data tests (4 failed, 1 passed)

| Test | Outcome | Message |
|---|---|---|
| test_one_row_per_applicant | passed |  |
| test_schema | failed | Failed: TODO(student): write this test |
| test_value_ranges | failed | Failed: TODO(student): write this test |
| test_missing_values | failed | Failed: TODO(student): write this test |
| test_default_rate | failed | Failed: TODO(student): write this test |

## Model tests (2 failed, 2 passed)

| Test | Outcome | Message |
|---|---|---|
| test_minimum_auc | passed |  |
| test_application_weekday_does_not_change_the_score | passed |  |
| test_gender_does_not_change_the_score | failed | AssertionError: Some applicants' scores changed when gender was altered |
| test_higher_income_does_not_raise_risk | failed | AssertionError: 139 applicants got riskier; largest increase 0.104 |
