import csv
import hashlib
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from hytwin.report import generate_demo


ROOT = Path(__file__).resolve().parents[1]


class EvidenceTests(unittest.TestCase):
    def test_demo_is_deterministic_and_matches_checked_in_evidence(self):
        if not (ROOT / "results/demo/manifest.json").exists():
            self.skipTest("Checked-in outputs are not included in the minimal container")
        with tempfile.TemporaryDirectory() as folder:
            generate_demo(Path(folder))
            expected = json.loads((ROOT / "results/demo/manifest.json").read_text())
            actual = json.loads((Path(folder) / "manifest.json").read_text())
            self.assertEqual(actual, expected)
            for name, digest in actual["files"].items():
                self.assertEqual(hashlib.sha256((Path(folder) / name).read_bytes()).hexdigest(), digest)

    def test_evidence_parses_and_sweep_has_physical_deadline(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            generate_demo(path)
            ET.parse(path / "overview.svg")
            summary = json.loads((path / "summary.json").read_text())
            self.assertEqual(len(summary["scenarios"]), 6)
            self.assertIn("synthetic", summary["provenance"]["data_origin"])
            with (path / "delay-sweep.csv").open(newline="") as stream:
                sweep = list(csv.DictReader(stream))
            self.assertEqual(len(sweep), 81)
            self.assertTrue(all(r["safe_entire_run"] == "True" for r in sweep if float(r["requested_delay_s"]) <= 15))
            self.assertTrue(all(r["safe_entire_run"] == "False" for r in sweep if float(r["requested_delay_s"]) > 15))

    def test_recovered_file_hashes_match_provenance(self):
        manifest_path = ROOT / "legacy/recovered/manifest.json"
        if not manifest_path.exists():
            self.skipTest("Historical source archive is not included in the minimal container")
        manifest = json.loads(manifest_path.read_text())
        for entry in manifest["artifacts"]:
            path = ROOT / entry["stored_path"]
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["blob_sha256"])

    def test_checked_proof_evidence_matches_final_model_sources(self):
        metadata = ROOT / "results/proofs/verification.json"
        if not metadata.exists():
            self.skipTest("Formal evidence is not included in the minimal container")
        record = json.loads(metadata.read_text())
        self.assertEqual(record["proved_archive_entries"], 9)
        self.assertEqual(len(record["proof_results"]), 9)
        for group in ("model_sha256", "evidence_sha256"):
            for name, digest in record[group].items():
                with self.subTest(path=name):
                    self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)
        for result in record["proof_results"]:
            self.assertEqual(result["status"], "proved")
            self.assertIn('PROVED ' + result["archive_entry"],
                          (ROOT / result["log"]).read_text())


if __name__ == "__main__":
    unittest.main()
