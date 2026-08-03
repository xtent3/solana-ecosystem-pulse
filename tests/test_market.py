import unittest

from solpulse.market import build_economic_metrics


class BuildEconomicMetricsTests(unittest.TestCase):
    def test_normalizes_public_market_and_ecosystem_payloads(self):
        payloads = {
            "price": {"solana": {"usd": 72.82, "usd_24h_change": -0.8293366}},
            "chains": [
                {"name": "Ethereum", "tvl": 1},
                {"name": "Solana", "tvl": 4_727_213_398.81443},
            ],
            "stablecoins": [
                {
                    "name": "Solana",
                    "totalCirculatingUSD": {
                        "peggedUSD": 15_655_014_220.520262,
                        "peggedEUR": 59_440_640.02,
                    },
                }
            ],
            "dex": {
                "total24h": 1_700_234_001.08,
                "total7d": 11_076_276_640.58,
                "change_1d": 7.63,
            },
        }

        metrics = build_economic_metrics(payloads)

        self.assertEqual(
            metrics,
            {
                "sol_price_usd": 72.82,
                "sol_price_change_24h_pct": -0.83,
                "defi_tvl_usd": 4_727_213_398.81,
                "stablecoin_supply_usd": 15_655_014_220.52,
                "dex_volume_24h_usd": 1_700_234_001.08,
                "dex_volume_7d_usd": 11_076_276_640.58,
                "dex_volume_change_24h_pct": 7.63,
            },
        )

    def test_rejects_missing_solana_rows_instead_of_returning_zero(self):
        payloads = {
            "price": {"solana": {"usd": 72.82, "usd_24h_change": 1}},
            "chains": [{"name": "Ethereum", "tvl": 1}],
            "stablecoins": [],
            "dex": {"total24h": 1, "total7d": 2, "change_1d": 3},
        }

        with self.assertRaisesRegex(ValueError, "Solana chain row"):
            build_economic_metrics(payloads)


if __name__ == "__main__":
    unittest.main()
