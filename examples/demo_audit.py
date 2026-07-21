import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from auditmodels import ModelAuditor


def run_credit_risk_audit():
    print("Running AuditModels Demo: Credit Risk Classification Model...")

    # 1. Generate Synthetic Credit Dataset
    np.random.seed(42)
    n_samples = 1000

    age = np.random.randint(18, 70, size=n_samples)
    income = np.random.normal(55000, 18000, size=n_samples)
    credit_score = np.random.normal(680, 60, size=n_samples)
    gender = np.random.choice(["Male", "Female"], size=n_samples, p=[0.52, 0.48])
    
    # Introduce missing values and duplicate rows for data audit demonstration
    df = pd.DataFrame({
        "age": age,
        "income": income,
        "credit_score": credit_score,
        "gender": gender,
        "email": [f"user_{i}@example.com" for i in range(n_samples)]  # PII column
    })
    
    # Inject missing values
    df.loc[np.random.choice(n_samples, 25, replace=False), "income"] = np.nan
    # Duplicate 10 rows
    df = pd.concat([df, df.iloc[:10]], ignore_index=True)

    # Generate Target (1 = Approved, 0 = Rejected)
    # Add artificial bias based on gender to test fairness detector
    approved = (
        (df["income"].fillna(50000) > 40000).astype(int) +
        (df["credit_score"] > 650).astype(int) +
        (df["gender"] == "Male").astype(int)
    ) >= 2
    y = approved.astype(int).values

    # Train Random Forest Model
    X_num = df[["age", "income", "credit_score"]].fillna(df[["age", "income", "credit_score"]].mean())
    X_train, X_test, y_train, y_test, df_train, df_test = train_test_split(
        X_num, y, df, test_size=0.3, random_state=42
    )

    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    # 2. Run Comprehensive Model Auditor
    auditor = ModelAuditor(model_name="Modelo de Riesgo Crediticio - Banco Demo")
    
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
        predict_fn=clf.predict,
        compliance_answers={
            "GOV-01": True,
            "DOC-01": True,
            "RISK-01": True,
            "PRIV-01": True,
            "SEC-01": False,  # Missing audit trails
            "EXP-01": True,
            "MON-01": False   # Missing concept drift monitoring
        }
    )

    # 3. Export Reports
    html_path = audit_result.export_html("credit_model_audit_report.html")
    md_path = audit_result.export_markdown("credit_model_audit_report.md")

    print("\n=======================================================")
    print(f"Puntuacion General de Auditoria: {audit_result.overall_score} / 100")
    print(f"Nivel de Riesgo Global: {audit_result.overall_risk_level}")
    print(f"Hallazgos/Alertas Totales: {len(audit_result.all_warnings)}")
    print(f"Reporte HTML Interactivo: file:///{html_path.replace('\\', '/')}")
    print(f"Resumen Markdown: file:///{md_path.replace('\\', '/')}")
    print("=======================================================\n")


if __name__ == "__main__":
    run_credit_risk_audit()
