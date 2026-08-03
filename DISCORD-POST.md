## 🚀 Solana Ecosystem Pulse — Zeroclaw Submission

**Submitter:** Manuel Pérez  
**Repo:** https://github.com/xtent3/solana-ecosystem-pulse  
**Demo:** [VIDEO-ENLACE-AQUI]  
**Live dashboard:** https://xtent3.github.io/solana-ecosystem-pulse/dashboard.html  

---

### ¿Qué es?

Un monitor de salud de Solana que:
- Consulta RPC directo de Solana (sin API keys)
- Trae datos de CoinGecko y DeFiLlama
- Genera dashboard HTML en vivo (slot, TPS, validators, SOL price, DeFi TVL)
- Detecta anomalías (baja TPS, stake delinquente)

Ejecutable local: `python -m solpulse --output output`

---

### Why this case? (30%)

Caso real: lo uso diario para verificar salud de Solana antes de ejecutar operaciones.

---

### Security (25%)

- ✅ No API keys
- ✅ No firmas de transacciones
- ✅ No wallets
- ✅ Read-only monitor
- ✅ 100% dependencias públicas

Ver `SECURITY-AUDIT.md` para detalle.

---

### Craft (20%)

- Sin dependencias externas (puro stdlib + Internet)
- Fallas de fuente son visibles, no suplantadas con ceros
- Escritura atómica de archivos
- 18/18 tests pass

---

### Reproducibilidad (15%)

```bash
git clone https://github.com/xtent3/solana-ecosystem-pulse.git
cd solana-ecosystem-pulse
python -m solpulse --output output
python -m unittest discover -s tests -v
```

---

### Showcase (10%)

Demo de 1 minuto: https://youtu.be/[ENLACE]

---

### License

MIT — ver `LICENSE`
