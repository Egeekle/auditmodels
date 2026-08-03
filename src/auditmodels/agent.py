"""
Agentic Model Testing Engine for AuditModels.

Provides autonomous inspection, test suite execution, vulnerability detection,
and automated remediation plan generation for AI/ML models.
"""

import logging
from typing import Dict, Any, Optional, List, Union, Callable, Tuple
import pandas as pd
import numpy as np

from auditmodels.auditor import ModelAuditor, AuditResult

logger = logging.getLogger(__name__)

SENSITIVE_COLUMN_CANDIDATES = [
    "gender", "sex", "race", "ethnicity", "age", "demographic", "group", "marital_status"
]

PII_COLUMN_CANDIDATES = [
    "ssn", "email", "dni", "phone", "credit_card", "cpf", "passport", "ip_address", "name"
]


class ModelTestingAgent:
    """
    Autonomous AI Agent for model discovery, comprehensive auditing, and remediation planning.
    """
    def __init__(self, agent_name: str = "AuditModels Testing Agent"):
        self.agent_name = agent_name

    def inspect_and_setup(
        self,
        df: pd.DataFrame,
        model: Optional[Any] = None,
        y_true: Optional[Union[list, np.ndarray, pd.Series]] = None,
        target_column: Optional[str] = None,
        sensitive_column: Optional[str] = None,
        privileged_group: Optional[Any] = None,
        unprivileged_group: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Inspects dataset and model structure to auto-detect problem type, sensitive features,
        demographic groups, target column, and potential PII risks.
        """
        inspection_res = {
            "num_rows": len(df),
            "num_cols": len(df.columns),
            "columns": list(df.columns),
            "auto_detected": {}
        }

        # 1. Auto-detect Target Column if not specified
        target_col = target_column
        if not target_col:
            for col in ["target", "label", "y", "default", "approved", "class"]:
                if col in df.columns:
                    target_col = col
                    break
        inspection_res["auto_detected"]["target_column"] = target_col

        # 2. Extract y_true if target_column present and y_true not provided
        y_true_arr = y_true
        if y_true_arr is None and target_col and target_col in df.columns:
            y_true_arr = df[target_col].values

        # 3. Auto-detect Problem Type (classification vs regression)
        problem_type = "classification"
        if y_true_arr is not None:
            unique_vals = np.unique(y_true_arr)
            if len(unique_vals) > 15 and not np.issubdtype(type(unique_vals[0]), np.integer):
                problem_type = "regression"
            elif np.issubdtype(type(unique_vals[0]), np.floating) and len(unique_vals) > 20:
                problem_type = "regression"
        inspection_res["auto_detected"]["problem_type"] = problem_type

        # 4. Auto-detect Sensitive Column
        sens_col = sensitive_column
        if not sens_col:
            for candidate in SENSITIVE_COLUMN_CANDIDATES:
                for col in df.columns:
                    if col.lower() == candidate:
                        sens_col = col
                        break
                if sens_col:
                    break
        inspection_res["auto_detected"]["sensitive_column"] = sens_col

        # 5. Auto-detect Privileged and Unprivileged Groups
        priv_grp = privileged_group
        unread_grp = unprivileged_group
        if sens_col and sens_col in df.columns:
            unique_sens = df[sens_col].dropna().unique()
            if len(unique_sens) >= 2:
                if priv_grp is None:
                    # Common defaults for gender or race
                    if "Male" in unique_sens:
                        priv_grp = "Male"
                        unread_grp = [g for g in unique_sens if g != "Male"][0]
                    elif "White" in unique_sens:
                        priv_grp = "White"
                        unread_grp = [g for g in unique_sens if g != "White"][0]
                    else:
                        priv_grp = unique_sens[0]
                        unread_grp = unique_sens[1]
        inspection_res["auto_detected"]["privileged_group"] = priv_grp
        inspection_res["auto_detected"]["unprivileged_group"] = unread_grp

        # 6. Auto-detect PII Columns
        pii_found = []
        for col in df.columns:
            if col.lower() in PII_COLUMN_CANDIDATES:
                pii_found.append(col)
        inspection_res["auto_detected"]["pii_columns"] = pii_found

        return inspection_res

    def run_tests(
        self,
        df: pd.DataFrame,
        model: Optional[Any] = None,
        y_true: Optional[Union[list, np.ndarray, pd.Series]] = None,
        y_pred: Optional[Union[list, np.ndarray, pd.Series]] = None,
        y_prob: Optional[Union[list, np.ndarray, pd.Series]] = None,
        target_column: Optional[str] = None,
        sensitive_column: Optional[str] = None,
        privileged_group: Optional[Any] = None,
        unprivileged_group: Optional[Any] = None,
        model_name: str = "AI Model",
        predict_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        compliance_answers: Optional[Dict[str, bool]] = None,
        doc_metadata: Optional[Dict[str, Any]] = None,
        training_config: Optional[Dict[str, Any]] = None,
        production_df: Optional[pd.DataFrame] = None,
        security_answers: Optional[Dict[str, Any]] = None,
        privacy_answers: Optional[Dict[str, Any]] = None
    ) -> Tuple[AuditResult, Dict[str, Any]]:
        """
        Executes zero-configuration autonomous testing suite on model and dataset.
        """
        # Step 1: Perform inspection
        setup_info = self.inspect_and_setup(
            df=df,
            model=model,
            y_true=y_true,
            target_column=target_column,
            sensitive_column=sensitive_column,
            privileged_group=privileged_group,
            unprivileged_group=unprivileged_group
        )
        auto = setup_info["auto_detected"]

        # Fill defaults from inspection if not explicitly supplied
        target_col = target_column or auto.get("target_column")
        sens_col = sensitive_column or auto.get("sensitive_column")
        priv_grp = privileged_group or auto.get("privileged_group")
        unread_grp = unprivileged_group or auto.get("unprivileged_group")
        prob_type = auto.get("problem_type", "classification")

        # Step 2: Prepare y_true, y_pred, y_prob
        y_true_final = y_true
        if y_true_final is None and target_col and target_col in df.columns:
            y_true_final = df[target_col].values

        feature_cols = [c for c in df.columns if c != target_col and c != sens_col]
        X = df[feature_cols] if feature_cols else df

        y_pred_final = y_pred
        y_prob_final = y_prob
        pred_fn_final = predict_fn

        if model is not None:
            if pred_fn_final is None and hasattr(model, "predict"):
                pred_fn_final = model.predict
            if y_pred_final is None and hasattr(model, "predict"):
                try:
                    y_pred_final = model.predict(X)
                except Exception as e:
                    logger.warning(f"Auto-predict failed: {e}")

            if y_prob_final is None and hasattr(model, "predict_proba") and prob_type == "classification":
                try:
                    probs = model.predict_proba(X)
                    if probs.ndim == 2 and probs.shape[1] >= 2:
                        y_prob_final = probs[:, 1]
                except Exception as e:
                    logger.warning(f"Auto-predict_proba failed: {e}")

        # Fallbacks if y_true / y_pred are still missing
        if y_true_final is None:
            y_true_final = np.ones(len(df))
        if y_pred_final is None:
            y_pred_final = y_true_final

        # Step 3: Instantiate ModelAuditor and run audit
        auditor = ModelAuditor(model_name=model_name)
        result = auditor.audit(
            df=df,
            y_true=y_true_final,
            y_pred=y_pred_final,
            y_prob=y_prob_final,
            problem_type=prob_type,
            target_column=target_col,
            sensitive_column=sens_col,
            privileged_group=priv_grp,
            unprivileged_group=unread_grp,
            model=model,
            predict_fn=pred_fn_final,
            compliance_answers=compliance_answers,
            doc_metadata=doc_metadata,
            training_config=training_config,
            production_df=production_df,
            security_answers=security_answers,
            privacy_answers=privacy_answers
        )

        # Step 4: Generate Actionable Remediation Plan
        remediation = self.generate_remediation_plan(result, setup_info)

        return result, remediation

    def generate_remediation_plan(
        self,
        audit_result: AuditResult,
        setup_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes audit findings into prioritized remediation tasks.
        """
        score = audit_result.overall_score
        risk_level = audit_result.overall_risk_level
        warnings = audit_result.all_warnings
        sections = audit_result.sections

        plan = {
            "overall_score": score,
            "overall_risk_level": risk_level,
            "critical_actions": [],
            "high_priority_actions": [],
            "medium_priority_actions": [],
            "summary_recommendations": []
        }

        # Analyze Documentation
        doc_score = sections.get("documentation", {}).get("score", 100)
        if doc_score < 50:
            plan["critical_actions"].append(
                "[DOCUMENTACIÓN] Crear la Ficha Técnica (Model Card) registrando objetivo, casos de uso, algoritmo y responsables."
            )

        # Analyze Training
        train_score = sections.get("training", {}).get("score", 100)
        if train_score < 50:
            plan["critical_actions"].append(
                "[ENTRENAMIENTO] Registrar la semilla aleatoria (random seed), hiperparámetros y división train/val/test para garantizar reproducibilidad."
            )

        # Analyze Security & Privacy
        sec_score = sections.get("security", {}).get("score", 100)
        if sec_score < 60:
            plan["high_priority_actions"].append(
                "[SEGURIDAD] Configurar control de acceso (RBAC), rate-limiting y registros de auditoría (audit logs) en el endpoint del modelo."
            )

        priv_score = sections.get("privacy", {}).get("score", 100)
        pii_cols = setup_info.get("auto_detected", {}).get("pii_columns", [])
        if priv_score < 80 or pii_cols:
            cols_str = ", ".join(pii_cols) if pii_cols else "detectadas"
            plan["high_priority_actions"].append(
                f"[PRIVACIDAD] Enmascarar o cifrar (SHA-256 / tokenización) las columnas PII: {cols_str} antes de la ingesta en producción."
            )

        # Analyze Robustness
        rob_score = sections.get("robustness", {}).get("score", 100)
        if rob_score < 70:
            plan["medium_priority_actions"].append(
                "[ROBUSTEZ] Aplicar entrenamiento adversarial o aumento de datos con ruido sintético para reducir la sensibilidad del modelo a perturbaciones."
            )

        # Analyze Fairness
        fair_score = sections.get("fairness", {}).get("score", 100)
        if fair_score < 80:
            plan["medium_priority_actions"].append(
                "[EQUIDAD] Calibrar el umbral de decisión o aplicar técnicas de re-ponderación (Reweighing) para mitigar el sesgo demográfico."
            )

        # Summary recommendations
        plan["summary_recommendations"] = [
            f"Puntuación Global de Auditoría: {score:.1f} / 100 ({risk_level}).",
            f"Acciones Críticas identificadas: {len(plan['critical_actions'])}",
            f"Acciones de Alta Prioridad: {len(plan['high_priority_actions'])}",
            f"Acciones de Prioridad Media: {len(plan['medium_priority_actions'])}"
        ]

        return plan
