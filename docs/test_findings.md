# Test findings (Week 4)

Team: 1

Run `python run.py testreport` and copy the counts from `reports/test_report.md`.

| Kind | Tests | Passed | Failed | Known failures (xfail) | Skipped |
|---|---|---|---|---|---|
| Unit | 5 | 5 | 0 | 0 | 0 |
| Data | 5 | 5 | 0 | 0 | 0 |
| Model | 4 | 2 | 2 | 0 | 0 |

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


  For the Unit tests, no tests failed. I predicted the test: joining a raw child table would raise an error would fail.


## Model Test Findings

### `test_gender_does_not_change_the_score`

**What failed:**  
The initial fallback model changed some applicants' predicted risk scores when their `CODE_GENDER` value was changed. The test detected score differences greater than 0.01.

**Why:**  
The fallback model was trained using all 164 available features, including `CODE_GENDER`. Consequently, gender could influence its predictions.

**Does it matter for the lender?**  
Yes. Gender is a protected attribute and should not influence lending decisions. Allowing gender to affect risk scores creates a fairness and compliance concern.

**Decision:**  
The final registered model uses five selected features: `DAYS_EMPLOYED`, `OWN_CAR_AGE`, `EXT_SOURCE_1`, `EXT_SOURCE_2`, and `EXT_SOURCE_3`. `CODE_GENDER` is excluded. The gender invariance test passes with this model. We decided to keep the test and use the selected-feature model rather than mark it as an expected failure.

### `test_higher_income_does_not_raise_risk`

**What failed:**  
The initial fallback model caused 139 applicants to receive higher risk scores after their income was increased by 50%. The largest increase was 0.104.

**Why:**  
The fallback model used all 164 available features, including income and income-related ratios. Increasing income changed those features, and the model did not consistently interpret higher income as lower risk.

**Does it matter for the lender?**  
Yes. An applicant earning more should not become riskier solely because their income increased while everything else remained equal.

**Decision:**  
The final registered model uses five selected features and excludes `AMT_INCOME_TOTAL` and the income-related ratios. We tested the model using the full validation dataframe because the production fixture only provides the five selected model features, while `change_income()` requires the original income column. The model produced zero riskier applicants, with a largest increase of 0.000. We decided to keep the test and not mark it as an expected failure.