# Test findings (Week 4)

Team: 1

Run `python run.py testreport` and copy the counts from `reports/test_report.md`.

| Kind | Tests | Passed | Failed | Known failures (xfail) | Skipped |
|---|---|---|---|---|---|
| Unit | 5 | 5 | 0 | TODO | TODO |
| Data | 5 | 5 | 0 | TODO | TODO |
| Model | TODO | TODO | TODO | TODO | TODO |

## Limits we chose, and why

### Data tests
- **`test_one_row_per_applicant`: exactly 5,000 rows and no duplicate `SK_ID_CURR`.** The
  sample has 5,000 applicants. A different count or a duplicate would mean a join or the
  sample changed.
- **`test_schema`: `SK_ID_CURR` and `TARGET` exist, `TARGET` only holds 0 and 1, and 8 key
  columns are numeric.** The model and the later weeks rely on these columns. A third
  `TARGET` value or a column turning into text would mean the labels or a feature broke.
- **`test_value_ranges`, age: `DAYS_BIRTH` between -25,550 and -6,570 (70 and 18 years).**
  Our data runs from -25,132 to -7,680, about 21 to 69 years. We used 18 to 70 because those
  are the assignment's limits for a real applicant, and the gap means normal data won't fail.
  A value past them would mean an impossible age or a broken conversion.
- **`test_value_ranges`, income: above 0.** Our lowest income is 27,000. A value of 0 or below
  isn't a real income and would also break the ratio features that divide by it.
- **`test_value_ranges`, `*_RATE` and `*_SHARE` columns: between 0 and 1, ignoring missing
  values.** These are shares, so anything outside 0 to 1 is impossible and would mean the
  calculation broke. Missing values are allowed because some applicants have no history to
  calculate from.
- **`test_missing_values`, required columns: `AMT_INCOME_TOTAL`, `AMT_CREDIT`, `DAYS_BIRTH`
  and `TARGET` are never missing.** All four are 0% missing in our data, and every applicant
  should have them.
- **`test_missing_values`, `EXT_SOURCE_2`: under 1% missing.** Ours is 0.24%, or 12 applicants.
  It is the strongest feature, so more missing values could quietly make scores worse.
- **`test_missing_values`, every column: none is 100% missing.** We did not set a tighter
  limit because the most-missing columns, `CC_UTILIZATION_MEAN` and `CC_UTILIZATION_MAX`, are
  72.7% missing. That is expected: 72.46% of applicants have no credit card records. A column
  that is completely empty would mean a join or a calculation failed.
- **`test_default_rate`: between 6% and 10%.** Ours is 8.08%, matching the roughly 8% in the
  full data. With 5,000 applicants, random sampling only moves the rate by about 0.4 points,
  so a rate outside this band would mean the sample or the labels changed.

## Findings

Write one section per test that failed. Name the test exactly as in the report (for example
`test_higher_income_does_not_raise_risk`). If no test failed, write "No test failed" and
say which test you expected to be the most likely to fail, and why.

### TODO: test name

- **What failed:** TODO (the assert message: how many applicants, by how much)
- **Why:** TODO (what in the model or the data causes it; check it, don't guess)
- **Does it matter for the lender?** TODO
- **Decision:** TODO (fixed the model, how; or kept as a known failure with
  `@pytest.mark.xfail(strict=True, ...)`, and what would make you fix it)

  For the Unit tests, no tests failed. I predicted the test: joining a raw child table would raise an error would fail.
