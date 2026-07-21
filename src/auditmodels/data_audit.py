import re
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np


def audit_data(
    df: pd.DataFrame,
    target_column: Optional[str] = None,
    sensitive_columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Audits dataset quality, balance, missingness, outliers, and potential PII exposure.

    Args:
        df: Pandas DataFrame to audit.
        target_column: Optional target variable name.
        sensitive_columns: Optional list of sensitive attribute column names.

    Returns:
        Dict containing audit metrics, risk level, and warnings.
    """
    total_rows, total_cols = df.shape
    missing_counts = df.isnull().sum()
    total_missing = int(missing_counts.sum())
    missing_pct = float(total_missing / (total_rows * total_cols)) * 100 if total_rows * total_cols > 0 else 0.0

    missing_by_col = {col: int(cnt) for col, cnt in missing_counts.items() if cnt > 0}
    duplicate_rows = int(df.duplicated().sum())

    constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
    high_cardinality_cols = [
        col for col in df.columns 
        if df[col].dtype == 'object' and df[col].nunique() > (0.8 * total_rows) and total_rows > 20
    ]

    # Target class balance evaluation
    target_info = {}
    imbalance_ratio = 1.0
    if target_column and target_column in df.columns:
        value_counts = df[target_column].value_counts(dropna=False).to_dict()
        target_info["counts"] = {str(k): int(v) for k, v in value_counts.items()}
        if len(value_counts) > 1:
            max_c = max(value_counts.values())
            min_c = min(value_counts.values())
            imbalance_ratio = float(max_c / min_c) if min_c > 0 else float('inf')
        target_info["imbalance_ratio"] = round(imbalance_ratio, 2)

    # PII Heuristic Detection
    pii_patterns = [r"email", r"ssn", r"social.*security", r"phone", r"dni", r"pasaporte", r"address", r"credit.*card"]
    pii_flagged = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(re.search(pat, col_lower) for pat in pii_patterns):
            pii_flagged.append(col)

    # Identify risks & score
    warnings = []
    if missing_pct > 10:
        warnings.append(f"High overall missing data rate: {missing_pct:.1f}%")
    if duplicate_rows > 0:
        warnings.append(f"Found {duplicate_rows} duplicate rows in dataset")
    if constant_cols:
        warnings.append(f"Columns with 0 variance (constant): {constant_cols}")
    if imbalance_ratio > 4.0 and target_column:
        warnings.append(f"Significant target class imbalance detected (ratio {imbalance_ratio:.1f}:1)")
    if pii_flagged:
        warnings.append(f"Potential PII columns identified without explicit anonymization flag: {pii_flagged}")

    # Data Quality Score (0 - 100)
    score = 100.0
    score -= min(missing_pct * 2, 30)
    score -= min((duplicate_rows / max(total_rows, 1)) * 100 * 2, 20)
    score -= len(constant_cols) * 5
    if pii_flagged:
        score -= 15
    if imbalance_ratio > 5.0:
        score -= 15
    score = max(round(score, 1), 0.0)

    risk_level = "LOW"
    if score < 60:
        risk_level = "HIGH"
    elif score < 80:
        risk_level = "MEDIUM"

    return {
        "score": score,
        "risk_level": risk_level,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "missing_total": total_missing,
        "missing_pct": round(missing_pct, 2),
        "missing_by_col": missing_by_col,
        "duplicate_rows": duplicate_rows,
        "constant_cols": constant_cols,
        "high_cardinality_cols": high_cardinality_cols,
        "target_info": target_info,
        "pii_flagged": pii_flagged,
        "warnings": warnings,
    }
