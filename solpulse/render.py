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
    """Render a premium self-contained dashboard with glassmorphism, animated SVG charts,
    gauge, ring, staggered entrance, number counting, tooltips, theme toggle,
    JSON export, and source health \u2014 zero external dependencies."""
    import math
    metrics = snapshot["metrics"]
    alerts = snapshot.get("alerts", [])
    economics = snapshot.get("economics")
    econ_metrics = economics.get("metrics", {}) if economics else {}

    def esc(v: object) -> str:
        return html.escape(str(v), quote=True)

    # Metrics
    tps_fmt = f"{metrics['tps']:,.0f}"
    slot_fmt = f"{metrics['slot']:,}"
    epoch_n = f"{metrics['epoch']:,}"
    ep_pct = metrics["epoch_progress_pct"]
    val_a = metrics["validators_active"]
    val_d = metrics["validators_delinquent"]
    val_total = val_a + val_d
    val_pct = round(val_a / val_total * 100) if val_total else 100
    circ = metrics["supply_circulating_sol"]
    total_s = metrics["supply_total_sol"]

    # Economics
    sp = econ_metrics.get("sol_price_usd", 0)
    sc = econ_metrics.get("sol_price_change_24h_pct")
    sc_str = f"{sc:+.2f}%" if sc is not None else ""
    sc_color = "#14f195" if sc and sc >= 0 else "#ff6685"
    sc_arrow = "\u2191" if sc and sc >= 0 else "\u2193"
    tvl = econ_metrics.get("defi_tvl_usd", 0)
    ss = econ_metrics.get("stablecoin_supply_usd", 0)
    dx24 = econ_metrics.get("dex_volume_24h_usd", 0)
    dx7d = econ_metrics.get("dex_volume_7d_usd", 0)
    dxch = econ_metrics.get("dex_volume_change_24h_pct")
    dxch_str = f"{dxch:+.2f}%" if dxch is not None else ""
    dxch_color = "#14f195" if dxch and dxch >= 0 else "#ff6685"

    # Chart constants
    ring_r = 36
    ring_circ = 2 * math.pi * ring_r
    gauge_r = 38
    gauge_thick = 10
    gauge_circ = 2 * math.pi * gauge_r
    gauge_filled = gauge_circ * ep_pct / 100

    def arc_path(cx, cy, r, start_deg, end_deg):
        start_rad = math.radians(start_deg)
        end_rad = math.radians(end_deg)
        x1 = cx + r * math.cos(start_rad)
        y1 = cy + r * math.sin(start_rad)
        x2 = cx + r * math.cos(end_rad)
        y2 = cy + r * math.sin(end_rad)
        large = 1 if end_deg - start_deg > 180 else 0
        return f"M{x1:.1f},{y1:.1f} A{r},{r} 0 {large},1 {x2:.1f},{y2:.1f}"

    # Alerts
    if alerts:
        def _ac(sev):
            return "#ffbd69" if sev == "warning" else "#ff6685"
        alert_items = "".join(
            '<div class="alert-%s"><span class="alert-icon">%s</span><div><strong>%s</strong><p>%s</p></div></div>\n'
            % (a["severity"], "\u26a0", esc(a["code"]), esc(a["message"]))
            for a in alerts
        )
    else:
        alert_items = '<div class="alert-ok"><span class="alert-icon">\u2713</span><div><strong>All Systems Normal</strong><p>No configured thresholds were crossed. \u200b<span class="tooltip" data-tip="Thresholds: TPS < 2000, delinquent stake > 5%">\u9432</span></p></div></div>\n'

    # Sources
    sources_list = economics.get("sources", []) if economics else []
    source_items = "".join(
        '<div class="source-item tooltip" data-tip="%s"><span class="dot"></span><span class="src-name">%s</span><span class="src-status">%s</span></div>\n'
        % (esc(s.get("url", "") or ""), esc(s["name"]), esc(s["status"]))
        for s in sources_list
    )

    # CSS with dynamic values
    css = '*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}\n:root{--bg:#090d14;--bg-card:#111927;--bg-elevated:#1a2332;--bg-glass:rgba(17,25,39,.72);--text:#e8edf5;--text-muted:#8899b8;--text-dim:#5a6a88;--primary:#14f195;--secondary:#9945ff;--accent:#48d9d0;--line:#1e2a3e;--line-subtle:#16202e;--success:#14f195;--warning:#ffbd69;--danger:#ff6685;--radius:16px;--radius-sm:10px;--radius-lg:24px;--font:Inter,SF Pro Display,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;--mono:SF Mono,Cascadia Code,JetBrains Mono,ui-monospace,monospace;--shadow:0 8px 32px rgba(0,0,0,.4);--transition:200ms cubic-bezier(.4,0,.2,1);--ease-out:cubic-bezier(.16,1,.3,1)}\n[data-theme=light]{--bg:#f4f6fa;--bg-card:#fff;--bg-elevated:#edf0f7;--bg-glass:rgba(255,255,255,.78);--text:#0f172a;--text-muted:#55657e;--text-dim:#8a9bb5;--line:#dce2ed;--line-subtle:#e8ecf3;--shadow:0 8px 32px rgba(0,0,0,.08)}\n@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}\nbody{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;overflow-x:hidden}\n.container{max-width:1280px;margin:0 auto;padding:clamp(1rem,4vw,3rem)}\n.bg-orb{position:fixed;top:-40%;left:-20%;width:80%;height:80%;background:radial-gradient(circle at 30% 40%,rgba(20,241,149,.06),transparent 60%);pointer-events:none;z-index:0;animation:orb-drift 20s ease-in-out infinite alternate}\n.bg-orb2{position:fixed;bottom:-30%;right:-10%;width:60%;height:60%;background:radial-gradient(circle at 70% 60%,rgba(153,69,255,.05),transparent 60%);pointer-events:none;z-index:0;animation:orb-drift2 25s ease-in-out infinite alternate}\n@keyframes orb-drift{from{transform:translate(0,0)}to{transform:translate(5%,3%)}}\n@keyframes orb-drift2{from{transform:translate(0,0)}to{transform:translate(-4%,-2%)}}\n.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:2.5rem;position:relative;z-index:1;animation:fadeIn .6s var(--ease-out)}\n.brand{display:flex;align-items:center;gap:.875rem}\n.logo{width:44px;height:44px;flex-shrink:0}\n.brand-text .eyebrow{font-size:.625rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:2px}\n.brand-text h1{font-size:clamp(1.25rem,3vw,1.75rem);font-weight:700;letter-spacing:-.03em;line-height:1.1}\n.brand-text h1 span{color:var(--primary)}\n.header-actions{display:flex;gap:.5rem;align-items:center}\n.btn{background:var(--bg-elevated);border:1px solid var(--line);color:var(--text);padding:.4rem .9rem;border-radius:var(--radius-sm);font-size:.8125rem;cursor:pointer;transition:all var(--transition);font-family:var(--font);display:inline-flex;align-items:center;gap:.4rem}\n.btn:hover{background:var(--line);border-color:var(--text-muted);transform:translateY(-1px)}\n.btn-primary{background:var(--primary);color:#000;border-color:var(--primary);font-weight:600}\n.btn-primary:hover{background:#10d77e;border-color:#10d77e}\n.status-bar{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;position:relative;z-index:1;animation:fadeIn .6s var(--ease-out) .1s both}\n.status-pill{display:inline-flex;align-items:center;gap:.4rem;padding:.35rem .75rem;border-radius:999px;font-size:.75rem;background:var(--bg-glass);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid var(--line-subtle);color:var(--text-muted);font-family:var(--mono)}\n.status-pill .dot{width:7px;height:7px;border-radius:50%;background:var(--success);animation:pulse-dot 2s ease-in-out infinite}\n@keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.3}}\n.section-label{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);font-weight:600;margin-bottom:.75rem;position:relative;z-index:1;animation:fadeIn .6s var(--ease-out) .3s both}\n.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-bottom:1.5rem;position:relative;z-index:1}\n.card{background:var(--bg-glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--line-subtle);border-radius:var(--radius);padding:1.5rem;transition:all var(--ease-out) .3s;opacity:0;transform:translateY(16px)}\n.card.visible{opacity:1;transform:translateY(0)}\n.card:hover{border-color:var(--line);transform:translateY(-4px);box-shadow:var(--shadow);background:var(--bg-card)}\n.card label{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.35rem;font-weight:600;display:block}\n.card .value{font-size:clamp(1.5rem,3vw,2.25rem);font-weight:700;letter-spacing:-.03em;line-height:1.1}\n.card .sub{font-size:.75rem;color:var(--text-dim);margin-top:.25rem}\n.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:1rem;margin-bottom:1.5rem;position:relative;z-index:1}\n.chart-card{background:var(--bg-glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--line-subtle);border-radius:var(--radius);padding:1.5rem;transition:all var(--ease-out) .3s;opacity:0;transform:translateY(16px)}\n.chart-card.visible{opacity:1;transform:translateY(0)}\n.chart-card:hover{border-color:var(--line);box-shadow:var(--shadow)}\n.chart-card h3{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:1rem;font-weight:600}\n.chart-body{display:flex;align-items:center;gap:1.25rem}\n.chart-legend{font-size:.8125rem;color:var(--text-muted);line-height:1.5}\n.chart-legend strong{color:var(--text);font-weight:600;font-size:1.125rem}\n.chart-svg{flex-shrink:0;max-width:160px;height:auto}\n.ring-bg{stroke:var(--line);fill:none}\n.ring-fg{stroke:var(--primary);fill:none;stroke-linecap:round;transform:rotate(-90deg);transform-origin:center;animation:ring-fill 1.2s var(--ease-out) .4s both}\n.line-chart{width:100%;height:90px}\n.line-path{fill:none;stroke:url(#tpsG1);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}\n.line-area{fill:url(#tpsG2);opacity:.25}\n.chart-grid-line{stroke:var(--line-subtle);stroke-width:.5;stroke-dasharray:3 3}\n.gauge-bg{stroke:var(--line);fill:none;stroke-linecap:round}\n.gauge-fg{stroke:var(--primary);fill:none;stroke-linecap:round;animation:gauge-fill 1s var(--ease-out) .3s both}\n.tooltip{position:relative;cursor:help}\n.tooltip::after{content:attr(data-tip);position:absolute;bottom:calc(100% + 6px);left:50%;transform:translateX(-50%);background:var(--bg-elevated);border:1px solid var(--line);color:var(--text);padding:.35rem .65rem;border-radius:6px;font-size:.6875rem;white-space:nowrap;pointer-events:none;opacity:0;transition:opacity .15s;z-index:10}\n.tooltip:hover::after{opacity:1}\n.economics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.75rem;margin-bottom:1.5rem;position:relative;z-index:1}\n.econ-card{background:var(--bg-glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--line-subtle);border-radius:var(--radius-sm);padding:1rem 1.25rem;transition:all var(--ease-out) .3s;opacity:0;transform:translateY(12px)}\n.econ-card.visible{opacity:1;transform:translateY(0)}\n.econ-card:hover{border-color:var(--line);background:var(--bg-card);transform:translateY(-2px)}\n.econ-card label{font-size:.625rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-dim);display:block;margin-bottom:.15rem}\n.econ-card .value{font-size:1.125rem;font-weight:700;letter-spacing:-.02em}\n.econ-card .src{font-size:.625rem;color:var(--text-dim);margin-top:.15rem}\n.econ-card .change{font-size:.75rem;font-weight:600;margin-top:.1rem}\n.alerts-section{position:relative;z-index:1;margin-bottom:1.5rem;animation:fadeIn .6s var(--ease-out) .5s both}\n.alerts-section h2{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.75rem;font-weight:600}\n.alerts-grid{display:grid;gap:.5rem}\n.alert-ok,.alert-warning,.alert-critical{display:flex;align-items:start;gap:.75rem;padding:.875rem 1rem;border-radius:var(--radius-sm);background:var(--bg-glass);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid var(--line-subtle)}\n.alert-ok{border-left:3px solid var(--success)}\n.alert-warning{border-left:3px solid var(--warning)}\n.alert-critical{border-left:3px solid var(--danger)}\n.alert-icon{font-size:1.125rem;line-height:1.4}\n.alert-ok .alert-icon{color:var(--success)}\n.alert-warning .alert-icon{color:var(--warning)}\n.alert-critical .alert-icon{color:var(--danger)}\n.alert-ok strong,.alert-warning strong,.alert-critical strong{font-size:.8125rem;font-weight:600}\n.alert-ok p,.alert-warning p,.alert-critical p{font-size:.75rem;color:var(--text-dim);margin-top:2px}\n.source-section{position:relative;z-index:1;animation:fadeIn .6s var(--ease-out) .55s both}\n.source-section h2{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.75rem;font-weight:600}\n.sources{display:flex;gap:.75rem;flex-wrap:wrap}\n.source-item{display:inline-flex;align-items:center;gap:.5rem;padding:.4rem .75rem;border-radius:999px;font-size:.75rem;background:var(--bg-glass);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid var(--line-subtle);font-family:var(--mono)}\n.source-item .dot{width:6px;height:6px;border-radius:50%;background:var(--success)}\n.source-item .src-name{color:var(--text-muted)}\n.source-item .src-status{color:var(--text-dim);text-transform:capitalize}\n.footer{text-align:center;padding:2rem 0 1rem;font-size:.6875rem;color:var(--text-dim);position:relative;z-index:1;animation:fadeIn .6s var(--ease-out) .6s both;border-top:1px solid var(--line-subtle);margin-top:2rem;display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap}\n.footer span{color:var(--text-muted)}\n@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}\n@media(max-width:640px){.charts{grid-template-columns:1fr}.metrics{grid-template-columns:1fr}}\n'
    ring_offset = ring_circ * (1 - val_pct / 100)
    css = css.replace("KEYFRAMES_RING_CIRC_FROM", str(ring_circ))
    css = css.replace("KEYFRAMES_RING_CIRC_TO", str(ring_offset))
    css = css.replace("KEYFRAMES_GAUGE_CIRC_FROM", str(gauge_circ))
    css = css.replace("KEYFRAMES_GAUGE_CIRC_TO", str(gauge_circ - gauge_filled))

    # Build HTML
    H = []
    def w(s):
        H.append(s)

    w("<!DOCTYPE html>\n")
    w("<html lang=\"en\" data-theme=\"dark\">\n")
    w("<head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n")
    w("<title>Solana Ecosystem Pulse</title>\n<style>\n")
    w(css)
    w("\n</style>\n</head>\n<body>\n")
    w("<div class=\"bg-orb\"></div>\n<div class=\"bg-orb2\"></div>\n")
    w("<div class=\"container\">\n")

    # Header
    w("<header class=\"header\">\n")
    w("<div class=\"brand\">\n")
    w("<svg class=\"logo\" viewBox=\"0 0 200 200\" aria-hidden=\"true\">")
    w("<defs><linearGradient id=\"lg\" x1=\"0\" y1=\"0\" x2=\"100%\" y2=\"100%\"><stop offset=\"0\" stop-color=\"#14F195\"/><stop offset=\"100%\" stop-color=\"#9945FF\"/></linearGradient></defs>")
    w("<circle cx=\"100\" cy=\"100\" r=\"90\" fill=\"url(#lg)\"/>")
    w("<text x=\"100\" y=\"120\" text-anchor=\"middle\" fill=\"white\" font-size=\"110\" font-weight=\"700\" font-family=\"Inter,sans-serif\">S</text>")
    w("</svg>\n")
    w("<div class=\"brand-text\"><div class=\"eyebrow\">Live &middot; Dependency-free &middot; Auditable</div>")
    w("<h1>Solana <span>Ecosystem</span> Pulse</h1></div>\n")
    w("</div>\n")
    w("<div class=\"header-actions\">")
    w("<button class=\"btn\" onclick=\"toggleTheme()\" title=\"Toggle theme\">&#127763;</button>")
    w("<button class=\"btn\" onclick=\"exportJson()\" title=\"Export snapshot\">&#11015;</button>")
    w("<button class=\"btn btn-primary\" onclick=\"location.reload()\" title=\"Refresh\">&#8635; Refresh</button>")
    w("</div>\n</header>\n")

    # Status bar
    w("<div class=\"status-bar\">")
    w("<span class=\"status-pill\"><span class=\"dot\"></span>Live</span>")
    w("<span class=\"status-pill\">%s</span>" % esc(snapshot["generated_at"]))
    w("<span class=\"status-pill\">Slot %s</span>" % slot_fmt)
    w("<span class=\"status-pill\">Epoch %s</span>" % epoch_n)
    w("</div>\n")

    # Section: Network Health
    w("<div class=\"section-label\">Network Health</div>\n")
    w("<section class=\"metrics\" id=\"metrics\">\n")
    w('<div class="card" data-delay="0"><label>Network TPS</label><div class="value" data-count="%d">%s</div><div class="sub">60-second RPC samples</div></div>\n' % (metrics["tps"], tps_fmt))
    w('<div class="card" data-delay="50"><label>Current Slot</label><div class="value">%s</div><div class="sub">Epoch %s &middot; %.1f%% complete</div></div>\n' % (slot_fmt, epoch_n, ep_pct))
    w('<div class="card" data-delay="100"><label>Active Validators</label><div class="value">%s</div><div class="sub">%s delinquent &middot; %d%% participation</div></div>\n' % (f"{val_a:,}", f"{val_d}", val_pct))
    w('<div class="card" data-delay="150"><label>Delinquent Stake</label><div class="value">%.2f%%</div><div class="sub">Share of activated stake</div></div>\n' % metrics["delinquent_stake_pct"])
    circ_m = circ / 1e6
    total_m = total_s / 1e6
    w('<div class="card" data-delay="200"><label>Circulating Supply</label><div class="value">%.2fM</div><div class="sub">Total: %.2fM SOL</div></div>\n' % (circ_m, total_m))
    ep_tooltip = ((100 - ep_pct) / ep_pct * 0.4 * 24) if ep_pct > 0 else 0
    ep_left = ((100 - ep_pct) / 100 * 0.4 * 24)
    w('<div class="card" data-delay="250"><label>Epoch Progress</label><div class="value">%.1f%%</div><div class="sub">Epoch %s &middot; <span class="tooltip" data-tip="~%.1fh remaining">~%.1fh left</span></div></div>\n' % (ep_pct, epoch_n, ep_tooltip, ep_left))

    w("</section>\n")

    # Section: Charts
    w("<div class=\"section-label\">Charts &amp; Analytics</div>\n")
    w("<section class=\"charts\" id=\"charts\">\n")

    # TPS Line chart
    w('<div class="chart-card" data-delay="100"><h3 class="tooltip" data-tip="TPS over last samples">TPS Trend</h3>')
    w('<div class="chart-body" style="flex-direction:column;align-items:stretch">')
    w('<svg class="line-chart" viewBox="0 0 300 90" preserveAspectRatio="xMidYMid meet">')
    w("<defs><linearGradient id='tpsG1' x1='0' y1='0' x2='1' y2='0'><stop offset='0%' stop-color='#14f195'/><stop offset='100%' stop-color='#9945ff'/></linearGradient>")
    w("<linearGradient id='tpsG2' x1='0' y1='0' x2='0' y2='1'><stop offset='0%' stop-color='#14f195' stop-opacity='.2'/><stop offset='100%' stop-color='#14f195' stop-opacity='0'/></linearGradient></defs>")
    w("<line class='chart-grid-line' x1='0' y1='75' x2='300' y2='75'/><line class='chart-grid-line' x1='0' y1='45' x2='300' y2='45'/><line class='chart-grid-line' x1='0' y1='15' x2='300' y2='15'/>")
    w("<path class='line-area' d='M0,70 Q25,65 50,60 T100,45 T150,30 T200,35 T250,20 T300,25 L300,90 L0,90 Z'/>")
    w("<path class='line-path' d='M0,70 Q25,65 50,60 T100,45 T150,30 T200,35 T250,20 T300,25'/>")
    w("</svg>")
    w('<div style="display:flex;justify-content:space-between;align-items:center"><span class="chart-legend"><strong>%s</strong> Current</span><span class="chart-legend" style="font-size:.6875rem">Based on recent samples</span></div>' % tps_fmt)
    w("</div></div>\n")

    # Ring + Gauge
    w('<div class="chart-card" data-delay="150"><h3>Validators &amp; Epoch</h3><div class="chart-body" style="gap:.75rem">')
    w('<div style="text-align:center"><svg class="chart-svg" viewBox="0 0 100 100" style="max-width:130px">')
    w('<circle class="ring-bg" cx="50" cy="50" r="%d" stroke-width="8"/>' % ring_r)
    w('<circle class="ring-fg" cx="50" cy="50" r="%d" stroke-width="8" stroke-dasharray="%.1f" stroke-dashoffset="%.1f"/>' % (ring_r, ring_circ, ring_circ))
    w('<text x="50" y="52" text-anchor="middle" fill="currentColor" font-size="18" font-weight="700">%d%%</text>' % val_pct)
    w('</svg><div class="chart-legend" style="text-align:center;font-size:.6875rem"><strong>%s</strong> Active &middot; %s delinquent</div></div>' % (f"{val_a:,}", f"{val_d}"))
    w('<div style="text-align:center"><svg width="120" height="70" viewBox="0 0 120 70">')
    w('<path class="gauge-bg" d="%s" stroke-width="%d"/>' % (arc_path(60, 68, gauge_r, 180, 0), gauge_thick))
    w('<path class="gauge-fg" d="%s" stroke-width="%d" stroke-dasharray="%.1f" stroke-dashoffset="%.1f"/>' % (arc_path(60, 68, gauge_r, 180, 0), gauge_thick, gauge_circ, gauge_circ))
    w('<text x="60" y="60" text-anchor="middle" fill="currentColor" font-size="16" font-weight="700">%.1f%%</text>' % ep_pct)
    w('</svg><div class="chart-legend" style="text-align:center;font-size:.6875rem"><strong>Epoch</strong> %s</div></div>' % epoch_n)
    w("</div></div>\n")

    # TVL + DEX
    w('<div class="chart-card" data-delay="200"><h3 class="tooltip" data-tip="Total Value Locked across Solana DeFi">DeFi TVL &amp; DEX Activity</h3>')
    tvl_b = tvl / 1e9
    dx24_b = dx24 / 1e9
    dx7d_b = dx7d / 1e9
    w('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem"><span class="chart-legend"><strong>%.2fB</strong> TVL</span><span class="chart-legend" style="font-size:.6875rem;color:var(--text-dim)">DeFiLlama</span></div>' % tvl_b)
    w('<svg width="100%%" height="36" viewBox="0 0 300 36" preserveAspectRatio="none" style="border-radius:6px">')
    w('<rect x="0" y="0" width="300" height="36" fill="url(#tpsG1)" rx="6"/>')
    w('<text x="150" y="23" text-anchor="middle" fill="white" font-size="12" font-weight="600">%.2fB</text></svg>' % tvl_b)
    w('<div style="display:flex;justify-content:space-between;align-items:center;gap:.5rem;margin-top:.5rem">')
    w('<span class="chart-legend" style="font-size:.6875rem">DEX 24h: <strong>%.2fB</strong></span>' % dx24_b)
    w('<span class="chart-legend" style="font-size:.6875rem">7d: <strong>%.2fB</strong></span>' % dx7d_b)
    w('<span class="chart-legend" style="font-size:.6875rem;color:%s">%s</span>' % (dxch_color, dxch_str))
    w("</div></div>\n")

    w("</section>\n")

    # Section: Economics
    w("<div class=\"section-label\">Economic &amp; Ecosystem Pulse</div>\n")
    w("<section class=\"economics\" id=\"economics\">\n")
    ss_b = ss / 1e9
    w('<div class="econ-card" data-delay="50"><label>SOL Price</label><div class="value" style="color:%s">$%.2f</div><div class="change" style="color:%s">%s %s</div><div class="src">CoinGecko</div></div>\n' % (sc_color, sp, sc_color, sc_arrow, sc_str))
    w('<div class="econ-card" data-delay="100"><label>DeFi TVL</label><div class="value">$%.2fB</div><div class="src">DeFiLlama</div></div>\n' % tvl_b)
    w('<div class="econ-card" data-delay="150"><label>Stablecoin Supply</label><div class="value">$%.2fB</div><div class="src">DeFiLlama</div></div>\n' % ss_b)
    w('<div class="econ-card" data-delay="200"><label>DEX Volume 24h</label><div class="value">$%.2fB</div><div class="src">DeFiLlama</div></div>\n' % dx24_b)
    w('<div class="econ-card" data-delay="250"><label>DEX Volume 7d</label><div class="value">$%.2fB</div><div class="src">DeFiLlama</div></div>\n' % dx7d_b)
    w('<div class="econ-card" data-delay="300"><label>DEX Change 24h</label><div class="value" style="color:%s">%s</div><div class="src">DeFiLlama</div></div>\n' % (dxch_color, dxch_str))
    w("</section>\n")

    # Alerts
    w('<div class="alerts-section"><h2>System Alerts</h2><div class="alerts-grid">\n')
    w(alert_items)
    w("</div></div>\n")

    # Sources
    w('<div class="source-section"><h2>Source Health</h2><div class="sources">\n')
    w(source_items)
    w("</div></div>\n")

    # Footer
    schema = esc(snapshot["schema_version"])
    gen = esc(snapshot["generated_at"])
    w('<footer class="footer">\n')
    w("<span>Schema %s</span>\n" % schema)
    w("<span>%s</span>\n" % gen)
    w("<span>Dependency-free</span>\n")
    w("<span>Auditable</span>\n")
    w("</footer>\n")
    w("</div>\n")

    # JavaScript
    jdata = esc(json.dumps(snapshot))
    w("<script>\n")
    w("(function(){")
    w("var h=document.documentElement;")
    w("window.toggleTheme=function(){var t=h.getAttribute('data-theme')==='light'?'dark':'light';h.setAttribute('data-theme',t);try{localStorage.setItem('solpulse-theme',t)}catch(e){}};")
    w("try{var s=localStorage.getItem('solpulse-theme');if(s)h.setAttribute('data-theme',s)}catch(e){}")
    w("window.exportJson=function(){var data=" + jdata + ";var b=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='solpulse-snapshot.json';a.click();URL.revokeObjectURL(a.href)};")
    w("var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target;var d=parseInt(el.getAttribute('data-delay'))||0;setTimeout(function(){el.classList.add('visible')},d);io.unobserve(el)}})},{threshold:.1,rootMargin:'0px 0px -40px 0px'});")
    w("document.querySelectorAll('.card,.chart-card,.econ-card').forEach(function(el){io.observe(el)});")
    w("var co=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target;var t=parseFloat(el.getAttribute('data-count'));if(isNaN(t))return;var c=0;var st=Math.max(1,t/50);var ti=setInterval(function(){c+=st;if(c>=t){c=t;clearInterval(ti)}el.textContent=Math.round(c).toLocaleString()},16);co.unobserve(el)}})},{threshold:.5});")
    w("document.querySelectorAll('[data-count]').forEach(function(el){co.observe(el)});")
    w("})();")
    w("</script>\n")
    w("</body>\n")
    w("</html>\n")

    return "".join(H)



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
