import os
import tempfile
import unittest

from auditmodels.reporting import generate_html_report, generate_markdown_report


def build_audit_result(**overrides):
    result = {
        "overall_score": 72.5,
        "overall_risk_level": "MEDIUM",
        "metadata": {"model_name": "Credit Model", "timestamp": "2024-01-01 00:00:00"},
        "all_warnings": ["Deriva severa detectada en 'age'."],
        "sections": {
            "data": {"score": 80.0, "risk_level": "LOW", "duplicate_rows": 3},
            "performance": {"score": 70.0, "risk_level": "MEDIUM"},
            "fairness": {"score": 55.0, "risk_level": "HIGH", "equal_opportunity_diff": 0.25,
                         "disparate_impact_ratio": 0.5, "passes_four_fifths_rule": False,
                         "demographic_parity_diff": 0.3},
            "robustness": {"score": 40.0, "risk_level": "HIGH"},
            "compliance": {"score": 50.0, "risk_level": "HIGH", "framework_breakdown": {}},
            "documentation": {"score": 60.0, "risk_level": "MEDIUM"},
            "training": {"score": 65.0, "risk_level": "MEDIUM"},
            "production": {"score": 75.0, "risk_level": "MEDIUM"},
            "security": {"score": 85.0, "risk_level": "LOW"},
            "privacy": {"score": 45.0, "risk_level": "HIGH", "pii_detected": ["email"]},
            "explainability": {"score": 90.0, "risk_level": "LOW",
                               "feature_importances": {"income": 0.6, "age": 0.4},
                               "top_features": ["income", "age"]},
        },
    }
    result.update(overrides)
    return result


class TestGenerateHtmlReport(unittest.TestCase):

    def _render(self, audit_result):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.html")
            returned = generate_html_report(audit_result, path)
            self.assertEqual(returned, path)
            with open(path, encoding="utf-8") as f:
                return f.read()

    def test_report_includes_model_metadata_and_scores(self):
        html = self._render(build_audit_result())
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Credit Model", html)
        self.assertIn("MEDIUM", html)
        self.assertIn("72.5", html)

    def test_warnings_and_feature_importances_are_rendered(self):
        html = self._render(build_audit_result())
        self.assertIn("Deriva severa detectada", html)
        self.assertIn("income", html)

    def test_remediation_plan_reflects_detected_issues(self):
        html = self._render(build_audit_result())
        self.assertIn("deduplicaci", html)
        self.assertIn("email", html)
        self.assertIn("regla del 80%", html)
        self.assertIn("adversarial", html)
        self.assertIn("ISO 42001", html)

    def test_clean_audit_falls_back_to_monitoring_recommendation(self):
        clean = build_audit_result(
            all_warnings=[],
            sections={
                "data": {"score": 100.0, "duplicate_rows": 0},
                "fairness": {"score": 100.0, "equal_opportunity_diff": 0.0, "passes_four_fifths_rule": True},
                "robustness": {"score": 100.0},
                "compliance": {"score": 100.0, "framework_breakdown": {"ISO/IEC 42001": {"score": 100}}},
                "privacy": {"score": 100.0, "pii_detected": []},
                "explainability": {"score": 100.0, "feature_importances": {}},
            },
        )
        html = self._render(clean)
        self.assertIn("monitoreo continuo", html)
        self.assertIn("Sin alertas", html)
        self.assertIn("Sin datos de importancia", html)

    def test_empty_audit_result_uses_defaults(self):
        html = self._render({})
        self.assertIn("AI Model", html)
        self.assertIn("MEDIUM", html)


class TestGenerateMarkdownReport(unittest.TestCase):

    def _render(self, audit_result):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "report.md")
            returned = generate_markdown_report(audit_result, path)
            self.assertEqual(returned, path)
            with open(path, encoding="utf-8") as f:
                return f.read()

    def test_summary_table_lists_all_phases(self):
        md = self._render(build_audit_result())
        for phase in ["data_audit", "performance_audit", "fairness_audit", "robustness_audit",
                      "explainability_audit", "security_audit", "privacy_audit",
                      "compliance_audit", "documentation_audit", "training_audit", "production_audit"]:
            self.assertIn(phase, md)

    def test_header_and_fairness_metrics(self):
        md = self._render(build_audit_result())
        self.assertIn("# 🛡️ Informe de Auditoría de IA - Credit Model", md)
        self.assertIn("72.5 / 100", md)
        self.assertIn("`MEDIUM`", md)
        self.assertIn("❌ NO CUMPLE", md)
        self.assertIn("income, age", md)

    def test_remediation_plan_reflects_detected_issues(self):
        md = self._render(build_audit_result())
        self.assertIn("Limpiar duplicados", md)
        self.assertIn("email", md)
        self.assertIn("Reweighing", md)
        self.assertIn("robustez", md)

    def test_clean_audit_falls_back_to_monitoring_recommendation(self):
        clean = build_audit_result(
            all_warnings=[],
            sections={
                "data": {"score": 100.0, "duplicate_rows": 0},
                "fairness": {"score": 100.0, "equal_opportunity_diff": 0.0, "passes_four_fifths_rule": True},
                "robustness": {"score": 100.0},
                "privacy": {"score": 100.0, "pii_detected": []},
                "explainability": {"score": 100.0},
            },
        )
        md = self._render(clean)
        self.assertIn("MLOps", md)
        self.assertIn("✅ Sin alertas", md)
        self.assertIn("✅ CUMPLE", md)
        self.assertIn("No especificadas", md)

    def test_empty_audit_result_uses_defaults(self):
        md = self._render({})
        self.assertIn("AI Model", md)
        self.assertIn("N/A", md)


if __name__ == "__main__":
    unittest.main()
