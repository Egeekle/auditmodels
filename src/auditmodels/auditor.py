import datetime
import logging
from typing import Dict, Any, Optional, List, Union, Callable
import pandas as pd
import numpy as np

from auditmodels.errors import (
    SECTION_STATUS_ERROR,
    AuditExecutionError,
    AuditModelsError,
    errored_section,
    skipped_section,
)

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

logger = logging.getLogger(__name__)


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
        self.errors = data.get("errors", [])

    @property
    def has_errors(self) -> bool:
        """True when at least one audit phase failed and was excluded from the overall score."""
        return bool(self.errors)

    def failed_sections(self) -> List[str]:
        return [name for name, section in self.sections.items() if section.get("status") == SECTION_STATUS_ERROR]

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
        y_true: Optional[Union[list, np.ndarray]] = None,
        y_pred: Optional[Union[list, np.ndarray]] = None,
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
        user_feedback_score: Optional[float] = None,
        feature_columns: Optional[List[str]] = None,
        strict: bool = False
    ) -> AuditResult:
        """
        Executes a comprehensive audit across Data, Performance, Fairness, Robustness, Governance,
        Documentation, Training Process, Explainability, Production Drift, Security, and Privacy.

        Phases that cannot run (missing inputs) or that fail are recorded with a null score and a
        SKIPPED / ERROR status, and are excluded from the weighted overall score instead of being
        credited with a perfect one. Set strict=True to propagate any phase failure to the caller.
        """
        all_warnings: List[str] = []
        sections: Dict[str, Dict[str, Any]] = {}
        errors: List[Dict[str, str]] = []

        def register(name: str, section: Dict[str, Any]) -> Dict[str, Any]:
            sections[name] = section
            all_warnings.extend(section.get("warnings", []))
            return section

        def run_section(name: str, audit_callable: Callable[..., Dict[str, Any]], **kwargs) -> Dict[str, Any]:
            try:
                return register(name, audit_callable(**kwargs))
            except Exception as e:
                logger.exception("Audit phase '%s' failed", name)
                if strict:
                    if isinstance(e, AuditModelsError):
                        raise
                    raise AuditExecutionError(f"Audit phase '{name}' failed: {e}") from e
                errors.append({"section": name, "error_type": type(e).__name__, "error": str(e)})
                return register(name, errored_section(f"Auditoría de '{name}' no completada: {e}", e))

        # 1. Data Audit (Steps 3 & 10)
        data_res = run_section(
            "data",
            audit_data,
            df=df,
            target_column=target_column,
            sensitive_columns=[sensitive_column] if sensitive_column else None,
        )

        # 2. Performance Audit (Step 5)
        if y_true is None or y_pred is None:
            register("performance", skipped_section(
                "Performance audit skipped: ground truth (y_true) and/or predictions (y_pred) not supplied."
            ))
        else:
            run_section(
                "performance",
                audit_performance,
                y_true=y_true,
                y_pred=y_pred,
                y_prob=y_prob,
                problem_type=problem_type,
            )

        # 3. Fairness Audit (Step 6)
        if y_true is None or y_pred is None:
            register("fairness", skipped_section(
                "Fairness audit skipped: ground truth (y_true) and/or predictions (y_pred) not supplied."
            ))
        elif not (sensitive_column and sensitive_column in df.columns):
            register("fairness", skipped_section(
                "Fairness audit skipped: sensitive column not supplied or absent from the dataset."
            ))
        elif privileged_group is None or unprivileged_group is None:
            register("fairness", skipped_section(
                "Fairness audit skipped: privileged / unprivileged group parameters not supplied."
            ))
        else:
            run_section(
                "fairness",
                audit_fairness,
                df=df,
                y_true=y_true,
                y_pred=y_pred,
                sensitive_column=sensitive_column,
                privileged_group=privileged_group,
                unprivileged_group=unprivileged_group,
            )

        # Features the model actually consumes: target and sensitive attributes are excluded so
        # that stress tests and importances are not computed on columns the model never saw.
        feature_cols = feature_columns or [c for c in df.columns if c not in (target_column, sensitive_column)]
        feature_df = df[feature_cols] if feature_cols else df

        # 4. Robustness Audit (Step 7)
        if predict_fn is None:
            rob_res = register("robustness", skipped_section(
                "Robustness stress test skipped: predict_fn not supplied."
            ))
        elif y_true is None:
            rob_res = register("robustness", skipped_section(
                "Robustness stress test skipped: ground truth (y_true) not supplied."
            ))
        else:
            rob_res = run_section(
                "robustness",
                audit_robustness,
                predict_fn=predict_fn,
                X_val=feature_df,
                y_val=y_true,
                problem_type=problem_type,
            )

        # 5. Explainability Audit (Step 8)
        if model is None:
            register("explainability", skipped_section(
                "Explainability audit skipped: trained model instance not provided."
            ))
        else:
            run_section(
                "explainability",
                audit_explainability,
                model=model,
                feature_names=feature_cols,
                X_sample=feature_df,
            )

        # 6. Compliance Audit (Steps 9 & 11)
        run_section("compliance", audit_compliance, answers=compliance_answers)

        # 7. Documentation Audit (Step 2)
        run_section("documentation", audit_documentation, doc_metadata=doc_metadata)

        # 8. Training Process Audit (Step 4)
        if training_config:
            training_config["problem_type"] = problem_type
        run_section("training", audit_training, training_config=training_config)

        # 9. Production & Drift Audit (Step 12)
        run_section(
            "production",
            audit_production,
            reference_df=df,
            production_df=production_df,
            latency_ms=latency_ms,
            error_rate=error_rate,
            concept_drift_detected=concept_drift_detected,
            user_feedback_score=user_feedback_score,
        )

        # 10. Security Audit (Step 9)
        robustness_score = rob_res.get("score")
        if robustness_score is None:
            # Robustness evidence is missing: assume the neutral 100 baseline but say so.
            robustness_score = 100.0
            all_warnings.append(
                "Seguridad: La evaluación de manipulación de entradas asume robustez nominal porque la fase de robustez no produjo evidencia."
            )
        sec_res = run_section(
            "security",
            audit_security,
            security_config=security_answers,
            robustness_score=robustness_score,
        )

        # 11. Privacy Audit (Step 10)
        run_section(
            "privacy",
            audit_privacy,
            privacy_config=privacy_answers,
            flagged_pii_cols=data_res.get("pii_flagged", []),
        )

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
        scored = {
            sec: (sections[sec]["score"], weight)
            for sec, weight in weights.items()
            if isinstance(sections.get(sec, {}).get("score"), (int, float))
        }
        unscored_sections = [sec for sec in weights if sec not in scored]
        total_weight = sum(weight for _, weight in scored.values())

        if total_weight > 0:
            # Renormalize over the phases that produced evidence so that skipped or failed
            # phases neither inflate nor deflate the overall score.
            overall_score = round(sum(score * weight for score, weight in scored.values()) / total_weight, 1)
        else:
            overall_score = 0.0

        if unscored_sections:
            all_warnings.append(
                f"Puntuación global calculada sobre {len(scored)} de {len(weights)} fases: "
                f"sin evidencia para {unscored_sections}."
            )

        if total_weight == 0:
            overall_risk_level = "UNKNOWN"
        elif overall_score >= 80:
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
            "errors": errors,
            "unscored_sections": unscored_sections,
            "evaluated_weight": round(total_weight, 4),
        }

        return AuditResult(full_audit_data)
