# Solana Ecosystem Pulse

<p align="center">
  <strong>A dependency-free, auditable Solana ecosystem monitor.</strong><br>
  Real network data · No API keys · No packages · 18/18 tests
</p>

---

A single CLI command generates four timestamped artifacts from one coherent snapshot:

| Artifact | Format | Purpose |
|---|---|---|
| `snapshot.json` | Machine-readable | Auditable data with schema version |
| `report.md` | Markdown | Human-readable summary |
| `dashboard.html` | Classic HTML | Responsive self-contained dashboard |
| `premium_dashboard.html` | Premium HTML | Brand-styled showcase with SVG icons, Solana gradients, embedded logos |

**No API keys.** **No third-party Python packages.** **No signing or transactions.** Just public data rendered beautifully.

It combines direct Solana mainnet JSON-RPC data with public CoinGecko and DeFiLlama endpoints. Source failures remain visible and unavailable values are omitted rather than replaced with misleading zeroes.

## Live metrics

**Network:** slot, epoch progress, observed TPS, active/delinquent validators, delinquent stake, total and circulating SOL supply.

**Economics:** SOL price and 24h change, Solana DeFi TVL, stablecoin supply, DEX volume (24h/7d), and 24h DEX-volume change.

**Anomalies:** deterministic threshold alerts for low observed TPS and elevated delinquent stake.

## Quick start

Requirements: Python 3.11+ and Internet access. No API keys and no third-party Python packages are required.

```bash
python -m solpulse --output output
```

Generated files:

```text
output/
├── dashboard.html          # Classic dashboard
├── premium_dashboard.html  # Premium brand-styled showcase
├── report.md               # Human-readable summary
└── snapshot.json           # Machine-readable auditable data
```

Open `output/premium_dashboard.html` directly, or serve it locally:

```bash
python -m http.server 8000 --directory output
```

Then visit `http://127.0.0.1:8000/dashboard.html`.

## CLI

```bash
python -m solpulse \
  --endpoint https://api.mainnet-beta.solana.com \
  --output output \
  --timeout 30
```

| Option | Default | Purpose |
|---|---|---|
| `--endpoint` | Solana public mainnet RPC | Override the JSON-RPC endpoint |
| `--output` | `output` | Destination for all three artifacts |
| `--timeout` | `30` | Timeout in seconds for each public request |

## Data sources

| Source | Metrics | Authentication |
|---|---|---|
| Solana JSON-RPC | network, epoch, validators, supply | none |
| CoinGecko Simple Price API | SOL/USD and 24h change | none |
| DeFiLlama Chains API | Solana DeFi TVL | none |
| DeFiLlama Stablecoins API | Solana USD-pegged supply | none |
| DeFiLlama DEX Overview API | Solana DEX volume | none |

Every economic source is collected independently. If one endpoint fails, the network report and other economic metrics still render; `economics.sources` records `ok` or `error` with the endpoint and error detail.

## Architecture

```text
Solana RPC ───────► rpc.py ───────┐
                                  ├─► collector.py ─► one snapshot
Public HTTP APIs ─► market.py ────┘         │
                                             ├─► snapshot.json
                                             ├─► report.md
                                             └─► dashboard.html
```

- `rpc.py`: strict JSON-RPC transport; RPC errors never become data.
- `market.py`: independent source collection and normalization.
- `metrics.py`: unit conversion and derived network metrics.
- `anomalies.py`: explainable threshold checks.
- `collector.py`: creates one coherent timestamped snapshot.
- `render.py`: renders all formats from that same snapshot and HTML-escapes external text.
- `_premium.py`: premium brand renderer with SVG icons, Solana gradients, embedded base64 logos.
- `artifacts.py`: atomically replaces output files.
- `cli.py`: command-line orchestration.

## Automation

`.github/workflows/update-pulse.yml` runs the generator every six hours and on manual dispatch. It validates the test suite first, refreshes `output/`, and commits only changed report artifacts back to the current branch. The workflow uses no secrets or paid APIs.

For local scheduling, run `python -m solpulse --output output` at any interval using Task Scheduler or cron.

## Verification

```bash
python -m unittest discover -s tests -v
python -m compileall -q solpulse tests
python -m solpulse --output output
```

The test suite covers:

- strict RPC error handling;
- JSON-RPC request construction;
- network metric derivation;
- partial economic-source failure;
- anomaly detection;
- HTML escaping of untrusted external text;
- cross-format consistency;
- atomic artifact writes;
- end-to-end CLI generation with injected transports.

## Output schema

The root object uses `schema_version: solpulse/v1` and contains:

- `generated_at`: UTC snapshot timestamp;
- `source`: Solana RPC endpoint;
- `metrics`: normalized network metrics;
- `economics.metrics`: available economic values;
- `economics.sources`: endpoint-level health;
- `alerts`: deterministic network alerts.

See `output/snapshot.json` for a current sample.

## Interpretation and limitations

- Observed TPS is computed from the two most recent performance samples; it is not a historical average.
- Threshold alerts are operational signals, not proof of an outage and not financial advice.
- Public endpoints may rate-limit callers. Failures are reported explicitly.
- Values from different public sources are collected within one run but are not guaranteed to share the same upstream block or publication timestamp.
- This project intentionally avoids social feeds and API-key-dependent sources to keep setup reproducible.

## License

MIT — see [LICENSE](LICENSE).
