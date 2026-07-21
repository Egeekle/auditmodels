import unittest
import pandas as pd
import numpy as np

from auditmodels.data_audit import audit_data
from auditmodels.performance_audit import audit_performance
from auditmodels.fairness_audit import audit_fairness
from auditmodels.robustness_audit import audit_robustness
from auditmodels.compliance_audit import audit_compliance
from auditmodels.auditor import ModelAuditor


class TestAuditModels(unittest.TestCase):

    def test_data_audit(self):
        df = pd.DataFrame({
            "a": [1, 2, np.nan, 4, 5],
            "b": [10, 10, 10, 10, 10],  # constant column
            "email": ["a@b.com", "b@c.com", "c@d.com", "d@e.com", "e@f.com"]
        })
        res = audit_data(df)
        self.assertIn("score", res)
        self.assertIn("constant_cols", res)
        self.assertEqual(res["constant_cols"], ["b"])
        self.assertIn("email", res["pii_flagged"])

    def test_performance_audit_classification(self):
        y_true = [1, 0, 1, 1, 0, 1, 0, 0]
        y_pred = [1, 0, 1, 0, 0, 1, 0, 1]
        res = audit_performance(y_true, y_pred, problem_type="classification")
        self.assertIn("accuracy", res)
        self.assertIn("f1_score", res)
        self.assertGreaterEqual(res["score"], 0)

    def test_performance_audit_regression(self):
        y_true = [10.0, 20.0, 30.0, 40.0]
        y_pred = [11.0, 19.0, 31.0, 39.0]
        res = audit_performance(y_true, y_pred, problem_type="regression")
        self.assertIn("mae", res)
        self.assertIn("r2_score", res)

    def test_fairness_audit(self):
        df = pd.DataFrame({"gender": ["M", "M", "F", "F", "F"]})
        y_true = [1, 1, 1, 0, 0]
        y_pred = [1, 1, 0, 0, 0]
        res = audit_fairness(
            df=df,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_column="gender",
            privileged_group="M",
            unprivileged_group="F"
        )
        self.assertIn("disparate_impact_ratio", res)
        self.assertIn("equal_opportunity_diff", res)

    def test_compliance_audit(self):
        res = audit_compliance(answers={"GOV-01": True, "SEC-01": False})
        self.assertIn("score", res)
        self.assertIn("checklist", res)

    def test_full_auditor(self):
        auditor = ModelAuditor("TestModel")
        df = pd.DataFrame({
            "age": [20, 30, 40, 50],
            "income": [20000, 40000, 60000, 80000],
            "gender": ["M", "F", "M", "F"]
        })
        y_true = [0, 1, 1, 1]
        y_pred = [0, 1, 1, 0]
        
        result = auditor.audit(
            df=df,
            y_true=y_true,
            y_pred=y_pred,
            sensitive_column="gender",
            privileged_group="M",
            unprivileged_group="F"
        )
        self.assertGreaterEqual(result.overall_score, 0)
        self.assertIn("data", result.sections)
        self.assertIn("performance", result.sections)


if __name__ == "__main__":
    unittest.main()
