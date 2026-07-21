from typing import Dict, Any, Optional, List, Union
import numpy as np
import pandas as pd


def audit_explainability(
    model: Any,
    feature_names: Optional[List[str]] = None,
    X_sample: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Audits model explainability, feature importance transparency, and decision interpretability.

    Args:
        model: Trained model instance (scikit-learn, XGBoost, etc.).
        feature_names: List of feature names.
        X_sample: Sample DataFrame to calculate permutation or SHAP importances.

    Returns:
        Dict containing explainability score, feature importance ranking, and warnings.
    """
    warnings = []
    importances = {}

    # Attempt tree feature importances
    if hasattr(model, "feature_importances_"):
        fi = model.feature_importances_
        names = feature_names or [f"feature_{i}" for i in range(len(fi))]
        sorted_indices = np.argsort(fi)[::-1]
        importances = {names[i]: round(float(fi[i]), 4) for i in sorted_indices}
    # Attempt linear coefficients
    elif hasattr(model, "coef_"):
        coef = np.abs(model.coef_).flatten()
        names = feature_names or [f"feature_{i}" for i in range(len(coef))]
        sorted_indices = np.argsort(coef)[::-1]
        importances = {names[i]: round(float(coef[i]), 4) for i in sorted_indices}
    else:
        warnings.append("No se pudieron extraer automáticamente las importancias de características del modelo.")

    # Check top feature dominance (risk of single feature over-reliance)
    top_feature_pct = 0.0
    if importances:
        top_feature_val = list(importances.values())[0]
        total_val = sum(importances.values())
        top_feature_pct = (top_feature_val / total_val * 100) if total_val > 0 else 0.0

        if top_feature_pct > 60.0:
            top_name = list(importances.keys())[0]
            warnings.append(f"Alta dominancia de una sola característica '{top_name}' ({top_feature_pct:.1f}% de importancia). Riesgo de sesgo por característica única.")

    # Score calculation
    score = 100.0
    if not importances:
        score -= 40
    if top_feature_pct > 60.0:
        score -= 20

    score = max(0.0, round(score, 1))
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "feature_importances": importances,
        "top_features": list(importances.keys())[:5] if importances else [],
        "has_explainability_interface": len(importances) > 0,
        "warnings": warnings,
    }
