import json
import unittest

from solpulse.market import HttpJsonClient, collect_economic_snapshot


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class CollectEconomicSnapshotTests(unittest.TestCase):
    def test_preserves_successful_metrics_when_one_source_fails(self):
        payloads = {
            "price": {"solana": {"usd": 72.82, "usd_24h_change": -0.829}},
            "chains": [{"name": "Solana", "tvl": 4_727_213_398.81}],
            "dex": {"total24h": 1_700_234_001.08, "total7d": 11_076_276_640.58, "change_1d": 7.63},
        }

        class FakeClient:
            def get(self, name, url):
                if name == "stablecoins":
                    raise OSError("temporary outage")
                return payloads[name]

        result = collect_economic_snapshot(FakeClient())

        self.assertEqual(result["metrics"]["sol_price_usd"], 72.82)
        self.assertEqual(result["metrics"]["defi_tvl_usd"], 4_727_213_398.81)
        self.assertEqual(result["metrics"]["dex_volume_24h_usd"], 1_700_234_001.08)
        self.assertNotIn("stablecoin_supply_usd", result["metrics"])
        statuses = {item["name"]: item["status"] for item in result["sources"]}
        self.assertEqual(statuses["price"], "ok")
        self.assertEqual(statuses["stablecoins"], "error")
        self.assertIn("temporary outage", result["sources"][2]["error"])

    def test_http_json_client_requests_json_with_timeout(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["user_agent"] = request.get_header("User-agent")
            return FakeResponse({"ok": True})

        client = HttpJsonClient(timeout=9, opener=opener)

        self.assertEqual(client.get("sample", "https://example.invalid/data"), {"ok": True})
        self.assertEqual(captured, {"url": "https://example.invalid/data", "timeout": 9, "user_agent": "solpulse/1.0"})


if __name__ == "__main__":
    unittest.main()
