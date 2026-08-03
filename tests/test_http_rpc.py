import json
import unittest

from solpulse.rpc import HttpRpcClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class HttpRpcClientTests(unittest.TestCase):
    def test_posts_json_rpc_and_returns_extracted_result(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = dict(request.header_items())
            captured["body"] = json.loads(request.data.decode("utf-8"))
            captured["timeout"] = timeout
            return FakeResponse({"jsonrpc": "2.0", "id": 1, "result": 999})

        client = HttpRpcClient(
            "https://rpc.example.invalid",
            timeout=12,
            opener=opener,
        )

        result = client.call("getSlot", [{"commitment": "finalized"}])

        self.assertEqual(result, 999)
        self.assertEqual(captured["url"], "https://rpc.example.invalid")
        self.assertEqual(captured["timeout"], 12)
        self.assertEqual(captured["headers"]["Content-type"], "application/json")
        self.assertEqual(
            captured["body"],
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSlot",
                "params": [{"commitment": "finalized"}],
            },
        )


if __name__ == "__main__":
    unittest.main()
