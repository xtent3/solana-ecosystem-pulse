"""Collect a coherent Solana network snapshot from an injected RPC client."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Protocol

from solpulse.anomalies import detect_anomalies
from solpulse.market import HttpJsonClient, collect_economic_snapshot
from solpulse.metrics import build_network_metrics


class RpcClient(Protocol):
    def call(self, method: str, params: list[Any] | None = None) -> Any: ...


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def collect_snapshot(
    rpc: RpcClient,
    *,
    source: str,
    generated_at: str | None = None,
    economic_client: HttpJsonClient | None = None,
) -> dict[str, Any]:
    """Collect a timestamped network snapshot with optional ecosystem metrics."""
    rpc_results = {
        "slot": rpc.call("getSlot"),
        "epoch_info": rpc.call("getEpochInfo"),
        "performance_samples": rpc.call("getRecentPerformanceSamples", [2]),
        "vote_accounts": rpc.call("getVoteAccounts"),
        "supply": rpc.call("getSupply", [{"commitment": "finalized"}]),
    }
    metrics = build_network_metrics(rpc_results)
    snapshot: dict[str, Any] = {
        "schema_version": "solpulse/v1",
        "generated_at": generated_at or utc_now(),
        "source": source,
        "metrics": metrics,
        "alerts": detect_anomalies(metrics),
    }
    if economic_client is not None:
        snapshot["economics"] = collect_economic_snapshot(economic_client)
    return snapshot
