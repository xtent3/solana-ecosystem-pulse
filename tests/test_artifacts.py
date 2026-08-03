import json
import tempfile
import unittest
from pathlib import Path

from solpulse.artifacts import write_artifacts


class WriteArtifactsTests(unittest.TestCase):
    def test_writes_consistent_json_markdown_and_html(self):
        snapshot = {
            "schema_version": "solpulse/v1",
            "generated_at": "2026-08-01T12:00:00Z",
            "source": "https://example.invalid/rpc",
            "metrics": {
                "slot": 123456,
                "epoch": 42,
                "epoch_progress_pct": 25.0,
                "tps": 1750.0,
                "validators_active": 1000,
                "validators_delinquent": 5,
                "delinquent_stake_pct": 0.25,
                "supply_total_sol": 600_000_000.0,
                "supply_circulating_sol": 520_000_000.0,
            },
            "alerts": [],
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)

            paths = write_artifacts(snapshot, output)

            self.assertEqual(set(paths), {"json", "markdown", "html"})
            self.assertEqual(json.loads(paths["json"].read_text("utf-8")), snapshot)
            for path in paths.values():
                self.assertTrue(path.exists())
                self.assertIn("2026-08-01T12:00:00Z", path.read_text("utf-8"))
            self.assertFalse(list(output.glob("*.tmp")))


if __name__ == "__main__":
    unittest.main()
