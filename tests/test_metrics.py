import unittest

from solpulse.metrics import build_network_metrics


class BuildNetworkMetricsTests(unittest.TestCase):
    def test_derives_network_health_metrics_from_rpc_results(self):
        rpc_results = {
            "slot": 500,
            "epoch_info": {
                "epoch": 42,
                "slotIndex": 250,
                "slotsInEpoch": 1000,
                "absoluteSlot": 500,
            },
            "performance_samples": [
                {"numTransactions": 120_000, "samplePeriodSecs": 60},
                {"numTransactions": 90_000, "samplePeriodSecs": 60},
            ],
            "vote_accounts": {
                "current": [{"activatedStake": 700}, {"activatedStake": 300}],
                "delinquent": [{"activatedStake": 25}],
            },
            "supply": {
                "value": {
                    "total": 600_000_000 * 1_000_000_000,
                    "circulating": 520_000_000 * 1_000_000_000,
                }
            },
        }

        metrics = build_network_metrics(rpc_results)

        self.assertEqual(metrics["slot"], 500)
        self.assertEqual(metrics["epoch"], 42)
        self.assertEqual(metrics["epoch_progress_pct"], 25.0)
        self.assertEqual(metrics["tps"], 1750.0)
        self.assertEqual(metrics["validators_active"], 2)
        self.assertEqual(metrics["validators_delinquent"], 1)
        self.assertEqual(metrics["delinquent_stake_pct"], 2.44)
        self.assertEqual(metrics["supply_total_sol"], 600_000_000.0)
        self.assertEqual(metrics["supply_circulating_sol"], 520_000_000.0)


if __name__ == "__main__":
    unittest.main()
