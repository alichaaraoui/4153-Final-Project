# Problem statement

Team: T Triple A

## 1. Who uses the model, and for what decision?

The consumer lender's underwriting team uses the model's estimated probability of
payment difficulty to help decide whether to approve an application, refer it for
manual review, or reject it. Scoring happens after application information has been
collected and before a loan is issued. Only information available at that point may
be used. For this project, we assume that without the model, staff apply lending
rules and review applications manually; the repository does not describe an existing
operational process. The model is intended to make risk assessment more consistent
and focus reviewers' attention on applications where review could change the decision.

## 2. The options

- **Approve:** estimated risk is low enough that lending has the lowest expected
  cost, and the application meets the lender's other eligibility requirements.
- **Refer for manual review:** the application is near a decision boundary, has
  important missing or inconsistent information, or falls outside the model's
  supported population. An underwriter checks the information and makes the final
  decision. Review should be used when its expected reduction in decision losses
  exceeds its cost, subject to reviewer capacity.
- **Reject:** estimated risk is high enough that rejecting has the lowest expected
  cost and further review is unlikely to change that conclusion.

Referral consumes staff time and delays the applicant's decision. It does not
guarantee a correct outcome, so evaluation must include the losses from decisions
made after review as well as the review fee or staff cost.

The available materials do not specify review time or a monetary cost per referral.
We represent this cost as C_review, in monetary units per application reviewed.
Review capacity and effectiveness must be established before choosing operational
thresholds; we do not assume review is free or perfectly accurate.

## 3. The cost of approving someone who defaults

Approving a borrower who defaults can cause losses from unrecovered principal
and collection expenses. We represent the loss as C_default, in monetary units
per approved borrower who defaults. No numerical cost or currency is provided
in the available project materials. AMT_CREDIT records the loan amount, but it
does not establish the loss after repayments and recoveries. TARGET records
payment difficulties rather than a monetary loss, so neither field supplies
the requested cost. Our analysis therefore leaves C_default symbolic.

## 4. The cost of rejecting someone who would have repaid

Rejecting an applicant who would repay loses the lender the profitable customer
opportunity represented by C_reject, in monetary units per rejected borrower
who would have repaid. The data does not provide that customer's expected net
profit or an assigned rejection cost, so a numerical cost and the ratio
C_default / C_reject cannot be calculated from the supplied information.

For a calibrated probability p of default, the simplified expected costs are
p * C_default for approval and (1 - p) * C_reject for rejection. If correct
decisions have zero incremental cost and referral is unavailable, the two costs
are equal at p = C_reject / (C_default + C_reject). Approve below this threshold
and reject above it. A higher default-to-rejection cost ratio lowers the threshold:
the lender accepts less risk because a bad approval is relatively more expensive.
The threshold is therefore not automatically 0.5. With referral available, compare
these costs with review cost plus the expected remaining decision loss after review.

## 5. Success metrics, and why

We will report the following on the fixed validation split, treating TARGET = 1
as the positive class:

- **ROC-AUC:** measures how well scores rank applicants with payment difficulties
  above those without them across thresholds. It describes overall ranking but
  does not specify the cost or precision of a lending policy.
- **PR-AUC:** this project's implementation uses average precision. It emphasizes
  how precisely the model identifies the minority default class as recall changes.
  The no-skill reference is approximately the default prevalence (about 0.08), not
  a guaranteed lower bound for every model.
- **KS:** the largest gap between the two classes' cumulative score distributions.
  It summarizes their strongest separation at a single threshold, but that
  threshold need not minimize business cost.
- **Expected cost per application:** translates the approve/refer/reject policy
  into monetary units once outcome costs are specified. Estimate it as the total default losses
  from approvals, opportunity losses from rejections, and review costs, divided
  by the number of applications. Include final decisions after review. If review
  outcomes are unavailable, report explicit scenarios rather than assume perfect
  review or claim a measured three-action cost.

Accuracy is a poor primary metric: predicting no payment difficulties for every
applicant would be about 92% accurate while identifying none of the defaults.
Ranking metrics also do not establish probability calibration, which matters for
the cost calculations, so we will inspect calibration before using probabilities
to set thresholds.

The saved baseline in `reports/metrics.json` achieves **ROC-AUC 0.710,
average precision 0.169, and KS 0.356**, evaluated on 1,000 applicants with
a positive rate of 8.1%. These results show useful ranking for an initial
baseline; they do not establish financial savings. Expected monetary cost
has not been computed because outcome costs and review outcomes are unavailable.

As provisional project targets, we propose ROC-AUC of at least 0.70, average
precision above the validation default rate, and KS of at least 0.25. These are
planning targets, not instructor requirements or measured results. Practical
usefulness additionally requires lower expected cost than the cheaper of
approve-all and reject-all, and comparison with the current policy if its outcomes
are available, while keeping referrals within capacity. We will report uncertainty
because the validation set contains only about 80 defaults. Choose policy thresholds
using training-only cross-validation and assess them on the fixed validation set;
do not repeatedly tune thresholds against its reported results.

## 6. Risks and sensitive features

Sensitive attributes present in the application table include CODE_GENDER and
DAYS_BIRTH (age, represented as days relative to the application date).
NAME_FAMILY_STATUS, CNT_CHILDREN, and CNT_FAM_MEMBERS also describe personal or
household circumstances that warrant scrutiny. These are risk-review categories,
not a claim that every field has the same legal status in every jurisdiction.

Potential proxies include NAME_EDUCATION_TYPE, OCCUPATION_TYPE, NAME_INCOME_TYPE,
AMT_INCOME_TOTAL, DAYS_EMPLOYED, REGION_POPULATION_RELATIVE,
REGION_RATING_CLIENT, REGION_RATING_CLIENT_W_CITY, NAME_HOUSING_TYPE, and the
housing-characteristic columns. EXT_SOURCE_1, EXT_SOURCE_2, and EXT_SOURCE_3 may
also carry biases from their underlying sources. Removing explicit sensitive
attributes alone cannot eliminate proxy effects.

A mistaken rejection can deny a creditworthy applicant access to needed funds;
an unnecessary referral can impose delays and extra documentation burdens. A
mistaken approval can expose the lender to losses and a borrower to unaffordable
debt. These errors could fall disproportionately on particular groups.

We propose comparing model performance with and without sensitive attributes and
examining approval rates, referrals, rejection of repayers, and approval of
defaulters across gender and age groups, with group counts and uncertainty. Small
groups cannot support strong fairness conclusions. Sensitive fields should have
restricted access for auditing, and their use in lending decisions requires an
explicit policy review. This document proposes these checks; it does not claim
they have already been performed.

## 7. Assumptions

- TARGET = 1 indicates payment difficulties, as described in the project README.
  We use it as the assignment's proxy for default; it is not a direct measurement
  of monetary loss or necessarily a complete failure to repay.
- The sampled applicants and fixed split are sufficiently representative for an
  initial baseline. Historical labeled borrowers may differ from future applicants
  or people who were previously denied credit, so generalization must be checked.
- Features and joined history are available before the decision. TARGET and
  applicant identifiers are not predictive inputs, and preprocessing is fitted
  only on training data to prevent leakage.
- For the symbolic cost comparison, we assume constant costs per outcome in a
  common monetary unit and zero incremental cost for correct decisions. These
  are simplifying assumptions, not measured facts. The available materials do
  not provide numerical costs, so we cannot select a numerical cost-optimal
  threshold or claim monetary savings.
- Probabilities must be sufficiently calibrated for cost-based decisions. Review
  has a finite cost and capacity, and its effectiveness must be measured or stated
  as a scenario. Human review remains available for uncertain applications.
- This is an offline educational baseline. No reported metric alone establishes
  readiness to make live lending decisions.

The most consequential assumption is that historical labels and relationships
represent the applicants who will actually be scored. If selection effects or a
change in the applicant population break that assumption, even good validation
ranking and low estimated costs may be misleading. We would need more representative
evaluation data and reassess calibration, thresholds, and subgroup performance
before relying on the model.
