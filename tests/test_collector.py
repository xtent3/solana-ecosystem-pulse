import unittest

from solpulse.collector import collect_snapshot


class FakeRpc:
    def __init__(self):
        self.calls = []

    def call(self, method, params=None):
        self.calls.append((method, params or []))
        responses = {
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
        }
        return responses[method]


class CollectSnapshotTests(unittest.TestCase):
    def test_collects_one_coherent_snapshot_with_expected_rpc_calls(self):
        rpc = FakeRpc()

        snapshot = collect_snapshot(
            rpc,
            source="https://example.invalid/rpc",
            generated_at="2026-08-01T12:00:00Z",
        )

        self.assertEqual(
            rpc.calls,
            [
                ("getSlot", []),
                ("getEpochInfo", []),
                ("getRecentPerformanceSamples", [2]),
                ("getVoteAccounts", []),
                ("getSupply", [{"commitment": "finalized"}]),
            ],
        )
        self.assertEqual(snapshot["schema_version"], "solpulse/v1")
        self.assertEqual(snapshot["generated_at"], "2026-08-01T12:00:00Z")
        self.assertEqual(snapshot["source"], "https://example.invalid/rpc")
        self.assertEqual(snapshot["metrics"]["tps"], 2000.0)
        self.assertEqual(snapshot["alerts"], [])
        self.assertNotIn("economics", snapshot)

    def test_includes_optional_economic_metrics_and_source_health(self):
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

        snapshot = collect_snapshot(
            FakeRpc(),
            source="https://example.invalid/rpc",
            generated_at="2026-08-01T12:00:00Z",
            economic_client=FakeEconomicClient(),
        )

        self.assertEqual(snapshot["economics"]["metrics"]["sol_price_usd"], 72.82)
        self.assertEqual(snapshot["economics"]["metrics"]["defi_tvl_usd"], 4_727_213_398.81)
        self.assertTrue(
            all(item["status"] == "ok" for item in snapshot["economics"]["sources"])
        )


if __name__ == "__main__":
    unittest.main()
