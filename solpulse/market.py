"""Normalize public Solana market and ecosystem API payloads."""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from typing import Any


SOURCE_URLS = {
    "price": "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true",
    "chains": "https://api.llama.fi/v2/chains",
    "stablecoins": "https://stablecoins.llama.fi/stablecoinchains",
    "dex": "https://api.llama.fi/overview/dexs/Solana?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true",
}


def _solana_row(rows: list[dict[str, Any]], description: str) -> dict[str, Any]:
    for row in rows:
        if str(row.get("name", "")).casefold() == "solana":
            return row
    raise ValueError(f"missing Solana {description} row")


def build_economic_metrics(payloads: dict[str, Any]) -> dict[str, float]:
    """Return normalized economic metrics or fail on incomplete source data."""
    try:
        price = payloads["price"]["solana"]
        chain = _solana_row(payloads["chains"], "chain")
        stablecoins = _solana_row(payloads["stablecoins"], "stablecoin")
        dex = payloads["dex"]
        pegged_usd = stablecoins["totalCirculatingUSD"]["peggedUSD"]
        return {
            "sol_price_usd": round(float(price["usd"]), 2),
            "sol_price_change_24h_pct": round(float(price["usd_24h_change"]), 2),
            "defi_tvl_usd": round(float(chain["tvl"]), 2),
            "stablecoin_supply_usd": round(float(pegged_usd), 2),
            "dex_volume_24h_usd": round(float(dex["total24h"]), 2),
            "dex_volume_7d_usd": round(float(dex["total7d"]), 2),
            "dex_volume_change_24h_pct": round(float(dex["change_1d"]), 2),
        }
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("missing Solana"):
            raise
        raise ValueError(f"invalid economic source payload: {exc}") from exc


class HttpJsonClient:
    """Dependency-free JSON client for public read-only ecosystem APIs."""

    def __init__(
        self,
        *,
        timeout: float = 20,
        opener: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        self.timeout = timeout
        self._opener = opener

    def get(self, name: str, url: str) -> Any:
        request = urllib.request.Request(url, headers={"User-Agent": "solpulse/1.0"})
        with self._opener(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))


def _metrics_for_source(name: str, payload: Any) -> dict[str, float]:
    """Normalize one source independently so other sources can survive failures."""
    if name == "price":
        price = payload["solana"]
        return {
            "sol_price_usd": round(float(price["usd"]), 2),
            "sol_price_change_24h_pct": round(float(price["usd_24h_change"]), 2),
        }
    if name == "chains":
        chain = _solana_row(payload, "chain")
        return {"defi_tvl_usd": round(float(chain["tvl"]), 2)}
    if name == "stablecoins":
        chain = _solana_row(payload, "stablecoin")
        value = chain["totalCirculatingUSD"]["peggedUSD"]
        return {"stablecoin_supply_usd": round(float(value), 2)}
    if name == "dex":
        return {
            "dex_volume_24h_usd": round(float(payload["total24h"]), 2),
            "dex_volume_7d_usd": round(float(payload["total7d"]), 2),
            "dex_volume_change_24h_pct": round(float(payload["change_1d"]), 2),
        }
    raise ValueError(f"unknown economic source: {name}")


def collect_economic_snapshot(
    client: HttpJsonClient,
    source_urls: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Collect independent public sources and preserve per-source health."""
    urls = source_urls or SOURCE_URLS
    metrics: dict[str, float] = {}
    sources: list[dict[str, str]] = []
    for name, url in urls.items():
        try:
            payload = client.get(name, url)
            metrics.update(_metrics_for_source(name, payload))
            sources.append({"name": name, "url": url, "status": "ok"})
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            sources.append(
                {"name": name, "url": url, "status": "error", "error": str(exc)}
            )
    return {"metrics": metrics, "sources": sources}
