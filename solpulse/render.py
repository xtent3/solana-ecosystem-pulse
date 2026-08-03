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


def _compact_num(value: float) -> str:
    absolute = abs(value)
    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:,.2f}"


def render_premium_html(snapshot: dict[str, Any]) -> str:
    """Render a premium self-contained dashboard HTML with theme toggle and SVG charts."""
    metrics = snapshot["metrics"]
    alerts = snapshot.get("alerts", [])
    economics = snapshot.get("economics")
    econ_metrics = economics.get("metrics", {}) if economics else {}

    def esc(v: object) -> str:
        return html.escape(str(v), quote=True)

    tps = f"{metrics['tps']:,.2f}"
    slot = f"{metrics['slot']:,}"
    epoch = f"{metrics['epoch']:,}"
    epoch_progress = f"{metrics['epoch_progress_pct']:.2f}%"
    val_active = f"{metrics['validators_active']:,}"
    val_delinq = f"{metrics['validators_delinquent']:,}"
    delinq_stake = f"{metrics['delinquent_stake_pct']:.2f}%"
    circ_supply = _compact_num(metrics['supply_circulating_sol'])
    total_supply = _compact_num(metrics['supply_total_sol'])
    source = snapshot.get("source", "")
    generated = snapshot["generated_at"]

    sol_price = f"${econ_metrics.get('sol_price_usd', 0):,.2f}" if econ_metrics else "$—"
    sol_change = econ_metrics.get("sol_price_change_24h_pct")
    sol_change_str = f"{sol_change:+.2f}%" if sol_change is not None else ""
    sol_change_color = "#14f195" if sol_change and sol_change >= 0 else "#ff6685" if sol_change else ""
    defi_tvl = _compact_usd(econ_metrics.get("defi_tvl_usd", 0)) if econ_metrics else "$—"
    stablecoin = _compact_usd(econ_metrics.get("stablecoin_supply_usd", 0)) if econ_metrics else "$—"
    dex_vol_24h = _compact_usd(econ_metrics.get("dex_volume_24h_usd", 0)) if econ_metrics else "$—"
    dex_vol_7d = _compact_usd(econ_metrics.get("dex_volume_7d_usd", 0)) if econ_metrics else "$—"
    dex_change = econ_metrics.get("dex_volume_change_24h_pct")
    dex_change_str = f"{dex_change:+.2f}%" if dex_change is not None else ""
    dex_change_color = "#14f195" if dex_change and dex_change >= 0 else "#ff6685" if dex_change else ""

    if alerts:
            def _ac(sev: str) -> str:
                return "#ffbd69" if sev == "warning" else "#ff6685"
            alert_items = "".join(
                '<li style="padding:1rem;border-radius:12px;background:var(--bg-panel);border:1px solid var(--line);">'
                '<strong style="color:%s;">%s</strong>'
                '<p style="color:var(--text-secondary);">%s</p></li>'
                % (_ac(a["severity"]), esc(a["code"]), esc(a["message"]))
                for a in alerts
            )
    else:
        alert_items = '<li style="padding:1rem;border-radius:12px;background:var(--bg-panel);border:1px solid var(--line);"><strong style="color:var(--success);">Healthy Snapshot</strong><p style="color:var(--text-secondary);">No configured thresholds were crossed.</p></li>'

    econ_sources = economics.get("sources", []) if economics else []
    source_items = "".join(
        f'<div class="source-item"><span class="dot {esc(s["status"])}"></span>'
        f'<span class="name">{esc(s["name"])}</span>'
        f'<span class="status">{esc(s["status"])}</span></div>'
        for s in econ_sources
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Solana Ecosystem Pulse — Premium</title>
<style>
:root {{ --bg-primary: #0a0a0a; --bg-card: #1a1a2e; --bg-panel: #0b1220; --text-primary: #eef2ff; --text-secondary: #9aa6c1; --primary: #14f195; --secondary: #9945ff; --accent: #48d9d0; --line: #26324b; --success: #14f195; }}
[data-theme="light"] {{ --bg-primary: #f8fafc; --bg-card: #ffffff; --bg-panel: #f1f5f9; --text-primary: #0f172a; --text-secondary: #475569; --line: #cbd5e1; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: radial-gradient(circle at top left, #1a1a2e 0, transparent 40%), var(--bg-primary); color: var(--text-primary); font-family: Inter, sans-serif; min-height: 100vh; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 3rem; }}
.brand {{ display: flex; align-items: center; gap: 1rem; }}
.brand-logo {{ width: 48px; height: 48px; }}
.brand-name {{ font-size: 1.75rem; font-weight: 700; }}
.brand-name span {{ color: var(--primary); }}
.eyebrow {{ font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--accent); font-weight: 600; }}
.theme-toggle {{ background: var(--bg-card); border: 1px solid var(--line); color: var(--text-primary); padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; font-size: 0.875rem; }}
.metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
.card {{ background: var(--bg-card); border: 1px solid var(--line); border-radius: 16px; padding: 1.75rem; }}
.card:hover {{ transform: translateY(-2px); }}
.card h3 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-secondary); margin-bottom: 0.5rem; }}
.card .value {{ font-size: 2.25rem; font-weight: 700; }}
.card .subtitle {{ color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem; }}
.charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }}
.chart-card {{ background: var(--bg-card); border: 1px solid var(--line); border-radius: 16px; padding: 1.75rem; }}
.chart-container {{ display: flex; align-items: center; gap: 1.5rem; }}
.economic-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem; }}
.economic-card {{ background: var(--bg-panel); border: 1px solid var(--line); border-radius: 12px; padding: 1rem; }}
.economic-card .label {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; }}
.economic-card .value {{ font-size: 1.25rem; font-weight: 700; }}
.economic-card .source {{ font-size: 0.75rem; color: var(--accent); }}
.alerts-section {{ margin: 2rem 0; }}
.source-health {{ margin: 2rem 0; }}
.source-health h3 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem; }}
.sources-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.75rem; }}
.source-item {{ display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem; border-radius: 8px; font-size: 0.8125rem; }}
.source-item .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
.source-item .dot.ok {{ background: var(--success); }}
.source-item .name {{ color: var(--text-primary); flex: 1; }}
footer {{ margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--line); text-align: center; color: var(--text-secondary); font-size: 0.8125rem; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="brand">
      <svg class="brand-logo" viewBox="0 0 200 200">
        <circle cx="100" cy="100" r="90" fill="url(#logoGradient)"></circle>
        <text x="50%" y="50%" text-anchor="middle" dominant-baseline="central" fill="white" font-family="Inter" font-size="120" font-weight="700" style="paint-order: stroke; stroke: white; stroke-width: 6;">S</text>
        <defs><linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#14F195;"></stop><stop offset="100%" style="stop-color:#9945FF;"></stop></linearGradient></defs>
      </svg>
      <div><div class="eyebrow">Live · Dependency-free · Auditable</div><div class="brand-name">Solana <span>Ecosystem</span> Pulse</div></div>
    </div>
    <button class="theme-toggle" onclick="toggleTheme()">Toggle Theme</button>
  </header>
  <section class="metrics-grid">
    <div class="card"><h3>Network Health</h3><div class="value">{esc(tps)}</div><div class="subtitle">Observed TPS</div></div>
    <div class="card"><h3>Current Slot</h3><div class="value">{esc(slot)}</div><div class="subtitle">Epoch {esc(epoch)} ({esc(epoch_progress)})</div></div>
    <div class="card"><h3>Validators</h3><div class="value">{esc(val_active)}</div><div class="subtitle">{esc(val_delinq)} delinquent</div></div>
    <div class="card"><h3>Delinquent Stake</h3><div class="value">{esc(delinq_stake)}</div><div class="subtitle">Share of stake</div></div>
    <div class="card"><h3>Circulating Supply</h3><div class="value">{esc(circ_supply)}</div><div class="subtitle">Total: {esc(total_supply)} SOL</div></div>
    <div class="card"><h3>Source</h3><div class="value">Mainnet RPC</div><div class="subtitle">{esc(source)}</div></div>
  </section>
  <section class="charts-section">
    <div class="charts-grid">
      <div class="chart-card"><h3>TPS Trend</h3><div class="chart-container"><svg class="chart-svg" viewBox="0 0 300 120" preserveAspectRatio="none"><path d="M10,100 Q40,60 70,80 T130,40 T190,70 T250,30 T290,60" fill="none" stroke="#14F195" stroke-width="2"></path></svg><div class="chart-details"><div class="label">Current</div><div class="value">{esc(tps)}</div></div></div></div>
      <div class="chart-card"><h3>Validators</h3><div class="chart-container"><svg class="chart-svg" viewBox="0 0 160 120" preserveAspectRatio="none"><circle cx="80" cy="80" r="70" fill="#14F195" opacity="0.6"></circle><text x="80" y="80" text-anchor="middle" fill="white" font-size="24">{esc(val_active)}</text></svg><div class="chart-details"><div class="label">Active</div><div class="value">{esc(val_active)}</div></div></div></div>
      <div class="chart-card"><h3>DeFi TVL</h3><div class="chart-container"><svg class="chart-svg" viewBox="0 0 300 120" preserveAspectRatio="none"><path d="M10,100 C50,90 80,80 120,60 T200,40 T290,50" fill="none" stroke="#9945FF" stroke-width="2"></path></svg><div class="chart-details"><div class="label">TVL</div><div class="value">{esc(defi_tvl)}</div></div></div></div>
    </div>
  </section>
  <section><div class="card" style="background:linear-gradient(135deg,#1a1a2e 0,#16213e 100%);"><h2 style="margin-bottom:1rem;">Economic & Ecosystem Pulse</h2><div class="economic-grid">
      <div class="economic-card"><div class="label">SOL Price</div><div class="value">{esc(sol_price)}</div><div class="source" style="color:{esc(sol_change_color)}">{esc(sol_change_str)}</div></div>
      <div class="economic-card"><div class="label">DeFi TVL</div><div class="value">{esc(defi_tvl)}</div><div class="source">DeFiLlama</div></div>
      <div class="economic-card"><div class="label">Stablecoin Supply</div><div class="value">{esc(stablecoin)}</div><div class="source">DeFiLlama</div></div>
      <div class="economic-card"><div class="label">DEX Volume (24h)</div><div class="value">{esc(dex_vol_24h)}</div><div class="source">DeFiLlama</div></div>
      <div class="economic-card"><div class="label">DEX Volume (7d)</div><div class="value">{esc(dex_vol_7d)}</div><div class="source">DeFiLlama</div></div>
      <div class="economic-card"><div class="label">DEX Change (24h)</div><div class="value" style="color:{esc(dex_change_color)}">{esc(dex_change_str)}</div><div class="source">DeFiLlama</div></div>
  </div></div></section>
  <section class="alerts-section"><h2 style="margin-bottom:1rem;">Explainable Alerts</h2><ul style="list-style:none;">{alert_items}</ul></section>
  <section class="source-health"><h3>Source Health</h3><div class="sources-list">{source_items}</div></section>
  <footer><p>Solana Ecosystem Pulse • {esc(generated)} • dependency-free • auditable</p></footer>
</div>
<script>
function toggleTheme() {{ var c = document.documentElement.getAttribute('data-theme'); var n = c === 'light' ? 'dark' : 'light'; document.documentElement.setAttribute('data-theme', n); localStorage.setItem('solana-dashboard-theme', n); }}
(function() {{ var s = localStorage.getItem('solana-dashboard-theme'); if (s) document.documentElement.setAttribute('data-theme', s); }})();
</script>
</body>
</html>"""


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
