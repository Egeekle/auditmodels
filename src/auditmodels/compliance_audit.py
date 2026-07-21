from typing import Dict, Any, Optional, List


DEFAULT_COMPLIANCE_CHECKLIST = [
    {
        "id": "GOV-01",
        "framework": "ISO/IEC 42001",
        "question": "Is there a documented AI governance policy and designated responsible roles?",
        "default": True,
    },
    {
        "id": "DOC-01",
        "framework": "ISO/IEC 42001",
        "question": "Are training data sources, model architecture, and version history fully documented?",
        "default": True,
    },
    {
        "id": "RISK-01",
        "framework": "NIST AI RMF",
        "question": "Has a risk management assessment been conducted for high-impact edge cases?",
        "default": True,
    },
    {
        "id": "PRIV-01",
        "framework": "EU AI Act",
        "question": "Are personal data processing policies compliant with local data privacy regulations (e.g. GDPR/LGPD)?",
        "default": True,
    },
    {
        "id": "SEC-01",
        "framework": "NIST AI RMF",
        "question": "Are access control logs and audit trails maintained for model inference and training data?",
        "default": False,
    },
    {
        "id": "EXP-01",
        "framework": "EU AI Act",
        "question": "Can the model output be explained to end-users or affected individuals upon request?",
        "default": True,
    },
    {
        "id": "MON-01",
        "framework": "ISO/IEC 42001",
        "question": "Is continuous monitoring established for data drift and concept drift in production?",
        "default": False,
    },
]


def audit_compliance(
    answers: Optional[Dict[str, bool]] = None
) -> Dict[str, Any]:
    """
    Audits model regulatory and governance compliance (NIST AI RMF, ISO/IEC 42001, EU AI Act).

    Args:
        answers: Dict mapping item IDs (e.g. 'GOV-01') to True/False responses.

    Returns:
        Dict containing compliance score, status by framework, and missing requirements.
    """
    answers = answers or {}
    total_items = len(DEFAULT_COMPLIANCE_CHECKLIST)
    passed_items = 0
    checklist_results = []
    warnings = []

    framework_scores = {}

    for item in DEFAULT_COMPLIANCE_CHECKLIST:
        item_id = item["id"]
        fw = item["framework"]
        is_compliant = answers.get(item_id, item["default"])

        if fw not in framework_scores:
            framework_scores[fw] = {"passed": 0, "total": 0}
        framework_scores[fw]["total"] += 1

        if is_compliant:
            passed_items += 1
            framework_scores[fw]["passed"] += 1
        else:
            warnings.append(f"Non-compliant item [{item_id}] ({fw}): {item['question']}")

        checklist_results.append({
            "id": item_id,
            "framework": fw,
            "question": item["question"],
            "status": "PASSED" if is_compliant else "FAILED"
        })

    score = round((passed_items / total_items) * 100, 1) if total_items > 0 else 100.0
    risk_level = "LOW" if score >= 80 else ("MEDIUM" if score >= 60 else "HIGH")

    return {
        "score": score,
        "risk_level": risk_level,
        "passed_count": passed_items,
        "total_count": total_items,
        "framework_breakdown": {
            fw: round((vals["passed"] / vals["total"]) * 100, 1)
            for fw, vals in framework_scores.items()
        },
        "checklist": checklist_results,
        "warnings": warnings,
    }
