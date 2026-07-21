import argparse
import sys
import pandas as pd
import numpy as np

from auditmodels.auditor import ModelAuditor


def main():
    parser = argparse.ArgumentParser(description="AuditModels: Comprehensive AI Model Auditing CLI")
    parser.add_argument("--data", type=str, help="Path to CSV dataset to audit")
    parser.add_argument("--target", type=str, help="Target column name")
    parser.add_argument("--predictions", type=str, help="Path to CSV file containing y_true and y_pred")
    parser.add_argument("--model-name", type=str, default="AI Model", help="Name of the model being audited")
    parser.add_argument("--output-html", type=str, default="audit_report.html", help="Output path for HTML report")
    parser.add_argument("--output-md", type=str, default="audit_report.md", help="Output path for Markdown summary")

    args = parser.parse_args()

    print(f"Running AuditModels for [{args.model_name}]...")

    if not args.data:
        print("Note: No dataset CSV provided. Run with --data path/to/dataset.csv or use the Python API.")
        print("Creating synthetic demo dataset audit...")
        
        # Synthetic Demo Run
        np.random.seed(42)
        n_samples = 500
        df = pd.DataFrame({
            "age": np.random.randint(18, 70, n_samples),
            "income": np.random.normal(50000, 15000, n_samples),
            "gender": np.random.choice(["Male", "Female"], n_samples, p=[0.5, 0.5]),
            "credit_score": np.random.normal(650, 50, n_samples)
        })
        y_true = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        # Add bias to predictions for female group to demonstrate audit warnings
        y_pred = y_true.copy()
        female_mask = df["gender"] == "Female"
        y_pred[female_mask] = np.random.choice([0, 1], female_mask.sum(), p=[0.8, 0.2])

        auditor = ModelAuditor(model_name=args.model_name)
        result = auditor.audit(
            df=df,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_column="gender",
            privileged_group="Male",
            unprivileged_group="Female"
        )
    else:
        df = pd.read_csv(args.data)
        if args.predictions:
            preds_df = pd.read_csv(args.predictions)
            y_true = preds_df["y_true"]
            y_pred = preds_df["y_pred"]
        else:
            if args.target not in df.columns:
                print(f"Error: Target column '{args.target}' not found in dataset.")
                sys.exit(1)
            y_true = df[args.target].values
            y_pred = y_true  # dummy if no predictions file

        auditor = ModelAuditor(model_name=args.model_name)
        result = auditor.audit(df=df, y_true=y_true, y_pred=y_pred, target_column=args.target)

    html_path = result.export_html(args.output_html)
    md_path = result.export_markdown(args.output_md)

    print(f"Audit Complete! Overall Score: {result.overall_score}/100 | Risk Level: {result.overall_risk_level}")
    print(f"HTML Audit Report saved to: {html_path}")
    print(f"Markdown Summary saved to: {md_path}")


if __name__ == "__main__":
    main()
