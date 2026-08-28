import unittest

import numpy as np

from auditmodels.explainability_audit import audit_explainability


class DummyTreeModel:
    def __init__(self, importances):
        self.feature_importances_ = np.array(importances)


class DummyLinearModel:
    def __init__(self, coef):
        self.coef_ = np.array(coef)


class OpaqueModel:
    pass


class TestAuditExplainability(unittest.TestCase):

    def test_tree_importances_are_sorted_descending(self):
        model = DummyTreeModel([0.1, 0.5, 0.4])
        res = audit_explainability(model, feature_names=["a", "b", "c"])
        self.assertEqual(list(res["feature_importances"].keys()), ["b", "c", "a"])
        self.assertEqual(res["top_features"], ["b", "c", "a"])
        self.assertTrue(res["has_explainability_interface"])
        self.assertEqual(res["score"], 100.0)
        self.assertEqual(res["risk_level"], "LOW")

    def test_generated_feature_names_when_not_provided(self):
        res = audit_explainability(DummyTreeModel([0.3, 0.7]))
        self.assertEqual(list(res["feature_importances"].keys()), ["feature_1", "feature_0"])

    def test_linear_coefficients_use_absolute_values(self):
        res = audit_explainability(DummyLinearModel([[-0.9, 0.2]]), feature_names=["a", "b"])
        self.assertEqual(res["feature_importances"], {"a": 0.9, "b": 0.2})

    def test_dominant_feature_triggers_warning_and_penalty(self):
        res = audit_explainability(DummyTreeModel([0.9, 0.05, 0.05]), feature_names=["a", "b", "c"])
        self.assertEqual(res["score"], 80.0)
        self.assertEqual(res["risk_level"], "LOW")
        self.assertTrue(any("'a'" in w for w in res["warnings"]))

    def test_opaque_model_is_penalized(self):
        res = audit_explainability(OpaqueModel())
        self.assertEqual(res["feature_importances"], {})
        self.assertEqual(res["top_features"], [])
        self.assertFalse(res["has_explainability_interface"])
        self.assertEqual(res["score"], 60.0)
        self.assertEqual(res["risk_level"], "MEDIUM")
        self.assertEqual(len(res["warnings"]), 1)

    def test_top_features_are_limited_to_five(self):
        res = audit_explainability(DummyTreeModel([0.1] * 8))
        self.assertEqual(len(res["top_features"]), 5)

    def test_zero_importances_do_not_divide_by_zero(self):
        res = audit_explainability(DummyTreeModel([0.0, 0.0]), feature_names=["a", "b"])
        self.assertEqual(res["score"], 100.0)
        self.assertEqual(res["warnings"], [])


if __name__ == "__main__":
    unittest.main()
