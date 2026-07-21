from typing import Dict, Any, Optional
import numpy as np
import pandas as pd


def calculate_psi(reference: np.ndarray, current: np.ndarray, num_buckets: int = 10) -> float:
    """
    Calculates the Population Stability Index (PSI) to measure data drift between reference and production data.
    PSI < 0.1: No significant shift
    0.1 <= PSI < 0.25: Moderate shift / warning
    PSI >= 0.25: Significant shift / action required
    """
    reference = reference[~np.isnan(reference)]
    current = current[~np.isnan(current)]
    
    if len(reference) == 0 or len(current) == 0:
        return 0.0

    percentiles = np.linspace(0, 100, num_buckets + 1)
    buckets = np.percentile(reference, percentiles)
    buckets[0] -= 1e-5
    buckets[-1] += 1e-5

    ref_counts, _ = np.histogram(reference, bins=buckets)
    curr_counts, _ = np.histogram(current, bins=buckets)

    ref_pct = ref_counts / len(reference)
    curr_pct = curr_counts / len(current)

    # Avoid zero division
    ref_pct = np.where(ref_pct == 0, 0.0001, ref_pct)
    curr_pct = np.where(curr_pct == 0, 0.0001, curr_pct)

    psi_val = np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct))
    return float(psi_val)


def audit_production(
    reference_df: pd.DataFrame,
    production_df: Optional[pd.DataFrame] = None,
    latency_ms: Optional[float] = None,
    error_rate: Optional[float] = None,
    concept_drift_detected: bool = False,
    user_feedback_score: Optional[float] = None
) -> Dict[str, Any]:
    """
    Audits production performance, data drift (PSI), concept drift, latencies, errors,
    and user feedback.

    Args:
        reference_df: Training / baseline reference dataset.
        production_df: Production dataset to check for data drift.
        latency_ms: Average model inference response time in milliseconds.
        error_rate: Request error rate in production (in %).
        concept_drift_detected: True if concept drift has been triggered statistically.
        user_feedback_score: Average user score/rating (0 to 100).

    Returns:
        Dict containing production audit score, drift metrics, and warnings.
    """
    warnings = []
    drift_by_column = {}

    if production_df is not None:
        numeric_cols = reference_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in production_df.columns:
                ref_vals = reference_df[col].values
                prod_vals = production_df[col].values
                psi = calculate_psi(ref_vals, prod_vals)
                drift_status = "STABLE" if psi < 0.1 else ("MODERATE_DRIFT" if psi < 0.25 else "SEVERE_DRIFT")
                drift_by_column[col] = {
                    "psi": round(psi, 4),
                    "status": drift_status
                }
                if drift_status == "SEVERE_DRIFT":
                    warnings.append(f"Deriva de Datos (Data Drift): Deriva severa detectada en la característica '{col}' (PSI={psi:.3f}).")

    if concept_drift_detected:
        warnings.append("Deriva de Concepto (Concept Drift): Se ha detectado una degradación estadística en el rendimiento del modelo en producción.")

    if latency_ms is not None and latency_ms > 200.0:
        warnings.append(f"Tiempo de Respuesta: Latencia elevada de inferencia en producción ({latency_ms:.1f}ms > 200ms).")

    if error_rate is not None and error_rate > 1.0:
        warnings.append(f"Tasa de Errores: Tasa de peticiones fallidas elevada en producción ({error_rate:.2f}% > 1.0%).")

    if user_feedback_score is not None and user_feedback_score < 80.0:
        warnings.append(f"Retroalimentación: Puntuación de satisfacción del usuario baja ({user_feedback_score:.1f}% < 80.0%).")

    score = 100.0
    severe_drift_count = sum(1 for v in drift_by_column.values() if v["status"] == "SEVERE_DRIFT")
    score -= severe_drift_count * 20
    if concept_drift_detected: score -= 25
    if latency_ms and latency_ms > 200: score -= 10
    if error_rate and error_rate > 1.0: score -= 15
    if user_feedback_score and user_feedback_score < 80.0: score -= 10

    score = max(0.0, round(score, 1))
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "drift_by_column": drift_by_column,
        "severe_drift_columns": [k for k, v in drift_by_column.items() if v["status"] == "SEVERE_DRIFT"],
        "concept_drift_detected": concept_drift_detected,
        "latency_ms": latency_ms,
        "error_rate_pct": error_rate,
        "user_feedback_score_pct": user_feedback_score,
        "warnings": warnings,
    }
