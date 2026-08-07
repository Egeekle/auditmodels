import logging
import os
import tempfile
import unittest

import numpy as np
import pandas as pd

from auditmodels.agent import ModelTestingAgent
from auditmodels.auditor import ModelAuditor
from auditmodels.errors import (
    SECTION_STATUS_ERROR,
    SECTION_STATUS_SKIPPED,
    AuditConfigurationError,
    AuditExecutionError,
    ReportGenerationError,
)
from auditmodels.fairness_audit import audit_fairness
from auditmodels.performance_audit import audit_performance
from auditmodels.production_audit import audit_production, calculate_psi
from auditmodels.reporting import generate_html_report, generate_markdown_report
from auditmodels.robustness_audit import audit_robustness


def setUpModule():
    # The expected failures below log full tracebacks; keep the test output readable.
    logging.disable(logging.CRITICAL)


def tearDownModule():
    logging.disable(logging.NOTSET)


def _sample_df():
    return pd.DataFrame({
        "age": [20, 30, 40, 50, 60, 70],
        "income": [1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0],
        "gender": ["M", "F", "M", "F", "M", "F"],
    })


class TestRobustnessErrorHandling(unittest.TestCase):

    def test_broken_predict_fn_is_reported_as_error_not_perfect_score(self):
        def broken_predict(_):
            raise RuntimeError("model endpoint unavailable")

        res = audit_robustness(broken_predict, _sample_df(), np.array([0, 1, 0, 1, 0, 1]))

        self.assertIsNone(res["score"])
        self.assertEqual(res["status"], SECTION_STATUS_ERROR)
        self.assertIn("model endpoint unavailable", res["error"])

    def test_non_numeric_dataset_is_skipped_without_score(self):
        df = pd.DataFrame({"gender": ["M", "F"]})
        res = audit_robustness(lambda x: np.zeros(len(x)), df, np.array([0, 1]))

        self.assertIsNone(res["score"])
        self.assertEqual(res["status"], SECTION_STATUS_SKIPPED)

    def test_unsupported_problem_type_raises(self):
        with self.assertRaises(AuditConfigurationError):
            audit_robustness(lambda x: np.zeros(len(x)), _sample_df(), np.zeros(6), problem_type="ranking")


class TestPerformanceErrorHandling(unittest.TestCase):

    def test_length_mismatch_raises(self):
        with self.assertRaises(AuditConfigurationError):
            audit_performance([1, 0, 1], [1, 0])

    def test_unsupported_problem_type_raises(self):
        with self.assertRaises(AuditConfigurationError):
            audit_performance([1, 0], [1, 0], problem_type="clustering")

    def test_score_basis_is_reported_when_auc_unavailable(self):
        res = audit_performance([1, 0, 1, 0], [1, 0, 1, 1])
        self.assertEqual(res["score_basis"], "f1_score")


class TestFairnessErrorHandling(unittest.TestCase):

    def test_unmatched_groups_raise_instead_of_scoring_zero(self):
        with self.assertRaises(AuditConfigurationError):
            audit_fairness(
                df=_sample_df(),
                y_true=[1, 0, 1, 0, 1, 0],
                y_pred=[1, 0, 1, 0, 1, 0],
                sensitive_column="gender",
                privileged_group="Male",
                unprivileged_group="Female",
            )

    def test_missing_sensitive_column_raises(self):
        with self.assertRaises(AuditConfigurationError):
            audit_fairness(
                df=_sample_df(),
                y_true=[1, 0, 1, 0, 1, 0],
                y_pred=[1, 0, 1, 0, 1, 0],
                sensitive_column="race",
                privileged_group="M",
                unprivileged_group="F",
            )


class TestProductionErrorHandling(unittest.TestCase):

    def test_psi_raises_on_empty_sample(self):
        with self.assertRaises(AuditConfigurationError):
            calculate_psi(np.array([np.nan, np.nan]), np.array([1.0, 2.0]))

    def test_undetectable_drift_is_flagged_not_silently_stable(self):
        reference = pd.DataFrame({"income": [1.0, 2.0, 3.0, 4.0], "score": [1.0, 2.0, 3.0, 4.0]})
        production = pd.DataFrame({"income": [np.nan, np.nan, np.nan, np.nan]})

        res = audit_production(reference_df=reference, production_df=production)

        self.assertEqual(sorted(res["not_evaluated_columns"]), ["income", "score"])
        self.assertNotEqual(res["drift_by_column"]["income"]["status"], "STABLE")
        self.assertTrue(any("no pudieron evaluarse" in w for w in res["warnings"]))


class TestAuditorPropagation(unittest.TestCase):

    def test_skipped_phases_do_not_inflate_overall_score(self):
        df = _sample_df()
        y_true = [0, 1, 0, 1, 0, 1]
        y_pred = [0, 1, 0, 1, 1, 1]

        result = ModelAuditor("TestModel").audit(df=df, y_true=y_true, y_pred=y_pred)

        self.assertIsNone(result.sections["fairness"]["score"])
        self.assertIsNone(result.sections["robustness"]["score"])
        self.assertIsNone(result.sections["explainability"]["score"])
        self.assertIn("fairness", result.raw_data["unscored_sections"])
        # Weights of the evaluated phases only (fairness/robustness/explainability excluded)
        self.assertAlmostEqual(result.raw_data["evaluated_weight"], 0.75)

    def test_failing_phase_is_recorded_and_excluded(self):
        df = _sample_df()
        y_true = [0, 1, 0, 1, 0, 1]

        def broken_predict(_):
            raise RuntimeError("boom")

        result = ModelAuditor("TestModel").audit(
            df=df, y_true=y_true, y_pred=y_true,
            sensitive_column="gender", privileged_group="X", unprivileged_group="Y",
            predict_fn=broken_predict,
        )

        self.assertTrue(result.has_errors)
        self.assertEqual(sorted(result.failed_sections()), ["fairness", "robustness"])
        self.assertIsNone(result.sections["fairness"]["score"])
        self.assertIn("fairness", result.raw_data["unscored_sections"])

    def test_strict_mode_propagates_phase_failure(self):
        df = _sample_df()
        with self.assertRaises(AuditConfigurationError):
            ModelAuditor("TestModel").audit(
                df=df, y_true=[0, 1, 0, 1, 0, 1], y_pred=[0, 1, 0, 1, 0, 1],
                sensitive_column="gender", privileged_group="X", unprivileged_group="Y",
                strict=True,
            )

    def test_report_generation_reports_io_failures(self):
        result = ModelAuditor("TestModel").audit(df=_sample_df())
        missing_dir = os.path.join(tempfile.gettempdir(), "auditmodels-does-not-exist", "report.html")

        with self.assertRaises(ReportGenerationError):
            generate_html_report(result.to_dict(), missing_dir)

    def test_reports_render_when_phases_are_unscored(self):
        result = ModelAuditor("TestModel").audit(df=_sample_df())
        with tempfile.TemporaryDirectory() as tmp:
            html_path = generate_html_report(result.to_dict(), os.path.join(tmp, "r.html"))
            md_path = generate_markdown_report(result.to_dict(), os.path.join(tmp, "r.md"))
            with open(md_path, encoding="utf-8") as f:
                self.assertIn("N/D (SKIPPED)", f.read())
            self.assertTrue(os.path.getsize(html_path) > 0)


class TestAgentErrorHandling(unittest.TestCase):

    def test_broken_model_prediction_propagates(self):
        class BrokenModel:
            def predict(self, X):
                raise ValueError("feature mismatch")

        df = pd.DataFrame({"f1": [1.0, 2.0, 3.0, 4.0], "target": [0, 1, 0, 1]})

        with self.assertRaises(AuditExecutionError):
            ModelTestingAgent().run_tests(df=df, model=BrokenModel(), target_column="target")

    def test_missing_ground_truth_skips_performance_instead_of_faking_it(self):
        df = pd.DataFrame({"f1": [1.0, 2.0, 3.0, 4.0], "f2": [4.0, 3.0, 2.0, 1.0]})

        result, remediation = ModelTestingAgent().run_tests(df=df)

        self.assertIsNone(result.sections["performance"]["score"])
        self.assertEqual(result.sections["performance"]["status"], SECTION_STATUS_SKIPPED)
        self.assertTrue(any("No se encontró la variable objetivo" in w for w in result.all_warnings))
        self.assertTrue(any("Fases sin evidencia" in r for r in remediation["summary_recommendations"]))

    def test_strict_mode_rejects_missing_ground_truth(self):
        df = pd.DataFrame({"f1": [1.0, 2.0], "f2": [2.0, 1.0]})
        with self.assertRaises(AuditConfigurationError):
            ModelTestingAgent().run_tests(df=df, strict=True)


if __name__ == "__main__":
    unittest.main()
