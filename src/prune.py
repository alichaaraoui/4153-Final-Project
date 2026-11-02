"""How few features does the final model need?

Run it with ``python run.py prune`` (or ``python -m src.prune``). Fewer features mean a smaller
model, a faster answer, and less to explain and to collect for every applicant.

Features are ranked by permutation importance: shuffle one column on rows the model never saw
and measure how much the AUC drops. Everything happens on the TRAIN split. In
``auc_by_feature_count`` the ranking is repeated inside each fold, because features ranked with
the rows that score them would make the short lists look better than they are.

It prints the features to copy into ``features:`` in config/final.yaml and writes
reports/prune.json.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

from src.experiment import load_training_data, load_week3_config
from src.models import make_model
from src.tune import model_spec
from src.utils import DEFAULT_CONFIG

PRUNE_FILE = "reports/prune.json"
INNER_FOLDS = 3     # folds for the ranking repeated inside each outer fold
N_REPEATS = 3       # shuffles per feature


def rank_features(
    model: Pipeline, X: pd.DataFrame, y: pd.Series, n_folds: int, seed: int
) -> pd.Series:
    """Every feature's mean drop in held-out AUC when it is shuffled, largest first.

    Args:
        model: An unfitted Pipeline that uses every column of ``X``. It is not changed.
        X: Feature rows (the TRAIN split only).
        y: Labels aligned with ``X``.
        n_folds: Number of stratified folds.
        seed: Seed for the folds and the shuffles.

    Returns:
        A Series from feature name to importance, sorted from most to least important.
    """
    folds = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
    drops = []
    for train_idx, test_idx in folds.split(X, y):
        fitted = clone(model).fit(X.iloc[train_idx], y.iloc[train_idx])
        result = permutation_importance(fitted, X.iloc[test_idx], y.iloc[test_idx],
                                        scoring="roc_auc", n_repeats=N_REPEATS,
                                        random_state=seed)
        drops.append(result.importances_mean)
    importance = pd.Series(np.mean(drops, axis=0), index=X.columns)
    return importance.sort_values(ascending=False, kind="stable")


def auc_by_feature_count(
    spec: dict[str, Any], X: pd.DataFrame, y: pd.Series, numeric: list[str],
    categorical: list[str], counts: list[int], config: dict[str, Any],
) -> pd.DataFrame:
    """CV AUC of the model on its top ``k`` features, for each ``k`` in ``counts``.

    Each outer fold ranks the features on its own training rows only, so the rows that score a
    short list had no part in choosing it.

    Args:
        spec: The model spec.
        X: Feature rows (the TRAIN split only).
        y: Labels aligned with ``X``.
        numeric: The numeric columns of ``X``.
        categorical: The categorical columns of ``X``.
        counts: How many features to try.
        config: The loaded Week 3 config.

    Returns:
        One row per count: ``n_features``, ``cv_auc_mean``, ``cv_auc_std``.
    """
    seed = config["seed"]
    folds = StratifiedKFold(n_splits=config["week3"]["cv_folds"], shuffle=True, random_state=seed)
    aucs: dict[int, list[float]] = {k: [] for k in counts}
    for train_idx, test_idx in folds.split(X, y):
        X_fit, y_fit = X.iloc[train_idx], y.iloc[train_idx]
        X_test, y_test = X.iloc[test_idx], y.iloc[test_idx]
        ranking = rank_features(make_model(spec, numeric, categorical, config), X_fit, y_fit,
                                INNER_FOLDS, seed)
        for k in counts:
            keep = set(ranking.index[:k])
            columns = [c for c in X.columns if c in keep]
            model = make_model(spec, [c for c in numeric if c in keep],
                               [c for c in categorical if c in keep], config)
            scores = model.fit(X_fit[columns], y_fit).predict_proba(X_test[columns])[:, 1]
            aucs[k].append(float(roc_auc_score(y_test, scores)))
    return pd.DataFrame([{"n_features": k, "cv_auc_mean": float(np.mean(aucs[k])),
                          "cv_auc_std": float(np.std(aucs[k]))} for k in counts])


def smallest_within_noise(curve: pd.DataFrame) -> int:
    """The fewest features whose CV AUC is within one std of the best count's CV AUC."""
    best = curve.loc[curve["cv_auc_mean"].idxmax()]
    close = curve[curve["cv_auc_mean"] >= best["cv_auc_mean"] - best["cv_auc_std"]]
    return int(close["n_features"].min())


def run_prune(config: dict[str, Any]) -> dict[str, Any]:
    """Rank the features, score each count, and write reports/prune.json."""
    seed, folds = config["seed"], config["week3"]["cv_folds"]
    spec = model_spec(config)
    data = load_training_data(config)
    counts = sorted({k for k in config["week3"]["final"]["prune_counts"]
                     if k < len(data.features)} | {len(data.features)})
    model = make_model(spec, data.numeric, data.categorical, config)
    curve = auc_by_feature_count(spec, data.X_train, data.y_train, data.numeric, data.categorical,
                                 counts, config)
    ranking = rank_features(model, data.X_train, data.y_train, folds, seed)
    suggested = smallest_within_noise(curve)
    record = {
        "chosen_on": "train cross-validation, ranked inside each fold",
        "suggested_count": suggested,
        "suggested_features": list(ranking.index[:suggested]),
        "curve": curve.to_dict(orient="records"),
        "importance": {name: float(value) for name, value in ranking.items()},
    }
    path = config["root"] / PRUNE_FILE
    path.write_text(json.dumps(record, indent=2) + "\n")
    return record


def main() -> None:
    """Command-line entry point: ``python -m src.prune``."""
    parser = argparse.ArgumentParser(description="Rank the features and score shorter lists.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="path to config.yaml")
    args = parser.parse_args()
    config = load_week3_config(args.config)
    record = run_prune(config)
    print(f"{'features':>8}{'CV AUC':>10}{'std':>8}")
    for row in record["curve"]:
        print(f"{row['n_features']:>8}{row['cv_auc_mean']:>10.4f}{row['cv_auc_std']:>8.4f}")
    print(f"\nFewest features within one std of the best: {record['suggested_count']}")
    print("features: " + json.dumps(record["suggested_features"]))
    print(f"\nWrote {PRUNE_FILE}")


if __name__ == "__main__":
    main()
