import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manage

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "synthetic"

class WorkbenchTests(unittest.TestCase):
    def test_synthetic_fixture_validates(self):
        self.assertEqual(manage.validate(FIXTURE, as_json=True), 0)

    def test_bootstrap_creates_blank_local_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "new-case"
            self.assertEqual(manage.init(target), 0)
            self.assertTrue((target / "scope.json").exists())
            self.assertTrue((target / "sources.csv").exists())
            self.assertTrue((target / "claims.jsonl").exists())

    def test_missing_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "case"
            shutil.copytree(FIXTURE, target)
            path = target / "observations.csv"
            text = path.read_text(encoding="utf-8").replace("SRC-001", "SRC-MISSING")
            path.write_text(text, encoding="utf-8")
            self.assertEqual(manage.validate(target, as_json=True), 1)

    def test_missing_alternative_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "case"
            shutil.copytree(FIXTURE, target)
            path = target / "claims.jsonl"
            claims = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            claims[0]["alternatives"] = []
            path.write_text("\n".join(json.dumps(c) for c in claims) + "\n", encoding="utf-8")
            self.assertEqual(manage.validate(target, as_json=True), 1)

    def test_agent_cannot_set_human_disposition(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "case"
            shutil.copytree(FIXTURE, target)
            path = target / "claims.jsonl"
            claims = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            claims[1]["state"] = "reviewed"
            claims[1]["human_disposition"] = "accepted_for_report"
            path.write_text("\n".join(json.dumps(c) for c in claims) + "\n", encoding="utf-8")
            self.assertEqual(manage.validate(target, as_json=True), 1)

if __name__ == "__main__":
    unittest.main()
