import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "runtime_parity_v1.py"

class RuntimeParityV1Tests(unittest.TestCase):
    def metrics(self):
        return {
            "dataset_class": "EMPIRICAL_MALECNS",
            "spatial_real_count": 7486,
            "topology_fallback_count": 4989,
            "responder_real_count": 9,
            "responder_total_count": 9,
            "accepted_causal_edge_count": 13,
            "scientific_outputs": {"fixture": "frozen-v1", "decision_trace_sha256": "a" * 64},
        }

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=ROOT, text=True, capture_output=True)

    def make_manifest(self, td, profile, artifact_bytes=b"same"):
        td = Path(td)
        artifact = td / f"{profile}.bin"
        artifact.write_bytes(artifact_bytes)
        metrics = td / f"{profile}-metrics.json"
        metrics.write_text(json.dumps(self.metrics()))
        out = td / f"{profile}.json"
        proc = self.run_cli("make", "--runtime-profile", profile, "--source-commit", "deadbeef", "--metrics-json", metrics, "--artifact", f"frozen-output={artifact}", "--output", out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return out

    def test_same_science_different_runtime_profiles_pass(self):
        with tempfile.TemporaryDirectory() as td:
            a = self.make_manifest(td, "habitat")
            b = self.make_manifest(td, "workstation")
            proc = self.run_cli("compare", a, b)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("PASS runtime parity", proc.stdout)

    def test_artifact_change_fails_parity(self):
        with tempfile.TemporaryDirectory() as td:
            a = self.make_manifest(td, "habitat", b"same")
            b = self.make_manifest(td, "workstation", b"changed")
            proc = self.run_cli("compare", a, b)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("scientific_digest differs", proc.stdout)

    def test_invariant_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            artifact = td / "out.bin"
            artifact.write_bytes(b"same")
            data = self.metrics()
            data["spatial_real_count"] = 7485
            metrics = td / "metrics.json"
            metrics.write_text(json.dumps(data))
            out = td / "manifest.json"
            proc = self.run_cli("make", "--runtime-profile", "bad-runtime", "--source-commit", "deadbeef", "--metrics-json", metrics, "--artifact", f"frozen-output={artifact}", "--output", out)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("invariant spatial_real_count", proc.stderr)

if __name__ == "__main__":
    unittest.main()
