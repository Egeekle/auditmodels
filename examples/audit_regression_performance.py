"""
Example script showing how to audit a regression model using the AuditModels framework.
Evaluates MAE, RMSE, R², data quality, and regulatory compliance.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from auditmodels import ModelAuditor


def audit_regression_model():
    print("Running AuditModels for Regression (e.g. Loan Interest Rate Prediction)...")

    # 1. Generate Synthetic Regression Dataset
    np.random.seed(42)
    n_samples = 800

    credit_score = np.random.normal(680, 50, n_samples).clip(300, 850)
    income = np.random.normal(60000, 15000, n_samples)
    loan_amount = np.random.exponential(scale=12000, size=n_samples) + 1000
    
    # Target: Interest Rate (in %)
    interest_rate = 25.0 - 0.02 * credit_score - 0.00005 * income + 0.0001 * loan_amount + np.random.normal(0, 1.2, n_samples)
    interest_rate = interest_rate.clip(4.0, 35.0)

    df = pd.DataFrame({
        "credit_score": credit_score,
        "income": income,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate
    })

    # Train a Simple Regression Model
    X = df[["credit_score", "income", "loan_amount"]]
    y = df["interest_rate"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    reg = LinearRegression()
    reg.fit(X_train, y_train)

    y_pred = reg.predict(X_test)

    # 2. Run AuditModels Performance & Data Audit
    auditor = ModelAuditor(model_name="Loan Interest Rate Predictor")
    
    audit_result = auditor.audit(
        df=X_test,
        y_true=y_test,
        y_pred=y_pred,
        problem_type="regression",
        model=reg,
        predict_fn=reg.predict,
        compliance_answers={
            "GOV-01": True,
            "DOC-01": True,
            "RISK-01": True,
            "PRIV-01": True,
            "SEC-01": True,
            "EXP-01": True,
            "MON-01": True
        },
        doc_metadata={
            "objective": "Predecir la tasa de interés óptima ajustada al riesgo del solicitante.",
            "use_cases": "Asignación dinámica de precios en la originación de préstamos.",
            "architecture": "Regresión lineal múltiple sobre variables crediticias y financieras.",
            "algorithm": "LinearRegression (Mínimos Cuadrados Ordinarios - OLS)",
            "version": "v2.1.0",
            "limitations": "Pobre desempeño en solicitantes con ingresos extremadamente atípicos (>1M USD).",
            "owners": "Mesa de Originación y Modelado Financiero"
        },
        training_config={
            "split_ratios": {"train": 0.75, "val": 0.0, "test": 0.25},
            "is_stratified": False,
            "hyperparameters": {"fit_intercept": True},
            "random_seed": 42,
            "reproducibility_verified": True,
            "model_version": "v2.1.0",
            "git_commit": "c4d2e1b"
        },
        production_df=X_test,
        security_answers={
            "has_rate_limiting": True,
            "output_precision_limited": True,
            "has_membership_defense": True,
            "is_generative": False,
            "has_access_control": True,
            "has_audit_logs": True
        },
        privacy_answers={
            "memorization_risk_checked": True,
            "has_anonymization": True,
            "retention_policy_defined": True
        },
        error_rate=0.04,
        concept_drift_detected=False,
        user_feedback_score=96.5
    )

    # 3. Export Reports
    html_path = audit_result.export_html("regression_model_audit_report.html")
    md_path = audit_result.export_markdown("regression_model_audit_report.md")

    print("\n=======================================================")
    print("REGRESSION MODEL AUDIT RESULTS")
    print(f"Overall Audit Score: {audit_result.overall_score} / 100")
    print(f"Global Risk Level:   {audit_result.overall_risk_level}")
    
    perf = audit_result.sections.get("performance", {})
    print(f"Mean Absolute Error (MAE): {perf.get('mae')}")
    print(f"Root Mean Squared Error (RMSE): {perf.get('rmse')}")
    print(f"Coefficient of Determination (R2): {perf.get('r2_score')}")
    
    print(f"HTML Report: file:///{html_path.replace('\\', '/')}")
    print(f"Markdown Summary: file:///{md_path.replace('\\', '/')}")
    print("=======================================================\n")


if __name__ == "__main__":
    audit_regression_model()
