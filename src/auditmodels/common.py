"""
Shared utilities used across the auditmodels audit modules.

Centralizes the scoring and risk-classification logic that was previously
duplicated in every ``*_audit`` module so thresholds live in a single place.
"""

from typing import Dict, List, Tuple

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

# Score thresholds shared by every audit dimension.
RISK_THRESHOLD_LOW = 80.0
RISK_THRESHOLD_MEDIUM = 60.0
RISK_THRESHOLD_HIGH = 40.0


def normalize_score(score: float, ndigits: int = 1) -> float:
    """
    Clamps a raw score to the [0, 100] domain and rounds it.

    Args:
        score: Raw computed score.
        ndigits: Number of decimals to round to.

    Returns:
        Rounded score, never below 0.0.
    """
    return max(0.0, round(float(score), ndigits))


def classify_risk_level(score: float) -> str:
    """
    Maps a 0-100 score to a three-level risk band (LOW / MEDIUM / HIGH).

    Used by the individual audit dimensions.
    """
    if score >= RISK_THRESHOLD_LOW:
        return RISK_LOW
    if score >= RISK_THRESHOLD_MEDIUM:
        return RISK_MEDIUM
    return RISK_HIGH


def classify_overall_risk_level(score: float) -> str:
    """
    Maps a 0-100 score to a four-level risk band including CRITICAL.

    Used for the aggregated overall audit score.
    """
    if score >= RISK_THRESHOLD_LOW:
        return RISK_LOW
    if score >= RISK_THRESHOLD_MEDIUM:
        return RISK_MEDIUM
    if score >= RISK_THRESHOLD_HIGH:
        return RISK_HIGH
    return RISK_CRITICAL


def build_recommendations(sections: Dict) -> Tuple[List[str], List[str]]:
    """
    Derives audit recommendations and a remediation plan from audit sections.

    Shared by the HTML and Markdown report generators so the remediation logic
    stays consistent across output formats.

    Args:
        sections: Mapping of audit dimension name to its result dict.

    Returns:
        Tuple of (recommendations, remediation_steps).
    """
    data_res = sections.get("data", {})
    fair_res = sections.get("fairness", {})
    rob_res = sections.get("robustness", {})
    comp_res = sections.get("compliance", {})
    priv_res = sections.get("privacy", {})

    recs: List[str] = []
    remediation_steps: List[str] = []

    if data_res.get("duplicate_rows", 0) > 0:
        recs.append("Limpiar duplicados y registros inconsistentes en los pipelines de ETL.")
        remediation_steps.append("ETL/Data Prep: Agregar deduplicación estricta y llaves primarias únicas.")
    if priv_res.get("pii_detected"):
        recs.append(f"Cifrar/Enmascarar columnas PII detectadas: {priv_res.get('pii_detected')}.")
        remediation_steps.append("Seguridad/Privacidad: Implementar hashing SHA-256 o tokenización en variables de identificación personal.")
    if abs(fair_res.get("equal_opportunity_diff", 0.0)) > 0.10 or not fair_res.get("passes_four_fifths_rule", True):
        recs.append("Mitigar el sesgo detectado en el modelo mediante re-ponderación de muestras (Reweighing) o post-procesamiento de umbral.")
        remediation_steps.append("Modelado/Fairness: Calibrar umbrales de decisión específicos por grupo para cumplir la regla del 80%.")
    if rob_res.get("score", 100.0) < 80.0:
        recs.append("Aumentar la robustez del modelo contra ruidos de entrada y anomalías.")
        remediation_steps.append("Modelado: Implementar entrenamiento adversarial o inyección de ruido sintético en el dataset de entrenamiento.")
    if not comp_res.get("framework_breakdown", {}).get("ISO/IEC 42001") or comp_res.get("score", 100.0) < 80.0:
        recs.append("Establecer un marco formal de gobierno de IA con roles definidos.")
        remediation_steps.append("Cumplimiento: Redactar la política de gobernanza y control de acceso del modelo conforme a ISO 42001.")

    if not recs:
        recs.append("Mantener el monitoreo continuo establecido de deriva y rendimiento predictivo.")
        remediation_steps.append("Operaciones/MLOps: Ejecutar re-evaluaciones automáticas de drift mensualmente.")

    return recs, remediation_steps
