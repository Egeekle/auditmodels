from typing import Dict, Any, Optional, List


def audit_privacy(
    privacy_config: Optional[Dict[str, Any]] = None,
    flagged_pii_cols: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Audits model training and inference data privacy controls, PII exposure, memorization risk,
    anonymization techniques, and data retention compliance.

    Args:
        privacy_config: Dict containing privacy self-assessment parameters.
        flagged_pii_cols: List of PII columns flagged by data_audit.

    Returns:
        Dict containing privacy audit score, risk level, and warnings.
    """
    config = privacy_config or {}
    flagged_pii_cols = flagged_pii_cols or []
    warnings = []

    # 1. Protection of Personal Data & PII Exposure
    if flagged_pii_cols:
        warnings.append(f"Protección de Datos: Columnas con PII potencial expuestas en texto plano: {flagged_pii_cols}")

    # 2. Risk of Memorizing Sensitive Info (Overfitting / Memorization Index)
    memorization_risk_checked = config.get("memorization_risk_checked", False)
    if not memorization_risk_checked:
        warnings.append("Memorización de Datos: No se han realizado pruebas de ataque de inferencia de membresía (membership inference) para evaluar memorización de datos de entrenamiento.")

    # 3. Anonymization Techniques
    has_anonymization = config.get("has_anonymization", False)
    if not has_anonymization and flagged_pii_cols:
        warnings.append("Técnicas de Anonimización: Se identificaron columnas PII pero no hay hashing, enmascaramiento o tokenización activa en el pipeline.")

    # 4. Data Retention Policies
    retention_policy_defined = config.get("retention_policy_defined", False)
    if not retention_policy_defined:
        warnings.append("Políticas de Retención: No existe una política definida de expiración o purga de datos históricos de consultas e inferencias.")

    # Score calculation (100 base)
    score = 100.0
    if flagged_pii_cols: score -= 20
    if not memorization_risk_checked: score -= 15
    if not has_anonymization and flagged_pii_cols: score -= 20
    if not retention_policy_defined: score -= 15

    score = max(0.0, round(score, 1))
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "pii_detected": flagged_pii_cols,
        "memorization_risk_mitigated": memorization_risk_checked,
        "anonymization_active": has_anonymization,
        "retention_policy_active": retention_policy_defined,
        "warnings": warnings,
    }
