import os
import sys
import tempfile
import unittest
from unittest import mock

import numpy as np
import pandas as pd

from auditmodels import cli


class TestCli(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.html_path = os.path.join(self.tmpdir.name, "report.html")
        self.md_path = os.path.join(self.tmpdir.name, "report.md")

    def _run(self, extra_args):
        argv = ["auditmodels", "--output-html", self.html_path, "--output-md", self.md_path] + extra_args
        with mock.patch.object(sys, "argv", argv):
            cli.main()

    def _write_dataset(self, name="data.csv", n=60):
        rng = np.random.RandomState(0)
        df = pd.DataFrame({
            "age": rng.randint(20, 60, n),
            "income": rng.normal(50000, 5000, n),
            "gender": rng.choice(["Male", "Female"], n),
            "target": rng.choice([0, 1], n),
        })
        path = os.path.join(self.tmpdir.name, name)
        df.to_csv(path, index=False)
        return path

    def test_synthetic_demo_run_generates_reports(self):
        self._run([])
        self.assertTrue(os.path.exists(self.html_path))
        self.assertTrue(os.path.exists(self.md_path))

    def test_dataset_with_target_column(self):
        data_path = self._write_dataset()
        self._run(["--data", data_path, "--target", "target", "--model-name", "MyModel"])
        with open(self.md_path, encoding="utf-8") as f:
            self.assertIn("MyModel", f.read())

    def test_dataset_with_separate_predictions_file(self):
        data_path = self._write_dataset()
        preds_path = os.path.join(self.tmpdir.name, "preds.csv")
        pd.DataFrame({"y_true": [0, 1] * 30, "y_pred": [0, 0] * 30}).to_csv(preds_path, index=False)
        self._run(["--data", data_path, "--predictions", preds_path])
        self.assertTrue(os.path.exists(self.html_path))

    def test_missing_target_column_exits_with_error(self):
        data_path = self._write_dataset()
        with self.assertRaises(SystemExit) as ctx:
            self._run(["--data", data_path, "--target", "nonexistent"])
        self.assertEqual(ctx.exception.code, 1)

    def test_agent_mode_with_synthetic_dataset(self):
        self._run(["--use-agent"])
        self.assertTrue(os.path.exists(self.html_path))
        self.assertTrue(os.path.exists(self.md_path))

    def test_agent_mode_with_provided_dataset(self):
        data_path = self._write_dataset()
        self._run(["--use-agent", "--data", data_path, "--target", "target"])
        self.assertTrue(os.path.exists(self.html_path))


if __name__ == "__main__":
    unittest.main()
