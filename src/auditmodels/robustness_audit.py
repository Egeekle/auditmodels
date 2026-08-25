import logging
from typing import Dict, Any, Callable, List
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, mean_squared_error

from auditmodels.errors import (
    SECTION_STATUS_OK,
    AuditConfigurationError,
    AuditExecutionError,
    errored_section,
    skipped_section,
)

logger = logging.getLogger(__name__)


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
    if problem_type not in ("classification", "regression"):
        raise AuditConfigurationError(f"Unsupported problem_type: {problem_type}")

    y_val = np.array(y_val)
    warnings = []
    numeric_df = X_val.select_dtypes(include=[np.number])

    if numeric_df.empty:
        return skipped_section("No numeric features available to apply noise perturbation stress tests.")

    # Impute missing values for numeric features during perturbation tests if needed
    cleaned_df = numeric_df.fillna(numeric_df.median())
    X_mat = cleaned_df.values
    feature_names = list(cleaned_df.columns)

    def safe_predict(input_data):
        try:
            return predict_fn(input_data)
        except Exception as matrix_error:
            # Fallback to DataFrame if the model requires feature names
            logger.debug("predict_fn rejected a NumPy matrix, retrying with a DataFrame", exc_info=True)
            df_input = pd.DataFrame(input_data, columns=feature_names)
            try:
                return predict_fn(df_input)
            except Exception as frame_error:
                raise AuditExecutionError(
                    f"predict_fn failed on both NumPy matrix ({matrix_error}) and DataFrame input ({frame_error})"
                ) from frame_error

    try:
        baseline_pred = safe_predict(X_mat)
    except AuditExecutionError as e:
        logger.exception("Robustness baseline prediction failed")
        return errored_section(f"Robustness test could not run: {e}", e)

    if problem_type == "classification":
        baseline_metric = float(accuracy_score(y_val, baseline_pred))
    else:
        baseline_metric = float(mean_squared_error(y_val, baseline_pred))

    noise_results = []
    failed_scales = []
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
            logger.exception("Perturbation test failed at noise scale %s", scale)
            failed_scales.append(scale)
            warnings.append(f"Failed perturbation test at noise scale {scale}: {str(e)}")

    if failed_scales and not noise_results:
        section = errored_section(
            f"Robustness test could not run: every perturbation test failed (noise scales {failed_scales})."
        )
        section["warnings"].extend(warnings)
        return section

    if failed_scales:
        warnings.append(
            f"Robustness score computed on partial evidence: {len(failed_scales)} of "
            f"{len(noise_scales)} perturbation tests failed."
        )

    if max_drop > 20:
        warnings.append(f"High sensitivity to input noise detected (max performance drop: {max_drop:.1f}%)")

    # Score calculation (100 = perfectly robust, no degradation)
    robustness_score = max(0.0, round(100.0 - max_drop * 2, 1))
    risk_level = "LOW" if robustness_score >= 80 else ("MEDIUM" if robustness_score >= 60 else "HIGH")

    return {
        "score": robustness_score,
        "status": SECTION_STATUS_OK,
        "risk_level": risk_level,
        "failed_noise_scales": failed_scales,
        "baseline_metric": round(baseline_metric, 4),
        "noise_perturbation_tests": noise_results,
        "max_performance_drop_pct": round(max_drop, 2),
        "warnings": warnings,
    }
