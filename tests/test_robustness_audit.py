import unittest

import numpy as np
import pandas as pd

from auditmodels.robustness_audit import audit_robustness


class TestAuditRobustness(unittest.TestCase):

    def setUp(self):
        rng = np.random.RandomState(42)
        self.X_val = pd.DataFrame({
            "f1": rng.normal(0, 1, 100),
            "f2": rng.normal(5, 2, 100),
        })
        self.y_val = (self.X_val["f1"] > 0).astype(int).values

    def test_no_numeric_features_skips_perturbation(self):
        X_val = pd.DataFrame({"cat": ["a", "b", "c"]})
        res = audit_robustness(lambda X: np.zeros(len(X)), X_val, np.array([0, 1, 0]))
        self.assertEqual(res["score"], 100.0)
        self.assertEqual(res["risk_level"], "LOW")
        self.assertEqual(len(res["warnings"]), 1)
        self.assertNotIn("baseline_metric", res)

    def test_failing_predict_fn_is_skipped_gracefully(self):
        def predict_fn(X):
            raise RuntimeError("boom")

        res = audit_robustness(predict_fn, self.X_val, self.y_val)
        self.assertEqual(res["score"], 100.0)
        self.assertIn("boom", res["warnings"][0])

    def test_predict_fn_requiring_dataframe_is_supported(self):
        def predict_fn(X):
            if not isinstance(X, pd.DataFrame):
                raise ValueError("needs feature names")
            return (X["f1"] > 0).astype(int).values

        res = audit_robustness(predict_fn, self.X_val, self.y_val)
        self.assertEqual(res["baseline_metric"], 1.0)
        self.assertEqual(len(res["noise_perturbation_tests"]), 2)

    def test_robust_classifier_scores_high(self):
        res = audit_robustness(lambda X: np.zeros(len(X)) + self.y_val, self.X_val, self.y_val)
        self.assertEqual(res["baseline_metric"], 1.0)
        self.assertEqual(res["max_performance_drop_pct"], 0.0)
        self.assertEqual(res["score"], 100.0)
        self.assertEqual(res["risk_level"], "LOW")
        self.assertEqual(res["warnings"], [])

    def test_noise_sensitive_classifier_is_penalized(self):
        def predict_fn(X):
            values = X["f1"].values if isinstance(X, pd.DataFrame) else X[:, 0]
            return (values > 0).astype(int)

        res = audit_robustness(predict_fn, self.X_val, self.y_val, noise_scales=[5.0])
        self.assertGreater(res["max_performance_drop_pct"], 20)
        self.assertLess(res["score"], 80.0)
        self.assertIn(res["risk_level"], ["MEDIUM", "HIGH"])
        self.assertTrue(any("sensitivity" in w for w in res["warnings"]))

    def test_regression_problem_type_uses_mse(self):
        y_val = self.X_val["f1"].values

        def predict_fn(X):
            return X["f1"].values if isinstance(X, pd.DataFrame) else X[:, 0]

        res = audit_robustness(predict_fn, self.X_val, y_val, problem_type="regression")
        self.assertAlmostEqual(res["baseline_metric"], 0.0)
        self.assertEqual(res["max_performance_drop_pct"], 0.0)
        self.assertEqual(len(res["noise_perturbation_tests"]), 2)

    def test_constant_and_missing_columns_are_handled(self):
        X_val = pd.DataFrame({
            "constant": [1.0] * 10,
            "with_nan": [1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        })
        y_val = np.array([0, 1] * 5)
        res = audit_robustness(lambda X: np.array([0, 1] * 5), X_val, y_val)
        self.assertEqual(res["baseline_metric"], 1.0)
        self.assertEqual(res["score"], 100.0)

    def test_perturbation_failure_is_recorded_as_warning(self):
        calls = {"n": 0}

        def predict_fn(X):
            calls["n"] += 1
            if calls["n"] > 1:
                raise RuntimeError("noisy failure")
            return self.y_val

        res = audit_robustness(predict_fn, self.X_val, self.y_val, noise_scales=[0.1])
        self.assertTrue(any("noisy failure" in w for w in res["warnings"]))
        self.assertEqual(res["noise_perturbation_tests"], [])


if __name__ == "__main__":
    unittest.main()
