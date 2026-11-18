# Why these applicants were declined

Model version 1, threshold 0.075: an applicant whose estimated probability of default is at or above the threshold is declined. Written by python run.py explain.

## Applicant 386641 (riskiest)

Estimated probability of default: 36.7% (threshold 7.5%). Main reasons:

1. external credit score 2 is 0.0229 (typical: 0.564) (raises the risk score by 1.10)
2. external credit score 3 is 0.229 (typical: 0.532) (raises the risk score by 0.51)
3. time in the current job is 0.5 years (typical: 4.4 years) (raises the risk score by 0.33)

## Applicant 122934 (typical decline)

Estimated probability of default: 13.3% (threshold 7.5%). Main reasons:

1. external credit score 2 is 0.344 (typical: 0.564) (raises the risk score by 0.72)
2. external credit score 3 is missing (typical: 0.532) (raises the risk score by 0.31)
3. time in the current job is 2.3 years (typical: 4.4 years) (raises the risk score by 0.25)

What lowered the risk: external credit score 1 is 0.533 (typical: 0.5).

## Applicant 270289 (borderline)

Estimated probability of default: 7.5% (threshold 7.5%). Main reasons:

1. external credit score 2 is 0.31 (typical: 0.564) (raises the risk score by 0.33)
2. external credit score 3 is 0.366 (typical: 0.532) (raises the risk score by 0.30)
3. external credit score 1 is missing (typical: 0.5) (raises the risk score by 0.18)

What lowered the risk: time in the current job is missing (typical: 4.4 years).
