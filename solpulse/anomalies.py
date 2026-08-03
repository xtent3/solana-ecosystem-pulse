"""Explainable threshold-based anomaly detection."""

from __future__ import annotations

from typing import Any


def detect_anomalies(
    metrics: dict[str, Any],
    *,
    min_tps: float = 1_000.0,
    max_delinquent_stake_pct: float = 5.0,
) -> list[dict[str, str]]:
    """Return deterministic alerts for network-health threshold breaches."""
    alerts: list[dict[str, str]] = []
    tps = float(metrics.get("tps", 0.0))
    delinquent_stake = float(metrics.get("delinquent_stake_pct", 0.0))

    if tps < min_tps:
        alerts.append(
            {
                "code": "low_tps",
                "severity": "warning",
                "message": f"Observed TPS {tps} is below threshold {float(min_tps)}.",
            }
        )
    if delinquent_stake > max_delinquent_stake_pct:
        alerts.append(
            {
                "code": "high_delinquent_stake",
                "severity": "critical",
                "message": (
                    f"Delinquent stake {delinquent_stake}% exceeds threshold "
                    f"{float(max_delinquent_stake_pct)}%."
                ),
            }
        )
    return alerts
