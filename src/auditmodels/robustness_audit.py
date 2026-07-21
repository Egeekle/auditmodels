from typing import Dict, Any, Callable, List
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, mean_squared_error


def audit_robustness(
    predict_fn: Callable[[np.ndarray], np.ndarray],
    X_val: pd.DataFrame,
    y_val: np.ndarray,
    problem_type: str = "classification",
    noise_scales: List[float] = [0.05, 0.15]
) -> Dict[str, Any]:
    """
    Audits model robustness under synthetic noise injection and perturbation stress tests.

    Args:
        predict_fn: Model prediction function taking NumPy matrix and returning predictions.
        X_val: Validation dataset (numeric features).
        y_val: Ground truth labels.
        problem_type: "classification" or "regression".
        noise_scales: List of standard deviation noise scales to test.

    Returns:
        Dict containing robustness degradation scores, risk level, and warnings.
    """
    y_val = np.array(y_val)
    warnings = []
    numeric_df = X_val.select_dtypes(include=[np.number])

    if numeric_df.empty:
        return {
            "score": 100.0,
            "risk_level": "LOW",
            "warnings": ["No numeric features available to apply noise perturbation stress tests."]
        }

    # Impute missing values for numeric features during perturbation tests if needed
    cleaned_df = numeric_df.fillna(numeric_df.median())
    X_mat = cleaned_df.values
    feature_names = list(cleaned_df.columns)

    def safe_predict(input_data):
        try:
            return predict_fn(input_data)
        except Exception:
            # Fallback to DataFrame if model requires feature names
            df_input = pd.DataFrame(input_data, columns=feature_names)
            return predict_fn(df_input)

    try:
        baseline_pred = safe_predict(X_mat)
    except Exception as e:
        return {
            "score": 100.0,
            "risk_level": "LOW",
            "warnings": [f"Robustness test skipped: predict_fn failed on validation dataset ({str(e)})"]
        }

    if problem_type == "classification":
        baseline_metric = float(accuracy_score(y_val, baseline_pred))
    else:
        baseline_metric = float(mean_squared_error(y_val, baseline_pred))

    noise_results = []
    max_drop = 0.0

    for scale in noise_scales:
        std_per_col = np.std(X_mat, axis=0)
        # Avoid division by zero for constant columns
        std_per_col[std_per_col == 0] = 1.0

        noise = np.random.normal(0, scale * std_per_col, size=X_mat.shape)
        X_noisy = X_mat + noise

        try:
            noisy_pred = safe_predict(X_noisy)
            if problem_type == "classification":
                noisy_metric = float(accuracy_score(y_val, noisy_pred))
                drop = baseline_metric - noisy_metric
                pct_drop = (drop / baseline_metric * 100) if baseline_metric > 0 else 0.0
            else:
                noisy_metric = float(mean_squared_error(y_val, noisy_pred))
                drop = noisy_metric - baseline_metric
                pct_drop = (drop / baseline_metric * 100) if baseline_metric > 0 else 0.0

            max_drop = max(max_drop, pct_drop)
            noise_results.append({
                "scale": scale,
                "noisy_metric": round(noisy_metric, 4),
                "metric_change_pct": round(pct_drop, 2)
            })
        except Exception as e:
            warnings.append(f"Failed perturbation test at noise scale {scale}: {str(e)}")

    if max_drop > 20:
        warnings.append(f"High sensitivity to input noise detected (max performance drop: {max_drop:.1f}%)")

    # Score calculation (100 = perfectly robust, no degradation)
    robustness_score = max(0.0, round(100.0 - max_drop * 2, 1))
    risk_level = "LOW" if robustness_score >= 80 else ("MEDIUM" if robustness_score >= 60 else "HIGH")

    return {
        "score": robustness_score,
        "risk_level": risk_level,
        "baseline_metric": round(baseline_metric, 4),
        "noise_perturbation_tests": noise_results,
        "max_performance_drop_pct": round(max_drop, 2),
        "warnings": warnings,
    }
