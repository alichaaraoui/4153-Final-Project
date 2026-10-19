"""Evaluation metrics for a default-probability model.

Accuracy is misleading when only about 8 percent of applicants default, so we use
ranking metrics that look at the scores themselves.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score, roc_curve

ArrayLike = np.ndarray | list


# PROVIDED
def roc_auc(y_true: ArrayLike, y_score: ArrayLike) -> float:
    """Area under the ROC curve.

    It is the chance that a random defaulter scores above a random non-defaulter.
    """
    return float(roc_auc_score(y_true, y_score))


# PROVIDED
def pr_auc(y_true: ArrayLike, y_score: ArrayLike) -> float:
    """Area under the precision-recall curve (average precision). Its floor is the default rate."""
    return float(average_precision_score(y_true, y_score))


# TODO(Ali)
def ks_statistic(y_true: ArrayLike, y_score: ArrayLike) -> float:
    """Kolmogorov-Smirnov (KS) statistic between the scores of the two classes.

    Args:
        y_true: 0/1 labels, where 1 means the applicant defaulted.
        y_score: Model scores (higher means riskier), same length as ``y_true``.

    Returns:
        A float between 0 and 1. It is 1.0 when every defaulter scores above every
        non-defaulter, and near 0 when the scores do not separate the classes at all.

    Hints:
        - KS is the largest vertical gap between the cumulative distribution of scores
          for defaulters and the one for non-defaulters, over all possible thresholds.
        - Sketch both cumulative curves on paper for a 4-row example before coding.
        - A function you already know from ROC curves can give you both cumulative rates
          at every threshold.
        - Return a plain Python float.
    """
    # roc_curve gives, at every threshold, the share of defaulters (tpr) and of
    # non-defaulters (fpr) scoring above it. KS is the largest gap between the two.
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(tpr - fpr))


# TODO(Ali)
def evaluate(y_true: ArrayLike, y_score: ArrayLike) -> dict[str, float]:
    """Compute every validation metric we report.

    Args:
        y_true: 0/1 labels.
        y_score: Model scores, same length as ``y_true``.

    Returns:
        ``{"roc_auc": ..., "pr_auc": ..., "ks": ...}`` with plain Python floats.

    Hints:
        - The three metric functions in this module already exist (one of them is yours).
        - These exact key names are read by other code and by the check script.
    """
    return {
        "roc_auc": roc_auc(y_true, y_score),
        "pr_auc": pr_auc(y_true, y_score),
        "ks": ks_statistic(y_true, y_score),
    }
