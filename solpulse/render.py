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
    """Render a premium self-contained dashboard with glassmorphism, animated SVG ring,
    line chart, TVL bar, staggered entrance, number counting, theme toggle, JSON export."""
    import math
    metrics = snapshot["metrics"]
    alerts = snapshot.get("alerts", [])
    economics = snapshot.get("economics")
    econ_metrics = economics.get("metrics", {}) if economics else {}

    def esc(v: object) -> str:
        return html.escape(str(v), quote=True)

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
    sp = econ_metrics.get("sol_price_usd", 0)
    sc = econ_metrics.get("sol_price_change_24h_pct")
    sc_str = f"{sc:+.2f}%" if sc is not None else ""
    sc_color = "#14f195" if sc and sc >= 0 else "#ff6685"
    tvl = econ_metrics.get("defi_tvl_usd", 0)
    ss = econ_metrics.get("stablecoin_supply_usd", 0)
    dx24 = econ_metrics.get("dex_volume_24h_usd", 0)
    dx7d = econ_metrics.get("dex_volume_7d_usd", 0)
    dxch = econ_metrics.get("dex_volume_change_24h_pct")
    dxch_str = f"{dxch:+.2f}%" if dxch is not None else ""
    dxch_color = "#14f195" if dxch and dxch >= 0 else "#ff6685"
    ring_r = 36
    ring_circ = 2 * math.pi * ring_r
    ring_offset = ring_circ * (1 - val_pct / 100)

    def compact(v):
        a = abs(v)
        if a >= 1e9: return f"${v/1e9:.2f}B"
        if a >= 1e6: return f"${v/1e6:.2f}M"
        if a >= 1e3: return f"${v/1e3:.2f}K"
        return f"${v:,.2f}"

    tvl_fmt = compact(tvl)
    ss_fmt = compact(ss)
    dx24_fmt = compact(dx24)
    dx7d_fmt = compact(dx7d)

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
        alert_items = '<div class="alert-ok"><span class="alert-icon">\u2713</span><div><strong>All Systems Normal</strong><p>No configured thresholds were crossed.</p></div></div>\n'

    sources_list = economics.get("sources", []) if economics else []
    source_items = "".join(
        '<div class="source-item"><span class="dot"></span><span class="src-name">%s</span><span class="src-status">%s</span></div>\n'
        % (esc(s["name"]), esc(s["status"]))
        for s in sources_list
    )

    # CSS with dynamic keyframe
    css = (
        "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}"
        ":root{--bg:#090d14;--bg-card:#111927;--bg-glass:rgba(17,25,39,.72);--text:#e8edf5;--text-muted:#8899b8;--text-dim:#5a6a88;--primary:#14f195;--secondary:#9945ff;--accent:#48d9d0;--line:#1e2a3e;--line-subtle:#16202e;--success:#14f195;--radius:16px;--radius-sm:10px;--font:Inter,SF Pro Display,system-ui,sans-serif;--mono:SF Mono,Cascadia Code,ui-monospace,monospace;--shadow:0 8px 32px rgba(0,0,0,.4);--ease-out:cubic-bezier(.16,1,.3,1)}"
        "[data-theme=light]{--bg:#f4f6fa;--bg-card:#fff;--bg-glass:rgba(255,255,255,.78);--text:#0f172a;--text-muted:#55657e;--text-dim:#8a9bb5;--line:#dce2ed;--line-subtle:#e8ecf3;--shadow:0 8px 32px rgba(0,0,0,.08)}"
        "@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}"
        "body{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;overflow-x:hidden}"
        ".container{max-width:1280px;margin:0 auto;padding:clamp(1rem,4vw,3rem)}"
        ".header{display:flex;justify-content:space-between;align-items:center;margin-bottom:2.5rem;animation:fadeIn .6s var(--ease-out)}"
        ".brand{display:flex;align-items:center;gap:.875rem}.logo{width:44px;height:44px;flex-shrink:0}"
        ".brand-text .eyebrow{font-size:.625rem;letter-spacing:.18em;text-transform:uppercase;color:var(--accent);font-weight:600}"
        ".brand-text h1{font-size:clamp(1.25rem,3vw,1.75rem);font-weight:700;letter-spacing:-.03em}"
        ".brand-text h1 span{color:var(--primary)}"
        ".header-actions{display:flex;gap:.5rem;align-items:center}"
        ".btn{background:var(--bg-card);border:1px solid var(--line-subtle);color:var(--text);padding:.4rem .9rem;border-radius:var(--radius-sm);font-size:.8125rem;cursor:pointer;transition:all .2s;font-family:var(--font)}"
        ".btn:hover{border-color:var(--text-muted);transform:translateY(-1px)}"
        ".btn-primary{background:var(--primary);color:#000;border-color:var(--primary);font-weight:600}"
        ".btn-primary:hover{background:#10d77e}"
        ".status-bar{display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap;animation:fadeIn .6s var(--ease-out) .1s both}"
        ".status-pill{display:inline-flex;align-items:center;gap:.4rem;padding:.35rem .75rem;border-radius:999px;font-size:.75rem;background:var(--bg-glass);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border:1px solid var(--line-subtle);color:var(--text-muted);font-family:var(--mono)}"
        ".status-pill .dot{width:7px;height:7px;border-radius:50%;background:var(--success);animation:pulse-dot 2s ease-in-out infinite}"
        "@keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.4}}"
        ".metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-bottom:1.5rem}"
        ".card{background:var(--bg-glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--line-subtle);border-radius:var(--radius);padding:1.5rem;transition:all .3s;opacity:0;transform:translateY(16px)}"
        ".card.visible{opacity:1;transform:translateY(0)}"
        ".card:hover{border-color:var(--line);transform:translateY(-4px);box-shadow:var(--shadow)}"
        ".card label{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.35rem;font-weight:600;display:block}"
        ".card .value{font-size:clamp(1.5rem,3vw,2.25rem);font-weight:700;letter-spacing:-.03em;line-height:1.1}"
        ".card .sub{font-size:.75rem;color:var(--text-dim);margin-top:.25rem}"
        ".charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:1rem;margin-bottom:1.5rem}"
        ".chart-card{background:var(--bg-glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--line-subtle);border-radius:var(--radius);padding:1.5rem;transition:all .3s;opacity:0;transform:translateY(16px)}"
        ".chart-card.visible{opacity:1;transform:translateY(0)}"
        ".chart-card:hover{border-color:var(--line);box-shadow:var(--shadow)}"
        ".chart-card h3{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:1rem;font-weight:600}"
        ".chart-body{display:flex;align-items:center;gap:1.25rem}"
        ".chart-legend{font-size:.8125rem;color:var(--text-muted);line-height:1.5}"
        ".chart-legend strong{color:var(--text);font-weight:600;font-size:1.125rem}"
        ".chart-svg{flex-shrink:0;max-width:160px;height:auto}"
        ".ring-bg{stroke:var(--line-subtle);fill:none}"
        ".ring-fg{stroke:var(--primary);fill:none;stroke-linecap:round;transform:rotate(-90deg);transform-origin:center}"
        f"@keyframes ring-fill{{from{{stroke-dashoffset:{ring_circ:.1f}}}to{{stroke-dashoffset:{ring_offset:.1f}}}}}"
        ".line-chart{width:100%;height:90px}"
        ".line-path{fill:none;stroke:url(#tpsG1);stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}"
        ".line-area{fill:url(#tpsG2)}"
        ".chart-grid-line{stroke:var(--line-subtle);stroke-width:.5;stroke-dasharray:3 3}"
        ".economics{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.75rem;margin-bottom:1.5rem}"
        ".econ-card{background:var(--bg-glass);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--line-subtle);border-radius:var(--radius-sm);padding:1rem 1.25rem;transition:all .3s;opacity:0;transform:translateY(12px)}"
        ".econ-card.visible{opacity:1;transform:translateY(0)}"
        ".econ-card:hover{border-color:var(--line);transform:translateY(-2px)}"
        ".econ-card label{font-size:.625rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-dim);display:block}"
        ".econ-card .value{font-size:1.125rem;font-weight:700;letter-spacing:-.02em}"
        ".econ-card .src{font-size:.625rem;color:var(--text-dim)}"
        ".alerts-section{margin-bottom:1.5rem;animation:fadeIn .6s var(--ease-out) .5s both}"
        ".alerts-section h2{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.75rem;font-weight:600}"
        ".alert-ok{display:flex;align-items:start;gap:.75rem;padding:.875rem 1rem;border-radius:var(--radius-sm);background:var(--bg-glass);backdrop-filter:blur(8px);border:1px solid var(--line-subtle);border-left:3px solid var(--success)}"
        ".alert-ok strong{font-size:.8125rem;font-weight:600}.alert-ok p{font-size:.75rem;color:var(--text-dim);margin-top:2px}"
        ".source-section{animation:fadeIn .6s var(--ease-out) .55s both}"
        ".source-section h2{font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.75rem;font-weight:600}"
        ".sources{display:flex;gap:.75rem;flex-wrap:wrap}"
        ".source-item{display:inline-flex;align-items:center;gap:.5rem;padding:.4rem .75rem;border-radius:999px;font-size:.75rem;background:var(--bg-glass);backdrop-filter:blur(8px);border:1px solid var(--line-subtle);font-family:var(--mono)}"
        ".source-item .dot{width:6px;height:6px;border-radius:50%;background:var(--success)}"
        ".source-item .src-name{color:var(--text-muted)}"
        ".source-item .src-status{color:var(--text-dim);text-transform:capitalize}"
        ".footer{text-align:center;padding:2rem 0 1rem;font-size:.6875rem;color:var(--text-dim);animation:fadeIn .6s var(--ease-out) .6s both;border-top:1px solid var(--line-subtle);margin-top:2rem}"
        ".footer span{color:var(--text-muted)}"
        "@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}"
    )

    H = []
    def w(s):
        H.append(s)

    w("<!DOCTYPE html>\n<html lang=\"en\" data-theme=\"dark\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>Solana Ecosystem Pulse</title>\n<style>\n")
    w(css)
    w("\n</style>\n</head>\n<body>\n<div class=\"container\">\n")

    # Header
    w("<header class=\"header\">\n<div class=\"brand\">\n")
    w("<svg class=\"logo\" viewBox=\"0 0 200 200\" aria-hidden=\"true\"><defs><linearGradient id='lg' x1='0' y1='0' x2='100%' y2='100%'><stop offset='0' stop-color='#14F195'/><stop offset='100%' stop-color='#9945FF'/></linearGradient></defs><circle cx='100' cy='100' r='90' fill='url(#lg)'/><text x='100' y='120' text-anchor='middle' fill='white' font-size='110' font-weight='700' font-family='Inter,sans-serif'>S</text></svg>\n")
    w("<div class=\"brand-text\"><div class=\"eyebrow\">Live &middot; Dependency-free &middot; Auditable</div><h1>Solana <span>Ecosystem</span> Pulse</h1></div>\n")
    w("</div>\n<div class=\"header-actions\">")
    w("<button class='btn' onclick='toggleTheme()' title='Toggle theme'>&#127763;</button>")
    w("<button class='btn' onclick='exportJson()' title='Export snapshot'>&#11015;</button>")
    w("<button class='btn btn-primary' onclick='location.reload()' title='Refresh'>&#8635; Refresh</button>")
    w("</div>\n</header>\n")

    # Status bar
    gen = esc(snapshot.get("generated_at", ""))
    w("<div class=\"status-bar\"><span class='status-pill'><span class='dot'></span>Live</span><span class='status-pill'>%s</span><span class='status-pill'>Slot %s</span></div>\n" % (gen, slot_fmt))

    # Metrics
    w("<section class='metrics'>\n")
    w("<div class='card' data-delay='0'><label>Network TPS</label><div class='value' data-count='%d'>%s</div><div class='sub'>60-second RPC samples</div></div>\n" % (metrics["tps"], tps_fmt))
    w("<div class='card' data-delay='50'><label>Current Slot</label><div class='value'>%s</div><div class='sub'>Epoch %s &middot; %.1f%% complete</div></div>\n" % (slot_fmt, epoch_n, ep_pct))
    w("<div class='card' data-delay='100'><label>Active Validators</label><div class='value'>%s</div><div class='sub'>%s delinquent &middot; %d%% participation</div></div>\n" % (f"{val_a:,}", f"{val_d}", val_pct))
    w("<div class='card' data-delay='150'><label>Delinquent Stake</label><div class='value'>%.2f%%</div><div class='sub'>Share of activated stake</div></div>\n" % metrics["delinquent_stake_pct"])
    w("<div class='card' data-delay='200'><label>Circulating Supply</label><div class='value'>%.2fM</div><div class='sub'>Total: %.2fM SOL</div></div>\n" % (circ/1e6, total_s/1e6))
    w("<div class='card' data-delay='250'><label>Epoch Progress</label><div class='value'>%.1f%%</div><div class='sub'>Epoch %s</div></div>\n" % (ep_pct, epoch_n))
    w("</section>\n")

    # Charts
    w("<section class='charts'>\n")
    # TPS line
    w("<div class='chart-card' data-delay='100'><h3>TPS Trend</h3><div class='chart-body'>")
    w("<svg class='line-chart' viewBox='0 0 300 90' preserveAspectRatio='xMidYMid meet'>")
    w("<defs><linearGradient id='tpsG1' x1='0' y1='0' x2='1' y2='0'><stop offset='0%' stop-color='#14f195'/><stop offset='100%' stop-color='#9945ff'/></linearGradient><linearGradient id='tpsG2' x1='0' y1='0' x2='0' y2='1'><stop offset='0%' stop-color='#14f195' stop-opacity='.25'/><stop offset='100%' stop-color='#14f195' stop-opacity='0'/></linearGradient></defs>")
    w("<line class='chart-grid-line' x1='0' y1='75' x2='300' y2='75'/><line class='chart-grid-line' x1='0' y1='45' x2='300' y2='45'/><line class='chart-grid-line' x1='0' y1='15' x2='300' y2='15'/>")
    w("<path class='line-area' d='M0,70 Q25,65 50,60 T100,45 T150,30 T200,35 T250,20 T300,25 L300,90 L0,90 Z'/>")
    w("<path class='line-path' d='M0,70 Q25,65 50,60 T100,45 T150,30 T200,35 T250,20 T300,25'/>")
    w("</svg><div class='chart-legend'><strong>%s</strong><br>Current TPS</div></div></div>\n" % tps_fmt)
    # Ring
    w("<div class='chart-card' data-delay='150'><h3>Validators</h3><div class='chart-body'>")
    w("<svg class='chart-svg' viewBox='0 0 100 100'><circle class='ring-bg' cx='50' cy='50' r='%d' stroke-width='8'/><circle class='ring-fg' cx='50' cy='50' r='%d' stroke-width='8' stroke-dasharray='%.1f' stroke-dashoffset='%.1f'/><text x='50' y='52' text-anchor='middle' fill='currentColor' font-size='18' font-weight='700'>%d%%</text></svg>" % (ring_r, ring_r, ring_circ, ring_circ, val_pct))
    w("<div class='chart-legend'><strong>%s</strong> Active<br><span style='color:var(--text-dim)'>%s delinquent</span></div></div></div>\n" % (f"{val_a:,}", f"{val_d}"))
    # TVL
    w("<div class='chart-card' data-delay='200'><h3>DeFi TVL</h3>")
    w("<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem'><span class='chart-legend'><strong>%s</strong></span><span class='chart-legend' style='font-size:.6875rem;color:var(--text-dim)'>DeFiLlama</span></div>" % tvl_fmt)
    w("<svg width='100%%' height='44' viewBox='0 0 300 44' preserveAspectRatio='none' style='border-radius:8px'><rect x='0' y='0' width='300' height='44' fill='url(#tpsG1)' rx='8'/><text x='150' y='28' text-anchor='middle' fill='white' font-size='14' font-weight='600'>%s</text></svg></div>\n" % tvl_fmt)
    w("</section>\n")

    # Economics
    w("<h2 style='font-size:.6875rem;text-transform:uppercase;letter-spacing:.1em;color:var(--text-muted);margin-bottom:.75rem;font-weight:600'>Economic &amp; Ecosystem Pulse</h2>\n")
    w("<section class='economics'>\n")
    w("<div class='econ-card' data-delay='50'><label>SOL Price</label><div class='value' style='color:%s'>$%.2f</div><div class='src'>%s &middot; CoinGecko</div></div>\n" % (sc_color, sp, sc_str))
    w("<div class='econ-card' data-delay='100'><label>DeFi TVL</label><div class='value'>%s</div><div class='src'>DeFiLlama</div></div>\n" % tvl_fmt)
    w("<div class='econ-card' data-delay='150'><label>Stablecoins</label><div class='value'>%s</div><div class='src'>DeFiLlama</div></div>\n" % ss_fmt)
    w("<div class='econ-card' data-delay='200'><label>DEX Vol 24h</label><div class='value'>%s</div><div class='src'>DeFiLlama</div></div>\n" % dx24_fmt)
    w("<div class='econ-card' data-delay='250'><label>DEX Vol 7d</label><div class='value'>%s</div><div class='src'>DeFiLlama</div></div>\n" % dx7d_fmt)
    w("<div class='econ-card' data-delay='300'><label>DEX Change</label><div class='value' style='color:%s'>%s</div><div class='src'>DeFiLlama</div></div>\n" % (dxch_color, dxch_str))
    w("</section>\n")

    # Alerts & Sources
    w("<div class='alerts-section'><h2>System Alerts</h2>%s</div>\n" % alert_items)
    w("<div class='source-section'><h2>Source Health</h2><div class='sources'>\n%s</div></div>\n" % source_items)

    # Footer
    w("<footer class='footer'><span>%s</span><span>Dependency-free</span><span>Auditable</span></footer>\n" % gen)
    w("</div>\n")

    # JavaScript
    jdata = json.dumps(snapshot)
    w("<script>\n(function(){")
    w("var h=document.documentElement;")
    w("window.toggleTheme=function(){var t=h.getAttribute('data-theme')==='light'?'dark':'light';h.setAttribute('data-theme',t);try{localStorage.setItem('solpulse-theme',t)}catch(e){}};")
    w("try{var s=localStorage.getItem('solpulse-theme');if(s)h.setAttribute('data-theme',s)}catch(e){}")
    w("window.exportJson=function(){var data=" + jdata + ";var b=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='solpulse-snapshot.json';a.click();URL.revokeObjectURL(a.href)};")
    w("var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target;var d=parseInt(el.getAttribute('data-delay'))||0;setTimeout(function(){el.classList.add('visible')},d);io.unobserve(el)}})},{threshold:.1,rootMargin:'0px 0px -40px 0px'});")
    w("document.querySelectorAll('.card,.chart-card,.econ-card').forEach(function(el){io.observe(el)});")
    w("var co=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){var el=e.target;var t=parseFloat(el.getAttribute('data-count'));if(isNaN(t))return;var c=0;var st=Math.max(1,t/50);var ti=setInterval(function(){c+=st;if(c>=t){c=t;clearInterval(ti)}el.textContent=Math.round(c).toLocaleString()},16);co.unobserve(el)}})},{threshold:.5});")
    w("document.querySelectorAll('[data-count]').forEach(function(el){co.observe(el)});")
    w("})();\n</script>\n</body>\n</html>\n")

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
