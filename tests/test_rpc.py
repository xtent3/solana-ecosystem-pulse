import unittest

from solpulse.rpc import RpcError, extract_result


class ExtractResultTests(unittest.TestCase):
    def test_returns_result_from_valid_rpc_response(self):
        payload = {"jsonrpc": "2.0", "id": 1, "result": {"absoluteSlot": 123}}

        self.assertEqual(extract_result(payload), {"absoluteSlot": 123})

    def test_rejects_rpc_error_instead_of_treating_it_as_data(self):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32000, "message": "node unhealthy"},
        }

        with self.assertRaisesRegex(RpcError, "node unhealthy"):
            extract_result(payload)

    def test_rejects_response_without_result(self):
        with self.assertRaisesRegex(RpcError, "missing result"):
            extract_result({"jsonrpc": "2.0", "id": 1})


if __name__ == "__main__":
    unittest.main()
