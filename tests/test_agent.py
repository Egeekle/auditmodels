import unittest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from auditmodels.agent import ModelTestingAgent


class TestModelTestingAgent(unittest.TestCase):

    def test_agent_inspect_and_setup(self):
        np.random.seed(42)
        n = 100
        df = pd.DataFrame({
            "age": np.random.randint(20, 60, n),
            "gender": np.random.choice(["Male", "Female"], n),
            "email": [f"user{i}@test.com" for i in range(n)],
            "target": np.random.choice([0, 1], n)
        })

        agent = ModelTestingAgent()
        setup = agent.inspect_and_setup(df)

        self.assertEqual(setup["num_rows"], 100)
        self.assertEqual(setup["auto_detected"]["target_column"], "target")
        self.assertEqual(setup["auto_detected"]["problem_type"], "classification")
        self.assertEqual(setup["auto_detected"]["sensitive_column"], "gender")
        self.assertIn("email", setup["auto_detected"]["pii_columns"])

    def test_agent_run_tests(self):
        np.random.seed(42)
        n = 200
        df = pd.DataFrame({
            "feature1": np.random.randn(n),
            "feature2": np.random.randn(n),
            "gender": np.random.choice(["Male", "Female"], n),
            "target": np.random.choice([0, 1], n)
        })

        X = df[["feature1", "feature2"]]
        y = df["target"]
        model = RandomForestClassifier(random_state=42).fit(X, y)

        agent = ModelTestingAgent()
        result, remediation = agent.run_tests(
            df=df,
            model=model,
            target_column="target",
            sensitive_column="gender"
        )

        self.assertGreaterEqual(result.overall_score, 0.0)
        self.assertIn(result.overall_risk_level, ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        self.assertIn("overall_score", remediation)
        self.assertIn("critical_actions", remediation)
        self.assertIn("high_priority_actions", remediation)


if __name__ == "__main__":
    unittest.main()
