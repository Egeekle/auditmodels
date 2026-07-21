from typing import Dict, Any, Optional, Union
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def audit_performance(
    y_true: Union[list, np.ndarray],
    y_pred: Union[list, np.ndarray],
    y_prob: Optional[Union[list, np.ndarray]] = None,
    problem_type: str = "classification",
    pos_label: Union[int, str] = 1
) -> Dict[str, Any]:
    """
    Audits model predictive performance for classification or regression tasks.

    Args:
        y_true: Ground truth target values.
        y_pred: Predicted target values.
        y_prob: Predicted probabilities (optional, classification only).
        problem_type: "classification" or "regression".
        pos_label: Positive class label for binary classification.

    Returns:
        Dict containing performance metrics, score (0-100), risk level, and warnings.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    warnings = []

    if problem_type == "classification":
        acc = float(accuracy_score(y_true, y_pred))
        
        # Check binary vs multiclass
        unique_labels = np.unique(y_true)
        is_binary = len(unique_labels) <= 2
        
        average = "binary" if is_binary else "weighted"
        prec = float(precision_score(y_true, y_pred, average=average, zero_division=0))
        rec = float(recall_score(y_true, y_pred, average=average, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, average=average, zero_division=0))
        
        auc = None
        gini = None
        ks_stat = None
        if y_prob is not None:
            try:
                y_prob = np.array(y_prob)
                if is_binary and y_prob.ndim == 2:
                    y_prob = y_prob[:, 1]
                auc = float(roc_auc_score(y_true, y_prob, multi_class="ovr" if not is_binary else "raise"))
                
                # Credit Risk metrics: Gini = 2*AUC - 1
                if is_binary:
                    gini = float(2 * auc - 1)
                    # KS Statistic = max(TPR - FPR)
                    from sklearn.metrics import roc_curve
                    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
                    ks_stat = float(np.max(tpr - fpr))
            except Exception as e:
                warnings.append(f"Could not compute ROC-AUC / Gini / KS: {str(e)}")

        cm = confusion_matrix(y_true, y_pred).tolist()

        if f1 < 0.6:
            warnings.append(f"Low F1-Score detected ({f1:.3f})")
        if prec < 0.5:
            warnings.append(f"Low Precision detected ({prec:.3f})")
        if rec < 0.5:
            warnings.append(f"Low Recall detected ({rec:.3f})")
        if gini is not None and gini < 0.40:
            warnings.append(f"Low Gini coefficient for credit risk modelling ({gini:.3f} < 0.40 threshold)")
        if ks_stat is not None and ks_stat < 0.30:
            warnings.append(f"Low KS statistic for credit risk modelling ({ks_stat:.3f} < 0.30 threshold)")

        score = round((auc * 100 if auc is not None else f1 * 100), 1)
        risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

        return {
            "problem_type": "classification",
            "score": score,
            "risk_level": risk_level,
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4) if auc is not None else None,
            "gini_coefficient": round(gini, 4) if gini is not None else None,
            "ks_statistic": round(ks_stat, 4) if ks_stat is not None else None,
            "confusion_matrix": cm,
            "warnings": warnings,
        }

    elif problem_type == "regression":
        mae = float(mean_absolute_error(y_true, y_pred))
        mse = float(mean_squared_error(y_true, y_pred))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_true, y_pred))

        if r2 < 0.5:
            warnings.append(f"Low R² coefficient of determination ({r2:.3f})")
        if r2 < 0.0:
            warnings.append("Model performs worse than horizontal mean baseline (negative R²)")

        # Score based on R2 mapped to 0-100
        score = max(0.0, min(100.0, round(r2 * 100, 1)))
        risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

        return {
            "problem_type": "regression",
            "score": score,
            "risk_level": risk_level,
            "mae": round(mae, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "r2_score": round(r2, 4),
            "warnings": warnings,
        }
    else:
        raise ValueError(f"Unsupported problem_type: {problem_type}")
