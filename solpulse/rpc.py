"""Minimal Solana JSON-RPC primitives."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from typing import Any


class RpcError(RuntimeError):
    """Raised when an RPC response cannot be used as trustworthy data."""


def extract_result(payload: dict[str, Any]) -> Any:
    """Return a JSON-RPC result or raise a descriptive error."""
    error = payload.get("error")
    if error is not None:
        if isinstance(error, dict):
            message = str(error.get("message", error))
        else:
            message = str(error)
        raise RpcError(message)
    if "result" not in payload:
        raise RpcError("missing result in RPC response")
    return payload["result"]


class HttpRpcClient:
    """Small dependency-free JSON-RPC client with an injectable opener."""

    def __init__(
        self,
        endpoint: str,
        *,
        timeout: float = 30,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self._opener = opener
        self._request_id = 0

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": method,
            "params": params or [],
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "solpulse/1.0"},
            method="POST",
        )
        try:
            with self._opener(request, timeout=self.timeout) as response:
                decoded = json.loads(response.read().decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RpcError(f"RPC transport failed for {method}: {exc}") from exc
        if not isinstance(decoded, dict):
            raise RpcError(f"invalid RPC response for {method}: expected object")
        return extract_result(decoded)
