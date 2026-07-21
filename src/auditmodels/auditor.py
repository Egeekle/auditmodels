import datetime
from typing import Dict, Any, Optional, List, Union, Callable
import pandas as pd
import numpy as np

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


class AuditResult:
    """
    Encapsulates the complete results of an AI model audit across all 13 methodology steps.
    """
    def __init__(self, data: Dict[str, Any]):
        self.raw_data = data
        self.overall_score = data.get("overall_score", 0.0)
        self.overall_risk_level = data.get("overall_risk_level", "UNKNOWN")
        self.all_warnings = data.get("all_warnings", [])
        self.sections = data.get("sections", {})

    def to_dict(self) -> Dict[str, Any]:
        return self.raw_data

    def export_html(self, output_path: str = "audit_report.html") -> str:
        return generate_html_report(self.raw_data, output_path)

    def export_markdown(self, output_path: str = "audit_report.md") -> str:
        return generate_markdown_report(self.raw_data, output_path)


class ModelAuditor:
    """
    Orchestrates full or modular audits for AI & ML models.
    """
    def __init__(self, model_name: str = "AI Model"):
        self.model_name = model_name

    def audit(
        self,
        df: pd.DataFrame,
        y_true: Union[list, np.ndarray],
        y_pred: Union[list, np.ndarray],
        y_prob: Optional[Union[list, np.ndarray]] = None,
        problem_type: str = "classification",
        target_column: Optional[str] = None,
        sensitive_column: Optional[str] = None,
        privileged_group: Optional[Any] = None,
        unprivileged_group: Optional[Any] = None,
        model: Optional[Any] = None,
        predict_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        compliance_answers: Optional[Dict[str, bool]] = None,
        doc_metadata: Optional[Dict[str, Any]] = None,
        training_config: Optional[Dict[str, Any]] = None,
        production_df: Optional[pd.DataFrame] = None,
        latency_ms: Optional[float] = None,
        security_answers: Optional[Dict[str, Any]] = None,
        privacy_answers: Optional[Dict[str, Any]] = None,
        error_rate: Optional[float] = None,
        concept_drift_detected: bool = False,
        user_feedback_score: Optional[float] = None
    ) -> AuditResult:
        """
        Executes a comprehensive audit across Data, Performance, Fairness, Robustness, Governance,
        Documentation, Training Process, Explainability, Production Drift, Security, and Privacy.
        """
        all_warnings = []
        sections = {}

        # 1. Data Audit (Steps 3 & 10)
        data_res = audit_data(df, target_column=target_column, sensitive_columns=[sensitive_column] if sensitive_column else None)
        sections["data"] = data_res
        all_warnings.extend(data_res.get("warnings", []))

        # 2. Performance Audit (Step 5)
        perf_res = audit_performance(y_true=y_true, y_pred=y_pred, y_prob=y_prob, problem_type=problem_type)
        sections["performance"] = perf_res
        all_warnings.extend(perf_res.get("warnings", []))

        # 3. Fairness Audit (Step 6)
        if sensitive_column and sensitive_column in df.columns and privileged_group is not None and unprivileged_group is not None:
            fair_res = audit_fairness(
                df=df,
                y_true=y_true,
                y_pred=y_pred,
                sensitive_column=sensitive_column,
                privileged_group=privileged_group,
                unprivileged_group=unprivileged_group
            )
            sections["fairness"] = fair_res
            all_warnings.extend(fair_res.get("warnings", []))
        else:
            sections["fairness"] = {
                "score": 100.0,
                "risk_level": "LOW",
                "warnings": ["Fairness audit skipped: sensitive column or group parameters not supplied."]
            }

        # 4. Robustness Audit (Step 7)
        if predict_fn is not None:
            rob_res = audit_robustness(predict_fn=predict_fn, X_val=df, y_val=y_true, problem_type=problem_type)
            sections["robustness"] = rob_res
            all_warnings.extend(rob_res.get("warnings", []))
        else:
            rob_res = {
                "score": 100.0,
                "risk_level": "LOW",
                "warnings": ["Robustness stress test skipped: predict_fn not supplied."]
            }
            sections["robustness"] = rob_res

        # 5. Explainability Audit (Step 8)
        if model is not None:
            feature_cols = [c for c in df.columns if c != target_column and c != sensitive_column]
            exp_res = audit_explainability(model=model, feature_names=feature_cols, X_sample=df)
            sections["explainability"] = exp_res
            all_warnings.extend(exp_res.get("warnings", []))
        else:
            sections["explainability"] = {
                "score": 100.0,
                "risk_level": "LOW",
                "warnings": ["Explainability audit skipped: trained model instance not provided."]
            }

        # 6. Compliance Audit (Steps 9 & 11)
        comp_res = audit_compliance(answers=compliance_answers)
        sections["compliance"] = comp_res
        all_warnings.extend(comp_res.get("warnings", []))

        # 7. Documentation Audit (Step 2)
        doc_res = audit_documentation(doc_metadata=doc_metadata)
        sections["documentation"] = doc_res
        all_warnings.extend(doc_res.get("warnings", []))

        # 8. Training Process Audit (Step 4)
        if training_config:
            training_config["problem_type"] = problem_type
        train_res = audit_training(training_config=training_config)
        sections["training"] = train_res
        all_warnings.extend(train_res.get("warnings", []))

        # 9. Production & Drift Audit (Step 12)
        prod_res = audit_production(
            reference_df=df,
            production_df=production_df,
            latency_ms=latency_ms,
            error_rate=error_rate,
            concept_drift_detected=concept_drift_detected,
            user_feedback_score=user_feedback_score
        )
        sections["production"] = prod_res
        all_warnings.extend(prod_res.get("warnings", []))

        # 10. Security Audit (Step 9)
        sec_res = audit_security(security_config=security_answers, robustness_score=rob_res.get("score", 100.0))
        sections["security"] = sec_res
        all_warnings.extend(sec_res.get("warnings", []))

        # 11. Privacy Audit (Step 10)
        priv_res = audit_privacy(privacy_config=privacy_answers, flagged_pii_cols=data_res.get("pii_flagged", []))
        sections["privacy"] = priv_res
        all_warnings.extend(priv_res.get("warnings", []))

        # Overall Weighted Score Calculation
        weights = {
            "data": 0.10,
            "performance": 0.15,
            "fairness": 0.10,
            "robustness": 0.10,
            "security": 0.10,
            "privacy": 0.15,
            "explainability": 0.10,
            "compliance": 0.10,
            "documentation": 0.05,
            "training": 0.05,
            "production": 0.05,
        }
        overall_score = sum(sections[sec].get("score", 0) * weight for sec, weight in weights.items())
        overall_score = round(overall_score, 1)

        if overall_score >= 80:
            overall_risk_level = "LOW"
        elif overall_score >= 60:
            overall_risk_level = "MEDIUM"
        elif overall_score >= 40:
            overall_risk_level = "HIGH"
        else:
            overall_risk_level = "CRITICAL"

        full_audit_data = {
            "overall_score": overall_score,
            "overall_risk_level": overall_risk_level,
            "metadata": {
                "model_name": self.model_name,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "all_warnings": all_warnings,
            "sections": sections,
        }

        return AuditResult(full_audit_data)
