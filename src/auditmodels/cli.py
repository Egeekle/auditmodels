import argparse
import logging
import sys
import pandas as pd
import numpy as np

from auditmodels.auditor import ModelAuditor
from auditmodels.agent import ModelTestingAgent
from auditmodels.errors import AuditModelsError

logger = logging.getLogger(__name__)


def _fail(message: str) -> None:
    """Reports a fatal CLI error on stderr and exits with a non-zero status."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(1)


def _load_csv(path: str, description: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as e:
        _fail(f"Could not read the {description} CSV '{path}': {e}")


def _synthetic_dataset(with_pii: bool = False) -> pd.DataFrame:
    np.random.seed(42)
    n_samples = 500
    df = pd.DataFrame({
        "age": np.random.randint(18, 70, n_samples),
        "income": np.random.normal(50000, 15000, n_samples),
        "gender": np.random.choice(["Male", "Female"], n_samples, p=[0.5, 0.5]),
        "credit_score": np.random.normal(650, 50, n_samples),
    })
    if with_pii:
        df["email"] = [f"user{i}@example.com" for i in range(n_samples)]
    return df


def main():
    parser = argparse.ArgumentParser(description="AuditModels: Comprehensive AI Model Auditing & Agentic Testing CLI")
    parser.add_argument("--data", type=str, help="Path to CSV dataset to audit")
    parser.add_argument("--target", type=str, help="Target column name")
    parser.add_argument("--predictions", type=str, help="Path to CSV file containing y_true and y_pred")
    parser.add_argument("--model-name", type=str, default="AI Model", help="Name of the model being audited")
    parser.add_argument("--output-html", type=str, default="audit_report.html", help="Output path for HTML report")
    parser.add_argument("--output-md", type=str, default="audit_report.md", help="Output path for Markdown summary")
    parser.add_argument("--use-agent", action="store_true", help="Use autonomous ModelTestingAgent for zero-config inspection & audit")
    parser.add_argument("--strict", action="store_true", help="Abort the run as soon as any audit phase fails instead of reporting it as an unscored phase")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging of audit phase failures")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    print(f"Running AuditModels for [{args.model_name}]...")

    try:
        if args.use_agent:
            print("[AGENT] Invoking ModelTestingAgent for autonomous model & dataset discovery...")
            agent = ModelTestingAgent(agent_name=f"Agent for {args.model_name}")

            if args.data:
                df = _load_csv(args.data, "dataset")
            else:
                print("No dataset provided; generating synthetic dataset for agentic audit...")
                df = _synthetic_dataset(with_pii=True)
                df["target"] = np.random.choice([0, 1], len(df), p=[0.7, 0.3])

            if args.target and args.target not in df.columns:
                _fail(f"Target column '{args.target}' not found in dataset. Available columns: {list(df.columns)}")

            result, remediation = agent.run_tests(
                df=df,
                target_column=args.target,
                model_name=args.model_name,
                strict=args.strict
            )

            print("\n[REMEDIATION PLAN] Generado por el Agente:")
            for action in remediation.get("critical_actions", []):
                print(f"  [CRITICAL] {action}")
            for action in remediation.get("high_priority_actions", []):
                print(f"  [HIGH] {action}")
            for action in remediation.get("medium_priority_actions", []):
                print(f"  [MEDIUM] {action}")

        elif not args.data:
            print("Note: No dataset CSV provided. Run with --data path/to/dataset.csv or use the Python API.")
            print("Creating synthetic demo dataset audit...")

            # Synthetic Demo Run
            df = _synthetic_dataset()
            y_true = np.random.choice([0, 1], len(df), p=[0.7, 0.3])
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
                unprivileged_group="Female",
                strict=args.strict
            )
        else:
            df = _load_csv(args.data, "dataset")
            if args.predictions:
                preds_df = _load_csv(args.predictions, "predictions")
                missing = [col for col in ("y_true", "y_pred") if col not in preds_df.columns]
                if missing:
                    _fail(f"Predictions file '{args.predictions}' is missing required column(s): {missing}")
                if len(preds_df) != len(df):
                    _fail(
                        f"Predictions file has {len(preds_df)} rows but the dataset has {len(df)}; "
                        "both must be aligned row by row."
                    )
                y_true = preds_df["y_true"]
                y_pred = preds_df["y_pred"]
            else:
                if not args.target:
                    _fail("--target is required when auditing a dataset without a --predictions file.")
                if args.target not in df.columns:
                    _fail(f"Target column '{args.target}' not found in dataset. Available columns: {list(df.columns)}")
                y_true = df[args.target].values
                y_pred = y_true
                print(
                    "Warning: no --predictions supplied; y_pred is set to y_true, "
                    "so performance and fairness metrics describe a perfect oracle, not your model.",
                    file=sys.stderr,
                )

            auditor = ModelAuditor(model_name=args.model_name)
            result = auditor.audit(df=df, y_true=y_true, y_pred=y_pred, target_column=args.target, strict=args.strict)

        html_path = result.export_html(args.output_html)
        md_path = result.export_markdown(args.output_md)
    except AuditModelsError as e:
        logger.debug("Audit run failed", exc_info=True)
        _fail(str(e))

    print(f"\nAudit Complete! Overall Score: {result.overall_score:.1f}/100 | Risk Level: {result.overall_risk_level}")
    print(f"HTML Audit Report saved to: {html_path}")
    print(f"Markdown Summary saved to: {md_path}")

    if result.has_errors:
        print("\nWarning: the following audit phases failed and were excluded from the score:", file=sys.stderr)
        for failure in result.errors:
            print(f"  - {failure['section']}: {failure['error_type']}: {failure['error']}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
