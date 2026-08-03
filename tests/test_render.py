import json
import unittest

from solpulse.render import render_html, render_json, render_markdown


class RenderSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = {
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
            "alerts": [
                {
                    "code": "example",
                    "severity": "warning",
                    "message": "Unsafe <script>alert('x')</script>",
                }
            ],
            "economics": {
                "metrics": {
                    "sol_price_usd": 72.82,
                    "sol_price_change_24h_pct": -0.83,
                    "defi_tvl_usd": 4_727_213_398.81,
                    "stablecoin_supply_usd": 15_655_014_220.52,
                    "dex_volume_24h_usd": 1_700_234_001.08,
                    "dex_volume_7d_usd": 11_076_276_640.58,
                    "dex_volume_change_24h_pct": 7.63,
                },
                "sources": [
                    {"name": "price", "url": "https://price.invalid", "status": "ok"},
                    {
                        "name": "stablecoins",
                        "url": "https://stable.invalid",
                        "status": "error",
                        "error": "Unsafe <script>alert('source')</script>",
                    },
                ],
            },
        }

    def test_json_round_trips_without_losing_snapshot_fields(self):
        rendered = json.loads(render_json(self.snapshot))
        self.assertEqual(rendered, self.snapshot)

    def test_markdown_contains_network_economics_and_source_health(self):
        rendered = render_markdown(self.snapshot)
        self.assertIn("2026-08-01T12:00:00Z", rendered)
        self.assertIn("123,456", rendered)
        self.assertIn("1,750.00", rendered)
        self.assertIn("$72.82", rendered)
        self.assertIn("$4.73B", rendered)
        self.assertIn("stablecoins", rendered)
        self.assertIn("error", rendered)

    def test_html_contains_same_values_and_escapes_external_text(self):
        rendered = render_html(self.snapshot)
        self.assertIn("2026-08-01T12:00:00Z", rendered)
        self.assertIn("123,456", rendered)
        self.assertIn("1,750.00", rendered)
        self.assertIn("$72.82", rendered)
        self.assertIn("$4.73B", rendered)
        self.assertIn("stablecoins", rendered)
        self.assertNotIn("<script>alert('x')</script>", rendered)
        self.assertIn("&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;", rendered)
        self.assertNotIn("<script>alert('source')</script>", rendered)
        self.assertIn("&lt;script&gt;alert(&#x27;source&#x27;)&lt;/script&gt;", rendered)


if __name__ == "__main__":
    unittest.main()
