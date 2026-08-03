import json
import tempfile
import unittest
from pathlib import Path

from solpulse.cli import main


class FakeRpc:
    def call(self, method, params=None):
        return {
            "getSlot": 500,
            "getEpochInfo": {
                "epoch": 42,
                "slotIndex": 250,
                "slotsInEpoch": 1000,
                "absoluteSlot": 500,
            },
            "getRecentPerformanceSamples": [
                {"numTransactions": 120_000, "samplePeriodSecs": 60}
            ],
            "getVoteAccounts": {
                "current": [{"activatedStake": 1000}],
                "delinquent": [],
            },
            "getSupply": {
                "value": {
                    "total": 600_000_000 * 1_000_000_000,
                    "circulating": 520_000_000 * 1_000_000_000,
                }
            },
        }[method]


class FakeEconomicClient:
    def get(self, name, url):
        return {
            "price": {"solana": {"usd": 72.82, "usd_24h_change": -0.829}},
            "chains": [{"name": "Solana", "tvl": 4_727_213_398.81}],
            "stablecoins": [
                {
                    "name": "Solana",
                    "totalCirculatingUSD": {"peggedUSD": 15_655_014_220.52},
                }
            ],
            "dex": {
                "total24h": 1_700_234_001.08,
                "total7d": 11_076_276_640.58,
                "change_1d": 7.63,
            },
        }[name]


class CliTests(unittest.TestCase):
    def test_main_generates_all_artifacts_in_requested_directory(self):
        endpoints = []
        economic_timeouts = []

        def rpc_factory(endpoint, *, timeout):
            endpoints.append((endpoint, timeout))
            return FakeRpc()

        def economic_factory(*, timeout):
            economic_timeouts.append(timeout)
            return FakeEconomicClient()

        with tempfile.TemporaryDirectory() as directory:
            code = main(
                [
                    "--endpoint",
                    "https://example.invalid/rpc",
                    "--output",
                    directory,
                    "--timeout",
                    "12",
                ],
                rpc_factory=rpc_factory,
                economic_factory=economic_factory,
                generated_at="2026-08-01T12:00:00Z",
            )

            self.assertEqual(code, 0)
            self.assertEqual(endpoints, [("https://example.invalid/rpc", 12.0)])
            self.assertEqual(economic_timeouts, [12.0])
            output = Path(directory)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {"snapshot.json", "report.md", "dashboard.html", "premium_dashboard.html"},
            )
            snapshot = json.loads((output / "snapshot.json").read_text("utf-8"))
            self.assertEqual(snapshot["source"], "https://example.invalid/rpc")
            self.assertEqual(snapshot["generated_at"], "2026-08-01T12:00:00Z")
            self.assertEqual(snapshot["economics"]["metrics"]["sol_price_usd"], 72.82)


if __name__ == "__main__":
    unittest.main()
