import sys
import os
sys.path.insert(0, os.path.abspath("."))

# Direct execution of audit tests

# We can modify the return of those functions in scratch or extract audit_result by re-running audit(...)
# Let's import ModelAuditor and run each example's exact flow to return the AuditResult object!

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from auditmodels import ModelAuditor

weights = {
    "data": 0.10, "performance": 0.15, "fairness": 0.10, "robustness": 0.10,
    "security": 0.10, "privacy": 0.15, "explainability": 0.10, "compliance": 0.10,
    "documentation": 0.05, "training": 0.05, "production": 0.05,
}

def print_audit_report(name, audit_result):
    print(f"\n==========================================================================================================")
    print(f"RESULTADOS DE LA PRUEBA: {name.upper()}")
    print(f"Puntuación Global (Overall Score): {audit_result.overall_score} / 100")
    print(f"Nivel de Riesgo Global:            {audit_result.overall_risk_level}")
    print("==========================================================================================================")
    print(f"{'Dimensión / Módulo':<22} | {'Score':<6} | {'Nivel Riesgo':<12} | {'Peso':<5} | {'Contribución':<12} | {'Valores de Métricas / Alertas'}")
    print("-" * 110)
    
    total_calc = 0.0
    for k, w in weights.items():
        sec = audit_result.sections.get(k, {})
        sc = sec.get("score", 0.0)
        rl = sec.get("risk_level", "N/A")
        contrib = round(sc * w, 2)
        total_calc += contrib
        
        # Details
        metrics = []
        if k == "data":
            metrics.append(f"Faltantes={sec.get('missing_pct')}%")
            metrics.append(f"Duplicados={sec.get('duplicate_rows')}")
            if sec.get('pii_flagged'): metrics.append(f"PII={sec.get('pii_flagged')}")
        elif k == "performance":
            if sec.get("problem_type") == "classification":
                metrics.append(f"ROC-AUC={sec.get('roc_auc')}")
                metrics.append(f"Gini={sec.get('gini_coefficient')}")
                metrics.append(f"KS={sec.get('ks_statistic')}")
                metrics.append(f"F1={sec.get('f1_score')}")
                metrics.append(f"Accuracy={sec.get('accuracy')}")
            else:
                metrics.append(f"R²={sec.get('r2_score')}")
                metrics.append(f"MAE={sec.get('mae')}")
                metrics.append(f"RMSE={sec.get('rmse')}")
        elif k == "fairness":
            if sec.get("sensitive_column"):
                metrics.append(f"Disparate Impact={sec.get('disparate_impact_ratio')}")
                metrics.append(f"Equal Opp Diff={sec.get('equal_opportunity_diff')}")
                metrics.append(f"Regla 80%={sec.get('passes_four_fifths_rule')}")
            else:
                metrics.append("Skipped (Sin variable sensible)")
        elif k == "robustness":
            metrics.append(f"Caída máx por ruido={sec.get('max_performance_drop_pct')}%")
        elif k == "explainability":
            top_feats = sec.get("top_features", [])
            metrics.append(f"Top Features={top_feats[:3]}")
        elif k == "security":
            metrics.append(f"Extracción={sec.get('extraction_risk')}")
            metrics.append(f"Audit Logs={sec.get('audit_logs')}")
        elif k == "privacy":
            metrics.append(f"PII={sec.get('pii_detected')}")
            metrics.append(f"Anonimización={sec.get('anonymization_active')}")
        elif k == "compliance":
            metrics.append(f"Aprobados={sec.get('passed_count')}/{sec.get('total_count')} ítems")
        elif k == "documentation":
            metrics.append(f"Model Card={sec.get('passed_count')}/{sec.get('total_required')} campos")
        elif k == "training":
            metrics.append(f"Split={sec.get('split_ratios')}")
            metrics.append(f"Seed={sec.get('random_seed')}")
        elif k == "production":
            metrics.append(f"Latencia={sec.get('latency_ms')}ms")
            metrics.append(f"Drift cols={sec.get('severe_drift_columns')}")

        warn_count = len(sec.get("warnings", []))
        if warn_count > 0:
            metrics.append(f"({warn_count} advertencias)")

        details_str = ", ".join(metrics)
        print(f"{k:<22} | {sc:>6.1f} | {rl:<12} | {w*100:>4.0f}% | {contrib:>6.2f} pts    | {details_str}")
    
    print("-" * 110)
    print(f"SUMA PONDERADA: {round(total_calc, 1)} pts / 100.0  ==> OVERALL SCORE CALCULADO: {audit_result.overall_score}\n")

# --- EXECUTE PRUEBA 1: CREDIT RISK ---
def run_p1():
    np.random.seed(42)
    n_samples = 1500
    loan_amount = np.random.exponential(scale=15000, size=n_samples) + 2000
    annual_inc = np.random.lognormal(mean=10.8, sigma=0.5, size=n_samples)
    dti = np.random.uniform(5.0, 45.0, size=n_samples)
    credit_score = np.random.normal(670, 70, size=n_samples).clip(300, 850)
    delinq_2yrs = np.random.poisson(lam=0.4, size=n_samples)
    revol_util = np.random.uniform(0.1, 0.95, size=n_samples)
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
        "ssn": [f"999-{i:02d}-{i:04d}" for i in range(n_samples)]
    })

    null_idx = np.random.choice(df.index, size=45, replace=False)
    df.loc[null_idx, "annual_inc"] = np.nan
    dups = df.iloc[:15].copy()
    df = pd.concat([df, dups], ignore_index=True)

    z = (
        -0.008 * (df["credit_score"].fillna(670) - 670)
        + 0.05 * (df["dti"] - 20)
        + 0.4 * df["delinq_2yrs"]
        + 1.5 * (df["revol_util"] - 0.5)
        - 0.00002 * (df["annual_inc"].fillna(50000) - 50000)
    )
    prob_default = 1 / (1 + np.exp(-z))
    df["default"] = (prob_default > 0.65).astype(int)

    feature_cols = ["loan_amount", "annual_inc", "dti", "credit_score", "delinq_2yrs", "revol_util"]
    df_clean = df.dropna(subset=["annual_inc"]).copy()
    X = df_clean[feature_cols]
    y = df_clean["default"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    df_test = df_clean.loc[X_test.index].copy()

    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    auditor = ModelAuditor(model_name="Modelo de Riesgo Crediticio (PD Scorecard)")
    return auditor.audit(
        df=df_test,
        y_true=y_test,
        y_pred=y_pred,
        y_prob=y_prob,
        problem_type="classification",
        target_column="default",
        sensitive_column="gender",
        privileged_group="Male",
        unprivileged_group="Female",
        model=model,
        predict_fn=model.predict,
        compliance_answers={
            "GOV-01": True, "DOC-01": True, "RISK-01": True, "PRIV-01": True, "SEC-01": True, "EXP-01": True, "MON-01": True
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
            "has_rate_limiting": True, "output_precision_limited": True, "has_membership_defense": True,
            "is_generative": False, "has_access_control": True, "has_audit_logs": True
        },
        privacy_answers={
            "memorization_risk_checked": True, "has_anonymization": True, "retention_policy_defined": True
        },
        error_rate=0.02,
        concept_drift_detected=False,
        user_feedback_score=98.1
    )

# --- EXECUTE PRUEBA 2: REGRESSION ---
def run_p2():
    np.random.seed(42)
    n_samples = 1200
    credit_score = np.random.normal(680, 60, n_samples).clip(300, 850)
    income = np.random.lognormal(mean=10.9, sigma=0.4, size=n_samples)
    loan_amount = np.random.uniform(2000, 40000, n_samples)
    dti = np.random.uniform(8.0, 40.0, n_samples)

    interest_rate = (
        22.0
        - 0.018 * (credit_score - 300)
        - 0.00002 * (income - 20000)
        + 0.00015 * loan_amount
        + 0.05 * dti
        + np.random.normal(0, 1.1, n_samples)
    ).clip(5.0, 36.0)

    df = pd.DataFrame({
        "credit_score": credit_score,
        "income": income,
        "loan_amount": loan_amount,
        "dti": dti,
        "interest_rate": interest_rate
    })

    X = df[["credit_score", "income", "loan_amount", "dti"]]
    y = df["interest_rate"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    df_test = df.loc[X_test.index].copy()

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    auditor = ModelAuditor(model_name="Modelo de Predicción de Tasa de Interés")
    return auditor.audit(
        df=df_test,
        y_true=y_test,
        y_pred=y_pred,
        problem_type="regression",
        target_column="interest_rate",
        model=model,
        predict_fn=model.predict,
        compliance_answers={
            "GOV-01": True, "DOC-01": True, "RISK-01": True, "PRIV-01": True, "SEC-01": True, "EXP-01": True, "MON-01": True
        },
        doc_metadata={
            "objective": "Predecir la tasa de interés óptima basada en el perfil de riesgo crediticio.",
            "use_cases": "Fijación automatizada de precio (risk-based pricing) en solicitudes de préstamo.",
            "architecture": "Regresión Lineal Múltiple OLS sin regularización.",
            "algorithm": "LinearRegression (Scikit-Learn OLS)",
            "version": "v1.0.0",
            "limitations": "No captura relaciones no lineales complejas sin ingeniería de atributos previa.",
            "owners": "Equipo de Tarificación y Modelado Financiero"
        },
        training_config={
            "split_ratios": {"train": 0.75, "val": 0.0, "test": 0.25},
            "is_stratified": False,
            "hyperparameters": {"fit_intercept": True},
            "random_seed": 42,
            "reproducibility_verified": True,
            "model_version": "v1.0.0",
            "git_commit": "c4d5e6f"
        },
        production_df=df_test,
        latency_ms=12.4,
        security_answers={
            "has_rate_limiting": True, "output_precision_limited": True, "has_membership_defense": True,
            "is_generative": False, "has_access_control": True, "has_audit_logs": True
        },
        privacy_answers={
            "memorization_risk_checked": True, "has_anonymization": True, "retention_policy_defined": True
        },
        error_rate=0.005,
        concept_drift_detected=False,
        user_feedback_score=96.5
    )

# --- EXECUTE PRUEBA 3: DEMO CLASS ---
def run_p3():
    np.random.seed(42)
    n = 500
    df = pd.DataFrame({
        "age": np.random.randint(18, 70, n),
        "income": np.random.randint(20000, 120000, n),
        "loan_amount": np.random.randint(1000, 30000, n),
        "credit_score": np.random.randint(300, 850, n),
        "gender": np.random.choice(["Male", "Female"], n),
        "email": [f"user{i}@example.com" for i in range(n)]
    })
    y_true = np.random.choice([0, 1], n, p=[0.7, 0.3])
    X = df[["age", "income", "loan_amount", "credit_score"]]
    model = RandomForestClassifier(random_state=42).fit(X, y_true)
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]

    auditor = ModelAuditor(model_name="Modelo Clasificador de Crédito (Demo)")
    return auditor.audit(
        df=df,
        y_true=y_true,
        y_pred=y_pred,
        y_prob=y_prob,
        problem_type="classification",
        target_column=None,
        sensitive_column="gender",
        privileged_group="Male",
        unprivileged_group="Female",
        model=model,
        predict_fn=model.predict
    )

res1 = run_p1()
print_audit_report("Prueba 1: Clasificación de Riesgo Crediticio (PD Scorecard)", res1)

res2 = run_p2()
print_audit_report("Prueba 2: Regresión de Tasa de Interés (Interest Rate Predictor)", res2)

res3 = run_p3()
print_audit_report("Prueba 3: Demo Básico (RandomForest Classifier sin Configuración)", res3)
