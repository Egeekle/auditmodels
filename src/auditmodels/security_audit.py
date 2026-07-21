from typing import Dict, Any, Optional


def audit_security(
    security_config: Optional[Dict[str, Any]] = None,
    robustness_score: float = 100.0
) -> Dict[str, Any]:
    """
    Audits model security across common vulnerabilities: model extraction, inversion,
    prompt injection (generative), input manipulation, access control, and audit logging.

    Args:
        security_config: Dict containing security self-assessment answers.
        robustness_score: Robustness score from robustness_audit to estimate input manipulation risk.

    Returns:
        Dict containing security audit score (0-100), risk level, and warnings.
    """
    config = security_config or {}
    warnings = []

    # 1. Model Extraction Risk
    # High risk if query rate limiting is disabled or precision of output probabilities is unlimited
    has_rate_limiting = config.get("has_rate_limiting", False)
    output_precision_limited = config.get("output_precision_limited", False)
    
    if not has_rate_limiting:
        warnings.append("Riesgo de Extracción de Modelo: No se detectó limitación de peticiones (rate limiting) en las APIs de inferencia.")
    if not output_precision_limited:
        warnings.append("Riesgo de Extracción de Modelo: El API devuelve probabilidades con alta precisión, facilitando la copia del modelo.")

    # 2. Model Inversion Risk
    # High risk if training data reconstruction is possible and no membership inference defense exists
    has_membership_defense = config.get("has_membership_defense", False)
    if not has_membership_defense:
        warnings.append("Riesgo de Inversión de Modelo: No hay defensas activas de inferencia de membresía (ej. privacidad diferencial o ruido en outputs).")

    # 3. Prompt Injection Risk (For Generative Models)
    is_generative = config.get("is_generative", False)
    has_prompt_sanitization = config.get("has_prompt_sanitization", False)
    if is_generative and not has_prompt_sanitization:
        warnings.append("Inyección de Prompts: El modelo generativo carece de capas de sanitización y validación de entradas de usuario.")

    # 4. Input Manipulation
    if robustness_score < 70.0:
        warnings.append(f"Manipulación de Entradas: El modelo tiene baja tolerancia a perturbaciones (Robustez={robustness_score:.1f}%), vulnerable a ataques adversariales sencillos.")

    # 5. Access Control & Audit Trail
    has_access_control = config.get("has_access_control", False)
    has_audit_logs = config.get("has_audit_logs", False)

    if not has_access_control:
        warnings.append("Control de Acceso: El entorno de despliegue no tiene autenticación / RBAC configurado para el acceso al modelo.")
    if not has_audit_logs:
        warnings.append("Registro de Auditoría: No hay registros inmutables (audit trails) que logueen las consultas e inferencias del modelo.")

    # Score calculation (100 base)
    score = 100.0
    if not has_rate_limiting: score -= 15
    if not output_precision_limited: score -= 10
    if not has_membership_defense: score -= 10
    if is_generative and not has_prompt_sanitization: score -= 20
    if robustness_score < 70.0: score -= 15
    if not has_access_control: score -= 15
    if not has_audit_logs: score -= 15

    score = max(0.0, round(score, 1))
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "extraction_risk": "HIGH" if not has_rate_limiting else "LOW",
        "inversion_risk": "HIGH" if not has_membership_defense else "LOW",
        "prompt_injection_risk": "HIGH" if (is_generative and not has_prompt_sanitization) else "LOW",
        "input_manipulation_risk": "HIGH" if robustness_score < 70.0 else "LOW",
        "access_control": "ENABLED" if has_access_control else "DISABLED",
        "audit_logs": "ENABLED" if has_audit_logs else "DISABLED",
        "warnings": warnings,
    }
