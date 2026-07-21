"""
AuditModels: Framework y Dashboard de Auditoría Integral para Modelos de IA.
"""

from auditmodels.auditor import ModelAuditor, AuditResult
from auditmodels.data_audit import audit_data
from auditmodels.performance_audit import audit_performance
from auditmodels.fairness_audit import audit_fairness
from auditmodels.robustness_audit import audit_robustness
from auditmodels.compliance_audit import audit_compliance
from auditmodels.documentation_audit import audit_documentation
from auditmodels.training_audit import audit_training
from auditmodels.explainability_audit import audit_explainability
from auditmodels.production_audit import audit_production
from auditmodels.security_audit import audit_security
from auditmodels.privacy_audit import audit_privacy
from auditmodels.reporting import generate_html_report, generate_markdown_report

__version__ = "0.1.0"

__all__ = [
    "ModelAuditor",
    "AuditResult",
    "audit_data",
    "audit_performance",
    "audit_fairness",
    "audit_robustness",
    "audit_compliance",
    "audit_documentation",
    "audit_training",
    "audit_explainability",
    "audit_production",
    "audit_security",
    "audit_privacy",
    "generate_html_report",
    "generate_markdown_report",
]
