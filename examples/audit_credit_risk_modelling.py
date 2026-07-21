"""
Audit script tailored specifically for Credit Risk Modelling (Probability of Default - PD).
Evaluates Gini Coefficient, KS Statistic, Disparate Impact across Protected Attributes, 
Data Quality, Robustness, and Financial AI Governance Compliance (Basel III / NIST / EU AI Act).
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

from auditmodels import ModelAuditor


def audit_credit_risk_modelling():
    print("Running AuditModels for Credit Risk Modelling (Probability of Default - PD)...")

    # 1. Generate Realistic Synthetic Credit Risk Dataset
    np.random.seed(42)
    n_samples = 1500

    # Financial & Demographic Features
    loan_amount = np.random.exponential(scale=15000, size=n_samples) + 2000
    annual_inc = np.random.lognormal(mean=10.8, sigma=0.5, size=n_samples)
    dti = np.random.uniform(5.0, 45.0, size=n_samples)  # Debt-to-income ratio
    credit_score = np.random.normal(670, 70, size=n_samples).clip(300, 850)
    delinq_2yrs = np.random.poisson(lam=0.4, size=n_samples)
    revol_util = np.random.uniform(0.1, 0.95, size=n_samples)

    # Sensitive Demographic Attributes
    gender = np.random.choice(["Male", "Female"], size=n_samples, p=[0.51, 0.49])
    age_group = np.random.choice(["<30", "30-50", ">50"], size=n_samples, p=[0.25, 0.55, 0.20])

    df = pd.DataFrame({
        "loan_amount": loan_amount,
        "annual_inc": annual_inc,
        "dti": dti,
        "credit_score": credit_score,
        "delinq_2yrs": delinq_2yrs,
        "revol_util": revol_util,
        "gender": gender,
        "age_group": age_group,
        "ssn": [f"{np.random.randint(100,999)}-{np.random.randint(10,99)}-{np.random.randint(1000,9999)}" for _ in range(n_samples)]
    })

    # Introduce data flaws for realistic audit testing
    df.loc[np.random.choice(n_samples, 35, replace=False), "annual_inc"] = np.nan
    df = pd.concat([df, df.iloc[:15]], ignore_index=True)  # Duplicates

    # Ground Truth Default Probability (1 = Default / Bad Credit, 0 = Good Credit / Non-Default)
    default_logit = (
        - 0.00005 * df["annual_inc"].fillna(50000)
        + 0.08 * df["dti"]
        - 0.012 * df["credit_score"]
        + 0.6 * df["delinq_2yrs"]
        + 1.5 * (df["revol_util"] > 0.8).astype(int)
    )
    p_default = 1 / (1 + np.exp(-default_logit))
    y_true = (np.random.rand(len(df)) < p_default).astype(int)

    # Feature Matrix for Training
    feature_cols = ["loan_amount", "annual_inc", "dti", "credit_score", "delinq_2yrs", "revol_util"]
    X = df[feature_cols].fillna(df[feature_cols].median())

    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X, y_true, df, test_size=0.3, random_state=42, stratify=y_true
    )

    # Train Credit Risk Gradient Boosting Classifier (PD Model)
    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, random_state=42)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]  # Probability of Default
    # Cutoff threshold at 0.35 (common conservative credit risk threshold)
    y_pred = (y_prob >= 0.35).astype(int)

    # 2. Run AuditModels Framework
    auditor = ModelAuditor(model_name="Credit Risk Modelling (PD Scorecard)")

    audit_result = auditor.audit(
        df=df_test,
        y_true=y_test,
        y_pred=y_pred,
        y_prob=y_prob,
        problem_type="classification",
        target_column=None,
        sensitive_column="gender",
        privileged_group="Male",
        unprivileged_group="Female",
        model=model,
        predict_fn=model.predict,
        compliance_answers={
            "GOV-01": True,   # Basel III / Internal rating policy documented
            "DOC-01": True,   # Model scorecard documented
            "RISK-01": True,  # Stress testing performed
            "PRIV-01": True,  # Data privacy policy
            "SEC-01": True,   # Audit log access
            "EXP-01": True,   # Adverse action notice / SHAP explainability
            "MON-01": False,  # Missing real-time data drift monitoring
        },
        doc_metadata={
            "objective": "Predecir la Probabilidad de Incumplimiento (PD) a 12 meses para solicitudes de crédito personal.",
            "use_cases": "Evaluación automatizada de riesgo en plataforma de préstamos digitales.",
            "architecture": "Pipeline Scikit-Learn (Imputador Mediana + Gradient Boosting Classifier).",
            "algorithm": "GradientBoostingClassifier (n_estimators=100, learning_rate=0.08)",
            "version": "v1.4.2",
            "limitations": "Baja representatividad en solicitantes sin historial crediticio (<21 años).",
            "owners": "Equipo de Riesgos Cuantitativos y Ciencia de Datos"
        },
        training_config={
            "split_ratios": {"train": 0.70, "val": 0.0, "test": 0.30},
            "is_stratified": True,
            "hyperparameters": {"n_estimators": 100, "learning_rate": 0.08, "random_state": 42},
            "random_seed": 42,
            "reproducibility_verified": True,
            "model_version": "v1.4.2",
            "git_commit": "a8f3b29"
        },
        production_df=df_test,
        latency_ms=45.2,
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
        error_rate=0.02,
        concept_drift_detected=False,
        user_feedback_score=98.1
    )

    # 3. Export Reports
    html_path = audit_result.export_html("credit_risk_modelling_audit_report.html")
    md_path = audit_result.export_markdown("credit_risk_modelling_audit_report.md")

    print("\n=======================================================")
    print("AUDIT RESULTS FOR CREDIT RISK MODELLING")
    print(f"Overall Audit Score: {audit_result.overall_score} / 100")
    print(f"Global Risk Level:   {audit_result.overall_risk_level}")
    
    perf = audit_result.sections.get("performance", {})
    print(f"ROC-AUC:            {perf.get('roc_auc')}")
    print(f"Gini Coefficient:   {perf.get('gini_coefficient')} (2*AUC - 1)")
    print(f"KS Statistic:       {perf.get('ks_statistic')}")
    
    fairness = audit_result.sections.get("fairness", {})
    print(f"Disparate Impact:   {fairness.get('disparate_impact_ratio')} (Four-fifths rule: {fairness.get('passes_four_fifths_rule')})")
    
    print(f"Total Warnings:     {len(audit_result.all_warnings)}")
    print(f"HTML Report:        file:///{html_path.replace('\\', '/')}")
    print(f"Markdown Summary:   file:///{md_path.replace('\\', '/')}")
    print("=======================================================\n")


if __name__ == "__main__":
    audit_credit_risk_modelling()
