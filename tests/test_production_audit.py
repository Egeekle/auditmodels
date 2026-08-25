import unittest

import numpy as np
import pandas as pd

from auditmodels.production_audit import audit_production, calculate_psi


class TestCalculatePSI(unittest.TestCase):

    def test_identical_distributions_have_near_zero_psi(self):
        values = np.random.RandomState(0).normal(0, 1, 1000)
        self.assertLess(calculate_psi(values, values.copy()), 0.01)

    def test_shifted_distribution_produces_severe_psi(self):
        rng = np.random.RandomState(0)
        reference = rng.normal(0, 1, 1000)
        current = rng.normal(5, 1, 1000)
        self.assertGreaterEqual(calculate_psi(reference, current), 0.25)

    def test_nan_values_are_ignored(self):
        reference = np.array([1.0, 2.0, np.nan, 3.0, 4.0])
        current = np.array([1.0, 2.0, 3.0, 4.0, np.nan])
        self.assertIsInstance(calculate_psi(reference, current), float)

    def test_empty_input_returns_zero(self):
        self.assertEqual(calculate_psi(np.array([np.nan]), np.array([1.0, 2.0])), 0.0)
        self.assertEqual(calculate_psi(np.array([1.0, 2.0]), np.array([])), 0.0)


class TestAuditProduction(unittest.TestCase):

    def setUp(self):
        rng = np.random.RandomState(42)
        self.reference_df = pd.DataFrame({
            "age": rng.normal(40, 5, 300),
            "income": rng.normal(50000, 5000, 300),
            "segment": ["A"] * 300,
        })

    def test_healthy_production_scores_low_risk(self):
        res = audit_production(reference_df=self.reference_df, latency_ms=50.0, error_rate=0.1, user_feedback_score=95.0)
        self.assertEqual(res["score"], 100.0)
        self.assertEqual(res["risk_level"], "LOW")
        self.assertEqual(res["warnings"], [])
        self.assertEqual(res["drift_by_column"], {})

    def test_stable_production_data_reports_no_drift(self):
        production_df = self.reference_df.copy()
        res = audit_production(reference_df=self.reference_df, production_df=production_df)
        self.assertEqual(res["severe_drift_columns"], [])
        self.assertEqual(res["drift_by_column"]["age"]["status"], "STABLE")
        self.assertNotIn("segment", res["drift_by_column"])

    def test_severe_drift_detected_and_penalized(self):
        rng = np.random.RandomState(1)
        production_df = pd.DataFrame({
            "age": rng.normal(70, 5, 300),
            "income": rng.normal(50000, 5000, 300),
        })
        res = audit_production(reference_df=self.reference_df, production_df=production_df)
        self.assertIn("age", res["severe_drift_columns"])
        self.assertEqual(res["drift_by_column"]["age"]["status"], "SEVERE_DRIFT")
        self.assertEqual(res["score"], 80.0)
        self.assertTrue(any("age" in w for w in res["warnings"]))

    def test_operational_issues_accumulate_penalties(self):
        res = audit_production(
            reference_df=self.reference_df,
            latency_ms=500.0,
            error_rate=5.0,
            concept_drift_detected=True,
            user_feedback_score=40.0,
        )
        self.assertEqual(res["score"], 40.0)
        self.assertEqual(res["risk_level"], "HIGH")
        self.assertEqual(len(res["warnings"]), 4)
        self.assertTrue(res["concept_drift_detected"])
        self.assertEqual(res["latency_ms"], 500.0)
        self.assertEqual(res["error_rate_pct"], 5.0)
        self.assertEqual(res["user_feedback_score_pct"], 40.0)

    def test_score_is_floored_at_zero(self):
        rng = np.random.RandomState(2)
        production_df = pd.DataFrame({
            "age": rng.normal(200, 5, 300),
            "income": rng.normal(500000, 5000, 300),
        })
        res = audit_production(
            reference_df=self.reference_df,
            production_df=production_df,
            latency_ms=900.0,
            error_rate=20.0,
            concept_drift_detected=True,
            user_feedback_score=10.0,
        )
        self.assertEqual(res["score"], 0.0)
        self.assertEqual(res["risk_level"], "HIGH")

    def test_medium_risk_boundary(self):
        res = audit_production(reference_df=self.reference_df, concept_drift_detected=True)
        self.assertEqual(res["score"], 75.0)
        self.assertEqual(res["risk_level"], "MEDIUM")


if __name__ == "__main__":
    unittest.main()
