from typing import Dict, Any, Optional, List


REQUIRED_DOCUMENTATION_FIELDS = {
    "objective": "Objetivo del modelo (qué problema resuelve y metas de negocio)",
    "use_cases": "Casos de uso autorizados y contexto de despliegue",
    "architecture": "Arquitectura del sistema (pipeline de datos, preprocesamiento, modelo)",
    "algorithm": "Algoritmos utilizados (ej. Gradient Boosting, Regresión Logística, Neural Net)",
    "version": "Versión del modelo (ej. v1.2.0 o hash de commit git)",
    "limitations": "Limitaciones conocidas y casos bordes no cubiertos",
    "owners": "Responsables del desarrollo, mantenimiento y gobernanza"
}


def audit_documentation(doc_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Audits the presence and completeness of AI model documentation metadata.

    Args:
        doc_metadata: Dict containing documentation fields.

    Returns:
        Dict containing documentation score (0-100), risk level, missing fields, and warnings.
    """
    doc_metadata = doc_metadata or {}
    missing_fields = []
    present_fields = []
    warnings = []

    for field_key, field_desc in REQUIRED_DOCUMENTATION_FIELDS.items():
        val = doc_metadata.get(field_key)
        if not val or (isinstance(val, str) and len(val.strip()) < 5):
            missing_fields.append(field_key)
            warnings.append(f"Falta documentación sobre: {field_desc}")
        else:
            present_fields.append(field_key)

    total_required = len(REQUIRED_DOCUMENTATION_FIELDS)
    passed_count = len(present_fields)
    score = round((passed_count / total_required) * 100, 1)

    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "passed_count": passed_count,
        "total_required": total_required,
        "present_fields": present_fields,
        "missing_fields": missing_fields,
        "documentation_metadata": doc_metadata,
        "warnings": warnings,
    }
