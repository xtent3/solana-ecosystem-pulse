"""Derive human-readable Solana network metrics from RPC results."""

from __future__ import annotations

from typing import Any

LAMPORTS_PER_SOL = 1_000_000_000


def _percentage(part: float, total: float) -> float:
    return round((part / total) * 100, 2) if total else 0.0


def build_network_metrics(rpc_results: dict[str, Any]) -> dict[str, Any]:
    """Normalize a coherent network snapshot from raw RPC method results."""
    epoch = rpc_results["epoch_info"]
    samples = rpc_results.get("performance_samples", [])
    votes = rpc_results["vote_accounts"]
    supply = rpc_results["supply"]["value"]

    transactions = sum(float(item["numTransactions"]) for item in samples)
    sampled_seconds = sum(float(item["samplePeriodSecs"]) for item in samples)

    active = votes.get("current", [])
    delinquent = votes.get("delinquent", [])
    active_stake = sum(float(item.get("activatedStake", 0)) for item in active)
    delinquent_stake = sum(float(item.get("activatedStake", 0)) for item in delinquent)

    return {
        "slot": int(rpc_results["slot"]),
        "epoch": int(epoch["epoch"]),
        "epoch_progress_pct": _percentage(
            float(epoch["slotIndex"]), float(epoch["slotsInEpoch"])
        ),
        "tps": round(transactions / sampled_seconds, 2) if sampled_seconds else 0.0,
        "validators_active": len(active),
        "validators_delinquent": len(delinquent),
        "delinquent_stake_pct": _percentage(
            delinquent_stake, active_stake + delinquent_stake
        ),
        "supply_total_sol": round(float(supply["total"]) / LAMPORTS_PER_SOL, 2),
        "supply_circulating_sol": round(
            float(supply["circulating"]) / LAMPORTS_PER_SOL, 2
        ),
    }
