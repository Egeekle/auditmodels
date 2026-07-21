from typing import Dict, Any, Union, Optional
import numpy as np
import pandas as pd


def audit_fairness(
    df: pd.DataFrame,
    y_true: Union[list, np.ndarray],
    y_pred: Union[list, np.ndarray],
    sensitive_column: str,
    privileged_group: Any,
    unprivileged_group: Any,
    pos_label: Union[int, str] = 1
) -> Dict[str, Any]:
    """
    Audits model fairness across sensitive demographic attributes.

    Calculates Demographic Parity, Equal Opportunity, Equalized Odds, and Disparate Impact.

    Args:
        df: DataFrame containing the sensitive attribute.
        y_true: Ground truth binary labels.
        y_pred: Predicted binary labels.
        sensitive_column: Name of sensitive column in df (e.g., 'gender', 'race').
        privileged_group: Value representing the privileged group (e.g., 'Male', 'White').
        unprivileged_group: Value representing the unprivileged group (e.g., 'Female').
        pos_label: Positive output value (e.g., 1 for credit approval).

    Returns:
        Dict containing fairness metrics, equity score (0-100), risk level, and warnings.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    sensitive_attr = df[sensitive_column].values

    priv_mask = (sensitive_attr == privileged_group)
    unpriv_mask = (sensitive_attr == unprivileged_group)

    warnings = []

    if priv_mask.sum() == 0 or unpriv_mask.sum() == 0:
        return {
            "score": 0.0,
            "risk_level": "CRITICAL",
            "warnings": [f"Sensitive group mask empty for '{sensitive_column}'. Privileged count: {priv_mask.sum()}, Unprivileged count: {unpriv_mask.sum()}"]
        }

    # Selection rates (P(y_pred = pos_label))
    rate_priv = float(np.mean(y_pred[priv_mask] == pos_label))
    rate_unpriv = float(np.mean(y_pred[unpriv_mask] == pos_label))

    # Disparate Impact Ratio = rate_unpriv / rate_priv
    disparate_impact = rate_unpriv / rate_priv if rate_priv > 0 else 0.0
    demographic_parity_diff = rate_unpriv - rate_priv

    # True Positive Rate (TPR) / Recall per group
    tp_priv = np.sum((y_pred[priv_mask] == pos_label) & (y_true[priv_mask] == pos_label))
    pos_true_priv = np.sum(y_true[priv_mask] == pos_label)
    tpr_priv = float(tp_priv / pos_true_priv) if pos_true_priv > 0 else 0.0

    tp_unpriv = np.sum((y_pred[unpriv_mask] == pos_label) & (y_true[unpriv_mask] == pos_label))
    pos_true_unpriv = np.sum(y_true[unpriv_mask] == pos_label)
    tpr_unpriv = float(tp_unpriv / pos_true_unpriv) if pos_true_unpriv > 0 else 0.0

    equal_opportunity_diff = tpr_unpriv - tpr_priv

    # False Positive Rate (FPR) per group
    fp_priv = np.sum((y_pred[priv_mask] == pos_label) & (y_true[priv_mask] != pos_label))
    neg_true_priv = np.sum(y_true[priv_mask] != pos_label)
    fpr_priv = float(fp_priv / neg_true_priv) if neg_true_priv > 0 else 0.0

    fp_unpriv = np.sum((y_pred[unpriv_mask] == pos_label) & (y_true[unpriv_mask] != pos_label))
    neg_true_unpriv = np.sum(y_true[unpriv_mask] != pos_label)
    fpr_unpriv = float(fp_unpriv / neg_true_unpriv) if neg_true_unpriv > 0 else 0.0

    equalized_odds_diff = max(abs(tpr_unpriv - tpr_priv), abs(fpr_unpriv - fpr_priv))

    # Evaluate 80% Rule (EEOC four-fifths rule for Disparate Impact)
    passes_80_rule = 0.8 <= disparate_impact <= 1.25

    if not passes_80_rule:
        warnings.append(
            f"Fails 80% rule for Disparate Impact ({disparate_impact:.3f}). "
            f"Selection rate for '{unprivileged_group}' ({rate_unpriv:.1%}) vs '{privileged_group}' ({rate_priv:.1%})."
        )
    if abs(equal_opportunity_diff) > 0.1:
        warnings.append(
            f"Significant Equal Opportunity Difference ({equal_opportunity_diff:+.3f}). "
            f"TPR for unprivileged: {tpr_unpriv:.3f}, privileged: {tpr_priv:.3f}."
        )

    # Score calculation (100 = perfect equity)
    di_penalty = min(abs(1.0 - disparate_impact) * 50, 40)
    eq_opp_penalty = abs(equal_opportunity_diff) * 40
    score = max(0.0, round(100.0 - di_penalty - eq_opp_penalty, 1))

    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "sensitive_column": sensitive_column,
        "privileged_group": str(privileged_group),
        "unprivileged_group": str(unprivileged_group),
        "selection_rate_privileged": round(rate_priv, 4),
        "selection_rate_unprivileged": round(rate_unpriv, 4),
        "disparate_impact_ratio": round(disparate_impact, 4),
        "demographic_parity_diff": round(demographic_parity_diff, 4),
        "equal_opportunity_diff": round(equal_opportunity_diff, 4),
        "equalized_odds_diff": round(equalized_odds_diff, 4),
        "passes_four_fifths_rule": passes_80_rule,
        "tpr_privileged": round(tpr_priv, 4),
        "tpr_unprivileged": round(tpr_unpriv, 4),
        "fpr_privileged": round(fpr_priv, 4),
        "fpr_unprivileged": round(fpr_unpriv, 4),
        "warnings": warnings,
    }
