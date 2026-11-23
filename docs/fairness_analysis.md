# Fairness analysis (Week 6)

Team: T Triple A

## 1. What we compared, and on which data

We evaluated Model Version 1 using 1,000 validation applicants. We divided applicants into groups based on gender (F and M) and age (18–29, 30–39, 40–49, 50–59, and 60+).

We used the validation dataset rather than the training dataset because we wanted to evaluate how the model performs on applicants it was not trained on. Using training data could make the results look better than the model's actual performance on new applicants.

The decision threshold was 0.075. Applicants with a predicted default risk below 0.075 were approved, while applicants with a score at or above 0.075 were declined.

Gender and age were used to organize the fairness comparisons. The proxy test also examined whether the other four features could predict CODE_GENDER. The supplied results do not establish whether gender or age were directly included as model features, so this should be verified in the model's feature list.

## 2. The table

## By gender
| Group | n | Defaulters | Approval rate | Default rate | Mean score | TPR (risk caught) | FPR (good payers declined) | Note |
|---|---|---|---|---|---|---|---|---|
| F | 669 | 38 | 64.4% [61%, 68%] | 5.7% | 0.074 | 68.4% [53%, 81%] | 33.6% [30%, 37%] |  |
| M | 331 | 43 | 53.2% [48%, 58%] | 13.0% | 0.096 | 72.1% [57%, 83%] | 43.1% [37%, 49%] |  |

The approval rate is higher for women by 11.25 percentage points. Men also have a higher observed default rate and mean predicted risk.

## By age_band
| Group | n | Defaulters | Approval rate | Default rate | Mean score | TPR (risk caught) | FPR (good payers declined) | Note |
|---|---|---|---|---|---|---|---|---|
| 18-29 | 143 | 16 | 29.4% [23%, 37%] | 11.2% | 0.129 | 93.8% [72%, 99%] | 67.7% [59%, 75%] | fewer than 30 defaulters: TPR unreliable |
| 30-39 | 282 | 28 | 53.2% [47%, 59%] | 9.9% | 0.088 | 71.4% [53%, 85%] | 44.1% [38%, 50%] | fewer than 30 defaulters: TPR unreliable |
| 40-49 | 235 | 18 | 67.7% [61%, 73%] | 7.7% | 0.075 | 66.7% [44%, 84%] | 29.5% [24%, 36%] | fewer than 30 defaulters: TPR unreliable |
| 50-59 | 216 | 13 | 70.4% [64%, 76%] | 6.0% | 0.067 | 61.5% [36%, 82%] | 27.6% [22%, 34%] | fewer than 30 defaulters: TPR unreliable |
| 60+ | 124 | 6 | 83.9% [76%, 89%] | 4.8% | 0.048 | 33.3% [10%, 70%] | 15.3% [10%, 23%] | fewer than 30 defaulters: TPR unreliable |

The approval rate increases with age. The youngest group has the lowest approval rate, while applicants aged 60 and above have the highest.

## 3. The gaps

### Gender Difference

Women are approved more often than men: 64.4% compared with 53.2%, a difference of 11.25 percentage points.

However, the observed default rates are also different. The default rate for men is 13.0%, compared with 5.7% for women. This suggests that part of the approval difference is related to different observed risk levels in the validation data.

The mean predicted scores support this explanation: 0.096 for men and 0.074 for women.

The FPR is also higher for men (43.1%) than for women (33.6%). This means that among applicants who actually repay, men are more likely to be incorrectly declined. This difference is important because it indicates that the model does not produce the same false-decline rate across the two groups.

The TPR is relatively similar: 72.1% for men and 68.4% for women. The model catches a similar proportion of actual defaulters in both groups, although the confidence intervals are wide.

Therefore, the gender approval gap appears partly connected to different observed default rates, but the FPR difference also raises a concern about unequal treatment of applicants who would actually repay.

### Age Difference
Age shows a larger approval gap. The approval rate ranges from 29.4% for applicants aged 18–29 to 83.9% for applicants aged 60 and above.

The youngest group also has the highest observed default rate (11.2%), while the oldest group has the lowest (4.8%). Their mean scores follow the same pattern: 0.129 for the youngest group and 0.048 for the oldest.

This suggests that differences in observed default rates explain some of the age-related approval gap.

However, the FPR also varies substantially. It is 67.7% for applicants aged 18–29 but only 15.3% for applicants aged 60 and above. In other words, younger applicants who would actually repay are much more likely to be declined.

This is an important fairness concern because the model may be treating equally reliable applicants differently depending on their age group.

## 4. How sure are we?

We used 95% Wilson confidence intervals for approval rates and the reported TPR and FPR values. These intervals help show how much uncertainty there is in the estimates.

### Gender
The approval intervals are:

Women: 61–68%.
Men: 48–58%.
These intervals do not overlap, providing evidence of a real approval-rate difference in this validation sample.

The FPR intervals are:

Women: 30–37%.
Men: 37–49%.
They meet at approximately 37%, so the difference is suggestive but less conclusive based on these intervals.

The TPR intervals overlap substantially:

Women: 53–81%.
Men: 57–83%.
Therefore, we cannot confidently conclude that the model catches defaulters at different rates by gender.

### Age
The approval intervals are:

18–29: 23–37%.
30–39: 47–59%.
40–49: 61–73%.
50–59: 64–76%.
60+: 76–89%.
The intervals for the youngest and oldest groups do not overlap. This supports a substantial approval difference between those groups.

The FPR intervals also show a substantial difference:

18–29: 59–75%.
60+: 10–23%.
These intervals do not overlap, suggesting that younger applicants who would repay are much more likely to be declined.

However, the TPR estimates are much less reliable. Every age group has fewer than 30 defaulters. For example, the 60+ group has only six defaulters, resulting in a very wide TPR interval of 10–70%.

This means that the apparently large TPR differences between age groups should not be treated as reliable conclusions.

### How many applicants would we need?
The current sample of 1,000 applicants provides useful evidence, but some groups, especially older applicants and actual defaulters, are small.

We would need substantially more validation applicants, with enough actual defaulters in every age and gender group, to estimate TPR and FPR reliably.

As a practical target, collecting at least 100 actual defaulters per group would provide a more useful basis for comparing these metrics. The required total sample size would depend on the default rate in each group.

The current evidence is strongest for the large approval and FPR differences between the youngest and oldest age groups. Smaller differences should be treated cautiously.

## 5. Proxies

We tested whether the other four model features could predict CODE_GENDER without directly using the gender column.

The proxy model achieved an AUC of 0.693, compared with 0.5 for a model with no predictive information about gender.

This indicates that the remaining features contain information associated with gender. Removing CODE_GENDER alone would therefore not eliminate all gender-related information from the model.

The strongest individual features were:
| Feature |	AUC for predicting gender |
|---------|------------------- |
| EXT_SOURCE_1 |	0.585 |
| DAYS_EMPLOYED |	0.566 |
| EXT_SOURCE_3 |	0.550 |
| OWN_CAR_AGE |	0.532 |
| EXT_SOURCE_2 |	0.527 |

These features may act as proxies because financial history, employment patterns, external credit information, and car ownership can differ across demographic groups.

The same concern applies to age. Even if DAYS_BIRTH is removed, other variables may still contain information associated with age.

This means that simply removing CODE_GENDER or DAYS_BIRTH does not guarantee fairness. The model may reconstruct some of the same demographic information from other features.

We recommend examining feature importance, testing demographic predictability from the remaining features, and measuring fairness outcomes after removing or changing potentially problematic features.

## 6. What we recommend

We would not ship this model without further investigation and fairness improvements.

The model has substantial differences in approval and false-positive rates across groups. The age-related differences are especially concerning: younger applicants have a much higher false-decline rate than older applicants.

Our recommendations are:

- Investigate the age-related differences. Determine whether the model is relying on age-related patterns that unfairly disadvantage younger applicants.
- Test alternative feature sets. Examine whether removing or transforming sensitive and proxy-related features reduces unfair differences without significantly harming predictive performance.
- Monitor fairness metrics. Add approval rate, FPR, TPR, and calibration differences across gender and age groups to regular model monitoring and alerts.
- Collect more validation data. Increase the number of applicants and actual defaulters in smaller demographic groups so that estimates become more reliable.
- Perform regular audits. Repeat the fairness analysis after retraining or changing the decision threshold.
- Keep human oversight. Applicants should have an appropriate process to question or appeal decisions, especially when automated decisions could seriously affect their financial opportunities.

In the United States, the Equal Credit Opportunity Act (ECOA) and Regulation B prohibit discrimination in credit decisions based on protected characteristics, including sex and age, subject to specific legal provisions and exceptions.

Age can be considered in certain circumstances under Regulation B, but it cannot be used in a way that improperly discriminates against applicants. Gender-based discrimination in credit decisions is also prohibited.

The model should therefore be reviewed by legal and compliance specialists before being used in real lending decisions. Removing explicit gender or age columns does not guarantee fairness because other features may act as proxies.

The final deployment decision should involve the data science team, compliance and legal specialists, and responsible lending decision-makers. They should consider predictive accuracy, fairness, legal obligations, and potential harm to applicants.

**Final recommendation:** Do not deploy Model Version 1 in its current form. Investigate the large age-related approval and FPR gaps, test alternative models, and require an independent fairness and compliance review before deployment.