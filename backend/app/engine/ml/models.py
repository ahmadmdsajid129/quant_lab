from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss


def train_and_evaluate_model(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    model_type: str = "GBDT",
) -> Dict[str, Any]:
    """
    Train supervised financial ML model and compute statistical & concept-drift diagnostics.
    """
    model_type = model_type.upper()
    if model_type == "RIDGE":
        clf = LogisticRegression(penalty="l2", C=1.0, random_state=42, max_iter=500)
    elif model_type == "RANDOM_FOREST":
        clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    elif model_type in ["GBDT", "HIST_GBDT"]:
        clf = HistGradientBoostingClassifier(max_iter=100, max_depth=4, random_state=42)
    else:
        raise ValueError(f"Unknown model type '{model_type}'. Available: RIDGE, RANDOM_FOREST, GBDT")

    # Fit model
    clf.fit(X_train, y_train)

    # Evaluate predictions
    preds_train = clf.predict(X_train)
    preds_test = clf.predict(X_test)
    probs_test = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else preds_test

    acc_train = float(accuracy_score(y_train, preds_train))
    acc_test = float(accuracy_score(y_test, preds_test))
    
    try:
        roc_auc = float(roc_auc_score(y_test, probs_test))
    except Exception:
        roc_auc = 0.50

    brier = float(brier_score_loss(y_test, probs_test))

    # Feature Importance extraction
    feature_importances: Dict[str, float] = {}
    if hasattr(clf, "feature_importances_"):
        fi = clf.feature_importances_
        feature_importances = {col: round(float(val), 4) for col, val in zip(X_train.columns, fi)}
    elif hasattr(clf, "coef_"):
        fi = np.abs(clf.coef_[0])
        norm_fi = fi / fi.sum() if fi.sum() > 0 else fi
        feature_importances = {col: round(float(val), 4) for col, val in zip(X_train.columns, norm_fi)}
    else:
        # Standard uniform fallback if model lacks direct importances
        feature_importances = {col: round(1.0 / len(X_train.columns), 4) for col in X_train.columns}

    # Sort feature importances descending
    feature_importances = dict(sorted(feature_importances.items(), key=lambda item: item[1], reverse=True))

    # Concept Drift Diagnostics: Kolmogorov-Smirnov 2-sample test
    drift_report: Dict[str, Any] = {}
    drifting_features_count = 0
    for col in X_train.columns:
        ks_stat, ks_pval = stats.ks_2samp(X_train[col], X_test[col])
        is_drift = bool(ks_pval < 0.05)
        if is_drift:
            drifting_features_count += 1
        drift_report[col] = {
            "ks_statistic": round(float(ks_stat), 4),
            "p_value": round(float(ks_pval), 4),
            "has_drift": is_drift,
        }

    return {
        "model_type": model_type,
        "n_train_samples": len(X_train),
        "n_test_samples": len(X_test),
        "metrics": {
            "accuracy_train": round(acc_train, 4),
            "accuracy_test": round(acc_test, 4),
            "roc_auc_test": round(roc_auc, 4),
            "brier_score": round(brier, 4),
        },
        "feature_importances": feature_importances,
        "concept_drift": {
            "drifting_features_count": drifting_features_count,
            "total_features": len(X_train.columns),
            "feature_diagnostics": drift_report,
        },
    }
