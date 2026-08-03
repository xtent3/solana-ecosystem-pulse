# Solana Ecosystem Pulse — Zeroclaw Submission

**Submitter:** Manuel Pérez  
**Repo:** https://github.com/xtent3/solana-ecosystem-pulse  
**Live demo:** `https://xtent3.github.io/solana-ecosystem-pulse/dashboard.html`  
**Zeroclaw bounty:** 5,000 USDG (7 tiers)  
**Deadline:** 2026-08-07 ~21:00 CDMX  

---

## Why this case? (30% score)

This project is a **real, autonomous Solana ecosystem monitor** that runs in production for Manuel's automated operations. It is not a test bot or a demo skeleton; it is a **production-grade dashboard** that:

- Provides **real-time network visibility** (slot, TPS, validators, epoch progress)
- Tracks **Solana DeFi economics** (TVL, stablecoin supply, DEX volume)
- Detects **operational anomalies** (low TPS, elevated delinquent stake)
- Runs **every 6 hours** via GitHub Actions with no human intervention
- Serves as a **monitoring tool** for manual review

It is the **exact tool** Manuel uses to verify Solana health before executing autonomous operations on-chain.

---

## Security (25% score)

| Aspect | Status |
|---|---|
| **API keys** | None required. All data comes from public endpoints. |
| **Signing transactions** | Not implemented. This is a **read-only** monitor. |
| **Wallet registration** | Not implemented. No on-chain actions are taken. |
| **Secrets management** | No secrets to manage. The codebase is clean. |
| **Dependency audit** | `pyproject.toml` pins exact versions. No transitive dependencies. |

**Custody model:** T0/T1 compatible — no private keys, no signature capability.

---

## Craft (20% score)

### Architecture

```text
Solana RPC ───────► rpc.py ───────┐
                                  ├─► collector.py ─► one snapshot
Public HTTP APIs ─► market.py ────┘         │
                                             ├─► snapshot.json
                                             ├─► report.md
                                             └─► dashboard.html
```

- **rpc.py**: strict JSON-RPC transport; RPC errors never become data.
- **market.py**: independent source collection (CoinGecko, DeFiLlama).
- **collector.py**: creates one coherent timestamped snapshot.
- **render.py**: renders all formats from the same snapshot; HTML-escapes external text.
- **artifacts.py**: atomically replaces output files.

### Features

- **No external Python packages** required — pure stdlib + Internet.
- **Independent economic sources** — if one fails, others still render.
- **Deterministic anomaly detection** — explainable thresholds for low TPS and delinquent stake.
- **Atomic writes** — output files are never half-written.

---

## Reproducibility (15% score)

### Local run

```bash
git clone https://github.com/xtent3/solana-ecosystem-pulse.git
cd solana-ecosystem-pulse
python -m solpulse --output output
```

### Tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q solpulse tests
```

All tests pass (18/18) on Windows and Linux.

### GitHub Actions

`.github/workflows/update-pulse.yml` runs every 6 hours and validates the test suite first.

---

## Showcase (10% score)

### Demo (5 s)

1. Open `output/dashboard.html` (self-contained, no server needed).
2. See real-time slot, TPS, validators, epoch progress.
3. Scroll to economics: SOL price, DeFi TVL, stablecoin supply, DEX volume.
4. Check alerts: any deterministic warnings.

### Live demo (1 min)

```bash
# Run in terminal
python -m solpulse --output output --timeout 45

# Serve locally (in a separate terminal)
python -m http.server 8000 --directory output
```

Visit `http://127.0.0.1:8000/dashboard.html` to see the live dashboard with current network metrics.

---

## What this project is NOT

- **Not a trading bot** — it does not place orders or manage funds.
- **Not a wallet service** — it does not store keys or sign transactions.
- **Not a social feed** — it does not monitor Twitter, Discord, or Telegram.

It is a **monitoring tool** — the same way a car dashboard shows speed and fuel, this shows Solana health.

---

## Next steps

Manuel uses this tool to:

1. Verify Solana health before executing operations.
2. Track DeFi adoption via TVL and volume metrics.
3. Detect anomalies that may require manual investigation.

If you use Solana, you can too.

---

## License

MIT — see [LICENSE](LICENSE).
