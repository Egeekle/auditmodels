"""
Example script demonstrating the autonomous ModelTestingAgent.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from auditmodels import ModelTestingAgent


def main():
    print("[AGENT] Starting Agentic Model Testing with ModelTestingAgent...")

    # 1. Generate a realistic Credit Scoring Dataset
    np.random.seed(42)
    n = 600
    df = pd.DataFrame({
        "age": np.random.randint(18, 75, n),
        "annual_income": np.random.normal(55000, 18000, n),
        "debt_to_income": np.random.uniform(0.05, 0.45, n),
        "credit_score": np.random.randint(350, 850, n),
        "gender": np.random.choice(["Male", "Female"], n, p=[0.5, 0.5]),
        "email": [f"applicant{i}@bankdemo.com" for i in range(n)],
        "ssn": [f"999-{i:02d}-{i:04d}" for i in range(n)]
    })

    # Target: 1 = Approved, 0 = Default Risk
    y_true = ((df["credit_score"] > 620) & (df["debt_to_income"] < 0.35)).astype(int)
    df["approved"] = y_true

    # 2. Train a RandomForest Model
    feature_cols = ["age", "annual_income", "debt_to_income", "credit_score"]
    X = df[feature_cols]
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X, y_true)

    # 3. Instantiate the ModelTestingAgent
    agent = ModelTestingAgent(agent_name="CreditRisk Agentic Auditor")

    # 4. Auto-inspect the dataset and model
    print("\n[STEP 1] Running Auto-Inspection...")
    setup_info = agent.inspect_and_setup(df=df, model=model, target_column="approved")
    print(f"  * Num Rows: {setup_info['num_rows']}, Num Cols: {setup_info['num_cols']}")
    print(f"  * Auto-detected Target Column: '{setup_info['auto_detected']['target_column']}'")
    print(f"  * Auto-detected Problem Type: '{setup_info['auto_detected']['problem_type']}'")
    print(f"  * Auto-detected Sensitive Column: '{setup_info['auto_detected']['sensitive_column']}'")
    print(f"  * Auto-detected Privileged Group: '{setup_info['auto_detected']['privileged_group']}'")
    print(f"  * Auto-detected PII Columns: {setup_info['auto_detected']['pii_columns']}")

    # 5. Run autonomous testing suite
    print("\n[STEP 2] Running Autonomous Test Suite...")
    audit_result, remediation = agent.run_tests(
        df=df,
        model=model,
        target_column="approved",
        model_name="Credit Risk RandomForest Classifier"
    )

    print(f"\n[RESULTS SUMMARY]")
    print(f"  * Overall Score: {audit_result.overall_score:.1f} / 100")
    print(f"  * Risk Level: {audit_result.overall_risk_level}")

    # 6. Export Reports
    html_file = "agent_credit_audit_report.html"
    md_file = "agent_credit_audit_report.md"
    audit_result.export_html(html_file)
    audit_result.export_markdown(md_file)
    print(f"\nExported HTML report to: {html_file}")
    print(f"Exported Markdown report to: {md_file}")

    # 7. Print Remediation Plan
    print("\n[REMEDIATION PLAN] Prioritized Action Items:")
    if remediation["critical_actions"]:
        print("  CRITICAL ACTIONS:")
        for action in remediation["critical_actions"]:
            print(f"    - {action}")
    if remediation["high_priority_actions"]:
        print("  HIGH PRIORITY ACTIONS:")
        for action in remediation["high_priority_actions"]:
            print(f"    - {action}")
    if remediation["medium_priority_actions"]:
        print("  MEDIUM PRIORITY ACTIONS:")
        for action in remediation["medium_priority_actions"]:
            print(f"    - {action}")


if __name__ == "__main__":
    main()
