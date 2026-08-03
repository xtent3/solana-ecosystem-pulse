"""Render one trusted snapshot into JSON, Markdown, and self-contained HTML."""

from __future__ import annotations

import html
import json
from typing import Any


def render_json(snapshot: dict[str, Any]) -> str:
    return json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _compact_usd(value: float) -> str:
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value:,.2f}"


def _economic_markdown(snapshot: dict[str, Any]) -> str:
    economics = snapshot.get("economics")
    if not economics:
        return ""
    metrics = economics.get("metrics", {})
    rows: list[tuple[str, str]] = []
    definitions = [
        ("SOL price", "sol_price_usd", lambda value: f"${value:,.2f}"),
        ("SOL price change (24h)", "sol_price_change_24h_pct", lambda value: f"{value:+.2f}%"),
        ("DeFi TVL", "defi_tvl_usd", _compact_usd),
        ("Stablecoin supply", "stablecoin_supply_usd", _compact_usd),
        ("DEX volume (24h)", "dex_volume_24h_usd", _compact_usd),
        ("DEX volume (7d)", "dex_volume_7d_usd", _compact_usd),
        ("DEX volume change (24h)", "dex_volume_change_24h_pct", lambda value: f"{value:+.2f}%"),
    ]
    for label, key, formatter in definitions:
        if key in metrics:
            rows.append((label, formatter(float(metrics[key]))))
    metric_rows = "\n".join(f"| {label} | {value} |" for label, value in rows)
    source_rows = "\n".join(
        f"| {item['name']} | {item['status']} | {item.get('error', '—')} |"
        for item in economics.get("sources", [])
    )
    return f"""

## Economic and ecosystem snapshot

| Metric | Value |
|---|---:|
{metric_rows}

### Source health

| Source | Status | Detail |
|---|---|---|
{source_rows}
"""


def render_markdown(snapshot: dict[str, Any]) -> str:
    metrics = snapshot["metrics"]
    alerts = snapshot.get("alerts", [])
    alert_lines = (
        "\n".join(
            f"- **{item['severity'].upper()} · {item['code']}** — {item['message']}"
            for item in alerts
        )
        if alerts
        else "- No threshold alerts in this snapshot."
    )
    economics = _economic_markdown(snapshot)
    return f"""# Solana Ecosystem Pulse

Generated: `{snapshot['generated_at']}`  
RPC source: `{snapshot['source']}`

## Network snapshot

| Metric | Value |
|---|---:|
| Slot | {metrics['slot']:,} |
| Epoch | {metrics['epoch']:,} |
| Epoch progress | {metrics['epoch_progress_pct']:.2f}% |
| Observed TPS | {metrics['tps']:,.2f} |
| Active validators | {metrics['validators_active']:,} |
| Delinquent validators | {metrics['validators_delinquent']:,} |
| Delinquent stake | {metrics['delinquent_stake_pct']:.2f}% |
| Total supply | {metrics['supply_total_sol']:,.2f} SOL |
| Circulating supply | {metrics['supply_circulating_sol']:,.2f} SOL |
{economics}

## Alerts

{alert_lines}

> Threshold alerts are deterministic indicators, not investment advice or proof of an outage.
"""


def _economic_html(snapshot: dict[str, Any], esc: Any) -> str:
    economics = snapshot.get("economics")
    if not economics:
        return ""
    metrics = economics.get("metrics", {})
    definitions = [
        ("SOL price", "sol_price_usd", lambda value: f"${value:,.2f}", "CoinGecko"),
        ("DeFi TVL", "defi_tvl_usd", _compact_usd, "DeFiLlama"),
        ("Stablecoin supply", "stablecoin_supply_usd", _compact_usd, "DeFiLlama"),
        ("DEX volume · 24h", "dex_volume_24h_usd", _compact_usd, "DeFiLlama"),
        ("DEX volume · 7d", "dex_volume_7d_usd", _compact_usd, "DeFiLlama"),
        ("DEX change · 24h", "dex_volume_change_24h_pct", lambda value: f"{value:+.2f}%", "DeFiLlama"),
    ]
    cards = "".join(
        f'<article class="card economic"><p>{esc(label)}</p><strong>{esc(formatter(float(metrics[key])))}</strong><span>{esc(note)}</span></article>'
        for label, key, formatter, note in definitions
        if key in metrics
    )
    sources = "".join(
        f'<li class="source {esc(item["status"])}"><b>{esc(item["name"])}</b><span>{esc(item["status"])} · {esc(item.get("error", item["url"]))}</span></li>'
        for item in economics.get("sources", [])
    )
    return f'<section><div class="section-head"><div><div class="eyebrow">Market context</div><h2>Economic & ecosystem pulse</h2></div></div><div class="grid">{cards}</div><h3>Source health</h3><ul>{sources}</ul></section>'


def render_html(snapshot: dict[str, Any]) -> str:
    metrics = snapshot["metrics"]
    alerts = snapshot.get("alerts", [])

    def esc(value: Any) -> str:
        return html.escape(str(value), quote=True)

    cards = [
        ("Observed TPS", f"{metrics['tps']:,.2f}", "60-second RPC samples"),
        ("Current slot", f"{metrics['slot']:,}", f"Epoch {metrics['epoch']:,}"),
        ("Epoch progress", f"{metrics['epoch_progress_pct']:.2f}%", "Current epoch completion"),
        ("Active validators", f"{metrics['validators_active']:,}", f"{metrics['validators_delinquent']:,} delinquent"),
        ("Delinquent stake", f"{metrics['delinquent_stake_pct']:.2f}%", "Share of activated stake"),
        ("Circulating supply", f"{metrics['supply_circulating_sol']:,.2f}", "SOL"),
    ]
    cards_html = "".join(
        f'<article class="card"><p>{esc(label)}</p><strong>{esc(value)}</strong><span>{esc(note)}</span></article>'
        for label, value, note in cards
    )
    alerts_html = (
        "".join(
            f'<li class="alert {esc(item["severity"])}"><b>{esc(item["code"])}</b><span>{esc(item["message"])}</span></li>'
            for item in alerts
        )
        if alerts
        else '<li class="healthy"><b>Healthy snapshot</b><span>No configured thresholds were crossed.</span></li>'
    )
    economics_html = _economic_html(snapshot, esc)
    snapshot_json = html.escape(render_json(snapshot), quote=False)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solana Ecosystem Pulse</title>
<style>
:root{{--ink:#eef2ff;--muted:#9aa6c1;--panel:#121a2c;--line:#26324b;--violet:#8b7cff;--cyan:#48d9d0;--warn:#ffbd69;--critical:#ff6685}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 15% 0,#20204a 0,transparent 34%),#080d18;color:var(--ink);font:15px/1.5 Inter,Segoe UI,sans-serif}}
main{{width:min(1120px,92vw);margin:auto;padding:56px 0 72px}} header{{display:flex;justify-content:space-between;gap:24px;align-items:end;margin-bottom:28px}}
.eyebrow{{color:var(--cyan);font:700 12px/1.2 ui-monospace,monospace;letter-spacing:.16em;text-transform:uppercase}} h1{{font-size:clamp(34px,7vw,72px);line-height:.95;margin:10px 0 16px;max-width:780px;letter-spacing:-.05em}} h2{{margin:5px 0 16px;font-size:24px}} h3{{margin:24px 0 12px;font-size:14px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em}} .lede{{color:var(--muted);max-width:680px;margin:0}}
.stamp{{text-align:right;color:var(--muted);font:13px/1.6 ui-monospace,monospace}} .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}} .network-head{{margin:0 0 14px}}
.card{{background:linear-gradient(145deg,rgba(25,35,59,.96),rgba(14,22,39,.96));border:1px solid var(--line);border-radius:18px;padding:22px;box-shadow:0 18px 45px rgba(15,9,50,.24)}} .card.economic{{background:linear-gradient(145deg,rgba(32,31,69,.96),rgba(14,25,43,.96))}} .card p{{margin:0;color:var(--muted)}} .card strong{{display:block;font-size:32px;letter-spacing:-.04em;margin:8px 0;color:white}} .card span{{color:var(--cyan);font-size:12px}}
section{{margin-top:22px;background:rgba(15,23,40,.86);border:1px solid var(--line);border-radius:18px;padding:22px}} ul{{list-style:none;padding:0;margin:0;display:grid;gap:10px}} li{{display:flex;gap:14px;padding:14px;border-radius:12px;background:#0b1220}} li b{{min-width:160px}} li span{{color:var(--muted)}} .source span{{overflow-wrap:anywhere;word-break:break-word}} .warning b,.source.error b{{color:var(--warn)}} .critical b{{color:var(--critical)}} .healthy b,.source.ok b{{color:var(--cyan)}} details{{margin-top:22px}} pre{{overflow:auto;background:#050914;border:1px solid var(--line);padding:18px;border-radius:14px;color:#b9c8e9}}
footer{{margin-top:24px;color:var(--muted);font-size:12px}} @media(max-width:760px){{header{{display:block}}.stamp{{text-align:left;margin-top:18px}}.grid{{grid-template-columns:1fr}}li{{display:block}}li b{{display:block;margin-bottom:5px}}}}
</style>
</head>
<body><main>
<header><div><div class="eyebrow">Live · dependency-free · auditable</div><h1>Solana Ecosystem Pulse</h1><p class="lede">A reproducible network and ecosystem snapshot generated from public Solana RPC, CoinGecko, and DeFiLlama data.</p></div><div class="stamp">{esc(snapshot['generated_at'])}<br>{esc(snapshot['source'])}</div></header>
<div class="network-head"><div class="eyebrow">Network health</div><h2>Solana mainnet snapshot</h2></div>
<div class="grid">{cards_html}</div>
{economics_html}
<section><h2>Explainable alerts</h2><ul>{alerts_html}</ul></section>
<details><summary>Machine-readable snapshot</summary><pre>{snapshot_json}</pre></details>
<footer>Schema {esc(snapshot['schema_version'])}. Source failures remain visible; unavailable values are never replaced with zero.</footer>
</main></body></html>
"""
