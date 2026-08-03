# Zeroclaw Submission — Checklist y Template

**Repo:** https://github.com/xtent3/solana-ecosystem-pulse  
**Bounty:** 5,000 USDG (7 tiers)  
**Deadline:** 2026-08-07 ~21:00 CDMX  

---

## ✅ Checklist de entrega (lo que ya está listo)

| Item | Status | Ubicación |
|---|---|---|
| Repo público en GitHub | ✅ | https://github.com/xtent3/solana-ecosystem-pulse |
| README-ZEROCRAWL.md | ✅ | Demo, security, craft, reproducibilidad |
| VIDEO-SCRIPT-ZEROCRAWL.md | ✅ | 1 minuto, sin voz necesaria |
| SECURITY-AUDIT.md | ✅ | T0/T1 compatible, sin keys, sin firmas |
| CLI ejecutable | ✅ | `python -m solpulse --output output` |
| Tests | ✅ | 18/18 tests pass |
| Dashboard HTML | ✅ | Auto-contenido, sin server |
| Automatización (cron) | ✅ | `.github/workflows/update-pulse.yml` |

---

## ⏳ Cosas que TÚ debes hacer (5 minutos)

### 1. Grabar video ≤3 minutos (3 minutos)

Usa el script en `VIDEO-SCRIPT-ZEROCRAWL.md`.

**Opciones:**
- **Con micrófono:** Grabar voz mientras muestras pantalla
- **Sin micrófono:** Usa texto en pantalla y graba solo acciones

**Herramientas gratuitas:**
- **OBS Studio** (Windows/macOS/Linux) — https://obsproject.com/
- **Camtasia** (trial gratis 14 días) — https://www.techsmith.com/video-editor.html

**Entregable:** Enlace a YouTube o Vimeo

---

### 2. Post para Discord (2 minutos)

Usa el template abajo.

**Entregable:** Copiar-pegar en el canal de Zeroclaw

---

## 📝 Template de post para Discord

```
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
```

---

## 📦 Archivos clave en el repo

| Archivo | Propósito |
|---|---|
| `README-ZEROCRAWL.md` | Presentación completa para Zeroclaw |
| `SECURITY-AUDIT.md` | Auditoría de seguridad (T0/T1 compatible) |
| `VIDEO-SCRIPT-ZEROCRAWL.md` | Script para video ≤3 min |
| `SUBMISSION.md` | Checklist original |
| `pyproject.toml` | Configuración (sin dependencias) |
| `solpulse/` | Código fuente |
| `tests/` | 18/18 tests pass |

---

## 📊 Evaluación por puntuación (Zeroclaw)

| Categoría | Tu caso | Puntuación estimada |
|---|---|---|
| Caso de uso real | ✅ Monitor de producción | 30/30 |
| Seguridad (T0/T1) | ✅ Sin keys, sin firmas | 25/25 |
| Craft | ✅ Sin deps, 18 tests | 18/20 |
| Reproducibilidad | ✅ CLI, tests, CI | 14/15 |
| Showcase | ⏳ (video pendiente) | 8/10 (estimado) |

**Total estimado:** ~95/100 (top 3 seguro, posiblemente top 1)

---

## 🔥 Next action (qué hacer AHORA)

1. **Grabar video** (usa el script en `VIDEO-SCRIPT-ZEROCRAWL.md`)
2. **Subir video** a YouTube/Vimeo
3. **Copiar-pegar** el template de Discord
4. **Pegar enlace al video** en el post de Discord
5. **Submit** antes del deadline

---

## ❓ Preguntas frecuentes

**¿Necesito editing profesional?**  
No. Zeroclaw valora casos reales, no producción cinematográfica. Grabación directa es suficiente.

**¿Puedo usar mi voz o texto en pantalla?**  
Ambas opciones están en el script. Sin micrófono: usa texto en pantalla.

**¿Qué pasa si no alcanzo el deadline?**  
El bounty cierra el 2026-08-07 ~21:00 CDMX. Sube antes, incluso con demo básica.

---

## 💡 Tips

- No esperes a tener el video perfecto — sube algo y mejora después
- El repo ya está en GitHub — solo falta el video y el post
- Si no tienes micrófono, usa texto en pantalla y graba solo pantalla
- Usa OBS Studio (gratis) para grabar — no necesitas Adobe Premiere

---

**¡Éxito con la submission!**